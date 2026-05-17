#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generar_reporte_v8.py
Autor: Lautaro Silva Pizzi (Pierre Auger Observatory - UMD)
Versión: 8.0
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
    d = a_deg - b_deg
    return (d + 180) % 360 - 180

def ensure_degrees(series, name="Var"):
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
    
    meta_data = [["Modelo", model], ["Primario", primario], ["Energía", e_range], ["Eventos", f"{len(df_new):,}"]]
    df_meta = pd.DataFrame(meta_data, columns=["Parámetro", "Valor"])
    pdf.create_styled_table(df_meta, title="Configuración")

    # --- 1. LIMPIEZA ---
    pdf.chapter_title("1. Limpieza de Datos")
    pdf.add_description(
        "Este reporte analiza simulaciones Monte Carlo procesadas con el pipeline v13. Esta version usa la siguiente logica:\n\n"
        "1. Itera sobre el MDEvent (mEvent.CountersBegin()) para encontrar TODOS los counters UMD (tanto Infill 4k como Anillo Denso 90k).\n"
        "2. Usa el SDEvent como diccionario de geometría para obtener r y phi.\n"
        "3. NO filtra por IsLowGainSaturated, en su lugar, guarda un flag.\n"
        "4. Versión HÍBRIDA (v12) para calcular la posicion:\n\n"
        "Combina la lógica original (v7) para el Anillo Denso con la corrección de Euler (v10) para el Infill:\n"
        "- Si ID es 90k (UMD): Se confía en GetAzimuthSP (Mantiene consistencia con Money Plots).\n"
        "- Si ID es Infill/Std: Se fuerza la Rotación de Euler (Arregla el bug de proyección).\n\n"
        "Versión DEBUG: Calcula y guarda 3 definiciones de Phi para comparación para el infill y mostrar que esta mal el uso del SP en el infill:\n"
        "a. Euler (3D Correcto) usando REC.\n"
        "b. Ground (2D Proyección simple).\n"
        "c. SP (Nativo de Auger).\n"
        "d. Agrego Euler usando MC.\n\n"
        "5. Guarda la señal REC (nMuones_REC) y la señal MC (nMuones_MC) para cada módulo individual para el UMD.\n"
        "6. Para el SD guarda las señal REC + MC: separa la parte EM de Muonica para el MC; y la total y Muonica para el REC.\n"
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

    is_degrees = False
    if not df_new.empty:
        if df_new['phi_plane_euler'].abs().max() > 7:
            is_degrees = True

    # =========================================================================
    # 2. VALIDACIÓN GEOMÉTRICA (INFILL)
    # =========================================================================
    pdf.chapter_title("2. Validación Geométrica (Infill)")
    pdf.add_description(
        "Este análisis demuestra la insuficiencia de la reconstrucción estándar ('Offline SP') para el Infill y valida "
        "la corrección de Euler implementada.\n\n"
        "1. Histograma (Superior): Compara 'Offline SP' contra 'Phi Ground'. La igualdad demuestra que la funcion que se supone"
        "que debe dar el valor del angulo polar en el plano de la lluvia, en realidad lo entrega en el plano del piso (por eso es"
        "una gaussiana muy fina centrada en cero).\n"
        "2. Plot Trompeta (REC): Muestra la corrección geométrica vs Cenit. La dispersión aumenta con la inclinación lo es el" 
        "comportamiento esperado y comprueba la hipotesis de que la correcion de euler es la correcta.\n"
        "3. La Serpiente (REC): Para eventos inclinados (>40 deg), la corrección muestra una clara modulación sinusoidal "
        "en función del azimut. El grosor de la banda del plot Trompeta se debe a la superposición de diferentes ángulos cenitales "
        "(a mayor theta, mayor amplitud de corrección), confirmando el origen físico y no aleatorio del patrón."
    )
    
    df_infill = df_new[df_new['counterId'] >= 100000].copy()
    if len(df_infill) > 0:
        vals_sp = ensure_degrees(df_infill['phi_plane_sp'], 'SP')
        vals_ground = ensure_degrees(df_infill['phi_plane_ground_MC'], 'Ground')
        vals_euler = ensure_degrees(df_infill['phi_plane_euler_MC_true_core'], 'Euler')
        vals_rec_phi = ensure_degrees(df_infill['phi_REC'], 'PhiRec')
        vals_theta_rec = ensure_degrees(df_infill['theta_REC'], 'ThetaRec')

        vals_sp_fixed = (vals_sp + vals_rec_phi) % 360
        vals_euler_fixed = (vals_euler + 180) % 360
        diff_offline_ground = ang_diff(vals_sp_fixed, vals_ground)
        diff_euler_ground = ang_diff(vals_euler_fixed, vals_ground)
        
        # Plot 1: Histograma
        fig_geo1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.hist(diff_offline_ground, bins=100, range=(-5, 5), color='forestgreen', alpha=0.7, label='SP Fixed - Ground')
        ax1.axvline(0, color='k', linestyle='--')
        ax1.set_title("Validación: [Offline SP] vs [Ground] (Son Iguales -> SP es Incorrecto)")
        ax1.set_xlabel("Diferencia (Grados)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        pdf.add_plot(fig_geo1)
        
        # Plot 2: Mariposa REC
        fig_geo2, ax2 = plt.subplots(figsize=(10, 6))
        n_sample = min(50000, len(df_infill))
        idx = np.random.choice(df_infill.index, n_sample, replace=False)
        sc = ax2.scatter(vals_theta_rec.loc[idx], diff_euler_ground.loc[idx], s=1, c='royalblue', alpha=0.1) 
        ax2.axhline(0, color='k', linestyle='--')
        ax2.set_title("La Mariposa (REC): Corrección Euler (Necesaria) vs Cenit")
        ax2.set_xlabel(r"$\theta_{REC}$ [Grados]")
        ax2.set_ylabel(r"Corrección $\phi_{Euler} - \phi_{Ground}$ [Grados]")
        ax2.set_ylim(-40, 40)
        ax2.grid(True, alpha=0.3)
        pdf.add_plot(fig_geo2)

        # Plot 3: Serpiente REC (Theta > 40)
        mask_inclined = vals_theta_rec > 40
        if mask_inclined.sum() > 500:
            idx_snake = np.random.choice(df_infill[mask_inclined].index, min(50000, mask_inclined.sum()), replace=False)
            fig_snake, ax_snake = plt.subplots(figsize=(10, 6))
            sc_snake = ax_snake.scatter(
                vals_euler_fixed.loc[idx_snake], 
                diff_euler_ground.loc[idx_snake], 
                c=vals_theta_rec.loc[idx_snake], 
                cmap='viridis', s=1, alpha=0.5
            )
            ax_snake.axhline(0, color='k', linestyle='--')
            ax_snake.set_title(r"La Serpiente (REC): $\theta_{REC} > 40^\circ$")
            ax_snake.set_xlabel(r"Azimut $\phi_{Euler}^{REC}$ (Fixed) [Grados]")
            ax_snake.set_ylabel(r"Corrección [Grados]")
            cbar = plt.colorbar(sc_snake, ax=ax_snake)
            cbar.set_label(r"$\theta_{REC}$")
            ax_snake.set_xlim(0, 360)
            ax_snake.grid(True, alpha=0.3)
            pdf.add_plot(fig_snake)
    else:
        pdf.cell(0, 10, "No se encontraron datos de Infill.", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # --- 3. PLOT 3D ---
    pdf.add_page()
    pdf.chapter_title("3. Visualización General (3D)")
    pdf.add_description(
        r"Representación del espacio de fases cubierto por la simulación. Se grafica la señal "
        r"de muones reconstruida ($N_{\mu}^{REC}$, eje Z y color) en función de la "
        r"distancia al core (r) y el ángulo cenital ($\theta$). Este gráfico permite "
        r"inspeccionar cualitativamente la dependencia de la señal con la geometría de la lluvia."
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
        r"1. Gráfico de Dispersión (Izq): Correlación entre la Energía Verdadera (log_{10}(E_{MC})) y la Reconstruida (log_{10}(E_{REC})). "
        r"La línea punteada roja representa la identidad ideal (y=x). Desviaciones indican problemas de calibración." + "\n"
        r"2. Histograma de Residuos (Der): Distribución del error relativo (log_{10}(E_{REC}) - log_{10}(E_{MC})). "
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
        "Los histogramas de residuos (derecha) permiten cuantificar la precisión angular del detector."
    )
    # THETA
    pdf.chapter_subtitle("Resolución en Theta (Cenital)")
    delta_theta = df_events["theta_REC"] - df_events["theta_MC"]
    fig_th, axs_th = plt.subplots(1, 2, figsize=(12, 4.5))
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
    
    pdf.chapter_subtitle("Resolución en Phi (Azimutal)")
    delta_phi = (df_events["phi_REC"] - df_events["phi_MC"] + 180) % 360 - 180
    fig_ph, axs_ph = plt.subplots(1, 2, figsize=(12, 4.5))
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

    # --- 7. LDF (LIMPIO) ---
    pdf.add_page()
    pdf.chapter_title("7. Composición Física del SD")
    pdf.add_description(
        "Perfil Lateral (LDF) de las componentes físicas de la lluvia (Monte Carlo).\n"
        "Se compara el número medio de muones (Verde) vs. la componente electromagnética (Naranja) "
        "en función de la distancia al core. Se eliminan las variables reconstruidas para observar "
        "el 'crossover' físico puro entre componentes."
    )
    r_bins = np.linspace(0, 2000, 41) 
    df_new['r_bin'] = pd.cut(df_new['r_core'], bins=r_bins)
    # Solo MC counts
    comp_stats = df_new.groupby('r_bin', observed=True).agg({
        'r_core': 'mean',
        'sd_nMuons_MC': 'mean',
        'sd_nEM_MC': 'mean'
    }).dropna()
    
    if not comp_stats.empty:
        fig_comp, ax_main = plt.subplots(figsize=(10, 6))
        l1 = ax_main.plot(comp_stats['r_core'], comp_stats['sd_nMuons_MC'], 'o-', color='forestgreen', label='MC Muons', markersize=4)
        l2 = ax_main.plot(comp_stats['r_core'], comp_stats['sd_nEM_MC'], 's-', color='darkorange', label='MC EM', markersize=4)
        
        ax_main.set_xlabel("Distancia al Core [m]")
        ax_main.set_ylabel("Número Medio de Partículas (Counts)")
        ax_main.set_yscale('log')
        # Ajuste de escala automático más limpio
        ax_main.grid(True, which="both", alpha=0.3)
        ax_main.legend()
        ax_main.set_title("LDF: Composición Física (Muones vs EM)")
        pdf.add_plot(fig_comp)
    else:
        pdf.cell(0, 10, "No hay estadística suficiente para LDF.", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


    # =========================================================================
    # 8. ESTUDIOS SISTEMÁTICOS (ENERGÍA E ISOTROPÍA) - ANTES DE ASIMETRÍA
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("8. Estudios Sistemáticos")
    pdf.add_description(
        r"1. Invarianza con Energía: Se estudia la estabilidad de A_1 en un rango de cenit fijo. "
        r"La asimetría geométrica debería ser invariante." + "\n"
        r"2. Isotropía Azimutal: Se verifica que A_1 no dependa de la dirección de arribo de la lluvia "
        r"($\phi_{input}$)."
    )
    
    theta_min_inv, theta_max_inv = 30, 50
    mask_sys = (df_new['theta_REC'] >= theta_min_inv) & (df_new['theta_REC'] < theta_max_inv) & (df_new['counterId'] >= 100000)
    df_sys = df_new[mask_sys].copy()
    
    # Preparar datos desacoplados
    phi_e_rec = ensure_degrees(df_sys['phi_plane_euler_MC_true_core'])
    df_sys['phi_rec_cen'] = (phi_e_rec + 180) % 360 - 180
    if 'phi_plane_euler_MC' in df_sys.columns:
        phi_e_mc = ensure_degrees(df_sys['phi_plane_euler_MC'])
        df_sys['phi_mc_cen'] = (phi_e_mc + 180) % 360 - 180
    else: df_sys['phi_mc_cen'] = df_sys['phi_rec_cen']
    
    phi_fit_centers = (np.linspace(-180, 180, 13)[:-1] + np.linspace(-180, 180, 13)[1:]) / 2

    # --- 8.1 Energía ---
    pdf.chapter_subtitle("Invarianza con la Energía")
    
    # [FIX v8.3] Detectar rango dinámico
    if e_limits_plot:
        e_start_bin, e_end_bin = e_limits_plot[0], e_limits_plot[1]
    else:
        e_start_bin = np.floor(df_new['logE_REC'].min() * 2) / 2
        e_end_bin = np.ceil(df_new['logE_REC'].max() * 2) / 2
        if e_end_bin <= e_start_bin: e_start_bin, e_end_bin = 17.5, 18.0

    e_bins = np.linspace(e_start_bin, e_end_bin, 7) # 5 intervalos
    e_cents = (e_bins[:-1] + e_bins[1:]) / 2
    res_en = {'rec': [], 'rec_err': [], 'mc': [], 'mc_err': []}
    
    for i in range(len(e_bins)-1):
        df_b = df_sys[(df_sys['logE_REC'] >= e_bins[i]) & (df_sys['logE_REC'] < e_bins[i+1])]
        if len(df_b) < 50: 
            for k in res_en: res_en[k].append(np.nan)
            continue
        # REC
        stats_r = df_b.groupby(pd.cut(df_b['phi_rec_cen'], 12), observed=True)['nMuones_REC'].agg(['mean','sem'])
        nr = stats_r['mean'].mean()
        try: 
            popt, pcov = curve_fit(fit_func_deg, phi_fit_centers, stats_r['mean']/nr, p0=[0.05], sigma=stats_r['sem']/nr, absolute_sigma=True)
            res_en['rec'].append(popt[0]); res_en['rec_err'].append(np.sqrt(pcov[0,0]))
        except: res_en['rec'].append(np.nan); res_en['rec_err'].append(np.nan)
        # MC
        stats_m = df_b.groupby(pd.cut(df_b['phi_mc_cen'], 12), observed=True)['nMuones_MC'].agg(['mean','sem'])
        nm = stats_m['mean'].mean()
        try:
            popt, pcov = curve_fit(fit_func_deg, phi_fit_centers, stats_m['mean']/nm, p0=[0.05], sigma=stats_m['sem']/nm, absolute_sigma=True)
            res_en['mc'].append(popt[0]); res_en['mc_err'].append(np.sqrt(pcov[0,0]))
        except: res_en['mc'].append(np.nan); res_en['mc_err'].append(np.nan)

    # [NUEVO] TABLA DE RESULTADOS ENERGIA
    tbl_en_data = []
    for j in range(len(e_cents)):
        if j < len(res_en['rec']):
            row = [
                f"{e_cents[j]:.2f}",
                res_en['rec'][j], res_en['rec_err'][j],
                res_en['mc'][j], res_en['mc_err'][j]
            ]
            tbl_en_data.append(row)
    df_tbl_en = pd.DataFrame(tbl_en_data, columns=["logE", "A1_REC", "Err_REC", "A1_MC", "Err_MC"])
    pdf.create_styled_table(df_tbl_en, title="Valores A1 vs Energía")

    fig_e, ax_e = plt.subplots(figsize=(10, 5))
    ax_e.errorbar(e_cents, res_en['rec'], yerr=res_en['rec_err'], fmt='o-', label='REC', color='navy')
    ax_e.errorbar(e_cents, res_en['mc'], yerr=res_en['mc_err'], fmt='s--', label='MC', color='forestgreen')
    valid_rec = [x for x in res_en['rec'] if not np.isnan(x)]
    valid_mc = [x for x in res_en['mc'] if not np.isnan(x)]
    if valid_rec: ax_e.axhline(np.mean(valid_rec), color='navy', linestyle=':', alpha=0.5, label='Media REC')
    if valid_mc: ax_e.axhline(np.mean(valid_mc), color='forestgreen', linestyle=':', alpha=0.5, label='Media MC')
    ax_e.set_xlabel("logE"); ax_e.set_ylabel("A1"); ax_e.legend(); ax_e.grid(True, alpha=0.3)
    pdf.add_plot(fig_e)

    # 8.2 Isotropía
    pdf.add_page()
    pdf.chapter_subtitle("Isotropía Azimutal")
    phi_in_edges = np.linspace(0, 360, 7)
    phi_in_cents = (phi_in_edges[:-1] + phi_in_edges[1:]) / 2
    res_iso = {'rec': [], 'rec_err': [], 'mc': [], 'mc_err': []}
    
    phi_in_deg = ensure_degrees(df_sys['phi_REC'])
    df_sys['sect'] = pd.cut(phi_in_deg, bins=phi_in_edges)
    
    for i in range(6):
        df_s = df_sys[df_sys['sect'].cat.codes == i]
        if len(df_s) < 50:
            for k in res_iso: res_iso[k].append(np.nan)
            continue
        # REC
        stats_r = df_s.groupby(pd.cut(df_s['phi_rec_cen'], 12), observed=True)['nMuones_REC'].agg(['mean','sem'])
        nr = stats_r['mean'].mean()
        try:
            popt, pcov = curve_fit(fit_func_deg, phi_fit_centers, stats_r['mean']/nr, p0=[0.05], sigma=stats_r['sem']/nr, absolute_sigma=True)
            res_iso['rec'].append(popt[0]); res_iso['rec_err'].append(np.sqrt(pcov[0,0]))
        except: res_iso['rec'].append(np.nan); res_iso['rec_err'].append(np.nan)
        # MC
        stats_m = df_s.groupby(pd.cut(df_s['phi_mc_cen'], 12), observed=True)['nMuones_MC'].agg(['mean','sem'])
        nm = stats_m['mean'].mean()
        try:
            popt, pcov = curve_fit(fit_func_deg, phi_fit_centers, stats_m['mean']/nm, p0=[0.05], sigma=stats_m['sem']/nm, absolute_sigma=True)
            res_iso['mc'].append(popt[0]); res_iso['mc_err'].append(np.sqrt(pcov[0,0]))
        except: res_iso['mc'].append(np.nan); res_iso['mc_err'].append(np.nan)
        
    # [NUEVO] TABLA DE RESULTADOS ISOTROPIA
    tbl_iso_data = []
    for j in range(len(phi_in_cents)):
        if j < len(res_iso['rec']):
            row = [
                f"{phi_in_cents[j]:.0f}",
                res_iso['rec'][j], res_iso['rec_err'][j],
                res_iso['mc'][j], res_iso['mc_err'][j]
            ]
            tbl_iso_data.append(row)
    df_tbl_iso = pd.DataFrame(tbl_iso_data, columns=["Phi_In", "A1_REC", "Err_REC", "A1_MC", "Err_MC"])
    pdf.create_styled_table(df_tbl_iso, title="Valores A1 vs Azimut Entrada")

    fig_i, ax_i = plt.subplots(figsize=(10, 5))
    ax_i.errorbar(phi_in_cents, res_iso['rec'], yerr=res_iso['rec_err'], fmt='o-', color='navy', label='REC')
    ax_i.errorbar(phi_in_cents, res_iso['mc'], yerr=res_iso['mc_err'], fmt='s--', color='forestgreen', label='MC')
    vr_iso = [x for x in res_iso['rec'] if not np.isnan(x)]
    vm_iso = [x for x in res_iso['mc'] if not np.isnan(x)]
    if vr_iso: ax_i.axhline(np.mean(vr_iso), color='navy', linestyle=':', alpha=0.5)
    if vm_iso: ax_i.axhline(np.mean(vm_iso), color='forestgreen', linestyle=':', alpha=0.5)
    ax_i.set_xlabel("Azimut Entrada"); ax_i.set_ylabel("A1"); ax_i.legend(); ax_i.grid(True, alpha=0.3)
    pdf.add_plot(fig_i)
    
    # =========================================================================
    # 9. ASIMETRÍA AZIMUTAL - ANILLO DENSO (10 Bines + Evolución)
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("9. Asimetría Azimutal (UMD - 90k)")
    pdf.add_description(
        r"Análisis de la modulación de la señal en función del ángulo azimutal (Phi) para el Anillo Denso (referencia)." + "\n"
        r"Se ajusta la función $S = S_0 * [1 + A_1 * \cos(\phi)]$ separando los eventos en bines de $sin^2(\theta)$." + "\n"
        r"Se espera observar un crecimiento de la amplitud de asimetría A_1 conforme aumenta el ángulo cenital."
    )
    
    # 10 Bines y hasta 75 grados
    N_theta_bins = 10
    th_min_val = df_new['theta_REC'].min()
    th_max_val = min(75, df_new['theta_REC'].max())
    
    s2_bins = np.linspace(np.sin(np.deg2rad(th_min_val))**2, np.sin(np.deg2rad(th_max_val))**2, N_theta_bins + 1)
    theta_bins_deg = np.rad2deg(np.arcsin(np.sqrt(s2_bins)))
    df_new['s2_theta'] = np.sin(np.deg2rad(df_new['theta_REC']))**2
    df_new['theta_bin_idx'] = pd.cut(df_new['s2_theta'], bins=s2_bins, labels=False, include_lowest=True)
    
    df_ana = df_new[
        (df_new['counterId'] >= 90000) & (df_new['counterId'] < 100000) & 
        (df_new['module_status'].isin(['candidate', 'rejected', 'saturated']))
    ].copy().reset_index(drop=True)
    
    phi_deg = np.rad2deg(df_ana['phi_plane_sp'])
    df_ana['phi_deg_centered'] = (phi_deg + 180) % 360 - 180
    phi_bin_edges = np.linspace(-180, 180, 13)
    phi_centers = (phi_bin_edges[:-1] + phi_bin_edges[1:]) / 2
    
    fit_table = []
    # Data for evolution plot
    evol_theta, evol_a1_umd_rec, evol_err_umd_rec = [], [], []
    evol_a1_umd_mc, evol_err_umd_mc, evol_a1_sd, evol_err_sd = [], [], [], []

    for i in range(N_theta_bins):
        # SALTO DE PAGINA FORZADO EN BIN 5 y 8
        if i == 3:
            pdf.add_page()

        th_min, th_max = theta_bins_deg[i], theta_bins_deg[i+1]
        pdf.chapter_subtitle(f"Bin {i}: Theta {th_min:.1f} - {th_max:.1f} deg")
        mask_bin = (df_ana['theta_bin_idx'] == i)
        df_sl = df_ana[mask_bin].copy()
        if len(df_sl) < 50: continue
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
        a1_vals, err_vals = {}, {}

        for ax_idx, (col, label, color) in enumerate(configs):
            ax = axs[ax_idx]
            if col not in stats.columns.levels[0]: continue
            means = stats[col]['mean']
            norm = means.mean()
            if pd.isna(norm) or norm == 0: continue
            y = means / norm
            yerr = (stats[col]['std'] / np.sqrt(stats[col]['count'])) / norm 
            ax.errorbar(phi_centers, y, yerr=yerr, fmt='o', color=color, label='Data', capsize=3)
            try:
                popt, pcov = curve_fit(fit_func_deg, phi_centers, y, p0=[0.05], sigma=yerr, absolute_sigma=True)
                A1, A1_err = popt[0], np.sqrt(pcov[0,0])
                ax.plot(np.linspace(-180, 180, 100), fit_func_deg(np.linspace(-180, 180, 100), *popt), 'k--', label=rf'Fit: $A_1 = {A1:.3f} \pm {A1_err:.3f}$')
                suffix = "UMD_REC" if "REC" in label and "UMD" in label else "UMD_MC" if "MC" in label else "SD_REC"
                bin_res[f'A1_{suffix}'] = A1
                bin_res[f'Err_{suffix}'] = A1_err
                a1_vals[col], err_vals[col] = A1, A1_err
            except: pass
            ax.set_title(label); ax.set_xlim(-180, 180); ax.grid(True, alpha=0.3); ax.legend(fontsize=8)
            if ax_idx == 0: ax.set_ylabel("S / <S>")
        plt.tight_layout(); pdf.add_plot(fig)
        fit_table.append(bin_res)
        
        evol_theta.append(i)
        evol_a1_umd_rec.append(a1_vals.get('nMuones_REC', np.nan))
        evol_err_umd_rec.append(err_vals.get('nMuones_REC', 0))
        evol_a1_umd_mc.append(a1_vals.get('nMuones_MC', np.nan))
        evol_err_umd_mc.append(err_vals.get('nMuones_MC', 0))
        evol_a1_sd.append(a1_vals.get('sdSignal_REC', np.nan))
        evol_err_sd.append(err_vals.get('sdSignal_REC', 0))

    if fit_table:
        pdf.add_page()
        pdf.chapter_title("9.1 Resumen Ajustes (Anillo Denso)")
        df_res = pd.DataFrame(fit_table)
        cols_ordered = ['theta_range'] + [c for c in df_res.columns if c != 'theta_range' and c != 'theta_idx']
        pdf.create_styled_table(df_res[cols_ordered], title="Resultados Detallados")
        
        # Plot de Evolución A1 vs Theta
        pdf.chapter_subtitle("Evolución de la Asimetría")
        fig_ev, ax_ev = plt.subplots(figsize=(10, 6))
        ax_ev.errorbar(evol_theta, evol_a1_umd_rec, yerr=evol_err_umd_rec, fmt='o-', color='navy', label=r'UMD $N_\mu^{REC}$')
        ax_ev.errorbar(evol_theta, evol_a1_umd_mc, yerr=evol_err_umd_mc, fmt='s--', color='forestgreen', label=r'UMD $N_\mu^{MC}$')
        ax_ev.errorbar(evol_theta, evol_a1_sd, yerr=evol_err_sd, fmt='^-.', color='firebrick', label='SD REC')
        ax_ev.set_xlabel(r"Bin de Theta (creciente en $\sin^2\theta$)")
        ax_ev.set_ylabel(r"Amplitud de Asimetría $A_1$")
        ax_ev.set_title("Evolución de la Asimetría con el Ángulo Cenital")
        ax_ev.legend(); ax_ev.grid(True, alpha=0.3)
        pdf.add_plot(fig_ev)

    # =========================================================================
    # 10. INFILL (Formato v7 + Lógica Física)
    # =========================================================================
    pdf.add_page()
    pdf.chapter_title("10. Perfiles Infill (Bines Anchos)")
    pdf.add_description(
        r"Perfiles de asimetría para el Infill (IDs >= 100k) utilizando la proyección de Euler." + "\n"
        r"Se utiliza la lógica física desacoplada: REC usa $\phi_{Euler}^{REC}$ y MC usa $\phi_{Euler}^{MC}$."
    )
    
    r_edges_manual = [0, 400, 800, 2000]
    r_labels_manual = ["0-400 m", "400-800 m", "800-2000 m"]
    theta_edges_manual = [20, 40, 60] 
    
    df_inf_v7 = df_new[(df_new['counterId'] >= 100000) & (df_new['module_status'].isin(['candidate', 'rejected', 'saturated']))].copy()
    
    # Pre-calculo angulos (Desacoplados)
    p_rec = ensure_degrees(df_inf_v7['phi_plane_euler'])
    df_inf_v7['p_rec_cen'] = (p_rec + 180) % 360 - 180
    if 'phi_plane_euler_MC' in df_inf_v7.columns:
        p_mc = ensure_degrees(df_inf_v7['phi_plane_euler_MC'])
        df_inf_v7['p_mc_cen'] = (p_mc + 180) % 360 - 180
    else: df_inf_v7['p_mc_cen'] = df_inf_v7['p_rec_cen']
    
    df_inf_v7['r_bin_manual'] = pd.cut(df_inf_v7['r_core'], bins=r_edges_manual, labels=False, include_lowest=True)
    df_inf_v7['theta_bin_manual'] = pd.cut(df_inf_v7['theta_REC'], bins=theta_edges_manual, labels=False, include_lowest=True)

    for i in range(len(theta_edges_manual) - 1):
        if i != 0:
            pdf.add_page()
        th_min = theta_edges_manual[i]
        th_max = theta_edges_manual[i+1]
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, f"Rango Theta: {th_min:.0f}° - {th_max:.0f}°", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        df_th = df_inf_v7[df_inf_v7['theta_bin_manual'] == i]
        if df_th.empty: continue

        # --- CAMBIO DE TAMAÑO PARA AJUSTAR EN PAGINA (15, 11) ---
        fig, axs = plt.subplots(3, 3, figsize=(15, 11), sharex=True)
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

            # Agrupar segun corresponda
            df_r['bin_rec'] = pd.cut(df_r['p_rec_cen'], bins=phi_bin_edges)
            df_r['bin_mc'] = pd.cut(df_r['p_mc_cen'], bins=phi_bin_edges)
            
            # Stats distinctas
            st_rec = df_r.groupby('bin_rec', observed=True)['nMuones_REC'].agg(['mean','sem'])
            st_mc = df_r.groupby('bin_mc', observed=True)['nMuones_MC'].agg(['mean','sem'])
            st_sd = df_r.groupby('bin_rec', observed=True)['sdSignal_REC'].agg(['mean','sem'])

            for k, (col, label, color) in enumerate(configs):
                ax = axs[j, k]
                if col == 'nMuones_REC': st = st_rec
                elif col == 'nMuones_MC': st = st_mc
                else: st = st_sd
                
                means = st['mean']; sems = st['sem']; norm = means.mean()
                if pd.isna(norm) or norm == 0: continue
                ax.errorbar(phi_centers, means/norm, yerr=sems/norm, fmt='o', color=color, markersize=6, capsize=4, elinewidth=1.5)
                ax.grid(True, alpha=0.3, linestyle='--'); ax.set_xlim(-180, 180)
                if j == 0: ax.set_title(label, fontsize=12, fontweight='bold')
                if j == 2: ax.set_xlabel(r"$\phi$ [deg]", fontsize=10)
                if k == 0: ax.set_ylabel(f"{r_label}\nNorm. Amp.", fontweight='bold', fontsize=9)
                vals = means/norm
                if not vals.isna().all():
                    v_span = vals.max() - vals.min(); rango = max(v_span, 0.05) 
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
        
    out_name = f"Reporte_V8_{os.path.basename(args.folder.rstrip('/'))}.pdf"
    pdf = AnalysisPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    try:
        run_analysis(pdf, args.folder)
        pdf.output(out_name)
        print(f"Reporte generado exitosamente: {out_name}")
    except Exception:
        traceback.print_exc()