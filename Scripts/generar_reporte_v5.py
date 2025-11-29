#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generar_reporte_5.py
Autor: Lautaro Silva Pizzi (Pierre Auger Observatory - UMD)
"""

import os
import glob
import sys
import io
import argparse
import traceback
import warnings
import re
from datetime import datetime

# --- Data Science Stack ---
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # Backend no interactivo
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import curve_fit

# --- PDF Generation ---
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Ignorar warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)

# =============================================================================
# 1. CLASE PDF & UTILS
# =============================================================================

class AnalysisPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "Análisis de Asimetría Azimutal - Auger UMD/SD", 0, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}} | {datetime.now().strftime('%Y-%m-%d')}", 0, align="C")

    def chapter_title(self, label):
        if self.get_y() > 250: self.add_page()
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(40, 60, 100)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"  {label}", 0, fill=True, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def chapter_subtitle(self, label):
        if self.get_y() > 260: self.add_page()
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(40, 60, 100)
        self.cell(0, 8, label, 0, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(2)

    def add_plot(self, fig):
        buf = io.BytesIO()
        try: fig.tight_layout()
        except: pass
        fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
        buf.seek(0)
        
        page_width = self.w - 2 * self.l_margin
        # Estimación de altura
        img_h_approx = page_width * 0.6 
        
        if self.get_y() + img_h_approx > self.page_break_trigger:
            self.add_page()
            
        self.image(buf, x=self.l_margin, w=page_width)
        self.ln(2) # Espacio reducido post-plot
        buf.close()
        plt.close(fig)

    def create_styled_table(self, df, title=None, col_widths=None):
        if self.get_y() > 220: self.add_page()
        if title:
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 8, title, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("Helvetica", "B", 9)
        page_width = self.w - 2 * self.l_margin
        if not col_widths:
            col_width = page_width / len(df.columns)
            col_widths = [col_width] * len(df.columns)
            
        self.set_fill_color(200, 220, 255)
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], 6, str(col), border=1, align='C', fill=True)
        self.ln()

        self.set_font("Courier", "", 8)
        fill = False
        for row in df.itertuples(index=False):
            self.set_fill_color(245, 245, 245) if fill else self.set_fill_color(255, 255, 255)
            for i, datum in enumerate(row):
                val = datum
                if isinstance(val, float):
                    val = f"{val:.4f}"
                self.cell(col_widths[i], 6, str(val), border=1, align='C', fill=True)
            self.ln()
            fill = not fill
        self.ln(5)

    def add_stats_box(self, stats_dict):
        """Caja de texto simple para métricas."""
        if self.get_y() > 250: self.add_page()
        self.set_font("Courier", "", 10)
        self.set_fill_color(240, 240, 240)
        
        # Calcular ancho máximo
        max_len = 0
        lines = []
        for k, v in stats_dict.items():
            line = f"{k}: {v}"
            lines.append(line)
            max_len = max(max_len, len(line))
        
        # Dibujar
        for line in lines:
            self.cell(0, 5, line, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

# =============================================================================
# 2. LOGICA DEL PIPELINE
# =============================================================================

def parse_metadata(folder_path):
    path_str = folder_path.lower()
    
    # Modelo
    model = "Desconocido"
    if "qgs" in path_str: model = "QGSJetII-04"
    elif "sib" in path_str: model = "SIBYLL 2.3d"
    elif "epos" in path_str: model = "EPOS-LHC"
    
    # Primario
    primario = "Desconocido"
    if "proton" in path_str: primario = "Protón"
    elif "iron" in path_str or "hierro" in path_str: primario = "Hierro"
    elif "helium" in path_str or "helio" in path_str: primario = "Helio"
    elif "oxygen" in path_str or "oxigeno" in path_str: primario = "Oxígeno"
    
    # Energía y Límites de Plot
    e_range = "Desconocido"
    limits = None 
    
    # Logica folder: "17" -> 17.5-18.0 // "18" -> 18.0-18.5
    if "17" in path_str and "18" not in path_str.replace("17",""): 
        e_range = "17.5 - 18.0 log(eV)"
        limits = (17.5, 18, 17, 21)
    elif "18" in path_str:
        e_range = "18.0 - 18.5 log(eV)"
        limits = (18, 18.5, 17.5, 21.5)
    else:
        # Default fallback
        limits = (17.0, 19.0)
        
    return model, primario, e_range, limits

def fit_func_deg(phi_deg, A1):
    return 1.0 * (1 + A1 * np.cos(np.deg2rad(phi_deg)))

def run_analysis(pdf, folder_path):
    
    # --- 1. CARGA ---
    model, primario, e_range, e_limits_plot = parse_metadata(folder_path)
    
    files = glob.glob(os.path.join(folder_path, "*.parquet"))
    files.sort()
    
    if not files: raise FileNotFoundError("No hay parquets.")
    
    print("Cargando DataFrames...")
    df_list = [pd.read_parquet(f) for f in files]
    df_raw = pd.concat(df_list, ignore_index=True)
    df_raw.replace([np.inf, -np.inf], np.nan, inplace=True)

    # --- PORTADA ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.ln(30)
    pdf.cell(0, 10, "Reporte de Análisis Físico", 0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "Validación MC y Asimetría UMD/SD", 0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(20)
    
    meta_data = [
        ["Modelo Hadrónico", model],
        ["Primario", primario],
        ["Rango Energía", e_range],
        ["Carpeta", os.path.basename(folder_path)],
        ["Eventos Totales", f"{df_raw['event_id'].nunique():,}"],
        ["Módulos Totales", f"{len(df_raw):,}"]
    ]
    df_meta = pd.DataFrame(meta_data, columns=["Parámetro", "Valor"])
    pdf.create_styled_table(df_meta, title="Configuración de la Simulación")

    # --- 2. LIMPIEZA ---
    pdf.chapter_title("1. Limpieza de Datos")
    
    n_rows_inicial = len(df_raw)
    nans_logE = df_raw['logE_REC'].isna().sum()
    
    # Drop
    df_new = df_raw.dropna(subset=['logE_REC', 'theta_REC', 'phi_REC']).copy()
    n_rows_final = len(df_new)
    n_dropped = n_rows_inicial - n_rows_final
    pct_dropped = (n_dropped / n_rows_inicial * 100) if n_rows_inicial > 0 else 0
    
    # Tabla Reporte
    report_data = [
        ["Filas Iniciales", f"{n_rows_inicial}"],
        ["Filas Eliminadas", f"{n_dropped} ({pct_dropped:.2f}%)"],
        ["Filas Finales", f"{n_rows_final}"],
        ["Causa Principal", f"NaN en logE_REC ({nans_logE})"],
    ]
    df_report = pd.DataFrame(report_data, columns=["Métrica", "Valor"])
    pdf.create_styled_table(df_report, title="REPORTE DE LIMPIEZA")
    
    # --- 3. PLOT 3D (TODOS LOS PUNTOS) ---
    pdf.chapter_title("2. Visualización General")
    
    # Filtro lógico (no sampling)
    df_plot_3d = df_new[
        (df_new['nMuones_REC'] > 0) &
        (df_new['r_core'] < 2800)
    ]
    # Si son demasiados (>200k), matplotlib puede tardar mucho en generar el PNG
    # pero el usuario pidió "todos". 
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    sc = ax.scatter(
        df_plot_3d["r_core"],
        df_plot_3d["theta_REC"],
        df_plot_3d["nMuones_REC"],
        c=df_plot_3d["nMuones_REC"],
        cmap="viridis",
        alpha=0.7,
        s=10
    )
    ax.set_xlabel("Distancia al core [m]", fontsize=10, labelpad=10)
    ax.set_ylabel(r"$\theta_{REC}$ [°]", fontsize=10, labelpad=10)
    ax.set_zlabel(r"$N_\mu^{REC}$", fontsize=10, labelpad=10) # <-- NOTACION
    ax.set_title(r"$N_\mu^{REC}$ vs distancia y $\theta$", fontsize=12)
    
    ax.set_xticks(np.arange(0, 2801, 500))
    ax.set_ylim(0, 68)
    
    z_max = df_plot_3d["nMuones_REC"].max()
    ax.set_zlim(0, z_max)
    
    cbar = plt.colorbar(sc, pad=0.1, shrink=0.7)
    cbar.set_label(r"$N_\mu^{REC}$", fontsize=10)
    ax.view_init(elev=30, azim=310)
    ax.grid(True)
    
    pdf.add_plot(fig)

    # --- DF EVENTOS ---
    event_cols = ["event_id", "logE_MC", "theta_MC", "phi_MC", "logE_REC", "theta_REC", "phi_REC"]
    df_events = df_new[event_cols].drop_duplicates()

    # --- 4. RESOLUCIÓN DE ENERGÍA ---
    pdf.chapter_title("3. Resolución de Energía")
    
    X_full = df_events["logE_MC"]
    Y_full = df_events["logE_REC"]
    deltaE_full = Y_full - X_full
    
    # 1. Plots PRIMERO
    fig_en, axs = plt.subplots(1, 2, figsize=(12, 5))
    
    # Scatter
    axs[0].scatter(X_full, Y_full, s=5, alpha=0.3, label='Datos')
    # Ideal
    axs[0].plot([17, 22], [17, 22], 'r--', label='Ideal y=x')
    axs[0].set_xlabel(r"$log_{10}(E_{MC})$")
    axs[0].set_ylabel(r"$log_{10}(E_{REC})$")
    axs[0].set_title("Comparación Energía")
    
    # LIMITES DINÁMICOS
    if e_limits_plot:
        axs[0].set_xlim(e_limits_plot[0], e_limits_plot[1])
        axs[0].set_ylim(e_limits_plot[2], e_limits_plot[3])
    
    axs[0].legend()
    axs[0].grid(True)
    
    # Histograma
    axs[1].hist(deltaE_full, bins=100, range=(-0.9, 0.9), alpha=0.7, color='steelblue', label='|dE| < 0.9')
    # Outliers
    outliers_vals = deltaE_full[deltaE_full.abs() >= 0.9]
    if len(outliers_vals) > 0:
        axs[1].hist(outliers_vals, bins=20, alpha=0.7, color='red', label='Outliers')
        
    axs[1].set_xlabel(r"$\Delta logE$")
    axs[1].set_title("Distribución de Diferencias")
    axs[1].legend()
    axs[1].grid(True)
    pdf.add_plot(fig_en)
    
    # Plot Residuales
    fig_res, ax_res = plt.subplots(figsize=(10, 4))
    ax_res.scatter(X_full, deltaE_full, s=5, alpha=0.3)
    ax_res.axhline(deltaE_full.mean(), color='r', linestyle='--', label=f'Sesgo={deltaE_full.mean():.3f}')
    ax_res.set_xlabel(r"$log_{10}(E_{MC})$")
    ax_res.set_ylabel(r"$\Delta logE$")
    ax_res.set_title("Dependencia del Sesgo con Energía")
    ax_res.set_ylim(-0.6, 0.6)
    ax_res.legend()
    ax_res.grid(True)
    pdf.add_plot(fig_res)

    # 2. Métricas AL FINAL
    umbral_E = 0.9
    df_fit = df_events[(deltaE_full.abs() < umbral_E)]
    cant_outliers = len(df_events) - len(df_fit)
    
    stats_energy = {
        "Sesgo (Mean)": f"{deltaE_full.mean():.4f}",
        "Resolución (Std)": f"{deltaE_full.std():.4f}",
        f"Outliers (> {umbral_E})": f"{cant_outliers} ({cant_outliers/len(df_events)*100:.2f}%)"
    }
    pdf.add_stats_box(stats_energy)

    # --- 5. RESOLUCIÓN ANGULAR ---
    pdf.chapter_title("4. Resolución Angular")

    # THETA
    pdf.chapter_subtitle("Theta (Cenital)")
    
    delta_theta = df_events["theta_REC"] - df_events["theta_MC"]
    
    # Plot
    fig_th, axs_th = plt.subplots(1, 2, figsize=(12, 5))
    axs_th[0].scatter(df_events["theta_MC"], df_events["theta_REC"], s=5, alpha=0.3)
    axs_th[0].plot([0, 65], [0, 65], 'r--')
    axs_th[0].set_xlabel("Theta MC")
    axs_th[0].set_ylabel("Theta REC")
    axs_th[0].grid(True)
    
    axs_th[1].hist(delta_theta, bins=100, range=(-5, 5), color='darkorange', alpha=0.7)
    axs_th[1].set_xlabel("Delta Theta")
    axs_th[1].grid(True)
    pdf.add_plot(fig_th)
    
    # Métricas Theta (Al final)
    umbral_theta = 10.0
    mal_theta = delta_theta.abs() > umbral_theta
    stats_theta = {
        "Sesgo": f"{delta_theta.mean():.4f} deg",
        "Resolución": f"{delta_theta.std():.4f} deg",
        f"Outliers (> {umbral_theta}°)": f"{mal_theta.sum()} ({mal_theta.mean()*100:.2f}%)"
    }
    pdf.add_stats_box(stats_theta)
    
    # PHI
    pdf.chapter_subtitle("Phi (Azimutal)")
    
    delta_phi = (df_events["phi_REC"] - df_events["phi_MC"] + 180) % 360 - 180
    
    # Plot
    fig_ph, axs_ph = plt.subplots(1, 2, figsize=(12, 5))
    axs_ph[0].scatter(df_events["phi_MC"], df_events["phi_REC"], s=5, alpha=0.3)
    axs_ph[0].plot([0, 360], [0, 360], 'r--')
    axs_ph[0].set_xlabel("Phi MC")
    axs_ph[0].set_ylabel("Phi REC")
    axs_ph[0].grid(True)
    
    axs_ph[1].hist(delta_phi, bins=100, range=(-15, 15), color='seagreen', alpha=0.7)
    axs_ph[1].set_xlabel("Delta Phi (ajustado)")
    axs_ph[1].grid(True)
    pdf.add_plot(fig_ph)

    # Métricas Phi (Al final)
    median_phi = delta_phi.median()
    mad_phi = (delta_phi - median_phi).abs().median()
    umbral_phi = 15.0
    mal_phi = delta_phi.abs() > umbral_phi
    
    stats_phi = {
        "Sesgo (Median)": f"{median_phi:.4f} deg",
        "Resolución (MAD)": f"{mad_phi:.4f} deg",
        f"Outliers (> {umbral_phi}°)": f"{mal_phi.sum()} ({mal_phi.mean()*100:.2f}%)"
    }
    pdf.add_stats_box(stats_phi)

    # --- 6. UNIFORMIDAD ---
    pdf.chapter_title("5. Uniformidad por Counter")
    
    # Agrupar
    df_counters = df_new.groupby(['event_id', 'counterId'])['nMuones_REC'].sum().reset_index()
    counter_stats = df_counters.groupby('counterId')['nMuones_REC'].agg(
        promedio='mean', std_dev='std'
    ).reset_index()
    stats_con_senal = counter_stats[counter_stats['promedio'] > 0].copy()
    stats_con_senal['counterId_str'] = stats_con_senal['counterId'].astype(str)
    
    df_dense = stats_con_senal[stats_con_senal['counterId'] < 100000].copy()
    df_infill = stats_con_senal[stats_con_senal['counterId'] >= 100000].copy()
    
    def make_uniformity_plot(df_data, label, col_mean, col_std):
        if df_data.empty: return None
        fig, axs = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        axs[0].bar(df_data['counterId_str'], df_data['promedio'], color=col_mean)
        axs[0].set_ylabel("Promedio")
        axs[0].grid(axis='y', linestyle='--', alpha=0.7)
        axs[0].set_title(f"Uniformidad: {label}")
        
        axs[1].bar(df_data['counterId_str'], df_data['std_dev'], color=col_std)
        axs[1].set_ylabel("Std Dev")
        axs[1].set_xlabel("ID")
        axs[1].grid(axis='y', linestyle='--', alpha=0.7)
        
        if len(df_data) > 30:
            ticks = np.arange(0, len(df_data), 5)
            axs[1].set_xticks(ticks)
            axs[1].set_xticklabels(df_data['counterId_str'].iloc[ticks], rotation=90)
        else:
            plt.xticks(rotation=90)
        return fig

    # Plot Denso
    fig_u1 = make_uniformity_plot(df_dense, "Anillo Denso (90k)", "royalblue", "lightcoral")
    if fig_u1: pdf.add_plot(fig_u1)
    
    # Plot Infill
    fig_u2 = make_uniformity_plot(df_infill, "Infill (104k)", "skyblue", "salmon")
    if fig_u2: pdf.add_plot(fig_u2)

    # --- 7. ASIMETRÍA ---
    pdf.chapter_title("6. Asimetría Azimutal")
    
    # Bins Theta
    N_theta_bins = 6
    s2_bins = np.linspace(
        np.sin(np.deg2rad(df_new['theta_REC'].min()))**2,
        np.sin(np.deg2rad(min(65, df_new['theta_REC'].max())))**2,
        N_theta_bins + 1
    )
    theta_bins_deg = np.rad2deg(np.arcsin(np.sqrt(s2_bins)))
    
    df_new['s2_theta'] = np.sin(np.deg2rad(df_new['theta_REC']))**2
    df_new['theta_bin_idx'] = pd.cut(df_new['s2_theta'], bins=s2_bins, labels=False, include_lowest=True)
    
    # Filtro Analysis
    df_ana = df_new[
        (df_new['counterId'] >= 90000) & (df_new['counterId'] < 100000) &
        (df_new['module_status'].isin(['candidate', 'rejected', 'saturated']))
    ].copy()
    
    phi_deg = np.rad2deg(df_ana['phi_plane'])
    df_ana['phi_deg_centered'] = (phi_deg + 180) % 360 - 180
    phi_bin_edges = np.linspace(-180, 180, 13)
    phi_centers = (phi_bin_edges[:-1] + phi_bin_edges[1:]) / 2
    
    fit_table = []

    for i in range(N_theta_bins):
        th_min, th_max = theta_bins_deg[i], theta_bins_deg[i+1]
        pdf.chapter_subtitle(f"Bin {i}: Theta {th_min:.1f} - {th_max:.1f} deg")
        
        df_sl = df_ana[
            (df_ana['theta_bin_idx'] == i) &
            (df_ana['nMuones_REC'].notna()) &
            (df_ana['nMuones_MC'].notna()) &
            (df_ana['sdSignal'].notna())
        ].copy()
        
        if len(df_sl) < 100:
            pdf.cell(0, 10, "Datos insuficientes", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            continue
            
        df_sl['phi_bin'] = pd.cut(df_sl['phi_deg_centered'], bins=phi_bin_edges)
        
        # Stats
        stats = df_sl.groupby('phi_bin', observed=True).agg({
            'nMuones_REC': ['mean', 'std', 'count'],
            'nMuones_MC': ['mean', 'std', 'count'],
            'sdSignal': ['mean', 'std', 'count']
        })
        
        # 3 Subplots
        fig, axs = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
        configs = [
            ('nMuones_REC', r'$N_\mu^{REC}$ (UMD)', 'navy'),
            ('nMuones_MC', r'$N_\mu^{MC}$ (UMD)', 'forestgreen'),
            ('sdSignal', 'SD REC', 'firebrick')
        ]
        
        bin_res = {'theta_idx': i, 'theta_range': f"{th_min:.1f}-{th_max:.1f}"}
        
        for ax_idx, (col, label, color) in enumerate(configs):
            ax = axs[ax_idx]
            means = stats[col]['mean']
            norm = means.mean()
            y = means / norm
            y_err = (stats[col]['std'] / np.sqrt(stats[col]['count'])) / norm
            x = phi_centers
            
            ax.errorbar(x, y, yerr=y_err, fmt='o', color=color, label='Data', capsize=3)
            
            try:
                popt, pcov = curve_fit(fit_func_deg, x, y, p0=[0.05], sigma=y_err)
                A1 = popt[0]
                A1_err = np.sqrt(pcov[0,0])
                
                x_fit = np.linspace(-180, 180, 100)
                ax.plot(x_fit, fit_func_deg(x_fit, *popt), 'k--', label=rf'Fit (fijo $\phi_0=0$) $A_1 = {A1:.3f} \pm {A1_err:.3f}$')
                
                key_base = label.split(' ')[0] # N_mu^REC, etc
                # Guardamos keys simples para el plot final
                suffix = "UMD_REC" if "REC" in label and "UMD" in label else "UMD_MC" if "MC" in label else "SD_REC"
                bin_res[f'A1_{suffix}'] = A1
                bin_res[f'Err_{suffix}'] = A1_err
            except:
                ax.text(0, 1.05, "Fit Fail")
                
            ax.set_title(label)
            ax.set_xlabel("Phi [deg]")
            ax.set_xlim(-180, 180)
            ax.grid(True)
            if ax_idx == 0: ax.set_ylabel("S / <S>")
            ax.legend(fontsize=8)
            
        plt.tight_layout()
        pdf.add_plot(fig)
        fit_table.append(bin_res)

    # --- 8. COMPARACIÓN FINAL ---
    if fit_table:
        pdf.chapter_title("7. Resumen de Ajustes (Comparación)")
        df_res = pd.DataFrame(fit_table)
        
        # Tabla simple
        cols_final = ['theta_range'] + [c for c in df_res.columns if 'A1' in c]
        pdf.create_styled_table(df_res[cols_final], title="Valores de Amplitud A1")
        
        # PLOT FINAL COMPARATIVO
        fig_final, ax_final = plt.subplots(figsize=(10, 6))
        x_vals = df_res['theta_idx']
        
        # UMD REC
        if 'A1_UMD_REC' in df_res.columns:
            ax_final.errorbar(x_vals, df_res['A1_UMD_REC'], yerr=df_res['Err_UMD_REC'], 
                              fmt='o-', color='navy', label=r'UMD $N_\mu^{REC}$')
            
        # UMD MC
        if 'A1_UMD_MC' in df_res.columns:
            ax_final.errorbar(x_vals, df_res['A1_UMD_MC'], yerr=df_res['Err_UMD_MC'], 
                              fmt='s--', color='forestgreen', label=r'UMD $N_\mu^{MC}$')
            
        # SD REC
        if 'A1_SD_REC' in df_res.columns:
            ax_final.errorbar(x_vals, df_res['A1_SD_REC'], yerr=df_res['Err_SD_REC'], 
                              fmt='^-.', color='firebrick', label='SD REC')
            
        ax_final.set_xlabel(r"Bin de Theta (creciente en $\sin^2\theta$)")
        ax_final.set_ylabel("Amplitud de Asimetría $A_1$")
        ax_final.set_title("Evolución de la Asimetría con el Ángulo Cenital")
        ax_final.legend()
        ax_final.grid(True, which='both', linestyle='--', alpha=0.5)
        
        pdf.add_plot(fig_final)

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="Carpeta con parquets")
    args = parser.parse_args()
    
    if not os.path.isdir(args.folder):
        print("Carpeta inválida.")
        sys.exit(1)
        
    out_name = f"Reporte_Final_{os.path.basename(args.folder.rstrip('/'))}.pdf"
    
    pdf = AnalysisPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    
    try:
        run_analysis(pdf, args.folder)
        pdf.output(out_name)
        print(f"Reporte generado exitosamente: {out_name}")
    except Exception as e:
        traceback.print_exc()