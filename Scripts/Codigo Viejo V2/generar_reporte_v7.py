#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generar_reporte_v7.py
Autor: Lautaro Silva Pizzi (Pierre Auger Observatory - UMD)
Versión: 7.0
"""

import os
import glob
import sys
import io
import argparse
import traceback
import warnings
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

    def add_description(self, text):
        self.set_font("Times", "", 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def add_plot(self, fig):
        buf = io.BytesIO()
        try: fig.tight_layout()
        except: pass
        fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
        buf.seek(0)
        
        page_width = self.w - 2 * self.l_margin
        img_h_approx = page_width * 0.6 
        
        if self.get_y() + img_h_approx > self.page_break_trigger:
            self.add_page()
            
        self.image(buf, x=self.l_margin, w=page_width)
        self.ln(2)
        buf.close()
        plt.close(fig)

    def create_styled_table(self, df, title=None, col_widths=None):
        if self.get_y() > 220: self.add_page()
        if title:
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 8, title, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("Helvetica", "B", 8) 
        page_width = self.w - 2 * self.l_margin
        
        if not col_widths:
            col_width = page_width / len(df.columns)
            col_widths = [col_width] * len(df.columns)
            
        self.set_fill_color(200, 220, 255)
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], 8, str(col), border=1, align='C', fill=True)
        self.ln()

        self.set_font("Courier", "", 7)
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
        if self.get_y() > 250: self.add_page()
        self.set_font("Courier", "", 10)
        self.set_fill_color(240, 240, 240)
        lines = [f"{k}: {v}" for k, v in stats_dict.items()]
        for line in lines:
            self.cell(0, 5, line, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(5)

# =============================================================================
# 2. FUNCIONES AUXILIARES
# =============================================================================

def parse_metadata(folder_path):
    path_str = folder_path.lower()
    
    model = "Desconocido"
    if "qgs" in path_str: model = "QGSJetII-04"
    elif "sib" in path_str: model = "SIBYLL 2.3d"
    elif "epos" in path_str: model = "EPOS-LHC"
    
    primario = "Desconocido"
    if "proton" in path_str: primario = "Protón"
    elif "iron" in path_str or "hierro" in path_str: primario = "Hierro"
    elif "helium" in path_str or "helio" in path_str: primario = "Helio"
    elif "oxygen" in path_str or "oxigeno" in path_str: primario = "Oxígeno"
    
    e_range = "Desconocido"
    limits = None 
    
    if "17" in path_str and "18" not in path_str.replace("17",""): 
        e_range = "17.5 - 18.0 log(eV)"
        limits = (17.5, 18.0, 17.0, 21.0)
    elif "18" in path_str:
        e_range = "18.0 - 18.5 log(eV)"
        limits = (18.0, 18.5, 17.5, 21.5)
    else:
        limits = (17.0, 19.0, 16.0, 22.0)
        
    return model, primario, e_range, limits

def fit_func_deg(phi_deg, A1):
    return 1.0 * (1 + A1 * np.cos(np.deg2rad(phi_deg)))

def ang_diff(a_deg, b_deg):
    """Calcula diferencia angular segura en GRADOS"""
    d = a_deg - b_deg
    return (d + 180) % 360 - 180

def ensure_degrees(series, name="Var"):
    """Detecta si está en radianes y convierte a grados"""
    max_val = series.abs().max()
    if max_val < 7.0: 
        return np.rad2deg(series)
    return series

# =============================================================================
# 3. LÓGICA PRINCIPAL
# =============================================================================

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
    
    # Filtro básico
    df_new = df_raw.dropna(subset=['logE_REC', 'theta_REC', 'phi_REC']).copy()
    
    # --- PORTADA ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.ln(30)
    pdf.cell(0, 10, "Reporte de Análisis Físico", 0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, f"Validación y Asimetría ({model} - {primario})", 0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(20)
    
    meta_data = [["Modelo", model], ["Primario", primario], ["Energía", e_range],
                 ["Eventos", f"{len(df_new):,}"]]
    df_meta = pd.DataFrame(meta_data, columns=["Parámetro", "Valor"])
    pdf.create_styled_table(df_meta, title="Configuración")

    # --- 1. LIMPIEZA ---
    pdf.chapter_title("1. Limpieza de Datos")
    pdf.add_description(
        "Este reporte analiza simulaciones Monte Carlo procesadas con el pipeline v12 (IDs normalizados). "
        "Se filtran eventos con fallos en la reconstrucción global (logE o Theta NaN)."
    )

    n_rows_inicial = len(df_raw)
    nans_logE = df_raw['logE_REC'].isna().sum()
    n_rows_final = len(df_new)
    n_dropped = n_rows_inicial - n_rows_final
    pct_dropped = (n_dropped / n_rows_inicial * 100) if n_rows_inicial > 0 else 0
    
    report_data = [
        ["Filas Iniciales", f"{n_rows_inicial}"],
        ["Filas Eliminadas", f"{n_dropped} ({pct_dropped:.2f}%)"],
        ["Filas Finales", f"{n_rows_final}"],
        ["Causa Principal", f"NaN en logE_REC ({nans_logE})"],
    ]
    df_report = pd.DataFrame(report_data, columns=["Métrica", "Valor"])
    pdf.create_styled_table(df_report, title="Estadísticas de Filtrado")

    # === DETECCIÓN DE UNIDADES ===
    is_degrees = False
    if not df_new.empty:
        if df_new['phi_plane_euler'].abs().max() > 7:
            is_degrees = True

    # =========================================================================
    # 2. VALIDACIÓN GEOMÉTRICA (INFILL)
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("2. Validación Geométrica (Infill)")
    
    # TEXTO DESCRIPTIVO CONCEPTUAL REVISADO
    pdf.add_description(
        "Este análisis demuestra la insuficiencia de la reconstrucción estándar ('Offline SP') para el Infill y valida "
        "la corrección de Euler implementada.\n\n"
        "1. Histograma (Superior): Compara 'Offline SP' contra 'Phi Ground' (proyección geométrica simple). "
        "La gaussiana centrada en cero indica que ambas variables son esencialmente idénticas. Esto confirma que el 'Offline SP' "
        "en el Infill no está corrigiendo adecuadamente la geometría del plano de la lluvia, comportándose como una simple proyección al suelo "
        "que 'lava' la asimetría física.\n\n"
        "2. Scatter 'La Mariposa' (Inferior): Compara la corrección propuesta ('Euler') contra la proyección simple ('Ground/SP'). "
        "Para lluvias verticales (Theta ~ 0), ambos métodos coinciden. Sin embargo, a medida que Theta crece (lluvias inclinadas), "
        "la diferencia aumenta drásticamente (forma de trompeta), demostrando que la corrección de Euler está introduciendo la "
        "información geométrica necesaria que el método estándar ignora."
    )
    
    df_infill = df_new[df_new['counterId'] >= 100000].copy()
    
    if len(df_infill) > 0:
        # 1. Convertimos TODO a GRADOS
        vals_sp = ensure_degrees(df_infill['phi_plane_sp'], 'SP')
        vals_ground = ensure_degrees(df_infill['phi_plane_ground'], 'Ground')
        vals_euler = ensure_degrees(df_infill['phi_plane_euler'], 'Euler')
        vals_rec_phi = ensure_degrees(df_infill['phi_REC'], 'PhiRec')

        # 2. PARCHES FÍSICOS
        vals_sp_fixed = (vals_sp + vals_rec_phi) % 360
        vals_euler_fixed = (vals_euler + 180) % 360
        
        # 3. Diferencias
        diff_offline_ground = ang_diff(vals_sp_fixed, vals_ground)
        diff_euler_ground = ang_diff(vals_euler_fixed, vals_ground)
        
        # Plot 1: Histograma SP vs Ground
        fig_geo1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.hist(diff_offline_ground, bins=100, range=(-5, 5), color='forestgreen', alpha=0.7, label='SP Fixed - Ground')
        ax1.axvline(0, color='k', linestyle='--')
        ax1.set_title("Validación: [Offline SP] vs [Ground] (Son Iguales -> SP es Incorrecto)")
        ax1.set_xlabel("Diferencia (Grados)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        pdf.add_plot(fig_geo1)
        
        # Plot 2: La Trompeta
        fig_geo2, ax2 = plt.subplots(figsize=(10, 6))
        n_sample = min(50000, len(df_infill))
        idx = np.random.choice(df_infill.index, n_sample, replace=False)
        s_theta = df_infill.loc[idx, 'theta_REC']
        s_diff = diff_euler_ground.loc[idx]
        
        sc = ax2.scatter(s_theta, s_diff, s=1, c='royalblue', alpha=0.1) 
        ax2.axhline(0, color='k', linestyle='--')
        ax2.set_title("La Mariposa: Corrección Euler (Necesaria) vs Cenit")
        ax2.set_xlabel(r"$\theta_{REC}$ [Grados]")
        ax2.set_ylabel(r"Corrección $\phi_{Euler} - \phi_{Ground}$ [Grados]")
        ax2.set_ylim(-40, 40)
        ax2.grid(True, alpha=0.3)
        pdf.add_plot(fig_geo2)
    else:
        pdf.cell(0, 10, "No se encontraron datos de Infill.", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # --- 3. PLOT 3D ---
    pdf.add_page()
    pdf.chapter_title("3. Visualización General (3D)")
    pdf.add_description(
        r"Representación del espacio de fases cubierto por la simulación. Se grafica la señal de muones reconstruida "
        r"($N_{\mu}^{REC}$, eje Z y color) en función de la distancia al core ($r$) y el ángulo cenital ($\theta$). "
        r"Este gráfico permite inspeccionar cualitativamente la dependencia de la señal con la geometría de la lluvia."
    )
    
    df_plot_3d = df_new[(df_new['nMuones_REC'] > 0) & (df_new['r_core'] < 2800)]
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(
        df_plot_3d["r_core"], df_plot_3d["theta_REC"], df_plot_3d["nMuones_REC"],
        c=df_plot_3d["nMuones_REC"], cmap="viridis", alpha=0.7, s=10
    )
    ax.set_xlabel("Distancia [m]", labelpad=10)
    ax.set_ylabel("Theta [deg]", labelpad=10)
    ax.set_zlabel("N_mu REC", labelpad=10)
    ax.set_title(r"Distribución de $N_\mu^{REC}$")
    ax.set_xticks(np.arange(0, 2801, 500))
    ax.set_ylim(0, 68)
    cbar = plt.colorbar(sc, pad=0.1, shrink=0.7)
    cbar.set_label(r"$N_\mu^{REC}$")
    ax.view_init(elev=30, azim=310)
    pdf.add_plot(fig)

    # --- 4. RESOLUCIÓN DE ENERGÍA ---
    pdf.add_page()
    pdf.chapter_title("4. Resolución de Energía")
    
    pdf.add_description(
        r"Se evalúa la calidad de la reconstrucción de la energía del evento primario." + "\n"
        r"1. Gráfico de Dispersión (Izq): Correlación entre la Energía Verdadera ($log_{10} E_{MC}$) y la Reconstruida ($log_{10} E_{REC}$). "
        r"La línea punteada roja representa la identidad ideal ($y=x$). Desviaciones indican problemas de calibración." + "\n"
        r"2. Histograma de Residuos (Der): Distribución del error relativo ($log_{10} E_{REC} - log_{10} E_{MC}$). "
        r"Una gaussiana centrada en 0 demuestra ausencia de sesgo sistemático. El ancho (Std) cuantifica la resolución energética."
    )
    
    df_events = df_new[["event_id", "logE_MC", "theta_MC", "phi_MC", "logE_REC", "theta_REC", "phi_REC"]].drop_duplicates()
    X_full = df_events["logE_MC"]
    Y_full = df_events["logE_REC"]
    deltaE_full = Y_full - X_full
    
    fig_en, axs = plt.subplots(1, 2, figsize=(12, 5))
    axs[0].scatter(X_full, Y_full, s=5, alpha=0.3, label='Datos')
    axs[0].plot([17, 22], [17, 22], 'r--', label='Ideal y=x')
    axs[0].set_xlabel(r"$log_{10}(E_{MC})$")
    axs[0].set_ylabel(r"$log_{10}(E_{REC})$")
    if e_limits_plot:
        axs[0].set_xlim(e_limits_plot[0], e_limits_plot[1])
        axs[0].set_ylim(e_limits_plot[2], e_limits_plot[3]) 
    axs[0].legend()
    axs[0].grid(True)
    
    axs[1].hist(deltaE_full, bins=100, range=(-0.9, 0.9), alpha=0.7, color='steelblue')
    axs[1].set_xlabel(r"$\Delta logE$")
    axs[1].grid(True)
    pdf.add_plot(fig_en)
    
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
    pdf.add_page()
    pdf.chapter_title("5. Resolución Angular")
    
    pdf.add_description(
        "Evaluación de la precisión en la reconstrucción de la dirección de llegada de la lluvia cósmica.\n"
        "Se comparan los ángulos cenital (Theta) y azimutal (Phi) reconstruidos contra los valores verdaderos de Monte Carlo.\n"
        "Los histogramas de residuos (derecha) permiten cuantificar la precisión angular del detector. Un sesgo cercano a cero y "
        "una desviación estándar baja son indicadores de una reconstrucción geométrica robusta."
    )
    
    # THETA
    pdf.chapter_subtitle("Resolución en Theta (Cenital)")
    delta_theta = df_events["theta_REC"] - df_events["theta_MC"]
    
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
    
    umbral_theta = 10.0
    mal_theta = delta_theta.abs() > umbral_theta
    stats_theta = {
        "Sesgo": f"{delta_theta.mean():.4f} deg",
        "Resolución": f"{delta_theta.std():.4f} deg",
        f"Outliers (> {umbral_theta}deg)": f"{mal_theta.sum()} ({mal_theta.mean()*100:.2f}%)"
    }
    pdf.add_stats_box(stats_theta)
    
    # PHI
    pdf.chapter_subtitle("Resolución en Phi (Azimutal)")
    delta_phi = (df_events["phi_REC"] - df_events["phi_MC"] + 180) % 360 - 180
    
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

    median_phi = delta_phi.median()
    mad_phi = (delta_phi - median_phi).abs().median()
    umbral_phi = 15.0
    mal_phi = delta_phi.abs() > umbral_phi
    stats_phi = {
        "Sesgo (Median)": f"{median_phi:.4f} deg",
        "Resolución (MAD)": f"{mad_phi:.4f} deg",
        f"Outliers (> {umbral_phi}deg)": f"{mal_phi.sum()} ({mal_phi.mean()*100:.2f}%)"
    }
    pdf.add_stats_box(stats_phi)

    # --- 6. UNIFORMIDAD ---
    pdf.add_page()
    pdf.chapter_title("6. Uniformidad por Counter")
    pdf.add_description(
        "Control de calidad detector a detector. Se grafica la señal media y la desviación estándar "
        "para cada estación individual.\n"
        "El objetivo es verificar que la respuesta sea uniforme a lo largo del array y detectar posibles "
        "estaciones defectuosas ('muertas' o ruidosas) que podrían sesgar el análisis de asimetría."
    )
    
    df_counters = df_new.groupby(['event_id', 'counterId'])['nMuones_REC'].sum().reset_index()
    counter_stats = df_counters.groupby('counterId')['nMuones_REC'].agg(promedio='mean', std_dev='std').reset_index()
    stats_con_senal = counter_stats[counter_stats['promedio'] > 0].copy()
    stats_con_senal['counterId_str'] = stats_con_senal['counterId'].astype(str)
    
    df_dense = stats_con_senal[(stats_con_senal['counterId'] >= 90000) & (stats_con_senal['counterId'] < 100000)].copy()
    df_infill_stats = stats_con_senal[stats_con_senal['counterId'] >= 100000].copy()
    
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

    fig_u1 = make_uniformity_plot(df_dense, "Anillo Denso (90k)", "royalblue", "lightcoral")
    if fig_u1: pdf.add_plot(fig_u1)
    fig_u2 = make_uniformity_plot(df_infill_stats, "Infill (104k)", "skyblue", "salmon")
    if fig_u2: pdf.add_plot(fig_u2)

    # =========================================================================
    # 7. COMPOSICIÓN FÍSICA DEL SD (CON SUMA MC)
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("7. Composición Física del SD")
    
    pdf.add_description(
        "Perfil Lateral (LDF) de las componentes de la lluvia.\n"
        "- Eje Izquierdo (Log): Número medio de partículas incidentes (MC Truth). Se desglosa en Muones (verde), "
        "Componente Electromagnética (naranja) y la Suma Total (violeta).\n"
        "- Eje Derecho (Log): Señal total reconstruida en el tanque en unidades VEM (negro).\n"
        "Este gráfico valida la correlación física esperada: cerca del core domina la componente EM, mientras que "
        "a grandes distancias la señal es dominada por la componente muónica."
    )
    
    r_bins = np.linspace(0, 2000, 41) 
    df_new['r_bin'] = pd.cut(df_new['r_core'], bins=r_bins)
    
    comp_stats = df_new.groupby('r_bin', observed=True).agg({
        'r_core': 'mean',
        'sd_nMuons_MC': 'mean',
        'sd_nEM_MC': 'mean',
        'sdSignal_REC': 'mean' 
    }).dropna()
    
    # Calculamos la suma total MC
    comp_stats['mc_total'] = comp_stats['sd_nMuons_MC'] + comp_stats['sd_nEM_MC']
    
    if not comp_stats.empty:
        fig_comp, ax_main = plt.subplots(figsize=(10, 6))
        
        # EJE IZQUIERDO: COUNTS (MC)
        l1 = ax_main.plot(comp_stats['r_core'], comp_stats['sd_nMuons_MC'], 'o-', color='forestgreen', label='MC Muons', markersize=4)
        l2 = ax_main.plot(comp_stats['r_core'], comp_stats['sd_nEM_MC'], 's-', color='darkorange', label='MC EM', markersize=4)
        l_tot = ax_main.plot(comp_stats['r_core'], comp_stats['mc_total'], '^-', color='purple', label='MC Total (Mu+EM)', linewidth=2, markersize=5)
        
        ax_main.set_xlabel("Distancia al Core [m]")
        ax_main.set_ylabel("Número Medio de Partículas (Counts)")
        ax_main.set_yscale('log')
        ymax = comp_stats['mc_total'].max() if len(comp_stats) > 0 else 10
        ax_main.set_ylim(0.1, ymax * 2)
        ax_main.grid(True, which="both", alpha=0.3)
        
        # EJE DERECHO: VEM (REC)
        ax_vem = ax_main.twinx()
        l3 = ax_vem.plot(comp_stats['r_core'], comp_stats['sdSignal_REC'], 'k--', label='REC VEM (Signal)', linewidth=2)
        ax_vem.set_ylabel("Señal Total Reconstruida (VEM)")
        ax_vem.set_yscale('log')
        
        # Leyenda Unificada
        lns = l1 + l2 + l_tot + l3
        labs = [l.get_label() for l in lns]
        ax_main.legend(lns, labs, loc='upper right')
        
        ax_main.set_title("LDF: Comparación Directa MC vs Señal VEM")
        pdf.add_plot(fig_comp)
    else:
        pdf.cell(0, 10, "No hay estadística suficiente para LDF.", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # --- 8. ASIMETRÍA AZIMUTAL - ANILLO DENSO ---
    pdf.add_page()
    pdf.chapter_title("8. Asimetría Azimutal (UMD - 90k)")
    pdf.add_description(
        r"Análisis de la modulación de la señal en función del ángulo azimutal (Phi) para el Anillo Denso (referencia)." + "\n"
        r"Se ajusta la función $S = S_0 [1 + A_1 \cos(\phi)]$ separando los eventos en bines de $sin^2(\theta)$." + "\n"
        r"Se espera observar un crecimiento de la amplitud de asimetría $A_1$ conforme aumenta el ángulo cenital, "
        r"debido al aumento en el camino recorrido por los muones en el detector y la atenuación diferencial de la componente EM."
    )
    
    N_theta_bins = 6
    th_min_val = df_new['theta_REC'].min()
    th_max_val = min(65, df_new['theta_REC'].max())
    
    s2_bins = np.linspace(np.sin(np.deg2rad(th_min_val))**2, 
                          np.sin(np.deg2rad(th_max_val))**2, 
                          N_theta_bins + 1)
    theta_bins_deg = np.rad2deg(np.arcsin(np.sqrt(s2_bins)))
    
    df_new['s2_theta'] = np.sin(np.deg2rad(df_new['theta_REC']))**2
    df_new['theta_bin_idx'] = pd.cut(df_new['s2_theta'], bins=s2_bins, labels=False, include_lowest=True)
    
    df_ana = df_new[
        (df_new['counterId'] >= 90000) & 
        (df_new['counterId'] < 100000) & 
        (df_new['module_status'].isin(['candidate', 'rejected', 'saturated']))
    ].copy().reset_index(drop=True)
    
    phi_deg = np.rad2deg(df_ana['phi_plane_sp'])
    df_ana['phi_deg_centered'] = (phi_deg + 180) % 360 - 180
    
    phi_bin_edges = np.linspace(-180, 180, 13)
    phi_centers = (phi_bin_edges[:-1] + phi_bin_edges[1:]) / 2
    
    fit_table = []

    for i in range(N_theta_bins):
        th_min, th_max = theta_bins_deg[i], theta_bins_deg[i+1]
        pdf.chapter_subtitle(f"Bin {i}: Theta {th_min:.1f} - {th_max:.1f} deg")
        
        mask_bin = (df_ana['theta_bin_idx'] == i)
        df_sl = df_ana[mask_bin].copy()
        
        if len(df_sl) < 50:
            pdf.cell(0, 10, "Datos insuficientes (< 50 filas)", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            continue
            
        try:
            df_sl['phi_bin'] = pd.cut(df_sl['phi_deg_centered'], bins=phi_bin_edges)
            stats = df_sl.groupby('phi_bin', observed=True).agg({
                'nMuones_REC': ['mean', 'std', 'count'], 
                'nMuones_MC': ['mean', 'std', 'count'], 
                'sdSignal_REC': ['mean', 'std', 'count'] 
            })
        except: continue
        
        fig, axs = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
        configs = [
            ('nMuones_REC', r'$N_\mu^{REC}$ (UMD)', 'navy'), 
            ('nMuones_MC', r'$N_\mu^{MC}$ (UMD)', 'forestgreen'), 
            ('sdSignal_REC', 'SD REC', 'firebrick') 
        ]
        
        bin_res = {'theta_idx': i, 'theta_range': f"{th_min:.1f}-{th_max:.1f}"}
        
        for ax_idx, (col, label, color) in enumerate(configs):
            ax = axs[ax_idx]
            if col not in stats.columns.levels[0]: continue

            means = stats[col]['mean']
            norm = means.mean()
            if pd.isna(norm) or norm == 0: continue

            y = means / norm
            yerr = (stats[col]['std'] / np.sqrt(stats[col]['count'])) / norm 
            x = phi_centers
            
            ax.errorbar(x, y, yerr=yerr, fmt='o', color=color, label='Data', capsize=3)
            
            try:
                popt, pcov = curve_fit(fit_func_deg, x, y, p0=[0.05], sigma=yerr, absolute_sigma=True)
                A1 = popt[0]
                A1_err = np.sqrt(pcov[0,0])
                x_fit = np.linspace(-180, 180, 100)
                ax.plot(x_fit, fit_func_deg(x_fit, *popt), 'k--', 
                        label=rf'Fit: $A_1 = {A1:.3f} \pm {A1_err:.3f}$')
                
                suffix = "UMD_REC" if "REC" in label and "UMD" in label else "UMD_MC" if "MC" in label else "SD_REC"
                bin_res[f'A1_{suffix}'] = A1
                bin_res[f'Err_{suffix}'] = A1_err
            except: pass
            
            ax.set_title(label)
            ax.set_xlim(-180, 180)
            ax.grid(True, alpha=0.3)
            if ax_idx == 0: ax.set_ylabel("S / <S>")
            ax.legend(fontsize=8)
            
        plt.tight_layout()
        pdf.add_plot(fig)
        fit_table.append(bin_res)

    if fit_table:
        pdf.add_page()
        pdf.chapter_title("8.1 Resumen Ajustes (Anillo Denso)")
        df_res = pd.DataFrame(fit_table)
        cols_ordered = ['theta_range'] + [c for c in df_res.columns if c != 'theta_range' and c != 'theta_idx']
        pdf.create_styled_table(df_res[cols_ordered], title="Resultados Detallados")

    # --- 9. PERFILES INFILL (Bines Anchos) ---
    pdf.add_page()
    pdf.chapter_title("9. Perfiles Infill (Bines Anchos)")
    pdf.add_description(
        r"Perfiles de asimetría para el Infill (IDs >= 100k) utilizando la proyección de Euler corregida y validada. "
        r"Debido a la menor estadística y mayor dispersión geométrica del Infill, los datos se agrupan en bines más anchos "
        r"de distancia ($r$) y ángulo cenital ($\theta$). Se presentan los ajustes cosenoidales para cada configuración."
    )
    
    r_edges_manual = [0, 400, 800, 2000]
    r_labels_manual = ["0-400 m", "400-800 m", "800-2000 m"]
    theta_edges_manual = [20, 40, 60] 
    
    df_infill = df_new[
        (df_new['counterId'] >= 100000) & 
        (df_new['module_status'].isin(['candidate', 'rejected', 'saturated']))
    ].copy()

    phi_vals = df_infill['phi_plane_euler']
    if is_degrees: phi_vals = np.deg2rad(phi_vals)
    phi_deg_infill = np.rad2deg(phi_vals)
    
    # CENTRADO: Usamos +180 para alinear con la definición física del Anillo
    df_infill['phi_deg_centered'] = (phi_deg_infill + 180) % 360 - 180
    
    df_infill['r_bin_manual'] = pd.cut(df_infill['r_core'], bins=r_edges_manual, labels=False, include_lowest=True)
    df_infill['theta_bin_manual'] = pd.cut(df_infill['theta_REC'], bins=theta_edges_manual, labels=False, include_lowest=True)

    for i in range(len(theta_edges_manual) - 1):
        th_min = theta_edges_manual[i]
        th_max = theta_edges_manual[i+1]
        
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, f"Rango Theta Consolidado: {th_min:.0f}° - {th_max:.0f}°", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        df_th = df_infill[df_infill['theta_bin_manual'] == i]
        if df_th.empty: continue

        fig, axs = plt.subplots(3, 3, figsize=(15, 18), sharex=True)
        configs = [
            ('nMuones_REC', r'$N_\mu^{REC}$', 'royalblue'), 
            ('nMuones_MC', r'$N_\mu^{MC}$', 'forestgreen'), 
            ('sdSignal_REC', 'SD Signal', 'crimson') 
        ]

        for j in range(3): 
            r_label = r_labels_manual[j]
            df_r = df_th[df_th['r_bin_manual'] == j].copy()
            
            if df_r.empty or len(df_r) < 50:
                axs[j, 0].set_ylabel(f"{r_label}\n(Poca Data)", fontweight='bold', fontsize=9)
                continue

            df_r['phi_bin'] = pd.cut(df_r['phi_deg_centered'], bins=phi_bin_edges)
            stats = df_r.groupby('phi_bin', observed=True).agg({
                'nMuones_REC': ['mean', 'sem'], 
                'nMuones_MC': ['mean', 'sem'], 
                'sdSignal_REC': ['mean', 'sem'] 
            })

            for k, (col, label, color) in enumerate(configs):
                ax = axs[j, k]
                means = stats[col]['mean']
                sems = stats[col]['sem']
                norm = means.mean()
                
                if pd.isna(norm) or norm == 0: continue

                ax.errorbar(phi_centers, means/norm, yerr=sems/norm, 
                            fmt='o', color=color, markersize=6, capsize=4, elinewidth=1.5)
                
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.set_xlim(-180, 180)
                
                if j == 0: ax.set_title(label, fontsize=12, fontweight='bold')
                if j == 2: ax.set_xlabel(r"$\phi$ [deg]", fontsize=10)
                if k == 0: ax.set_ylabel(f"{r_label}\nNorm. Amp.", fontweight='bold', fontsize=9)
                
                vals = means/norm
                if not vals.isna().all():
                    v_span = vals.max() - vals.min()
                    rango = max(v_span, 0.05) 
                    ax.set_ylim(vals.mean() - rango, vals.mean() + rango)

        plt.subplots_adjust(hspace=0.1, wspace=0.15)
        pdf.add_plot(fig)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="Carpeta con parquets")
    args = parser.parse_args()
    
    if not os.path.isdir(args.folder):
        print("Carpeta inválida.")
        sys.exit(1)
        
    out_name = f"Reporte_V15_Final_{os.path.basename(args.folder.rstrip('/'))}.pdf"
    
    pdf = AnalysisPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    
    try:
        run_analysis(pdf, args.folder)
        pdf.output(out_name)
        print(f"Reporte generado exitosamente: {out_name}")
    except Exception:
        traceback.print_exc()