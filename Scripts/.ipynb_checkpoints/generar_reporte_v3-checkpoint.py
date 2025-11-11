#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para generar un reporte en PDF del análisis de datos de simulaciones.
Toma una carpeta de archivos parquet como entrada.

Uso:
  python generar_reporte.py /ruta/a/tu/carpeta/parquet


CAMBIE COMO ES EL FITEO Y SAQUE EL A0 Y LA FASE RELATIVA CENTRANDO LA ASIMETRIA EN PHI=0
"""

import os
import glob
import sys
import io
import argparse
from datetime import datetime

# --- Imports de tu análisis ---
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # <-- IMPORTANTE: Modo no-interactivo para scripts
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
    """Clase personalizada para tener header y footer en el PDF."""
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

    # ❗️ CAMBIO: La portada ahora recibe los stats
    def add_title_page(self, folder_path, file_count, total_modules, total_events):
        """Añade una portada al reporte."""
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
        # ❗️ Stats añadidos a la portada
        self.multi_cell(0, 10, f"Archivos procesados: {file_count}", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.multi_cell(0, 10, f"Total de módulos (filas): {total_modules:,}", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.multi_cell(0, 10, f"Total de eventos (lluvias): {total_events:,}", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(20)


def add_heading(pdf, text, level=1):
    """Añade un título de sección."""
    if level == 1:
        if pdf.get_y() > 200:
            pdf.add_page()
        else:
            pdf.ln(10)
        pdf.set_font("DejaVu", "B", 16)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, text, fill=True, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
    elif level == 2:
        if pdf.get_y() > 220:
            pdf.add_page()
        else:
            pdf.ln(5)
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, text, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

def add_body_text(pdf, text, is_mono=False):
    """Añade texto normal o monoespaciado."""
    if is_mono:
        pdf.set_font("DejaVuMono", size=9)
    else:
        pdf.set_font("DejaVu", size=10)
    pdf.multi_cell(0, 5, str(text))
    pdf.ln(2)

def add_dataframe(pdf, df, title=""):
    """Añade una versión de texto de un DataFrame."""
    if title:
        add_heading(pdf, title, level=2)
    df_text = df.to_string()
    add_body_text(pdf, df_text, is_mono=True)

def add_plot(pdf, fig=None):
    """Guarda la figura actual de plt en el PDF."""
    if fig is None:
        fig = plt.gcf()
    
    buf = io.BytesIO()
    try:
        fig.tight_layout(pad=1.5)
    except Exception:
        pass 

    fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    buf.seek(0)
    
    page_width = pdf.w - 2 * pdf.l_margin
    
    img_height = page_width * 0.7 
    if pdf.get_y() + img_height > pdf.page_break_trigger:
        pdf.add_page()
        
    pdf.image(buf, x=pdf.l_margin, w=page_width)
    pdf.ln(5)
    buf.close()
    plt.close(fig)


# =============================================================================
# 2. TU CÓDIGO DE ANÁLISIS (ADAPTADO)
# =============================================================================

# --- ❗️ 1. FUNCIÓN DE FIT (CORREGIDA, A0=1, phi0=0) ❗️ ---
def fit_func_deg(phi_deg, A1):
    """
    A1 = Amplitud de la asimetría (el 'A' que buscás)
    phi0_deg está fijo en 0.0
    """
    return 1 + A1 * np.cos(np.deg2rad(phi_deg))

# ❗️ CAMBIO: run_analysis ahora recibe el DataFrame ya cargado
def run_analysis(df_new, pdf):
    """
    Ejecuta todo tu pipeline de análisis, enviando los outputs al objeto PDF.
    """
    
    # --- 1. Carga y Limpieza (YA HECHA EN MAIN) ---
    add_heading(pdf, "1. Resumen de Datos")
    add_body_text(pdf, f"DataFrame 'df_new' (módulos) cargado con {len(df_new)} filas.")
    add_dataframe(pdf, df_new.head(), title="df_new.head()")


    # --- 2. Crear el DataFrame de EVENTOS ---
    event_cols = [
        "event_id",
        "logE_MC", "theta_MC", "phi_MC", "primary",
        "logE_REC", "theta_REC", "phi_REC"
    ]
    df_events = df_new[event_cols].drop_duplicates()

    add_body_text(pdf, f"DataFrame 'df_events' (lluvias) creado con {len(df_events)} filas únicas.")
    add_dataframe(pdf, df_events.head(), title="df_events.head()")

    # --- 3. Gráfico 3D ---
    add_heading(pdf, "2. Visualización 3D de Muones")
    add_body_text(pdf, "Generando gráfico 3D (nMuones vs r_core vs theta_REC)...")

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    df_plot = df_new[
        (df_new['nMuones'] > 0) &
        (df_new['r_core'] < 3000)
    ]
    sc = ax.scatter(
        df_plot["r_core"], df_plot["theta_REC"], df_plot["nMuones"],
        c=df_plot["nMuones"], cmap="viridis", alpha=0.7, s=10
    )
    ax.set_xlabel("Distancia al core [m]", fontsize=12, labelpad=10)
    ax.set_ylabel(r"$\theta_{REC}$ [°]", fontsize=12, labelpad=10)
    ax.set_zlabel("Número de muones", fontsize=12, labelpad=10)
    plt.title(r"Número de muones vs distancia al core y $\theta$", fontsize=14, pad=20)
    ax.set_xticks(np.arange(0, 3000 + 1, 400))
    ax.set_yticks(np.arange(0, 66 + 1, 5))
    ax.set_ylim(0, 68)
    z_max = df_plot["nMuones"].max()
    if z_max > 0:
        ax.set_zticks(np.arange(0, z_max + 1, 100))
        ax.set_zlim(0, z_max)
    cbar = plt.colorbar(sc, pad=0.1, shrink=0.8)
    cbar.set_label("Número de muones", fontsize=12)
    ax.view_init(elev=30, azim=310)
    ax.grid(True)
    
    add_plot(pdf, fig)
    
    # --- 4. Análisis de ENERGÍA ---
    add_heading(pdf, "3. Análisis de Resolución")
    add_heading(pdf, "--- 3.1. Energía (logE) ---", level=2)
    
    df_events_clean = df_events.dropna(subset=['logE_MC', 'logE_REC'])
    X_full = df_events_clean["logE_MC"]
    Y_full = df_events_clean["logE_REC"]
    deltaE_full = Y_full - X_full

    umbral_E = 0.9
    df_fit = df_events_clean[(deltaE_full.abs() < umbral_E)]
    
    X_fit_clean = df_fit["logE_MC"]
    Y_fit_clean = df_fit["logE_REC"]
    coefs_clean = np.polyfit(X_fit_clean, Y_fit_clean, 1)
    pendiente_m = coefs_clean[0]
    ordenada_b = coefs_clean[1]
    r_cuadrado = r2_score(Y_fit_clean, np.polyval(coefs_clean, X_fit_clean))

    results_text = (
        f"Resultados del Ajuste Lineal (FILTRADO con |ΔlogE| < {umbral_E}):\n"
        f"  Pendiente (m): {pendiente_m:.4f}\n"
        f"  Ordenada (b):  {ordenada_b:.4f}\n"
        f"  R^2 del ajuste:  {r_cuadrado:.4f}"
    )
    add_body_text(pdf, results_text, is_mono=True)

    fig_e = plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.scatter(X_full, Y_full, s=5, alpha=0.3, label='Datos (todos)')
    plt.plot([X_full.min(), X_full.max()], [X_full.min(), X_full.max()], 'r--', label=r"$Ideal: y=x$")
    X_line = np.linspace(X_full.min(), X_full.max(), 100)
    Y_line = np.polyval(coefs_clean, X_line)
    plt.plot(X_line, Y_line, 'g-', label=f'Ajuste (filtrado): y={pendiente_m:.2f}x + {ordenada_b:.2f}')
    plt.xlabel(r"$log_{10}(E_{MC} / eV)$")
    plt.ylabel(r"$log_{10}(E_{REC} / eV)$")
    plt.title("Comparación de Energías")
    plt.legend()
    plt.grid(True)
    plt.ylim(17.0, Y_full.max() + 0.5)

    plt.subplot(1, 2, 2)
    plt.hist(deltaE_full, bins=100, range=(-umbral_E, umbral_E), alpha=0.7, color='steelblue', label=f'Datos |ΔlogE| < {umbral_E}')
    plt.hist(deltaE_full[deltaE_full.abs() >= umbral_E], bins=20, alpha=0.7, color='red', label=f'Outliers |ΔlogE| > {umbral_E}')
    plt.xlabel(r"$\Delta log_{10}(E) = log_{10}(E_{REC}) - log_{10}(E_{MC})$")
    plt.ylabel("Frecuencia")
    plt.title("Distribución de Diferencias (Energía)")
    plt.legend()
    plt.grid(True)
    
    add_plot(pdf, fig_e)
    
    metrics_text_e = (
        "Métricas de Energía (sobre el total de datos):\n"
        f"  Sesgo (Promedio ΔlogE total): {deltaE_full.mean():.4f}\n"
        f"  Resolución (Std ΔlogE total): {deltaE_full.std():.4f}\n"
    )
    add_body_text(pdf, metrics_text_e, is_mono=True)

    # --- 5. Plot de Residuales (Energía) ---
    add_heading(pdf, "--- 3.2. Residuales de Energía vs. Energía MC ---", level=2)
    fig_res_e = plt.figure(figsize=(10, 5))
    plt.scatter(X_full, deltaE_full, s=5, alpha=0.3)
    plt.axhline(deltaE_full.mean(), color='r', linestyle='--', label=f'Sesgo Promedio = {deltaE_full.mean():.3f}')
    plt.xlabel(r"$log_{10}(E_{MC} / eV)$")
    plt.ylabel(r"$\Delta log_{10}(E)$")
    plt.title("Dependencia del Sesgo de Energía con la Energía Real")
    plt.legend()
    plt.grid(True)
    plt.ylim(-0.6, 0.6)
    
    add_plot(pdf, fig_res_e)

    # --- 6. Análisis de THETA ---
    add_heading(pdf, "--- 3.3. Ángulo Cenital (Theta) ---", level=2)
    fig_th = plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.scatter(df_events["theta_MC"], df_events["theta_REC"], s=5, alpha=0.3)
    plt.plot([0, 65], [0, 65], 'r--', label=r"$Ideal: \theta_{REC} = \theta_{MC}$")
    plt.xlabel(r"$\theta_{MC} [°]$")
    plt.ylabel(r"$\theta_{REC} [°]$")
    plt.title(r"Comparación de Ángulos $\theta$")
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    delta_theta = df_events["theta_REC"] - df_events["theta_MC"]
    plt.hist(delta_theta, bins=100, range=(-5, 5), alpha=0.7, color='darkorange')
    plt.xlabel(r"$\Delta \theta = \theta_{REC} - \theta_{MC} [°]$")
    plt.ylabel("Frecuencia")
    plt.title(r"Distribución de Diferencias $\Delta \theta$")
    plt.grid(True)
    
    add_plot(pdf, fig_th)

    umbral_theta = 5.0
    mal_theta = delta_theta.abs() > umbral_theta
    metrics_text_th = (
        "Métricas de Theta:\n"
        f"  Sesgo (Promedio Δθ): {delta_theta.mean():.4f}°\n"
        f"  Resolución (Std Dev Δθ): {delta_theta.std():.4f}°\n"
        f"  Eventos con |Δθ| > {umbral_theta}°: {mal_theta.sum()} (de {len(df_events)} eventos, {mal_theta.mean()*100:.2f}%)"
    )
    add_body_text(pdf, metrics_text_th, is_mono=True)

    # --- 7. Análisis de PHI ---
    add_heading(pdf, "--- 3.4. Ángulo Azimutal (Phi) ---", level=2)
    fig_ph = plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.scatter(df_events["phi_MC"], df_events["phi_REC"], s=5, alpha=0.3)
    plt.plot([0, 360], [0, 360], 'r--', label=r"$Ideal: \phi_{REC} = \phi_{MC}$")
    plt.xlabel(r"$\phi_{MC} [°]$")
    plt.ylabel(r"$\phi_{REC} [°]$")
    plt.title(r"Comparación de Ángulos $\phi$")
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    delta_phi = (df_events["phi_REC"] - df_events["phi_MC"] + 180) % 360 - 180
    plt.hist(delta_phi, bins=100, range=(-15, 15), alpha=0.7, color='seagreen')
    plt.xlabel(r"$\Delta \phi = \phi_{REC} - \phi_{MC} [°]$ (ajustado a [-180,180])")
    plt.ylabel("Frecuencia")
    plt.title(r"Distribución de Diferencias $\Delta \phi$")
    plt.grid(True)

    add_plot(pdf, fig_ph)
    
    median_phi = delta_phi.median()
    mad_phi = (delta_phi - median_phi).abs().median()
    umbral_phi = 10.0
    mal_phi = delta_phi.abs() > umbral_phi
    metrics_text_ph = (
        "Métricas de Phi:\n"
        f"  Sesgo (Mediana Δφ): {median_phi:.4f}°\n"
        f"  Resolución (MAD Δφ): {mad_phi:.4f}°\n"
        f"  Eventos con |Δφ| > {umbral_phi}°: {mal_phi.sum()} (de {len(df_events)} eventos, {mal_phi.mean()*100:.2f}%)"
    )
    add_body_text(pdf, metrics_text_ph, is_mono=True)

    # --- 8. Uniformidad por COUNTER ---
    add_heading(pdf, "4. Uniformidad por Counter")
    df_counters = df_new.groupby(['event_id', 'counterId'])['nMuones'].sum().reset_index()
    counter_stats = df_counters.groupby('counterId')['nMuones'].agg(
        promedio='mean', std_dev='std', cantidad='count'
    ).reset_index()
    stats_con_senal = counter_stats[counter_stats['promedio'] > 0].copy()
    stats_con_senal['counterId_str'] = stats_con_senal['counterId'].astype(str)

    add_body_text(pdf, f"Mostrando {len(stats_con_senal)} counters con señal (de {len(counter_stats)} totales)")

    fig_unif, axs = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
    fig_unif.suptitle("Uniformidad de Respuesta por Counter (Solo counters con señal)", fontsize=16)
    axs[0].bar(stats_con_senal['counterId_str'], stats_con_senal['promedio'], color='skyblue')
    axs[0].set_ylabel("Promedio de muones")
    axs[0].grid(axis='y')
    axs[1].bar(stats_con_senal['counterId_str'], stats_con_senal['std_dev'], color='salmon')
    axs[1].set_ylabel("Desviación estándar")
    axs[1].set_xlabel("ID de counter (no a escala)")
    axs[1].grid(axis='y')
    tick_labels = stats_con_senal['counterId_str'].values
    tick_positions = np.arange(len(tick_labels))
    axs[1].set_xticks(tick_positions[::10])
    axs[1].set_xticklabels(tick_labels[::10], rotation=90)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    add_plot(pdf, fig_unif)

    # --- 9. MAPAS POLARES ---
    add_heading(pdf, "5. Mapas Polares por Bin de Theta")
    
    r_max = 500
    r_bin_size = 10
    phi_bins = 24
    r_bins = np.arange(0, r_max + r_bin_size, r_bin_size)
    phi_edges = np.linspace(0, 2*np.pi, phi_bins + 1)
    R, Phi = np.meshgrid(r_bins, phi_edges)

    N_theta_bins = 6
    theta_min_deg = 0
    theta_max_deg = 66
    theta_min_real = df_new['theta_REC'].min()
    theta_max_real = df_new['theta_REC'].max()
    add_body_text(pdf, f"Rango de Theta en los datos: [{theta_min_real:.2f}°, {theta_max_real:.2f}°]")
    theta_max_deg = min(theta_max_deg, theta_max_real)
    
    s2_min = np.sin(np.deg2rad(theta_min_deg))**2
    s2_max = np.sin(np.deg2rad(theta_max_deg))**2
    s2_bins = np.linspace(s2_min, s2_max, N_theta_bins + 1)
    theta_bins_deg = np.rad2deg(np.arcsin(np.sqrt(s2_bins)))
    
    add_body_text(pdf, f"Bordes de bins en Theta (grados): {np.round(theta_bins_deg, 2)}")
    
    if 's2_theta' not in df_new.columns:
        df_new['s2_theta'] = np.sin(np.deg2rad(df_new['theta_REC']))**2
        df_new['theta_bin'] = pd.cut(df_new['s2_theta'], bins=s2_bins, labels=False, include_lowest=True)
    
    df_mapa_total = df_new[
        (df_new['r_core'].between(0, r_max)) &
        (df_new['nMuones'].notna()) &
        (df_new['phi_plane'].notna())
    ].copy()

    for i in range(N_theta_bins):
        df_bin = df_mapa_total[df_mapa_total['theta_bin'] == i]
        if df_bin.empty:
            add_body_text(pdf, f"Sin datos para el bin de theta {i}. Saltando.")
            continue

        th_min_label = theta_bins_deg[i]
        th_max_label = theta_bins_deg[i+1]
        plot_title = rf"Mapa polar, $\theta \approx$ [{th_min_label:.1f}°, {th_max_label:.1f}°]"
        add_body_text(pdf, f"Ploteando bin {i}: {plot_title}")
        
        Z, _, _ = np.histogram2d(
            x=df_bin['r_core'], y=df_bin['phi_plane'],
            bins=[r_bins, phi_edges], weights=df_bin['nMuones']
        )
        counts, _, _ = np.histogram2d(
            x=df_bin['r_core'], y=df_bin['phi_plane'],
            bins=[r_bins, phi_edges]
        )
        Z_T = Z.T
        counts_T = counts.T
        Z_avg = np.divide(Z_T, counts_T, out=np.zeros_like(Z_T), where=counts_T != 0)
        
        fig_polar, ax = plt.subplots(figsize=(8,8), subplot_kw=dict(polar=True))
        c = ax.pcolormesh(Phi, R, Z_avg, cmap='viridis', shading='auto')
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_rlim(0, r_max)
        fig_polar.colorbar(c, ax=ax, label="Número promedio de muones")
        plt.title(plot_title)
        
        add_plot(pdf, fig_polar)


    # --- 11. ANÁLISIS DE ASIMETRÍA (CON FITS) ---
    add_heading(pdf, "6. Análisis de Asimetría Azimutal (Anillo Denso)")

    # --- Parámetros de binning (en grados) ---
    phi_plot_bins = 12
    phi_bin_edges = np.linspace(-180, 180, phi_plot_bins + 1)
    phi_bin_labels = range(phi_plot_bins)
    phi_bin_centers = (phi_bin_edges[:-1] + phi_bin_edges[1:]) / 2.0

    # --- CREAMOS EL DF "LIMPIO" --- Ya no hago mas esto porque creo q es al pedo
    df_limpio = df_new.copy()
    
    if 'phi_plane_centered_deg' not in df_limpio.columns:
        phi_plane_deg = np.rad2deg(df_limpio['phi_plane'])
        df_limpio['phi_plane_centered_deg'] = (phi_plane_deg + 180) % 360 - 180

    # --- FILTRAMOS POR ID para el Anillo Denso ---
    df_anillo_denso = df_limpio[
        (df_limpio['counterId'] >= 90000) &
        (df_limpio['counterId'] < 100000)
    ].copy()
    add_body_text(pdf, f"Usando {len(df_anillo_denso)} filas (módulos) 'limpios' del Anillo Denso")
    
    # --- INICIALIZAMOS LISTA PARA EL RESUMEN ---
    fit_results = []
    
    # --- Bucle anidado ---
    for i in range(N_theta_bins):
        
        th_min_label = theta_bins_deg[i]
        th_max_label = theta_bins_deg[i+1]
        theta_range_str = f"[{th_min_label:.1f}°, {th_max_label:.1f}°]"
        plot_title_prefix = f"Asimetría del Anillo Denso para $\\theta \\approx$ {theta_range_str}"

        df_slice = df_anillo_denso[
            (df_anillo_denso['theta_bin'] == i) &
            (df_anillo_denso['sdSignal'].notna()) &
            (df_anillo_denso['nMuones'].notna())
        ].copy()

        if df_slice.empty or len(df_slice) < 50:
            add_body_text(pdf, f"  Bin de theta {i} ({theta_range_str}): Datos insuficientes. Saltando.")
            continue
        
        add_body_text(pdf, f"  Procesando bin de theta {i} ({theta_range_str}): {len(df_slice)} módulos encontrados.")

        # --- CÁLCULO DE DENSIDAD ---
        df_slice['phi_bin'] = pd.cut(df_slice['phi_plane_centered_deg'], bins=phi_bin_edges, labels=phi_bin_labels, include_lowest=True)
        
        phi_stats_cat = df_slice.groupby('phi_bin', observed=True).agg(
            umd_mean_density=('nMuones', 'mean'),
            umd_std_dev=('nMuones', 'std'),
            umd_N_entries=('nMuones', 'count'),
            sd_mean_density=('sdSignal', 'mean'),
            sd_std_dev=('sdSignal', 'std'),
            sd_N_entries=('sdSignal', 'count')
        )
        
        phi_stats_cat['umd_sem'] = phi_stats_cat['umd_std_dev'] / np.sqrt(phi_stats_cat['umd_N_entries'])
        phi_stats_cat['sd_sem'] = phi_stats_cat['sd_std_dev'] / np.sqrt(phi_stats_cat['sd_N_entries'])

        umd_overall_mean = phi_stats_cat['umd_mean_density'].mean()
        sd_overall_mean = phi_stats_cat['sd_mean_density'].mean()

        phi_stats_cat['umd_S_norm'] = phi_stats_cat['umd_mean_density'] / umd_overall_mean
        phi_stats_cat['umd_S_norm_err'] = phi_stats_cat['umd_sem'] / umd_overall_mean
        phi_stats_cat['sd_S_norm'] = phi_stats_cat['sd_mean_density'] / sd_overall_mean
        phi_stats_cat['sd_S_norm_err'] = phi_stats_cat['sd_sem'] / sd_overall_mean
        
        int_index = phi_stats_cat.index.astype(int)
        phi_stats = pd.DataFrame({
            'phi_center': phi_bin_centers[int_index],
            'umd_S_norm': phi_stats_cat['umd_S_norm'],
            'umd_S_norm_err': phi_stats_cat['umd_S_norm_err'],
            'sd_S_norm': phi_stats_cat['sd_S_norm'],
            'sd_S_norm_err': phi_stats_cat['sd_S_norm_err'],
            'N_umd': phi_stats_cat['umd_N_entries'],
            'N_sd': phi_stats_cat['sd_N_entries']
        })

        # --- Plotear (2 subplots) ---
        fig_asym, axs = plt.subplots(1, 2, figsize=(18, 7), sharey=True)
        fig_asym.suptitle(plot_title_prefix, fontsize=16)

        # --- Plot 1: UMD (nMuones) ---
        x_umd = phi_stats['phi_center']
        y_umd = phi_stats['umd_S_norm']
        yerr_umd = phi_stats['umd_S_norm_err']
        
        axs[0].errorbar(x_umd, y_umd, yerr=yerr_umd, fmt='o', ms=8, mec='black', mfc='navy', capsize=5, label='UMD (Datos)')
        
        try:
            # ❗️ CAMBIO: p0 ahora solo tiene 1 parámetro (A1)
            popt_umd, pcov_umd = curve_fit(fit_func_deg, x_umd, y_umd, p0=[0.05], sigma=yerr_umd)
            # ❗️ CAMBIO: popt ahora es [A1]
            A1_umd, A1_err_umd = popt_umd[0], np.sqrt(pcov_umd[0,0])
            
            phi_smooth_deg = np.linspace(-180, 180, 100)
            axs[0].plot(phi_smooth_deg, fit_func_deg(phi_smooth_deg, *popt_umd),
                        'b:', label=rf'Fit (fijo $\phi_0=0$) $A_1 = {A1_umd:.3f} \pm {A1_err_umd:.3f}$')
            fit_results.append({
                'theta_bin': i, 'theta_range': theta_range_str, 'detector': 'UMD',
                'A1': A1_umd, 'A1_err': A1_err_umd, 'phi0_deg': 0.0, # Fijo
                'N_modulos': phi_stats['N_umd'].sum()
            })
        except RuntimeError:
            add_body_text(pdf, f"  Fit de UMD no convergió para el bin {i}.")

        axs[0].set_title('UMD (nMuones)')

        # --- Plot 2: SD (sdSignal) ---
        x_sd = phi_stats['phi_center']
        y_sd = phi_stats['sd_S_norm']
        yerr_sd = phi_stats['sd_S_norm_err']

        axs[1].errorbar(x_sd, y_sd, yerr=yerr_sd, fmt='o', ms=8, mec='black', mfc='darkred', capsize=5, label='SD (Datos)')

        try:
            # ❗️ CAMBIO: p0 ahora solo tiene 1 parámetro (A1)
            popt_sd, pcov_sd = curve_fit(fit_func_deg, x_sd, y_sd, p0=[0.05], sigma=yerr_sd)
            # ❗️ CAMBIO: popt ahora es [A1]
            A1_sd, A1_err_sd = popt_sd[0], np.sqrt(pcov_sd[0,0])

            phi_smooth_deg = np.linspace(-180, 180, 100)
            axs[1].plot(phi_smooth_deg, fit_func_deg(phi_smooth_deg, *popt_sd),
                        'r:', label=rf'Fit (fijo $\phi_0=0$) $A_1 = {A1_sd:.3f} \pm {A1_err_sd:.3f}$')
            fit_results.append({
                'theta_bin': i, 'theta_range': theta_range_str, 'detector': 'SD',
                'A1': A1_sd, 'A1_err': A1_err_sd, 'phi0_deg': 0.0, # Fijo
                'N_modulos': phi_stats['N_sd'].sum()
            })
        except RuntimeError:
            add_body_text(pdf, f"  Fit de SD no convergió para el bin {i}.")

        axs[1].set_title('SD (sdSignal - Total)')
        
        for ax in axs:
            ax.set_xlabel(r"Ángulo azimutal $\phi$ [°]")
            ax.set_ylabel(r"Señal / Promedio (S / <S>)")
            ax.set_xticks(np.linspace(-180, 180, 5), [r'$-180^\circ$', r'$-90^\circ$', '0°', r'$90^\circ$', r'$180^\circ$'])
            ax.set_xlim(-180, 180)
            ax.axhline(1.0, color='gray', linestyle='--', label='Promedio (Simetría)')
            ax.grid(True)
            ax.legend()
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        add_plot(pdf, fig_asym) # En lugar de plt.show()


    # --- 8. IMPRIMIR RESUMEN ESTADÍSTICO ---
    add_heading(pdf, "7. Resumen de Fits de Asimetría (A1)")
    
    if fit_results:
        df_results = pd.DataFrame(fit_results)
        add_dataframe(pdf, df_results, title="Resultados del Fit (A1, phi0=0 fijo)")
    else:
        add_body_text(pdf, "No se completó ningún fit.")
    
    add_body_text(pdf, "\n\n--- FIN DEL REPORTE ---")


# =============================================================================
# 3. FUNCIÓN PRINCIPAL (MAIN)
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generador de Reportes de Análisis de Datos")
    parser.add_argument("folder_path", type=str, help="Ruta a la carpeta que contiene los archivos .parquet")
    
    args = parser.parse_args()
    
    folder_path = os.path.abspath(args.folder_path)
    
    if not os.path.isdir(folder_path):
        print(f"Error: La ruta especificada no es un directorio válido: {folder_path}", file=sys.stderr)
        sys.exit(1)
        
    cleaned_path = folder_path.rstrip(os.sep)
    base_name = os.path.basename(cleaned_path)
    output_filename = f"Reporte_{base_name}_v3.pdf"
    
    print(f"Iniciando generación de reporte...")
    print(f"Carpeta de entrada: {folder_path}")
    print(f"Archivo de salida: {output_filename}")
    
    # Inicializar PDF
    pdf = PDF()
    
    # --- AÑADIR FUENTES UNICODE ---
    try:
        # Busca las fuentes en la misma carpeta que el script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pdf.add_font("DejaVu", "", os.path.join(script_dir, "DejaVuSans.ttf"))
        pdf.add_font("DejaVu", "B", os.path.join(script_dir, "DejaVuSans-Bold.ttf"))
        pdf.add_font("DejaVuMono", "", os.path.join(script_dir, "DejaVuSansMono.ttf"))
        
        pdf.set_font("DejaVu", size=10)
        pdf.set_fallback_fonts(["DejaVu"])
    except FileNotFoundError:
        print("\n" + "="*60, file=sys.stderr)
        print("  ERROR: No se encontraron los archivos de fuente (.ttf).", file=sys.stderr)
        print("  Asegúrate de tener 'DejaVuSans.ttf', 'DejaVuSans-Bold.ttf',", file=sys.stderr)
        print("  y 'DejaVuSansMono.ttf' en la misma carpeta que este script.", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)
        sys.exit(1)
    
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    
    # --- ❗️ CORRECCIÓN DE LÓGICA DE CARGA ❗️ ---
    try:
        # 1. Cargar datos ANTES de la portada
        print("Cargando datos para el resumen de portada...")
        all_parquet_files = glob.glob(os.path.join(folder_path, "*.parquet"))
        if not all_parquet_files:
            print(f"Error: No se encontraron archivos .parquet en {folder_path}", file=sys.stderr)
            sys.exit(1)
            
        df_list = []
        for fpath in all_parquet_files:
            df_list.append(pd.read_parquet(fpath))
        df_new = pd.concat(df_list, ignore_index=True)
        
        # 2. Limpieza básica
        df_new.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_new.dropna(subset=['logE_REC', 'theta_REC', 'phi_REC'], inplace=True)
        
        total_modules = len(df_new)
        total_events = df_new["event_id"].nunique()
        
        # 3. Portada (ahora con los números correctos)
        pdf.add_title_page(folder_path, len(all_parquet_files), total_modules, total_events)
        
        # 4. Ejecutar el análisis (pasando el df ya cargado)
        run_analysis(df_new, pdf) # ❗️ Pasamos el DF, no el path

    except Exception as e:
        print(f"\nERROR DURANTE LA EJECUCIÓN DEL ANÁLISIS:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 16)
        pdf.set_text_color(255, 0, 0) # Rojo
        pdf.cell(0, 10, "ERROR EN EL SCRIPT", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("DejaVuMono", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 5, f"El análisis falló con el siguiente error:\n\n{traceback.format_exc()}")
        
    # Guardar el PDF
    pdf.output(output_filename)
    print(f"¡Reporte guardado exitosamente como '{output_filename}'!")


if __name__ == "__main__":
    main()