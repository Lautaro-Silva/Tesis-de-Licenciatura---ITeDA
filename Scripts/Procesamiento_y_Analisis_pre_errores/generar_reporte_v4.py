#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para generar un reporte en PDF del análisis de datos de simulaciones.
Toma una carpeta de archivos parquet como entrada.

Uso:
  python generar_reporte.py /ruta/a/tu/carpeta/parquet
"""

import os
import glob
import sys
import io
import argparse
import traceback
from datetime import datetime

# --- Imports de tu análisis ---
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Modo no-interactivo
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit

# --- Imports para el PDF ---
from fpdf import FPDF
from fpdf.enums import XPos, YPos 

# =============================================================================
# 1. CLASE Y FUNCIONES AUXILIARES PARA EL PDF
# =============================================================================

class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, "Reporte de Análisis de Datos (Simulaciones)", 0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 5, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", border=0, align="C")

    def add_title_page(self, folder_path, file_count, total_modules, total_events):
        self.add_page()
        self.set_font("DejaVu", "B", 24)
        self.cell(0, 30, "Reporte de Análisis", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_font("DejaVu", "", 12)
        self.multi_cell(0, 10, f"Este documento resume el análisis de los datos de simulación encontrados en la siguiente carpeta:", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_font("DejaVuMono", "", 10)
        self.multi_cell(0, 8, f"{folder_path}", align="L", border=1, 
                        padding=5, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_font("DejaVu", "", 12)
        self.ln(10)
        self.multi_cell(0, 10, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.multi_cell(0, 10, f"Archivos procesados: {file_count}", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.multi_cell(0, 10, f"Total de módulos (filas): {total_modules:,}", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.multi_cell(0, 10, f"Total de eventos (lluvias): {total_events:,}", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)

def add_heading(pdf, text, level=1):
    if level == 1:
        if pdf.get_y() > 200: pdf.add_page()
        else: pdf.ln(10)
        pdf.set_font("DejaVu", "B", 16)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, text, fill=True, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
    elif level == 2:
        if pdf.get_y() > 220: pdf.add_page()
        else: pdf.ln(5)
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, text, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

def add_body_text(pdf, text, is_mono=False):
    if is_mono: pdf.set_font("DejaVuMono", size=9)
    else: pdf.set_font("DejaVu", size=10)
    pdf.multi_cell(0, 5, str(text))
    pdf.ln(2)

def add_dataframe(pdf, df, title=""):
    if title: add_heading(pdf, title, level=2)
    df_text = df.to_string()
    add_body_text(pdf, df_text, is_mono=True)

def add_plot(pdf, fig=None):
    if fig is None: fig = plt.gcf()
    buf = io.BytesIO()
    try: fig.tight_layout(pad=1.5)
    except Exception: pass 
    fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    buf.seek(0)
    page_width = pdf.w - 2 * pdf.l_margin
    img_height = page_width * 0.7 
    if pdf.get_y() + img_height > pdf.page_break_trigger: pdf.add_page()
    pdf.image(buf, x=pdf.l_margin, w=page_width)
    pdf.ln(5)
    buf.close()
    plt.close(fig)

# =============================================================================
# 2. LÓGICA DE ANÁLISIS
# =============================================================================

# --- ❗️ 1. FUNCIÓN DE FIT (CORREGIDA: A0=1, phi0=0 FIJOS) ❗️ ---
def fit_func_deg_fixed(phi_deg, A1):
    """
    A1 = Amplitud de la asimetría.
    A0 fijo en 1.0.
    phi0 fijo en 0.0 grados.
    """
    return 1.0 * (1 + A1 * np.cos(np.deg2rad(phi_deg)))


def run_analysis(df_new, pdf):
    
    # --- 1. Resumen Inicial ---
    add_heading(pdf, "1. Resumen de Datos")
    add_body_text(pdf, f"DataFrame cargado con {len(df_new)} filas.")
    add_dataframe(pdf, df_new.head(), title="df_new.head()")

    # --- 2. DataFrame de Eventos ---
    event_cols = ["event_id", "logE_MC", "theta_MC", "phi_MC", "primary", "logE_REC", "theta_REC", "phi_REC"]
    df_events = df_new[event_cols].drop_duplicates()
    add_body_text(pdf, f"Eventos únicos: {len(df_events):,}")

    # --- 3. Gráfico 3D ---
    add_heading(pdf, "2. Visualización 3D de Muones")
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    df_plot = df_new[(df_new['nMuones'] > 0) & (df_new['r_core'] < 3000)]
    sc = ax.scatter(df_plot["r_core"], df_plot["theta_REC"], df_plot["nMuones"],
                    c=df_plot["nMuones"], cmap="viridis", alpha=0.7, s=10)
    ax.set_xlabel("Distancia al core [m]"); ax.set_ylabel(r"$\theta_{REC}$ [°]"); ax.set_zlabel("N Muones")
    cbar = plt.colorbar(sc, pad=0.1, shrink=0.8); cbar.set_label("N Muones")
    ax.view_init(elev=30, azim=310)
    add_plot(pdf, fig)
    
    # --- 4. Resolución de Energía ---
    add_heading(pdf, "3. Análisis de Resolución")
    add_heading(pdf, "--- 3.1. Energía (logE) ---", level=2)
    df_events_clean = df_events.dropna(subset=['logE_MC', 'logE_REC'])
    deltaE = df_events_clean["logE_REC"] - df_events_clean["logE_MC"]
    
    # Fit lineal robusto
    umbral_E = 0.9
    df_fit = df_events_clean[(deltaE.abs() < umbral_E)]
    coefs = np.polyfit(df_fit["logE_MC"], df_fit["logE_REC"], 1)
    
    fig_e = plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.scatter(df_events_clean["logE_MC"], df_events_clean["logE_REC"], s=5, alpha=0.3)
    plt.plot([17, 18.5], [17, 18.5], 'r--')
    x_line = np.linspace(17, 18.5, 100)
    plt.plot(x_line, np.polyval(coefs, x_line), 'g-', label=f'Fit: y={coefs[0]:.2f}x + {coefs[1]:.2f}')
    plt.legend(); plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.hist(deltaE, bins=100, range=(-0.9, 0.9), alpha=0.7, color='steelblue')
    plt.grid(True)
    add_plot(pdf, fig_e)
    
    # Residuales
    fig_res = plt.figure(figsize=(10, 4))
    plt.scatter(df_events_clean["logE_MC"], deltaE, s=5, alpha=0.3)
    plt.axhline(deltaE.mean(), color='r', linestyle='--')
    plt.ylim(-0.6, 0.6); plt.grid(True)
    plt.title("Residuales Energía")
    add_plot(pdf, fig_res)

    # --- 5. Resolución Angular ---
    add_heading(pdf, "--- 3.2. Resolución Angular ---", level=2)
    fig_ang = plt.figure(figsize=(12, 5))
    
    # Theta
    plt.subplot(1, 2, 1)
    delta_theta = df_events["theta_REC"] - df_events["theta_MC"]
    plt.hist(delta_theta, bins=100, range=(-5, 5), color='orange', alpha=0.7)
    plt.title(r"$\Delta \theta$")
    
    # Phi
    plt.subplot(1, 2, 2)
    delta_phi = (df_events["phi_REC"] - df_events["phi_MC"] + 180) % 360 - 180
    plt.hist(delta_phi, bins=100, range=(-15, 15), color='green', alpha=0.7)
    plt.title(r"$\Delta \phi$")
    add_plot(pdf, fig_ang)

    # --- 6. Uniformidad ---
    add_heading(pdf, "4. Uniformidad por Counter")
    df_counters = df_new.groupby(['event_id', 'counterId'])['nMuones'].sum().reset_index()
    counter_stats = df_counters.groupby('counterId')['nMuones'].agg(mean='mean', std='std').reset_index()
    # Filtrar sin señal para limpiar plot
    counter_stats = counter_stats[counter_stats['mean'] > 0]
    counter_stats['id_str'] = counter_stats['counterId'].astype(str)
    
    fig_unif, axs = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
    axs[0].bar(counter_stats['id_str'], counter_stats['mean'], color='skyblue'); axs[0].set_ylabel("Mean")
    axs[1].bar(counter_stats['id_str'], counter_stats['std'], color='salmon'); axs[1].set_ylabel("Std")
    plt.xticks(rotation=90); plt.tight_layout()
    add_plot(pdf, fig_unif)

    # --- 7. MAPAS POLARES ---
    add_heading(pdf, "5. Mapas Polares (Muones)")
    
    # Configuración Binning
    phi_bins = 24
    phi_edges = np.linspace(0, 2*np.pi, phi_bins + 1)
    r_bins = np.arange(0, 510, 10)
    R, Phi = np.meshgrid(r_bins, phi_edges)

    theta_bins_deg = [0, 21.8, 31.6, 40.0, 47.9, 56.0, 65.3] # Aprox based on sin2
    N_theta_bins = len(theta_bins_deg) - 1
    
    if 's2_theta' not in df_new.columns:
        df_new['s2_theta'] = np.sin(np.deg2rad(df_new['theta_REC']))**2
    
    # Calcular bins de theta
    s2_bins = np.sin(np.deg2rad(theta_bins_deg))**2
    df_new['theta_bin'] = pd.cut(df_new['s2_theta'], bins=s2_bins, labels=False, include_lowest=True)
    
    df_mapa = df_new[(df_new['r_core'] < 500) & (df_new['nMuones'].notna())].copy()

    for i in range(N_theta_bins):
        df_slice = df_mapa[df_mapa['theta_bin'] == i]
        if df_slice.empty: continue
            
        Z, _, _ = np.histogram2d(df_slice['r_core'], df_slice['phi_plane'], bins=[r_bins, phi_edges], weights=df_slice['nMuones'])
        counts, _, _ = np.histogram2d(df_slice['r_core'], df_slice['phi_plane'], bins=[r_bins, phi_edges])
        
        with np.errstate(divide='ignore', invalid='ignore'):
            Z_avg = Z.T / counts.T
            Z_avg[counts.T == 0] = 0
            
        fig_pol, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        c = ax.pcolormesh(Phi, R, Z_avg, cmap='viridis', shading='auto')
        ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
        plt.title(f"Bin Theta {i}: [{theta_bins_deg[i]:.1f}, {theta_bins_deg[i+1]:.1f}] deg")
        add_plot(pdf, fig_pol)

    # --- 8. ANÁLISIS DE ASIMETRÍA (FIT FIJO) ---
    add_heading(pdf, "6. Asimetría Azimutal (Anillo Denso)")
    add_body_text(pdf, "Fit realizado con A0=1.0 y phi0=0.0 fijos.")
    
    # Preparar datos (Limpieza y filtrado ID)
    status_buenos = ['candidate', 'rejected', 'saturated']
    # ❗️ SIN FILTRO DE SATURACIÓN (comentado)
    df_asym = df_new[df_new['module_status'].isin(status_buenos)].copy()
    
    # Convertir a grados centrado
    phi_deg = np.rad2deg(df_asym['phi_plane'])
    df_asym['phi_deg'] = (phi_deg + 180) % 360 - 180
    
    # Filtrar Anillo Denso
    df_denso = df_asym[(df_asym['counterId'] >= 90000) & (df_asym['counterId'] < 100000)].copy()
    
    # Bins para el plot 1D
    phi_1d_bins = 24
    phi_1d_edges = np.linspace(-180, 180, phi_1d_bins + 1)
    phi_1d_centers = (phi_1d_edges[:-1] + phi_1d_edges[1:]) / 2.0
    
    fit_results = []

    for i in range(N_theta_bins):
        df_bin = df_denso[
            (df_denso['theta_bin'] == i) & 
            (df_denso['sdSignal'].notna()) & 
            (df_denso['nMuones'].notna())
        ].copy()
        
        if len(df_bin) < 50: continue
            
        title_str = f"Theta [{theta_bins_deg[i]:.1f}, {theta_bins_deg[i+1]:.1f}]"
        add_body_text(pdf, f"Procesando {title_str}...")
        
        # --- GroupBy para UMD y SD ---
        df_bin['phi_bin_idx'] = pd.cut(df_bin['phi_deg'], bins=phi_1d_edges, labels=False, include_lowest=True)
        
        stats = df_bin.groupby('phi_bin_idx').agg(
            umd_mean=('nMuones', 'mean'), umd_std=('nMuones', 'std'), umd_n=('nMuones', 'count'),
            sd_mean=('sdSignal', 'mean'), sd_std=('sdSignal', 'std'), sd_n=('sdSignal', 'count')
        )
        
        # SEM y Normalización
        stats['umd_sem'] = stats['umd_std'] / np.sqrt(stats['umd_n'])
        stats['sd_sem'] = stats['sd_std'] / np.sqrt(stats['sd_n'])
        
        norm_umd = stats['umd_mean'].mean()
        norm_sd = stats['sd_mean'].mean()
        
        stats['umd_y'] = stats['umd_mean'] / norm_umd
        stats['umd_err'] = stats['umd_sem'] / norm_umd
        stats['sd_y'] = stats['sd_mean'] / norm_sd
        stats['sd_err'] = stats['sd_sem'] / norm_sd
        
        x_vals = phi_1d_centers[stats.index.astype(int)]
        
        # --- Plot ---
        fig_fit, axs = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
        
        # UMD
        axs[0].errorbar(x_vals, stats['umd_y'], yerr=stats['umd_err'], fmt='o', color='navy', label='UMD')
        try:
            # ❗️ FIT FIJO (solo p0=[0.05])
            popt, pcov = curve_fit(fit_func_deg_fixed, x_vals, stats['umd_y'], p0=[0.05], sigma=stats['umd_err'])
            A1, A1_err = popt[0], np.sqrt(pcov[0,0])
            
            x_smooth = np.linspace(-180, 180, 100)
            axs[0].plot(x_smooth, fit_func_deg_fixed(x_smooth, *popt), 'b--', label=rf'Fit $A_1={A1:.4f} \pm {A1_err:.4f}$')
            
            fit_results.append({'theta_idx': i, 'range': title_str, 'det': 'UMD', 'A1': A1, 'A1_err': A1_err})
        except: pass
        axs[0].set_title("UMD (nMuones)"); axs[0].legend()
        
        # SD
        axs[1].errorbar(x_vals, stats['sd_y'], yerr=stats['sd_err'], fmt='o', color='darkred', label='SD')
        try:
            # ❗️ FIT FIJO
            popt, pcov = curve_fit(fit_func_deg_fixed, x_vals, stats['sd_y'], p0=[0.05], sigma=stats['sd_err'])
            A1, A1_err = popt[0], np.sqrt(pcov[0,0])
            
            axs[1].plot(x_smooth, fit_func_deg_fixed(x_smooth, *popt), 'r--', label=rf'Fit $A_1={A1:.4f} \pm {A1_err:.4f}$')
            
            fit_results.append({'theta_idx': i, 'range': title_str, 'det': 'SD', 'A1': A1, 'A1_err': A1_err})
        except: pass
        axs[1].set_title("SD (sdSignal)"); axs[1].legend()
        
        for ax in axs:
            ax.set_xlim(-180, 180); ax.axhline(1, color='gray', linestyle=':')
            ax.set_xticks(np.arange(-180, 181, 90))
        
        add_plot(pdf, fig_fit)

    # --- 9. Tabla Resumen ---
    add_heading(pdf, "7. Tabla de Resultados (A1)")
    if fit_results:
        df_res = pd.DataFrame(fit_results)
        add_dataframe(pdf, df_res)
    else:
        add_body_text(pdf, "No se obtuvieron resultados de fit.")
        
    add_body_text(pdf, "\n--- FIN ---")

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path", type=str)
    args = parser.parse_args()
    
    folder_path = os.path.abspath(args.folder_path)
    if not os.path.isdir(folder_path):
        print("Directorio no válido.")
        return

    base_name = os.path.basename(folder_path.rstrip(os.sep))
    out_name = f"Reporte_{base_name}.pdf"
    
    print(f"Procesando: {folder_path}")
    
    pdf = PDF()
    # Cargar fuentes (ajustar paths si es necesario)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pdf.add_font("DejaVu", "", os.path.join(script_dir, "DejaVuSans.ttf"))
        pdf.add_font("DejaVu", "B", os.path.join(script_dir, "DejaVuSans-Bold.ttf"))
        pdf.add_font("DejaVuMono", "", os.path.join(script_dir, "DejaVuSansMono.ttf"))
        pdf.set_font("DejaVu", size=10)
    except:
        print("Advertencia: Fuentes DejaVu no encontradas. Usando default.")
        pdf.set_font("Arial", size=10)

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()

    try:
        files = glob.glob(os.path.join(folder_path, "*.parquet"))
        if not files: raise Exception("No hay parquets.")
        
        # Carga única
        df_list = [pd.read_parquet(f) for f in files]
        df_new = pd.concat(df_list, ignore_index=True)
        
        # Portada
        pdf.add_title_page(folder_path, len(files), len(df_new), df_new['event_id'].nunique())
        
        # Análisis
        run_analysis(df_new, pdf)
        
        pdf.output(out_name)
        print(f"Generado: {out_name}")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()