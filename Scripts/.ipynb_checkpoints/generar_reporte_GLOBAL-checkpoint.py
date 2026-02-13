#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generar_reporte_GLOBAL.py
Autor: Lautaro Silva Pizzi
Versión: 1.0
"""

import os
import glob
import pdfplumber
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.stats import norm
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
import io
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# =============================================================================
# 1. CONFIGURACIÓN
# =============================================================================
COLORS = {'Proton': 'royalblue', 'Helio': 'forestgreen', 'Hierro': 'firebrick', 'Oxigeno': 'purple'}
MARKERS = {'SIBYLL': 'o', 'QGSJet': 's', 'EPOS': '^'}
THETA_LABELS = [
    r"$0^{\circ}-21^{\circ}$", r"$21^{\circ}-31^{\circ}$", r"$31^{\circ}-40^{\circ}$", 
    r"$40^{\circ}-48^{\circ}$", r"$48^{\circ}-56^{\circ}$", r"$56^{\circ}-60^{\circ}$",
    r"$60^{\circ}-64^{\circ}$", r"$64^{\circ}-68^{\circ}$", r"$68^{\circ}-72^{\circ}$", r"$72^{\circ}-75^{\circ}$"
]

# =============================================================================
# 2. CLASE PDF
# =============================================================================
class GlobalReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Reporte Global de Tesis - Asimetría UMD/SD", 0, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(10, 25, 200, 25); self.ln(10)

    def footer(self):
        self.set_y(-15); self.set_font("Helvetica", "I", 8); self.cell(0, 10, f"Pág {self.page_no()}", 0, align="C")

    def section_title(self, title):
        self.ln(5); self.set_font("Helvetica", "B", 14); self.set_fill_color(230, 230, 250)
        self.cell(0, 10, f" {title}", 0, align='L', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def add_text(self, text):
        self.set_font("Times", "", 11)
        self.multi_cell(0, 5, text)
        self.ln(5)
    
    def add_formula(self, formula_text):
        self.ln(2)
        self.set_font("Courier", "B", 11)
        self.set_fill_color(245, 245, 245) 
        self.cell(0, 10, formula_text, 0, align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def add_plot_from_fig(self, fig):
        buf = io.BytesIO()
        try: fig.tight_layout()
        except: pass
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        self.image(buf, w=190); self.ln(5); buf.close(); plt.close(fig)

    def create_styled_table(self, df, title=None, col_widths=None):
        if title:
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 8, title, 0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

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
                if isinstance(val, float): val = f"{val:.4f}"
                else: val = str(val)
                self.cell(col_widths[i], 6, val, border=1, align='C', fill=True)
            self.ln()
            fill = not fill
        self.ln(5)

# =============================================================================
# 3. EXTRACCIÓN Y LIMPIEZA DE DATOS
# =============================================================================
def parse_metadata(filename):
    f = filename.lower()
    model = 'SIBYLL' if 'sib' in f else 'QGSJet' if 'qgs' in f else 'EPOS' if 'epos' in f else 'Unknown'
    if 'proton' in f: primary = 'Proton'
    elif 'iron' in f or 'hierro' in f: primary = 'Hierro'
    elif 'helium' in f or 'helio' in f: primary = 'Helio'
    elif 'oxygen' in f or 'oxigeno' in f: primary = 'Oxigeno'
    else: primary = 'Unknown'
    energy = '18.0' if '18' in f and '17' not in f else '17.5'
    return model, primary, energy

def extract_all_tables(pdf_path):
    tables_data = {'main': [], 'energy': [], 'isotropy': []}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2: continue
                    header = [str(x).replace('\n', '') for x in table[0]]
                    header_str = " ".join(header)
                    
                    if "logE" in header_str and "A1_REC" in header_str:
                        for row in table[1:]:
                            try: tables_data['energy'].append({'logE': float(row[0]), 'A1': float(row[1]), 'Err': float(row[2])})
                            except: pass
                    elif "Phi_In" in header_str and "A1_REC" in header_str:
                        for row in table[1:]:
                            try: tables_data['isotropy'].append({'Phi_In': float(row[0]), 'A1': float(row[1]), 'Err': float(row[2])})
                            except: pass
                    elif len(table[0]) >= 5 and ("Range" in str(table[0][0]) or "-" in str(table[1][0])):
                        start = 1 if "Range" in str(table[0][0]) else 0
                        for row in table[start:]:
                            try:
                                d = {'Theta_Range': row[0], 'A1_UMD_REC': float(row[1]), 'Err_UMD_REC': float(row[2]),
                                     'A1_UMD_MC': float(row[3]), 'Err_UMD_MC': float(row[4])}
                                if len(row) >= 7: d.update({'A1_SD_REC': float(row[5]), 'Err_SD_REC': float(row[6])})
                                else: d.update({'A1_SD_REC': np.nan, 'Err_SD_REC': np.nan})
                                tables_data['main'].append(d)
                            except: pass
    except: pass
    return tables_data

def clean_systematic_table(df, key_col, decimals=2):
    """Limpia tablas sistemáticas: redondea, agrupa y promedia."""
    if df.empty: return df
    # Redondear clave para evitar 17.5 vs 17.50001
    df[key_col] = df[key_col].round(decimals)
    # Agrupar por clave y promediar valores (A1, Err) - Esto fusiona duplicados
    df_clean = df.groupby(key_col, as_index=False).mean()
    return df_clean.sort_values(key_col).reset_index(drop=True)

def get_consolidated_data(pattern="Reporte_V8_*.pdf"):
    files = glob.glob(pattern); files.sort()
    print(f"--> Procesando {len(files)} archivos...")
    main_list = []
    special_tables = {'energy': pd.DataFrame(), 'isotropy': pd.DataFrame()}
    
    extracted_sys = False 
    
    for f in files:
        mod, prim, en = parse_metadata(os.path.basename(f))
        extracted = extract_all_tables(f)
        
        # 1. Datos Principales
        for row in extracted['main']:
            row.update({'Model': mod, 'Primary': prim, 'Energy': en, 'File': f})
            main_list.append(row)
        
        # 2. Datos Sistemáticos (Solo PRIMER archivo Helio SIBYLL)
        if not extracted_sys and prim == 'Helio' and mod == 'SIBYLL':
            if extracted['energy']:
                special_tables['energy'] = pd.DataFrame(extracted['energy'])
            if extracted['isotropy']:
                special_tables['isotropy'] = pd.DataFrame(extracted['isotropy'])
            
            if not special_tables['energy'].empty or not special_tables['isotropy'].empty:
                extracted_sys = True
                print(f"   -> Tablas sistemáticas extraídas de: {os.path.basename(f)}")

    # LIMPIEZA FINAL
    if not special_tables['energy'].empty:
        special_tables['energy'] = clean_systematic_table(special_tables['energy'], 'logE', 2)
        
    if not special_tables['isotropy'].empty:
        special_tables['isotropy'] = clean_systematic_table(special_tables['isotropy'], 'Phi_In', 0)

    df_main = pd.DataFrame(main_list)
    if not df_main.empty:
        df_main.drop_duplicates(subset=['Primary', 'Model', 'Energy', 'Theta_Range'], inplace=True)
        df_main['Theta_Bin_Idx'] = df_main.groupby(['Primary', 'Model', 'Energy']).cumcount()
        
    return df_main, special_tables

# =============================================================================
# 4. PLOTS
# =============================================================================

def calc_mf(mu1, sig1, mu2, sig2):
    denom = np.sqrt(sig1**2 + sig2**2)
    if denom == 0: return 0.0
    return abs(mu1 - mu2) / denom

# --- PLOT 1: GRAND FINALE ---
def plot_grand_finale(df):
    fig, ax = plt.subplots(figsize=(14, 8))
    groups = df.groupby(['Primary', 'Model', 'Energy'])
    prim_shift = {'Proton': -0.2, 'Helio': 0.0, 'Oxigeno': 0.1, 'Hierro': 0.2}
    det_shift  = {'UMD_REC': 0.0, 'UMD_MC': 0.02, 'SD_REC': -0.02}

    for (prim, mod, en), group in groups:
        group = group.sort_values('Theta_Bin_Idx')
        x_base = group['Theta_Bin_Idx'].values
        
        c = COLORS.get(prim, 'gray')
        m = MARKERS.get(mod, 'o')
        shift = prim_shift.get(prim, 0)
        
        ax.errorbar(x_base + shift + det_shift['UMD_MC'], group['A1_UMD_MC'], yerr=group['Err_UMD_MC'], 
                    fmt=m, color=c, alpha=0.3, markersize=5, label='_nolegend_')
        ax.errorbar(x_base + shift + det_shift['SD_REC'], group['A1_SD_REC'], yerr=group['Err_SD_REC'], 
                    fmt=m, color=c, mfc='white', mec=c, mew=1.5, alpha=0.7, label='_nolegend_')
        ax.errorbar(x_base + shift + det_shift['UMD_REC'], group['A1_UMD_REC'], yerr=group['Err_UMD_REC'], 
                    fmt=m, color=c, mfc=c, alpha=1.0, label='_nolegend_')

    ax.set_title(r"Panorama Completo: Asimetría $A_1$ (UMD Anillo Denso)", pad=15)
    ax.set_ylabel(r"Amplitud de Asimetría ($A_1$)")
    ax.set_xlabel(r"Rango Angular Cenital ($\theta$)")
    
    ticks = np.unique(df['Theta_Bin_Idx'])
    ax.set_xticks(ticks)
    labels = [THETA_LABELS[i] if i < len(THETA_LABELS) else str(i) for i in ticks]
    ax.set_xticklabels(labels, rotation=45)
    
    ax.grid(True, which='both', linestyle='--', alpha=0.4)
    ax.set_ylim(bottom=0)

    leg_prim = [Line2D([0],[0], color=v, marker='o', lw=0, label=k) for k,v in COLORS.items()]
    l1 = plt.legend(handles=leg_prim, title="Primario", loc='upper left', bbox_to_anchor=(0.01, 0.98))
    ax.add_artist(l1)
    
    leg_mod = [Line2D([0],[0], color='k', marker=v, lw=0, label=k) for k,v in MARKERS.items()]
    l2 = plt.legend(handles=leg_mod, title="Modelo", loc='upper left', bbox_to_anchor=(0.15, 0.98))
    ax.add_artist(l2)
    
    leg_det = [
        Line2D([0],[0], color='k', marker='o', mfc='k', lw=0, label='UMD REC'),
        Line2D([0],[0], color='k', marker='o', mfc='white', mec='k', mew=1.5, lw=0, label='SD REC'),
        Line2D([0],[0], color='gray', marker='o', alpha=0.4, lw=0, label='UMD MC')
    ]
    plt.legend(handles=leg_det, title="Detector", loc='upper left', bbox_to_anchor=(0.30, 0.98))
    return fig

# --- UTILS GAUSSIANAS ---
def plot_annotated_gaussians(ax, mus, sigs, labels, colors, title):
    x_min = min([m - 4*s for m, s in zip(mus, sigs)])
    x_max = max([m + 4*s for m, s in zip(mus, sigs)])
    x = np.linspace(x_min, x_max, 500)
    max_y_plot = 0
    
    for mu, sig, lab, col in zip(mus, sigs, labels, colors):
        y = norm.pdf(x, mu, sig)
        ax.plot(x, y, color=col, lw=2)
        ax.fill_between(x, y, alpha=0.1, color=col)
        peak_y = norm.pdf(mu, mu, sig)
        ax.text(mu, peak_y + (peak_y*0.05), lab, ha='center', color=col, fontweight='bold', fontsize=10)
        if peak_y > max_y_plot: max_y_plot = peak_y

    ax.set_ylim(0, max_y_plot * 1.2)
    ax.set_title(title)
    ax.set_xlabel(r"Amplitud $A_1$")
    ax.set_ylabel("Densidad de Probabilidad")
    ax.grid(False)

def plot_gaussians_with_table(ax_gauss, ax_table, mus, sigs, labels):
    x_min = min([m - 4*s for m, s in zip(mus, sigs)])
    x_max = max([m + 4*s for m, s in zip(mus, sigs)])
    x = np.linspace(x_min, x_max, 500)
    
    cmap = plt.get_cmap('viridis')
    cols = [cmap(i) for i in np.linspace(0, 0.9, len(mus))]
    
    for mu, sig, lab, col in zip(mus, sigs, labels, cols):
        y = norm.pdf(x, mu, sig)
        ax_gauss.plot(x, y, label=lab, color=col, lw=2)
        ax_gauss.fill_between(x, y, alpha=0.1, color=col)
        peak_y = norm.pdf(mu, mu, sig)
        ax_gauss.text(mu, peak_y, lab, ha='center', va='bottom', color=col, fontsize=9, fontweight='bold')

    # Matriz MF
    cell_text = []
    for i in range(len(mus)):
        row = []
        for j in range(len(mus)):
            if i == j: val = "-"
            else: val = f"{calc_mf(mus[i], sigs[i], mus[j], sigs[j]):.1f}"
            row.append(val)
        cell_text.append(row)
        
    ax_table.axis('off')
    tbl = ax_table.table(cellText=cell_text, rowLabels=labels, colLabels=labels, loc='center', cellLoc='center')
    tbl.scale(1, 1.5); tbl.set_fontsize(10)

# --- PLOT 2: DISCRIMINACIÓN MASAS (SIBYLL 17.5) ---
def plot_mass_mf(df, model='SIBYLL', energy='17.5', bin_idx=5):
    sub = df[(df['Model']==model) & (df['Energy']==energy) & (df['Theta_Bin_Idx']==bin_idx)]
    if sub.empty: return None, 0.0
    
    mus, sigs, labs, cols = [], [], [], []
    proton_stats, iron_stats = None, None
    
    for p in ['Proton', 'Helio', 'Oxigeno', 'Hierro']:
        r = sub[sub['Primary']==p]
        if not r.empty:
            m, s = r['A1_UMD_REC'].values[0], r['Err_UMD_REC'].values[0]
            mus.append(m); sigs.append(s); labs.append(p); cols.append(COLORS.get(p))
            if p == 'Proton': proton_stats = (m, s)
            if p == 'Hierro': iron_stats = (m, s)
    
    if len(mus) < 2: return None, 0.0
    
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_annotated_gaussians(ax, mus, sigs, labs, cols, f"Discriminación de Masa ({model} {energy} - Bin {bin_idx})")
    
    mf_p_fe = 0.0
    if proton_stats and iron_stats:
        mf_p_fe = calc_mf(proton_stats[0], proton_stats[1], iron_stats[0], iron_stats[1])
        ax2 = ax.twinx()
        limit_sigma = max(4.0, mf_p_fe + 1.0)
        ax2.set_ylim(0, limit_sigma)
        ax2.set_ylabel(r"Separación MF ($\sigma$)", color='navy')
        ax2.axhline(mf_p_fe, color='navy', linestyle='--', linewidth=1.5, alpha=0.7)
        ax2.text(ax.get_xlim()[1], mf_p_fe + 0.1, rf" MF: {mf_p_fe:.2f}$\sigma$", 
                 ha='right', va='bottom', color='navy', fontweight='bold')
        
    return fig, mf_p_fe

# --- PLOT 3: MODELOS (HELIO 17.5) ---
def plot_models_mf(df, primary='Helio', energy='17.5', bin_idx=5):
    sub = df[(df['Primary']==primary) & (df['Energy']==energy) & (df['Theta_Bin_Idx']==bin_idx)]
    if sub.empty: return None, 0.0
    
    models_target = ['SIBYLL', 'QGSJet']
    mus, sigs, labs, cols = [], [], [], []
    stats = {}
    
    for m in models_target:
        r = sub[sub['Model']==m]
        if not r.empty:
            val, err = r['A1_UMD_REC'].values[0], r['Err_UMD_REC'].values[0]
            mus.append(val); sigs.append(err)
            labs.append(m); cols.append('black' if m=='SIBYLL' else 'gray')
            stats[m] = (val, err)
            
    if len(mus) < 2: return None, 0.0
    
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_annotated_gaussians(ax, mus, sigs, labs, cols, f"Incertidumbre Hadrónica ({primary} {energy} - Bin {bin_idx})")
    
    mf_val = 0.0
    if 'SIBYLL' in stats and 'QGSJet' in stats:
        mf_val = calc_mf(stats['SIBYLL'][0], stats['SIBYLL'][1], stats['QGSJet'][0], stats['QGSJet'][1])
        ax2 = ax.twinx()
        limit_sigma = max(4.0, mf_val + 1.0)
        ax2.set_ylim(0, limit_sigma)
        ax2.set_ylabel(r"Separación MF ($\sigma$)", color='darkred')
        ax2.axhline(mf_val, color='darkred', linestyle='--', linewidth=1.5, alpha=0.7)
        ax2.text(ax.get_xlim()[1], mf_val + 0.1, rf" MF: {mf_val:.2f}$\sigma$", 
                 ha='right', va='bottom', color='darkred', fontweight='bold')
            
    return fig, mf_val

# --- PLOT 4 & 5: SISTEMATICOS ---
def plot_systematic_gaussians(df_sys, label_col, title):
    if df_sys is None or df_sys.empty: return None
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    mus = df_sys['A1'].values
    sigs = df_sys['Err'].values
    if label_col == 'logE': labels = [f"{x:.2f}" for x in df_sys[label_col]]
    else: labels = [f"{x:.0f}" for x in df_sys[label_col]]
    
    plot_gaussians_with_table(ax1, ax2, mus, sigs, labels)
    ax1.set_title(title)
    ax1.set_xlabel(r"$A_1$")
    ax1.set_ylabel("Densidad")
    return fig

def create_mf_matrix_df(df_sys, label_col):
    if df_sys is None or df_sys.empty: return pd.DataFrame()
    vals = df_sys['A1'].values
    errs = df_sys['Err'].values
    if label_col == 'logE': cols = [f"{x:.2f}" for x in df_sys[label_col]]
    else: cols = [f"{x:.0f}" for x in df_sys[label_col]]
    
    matrix = []
    for i in range(len(vals)):
        row = []
        for j in range(len(vals)):
            if i == j: row.append("-")
            else:
                f = calc_mf(vals[i], errs[i], vals[j], errs[j])
                row.append(f"{f:.2f}")
        matrix.append(row)
    return pd.DataFrame(matrix, columns=cols, index=cols)

# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=== Generador de Reporte Global (Fix Definitivo) ===")
    
    df, special_tables = get_consolidated_data(pattern="Reporte_V8_*.pdf")
    if df.empty:
        print("No se encontraron datos.")
        return

    pdf = GlobalReportPDF()
    pdf.alias_nb_pages()
    
    # PAG 1
    pdf.add_page(); pdf.section_title("1. Panorama Global")
    fig1 = plot_grand_finale(df)
    pdf.add_plot_from_fig(fig1)
    
    # PAG 2
    pdf.add_page(); pdf.section_title("2. Discriminación de Masa (SIBYLL 17.5)")
    pdf.add_text("Se evalúa la capacidad de discriminación utilizando el Merit Factor (MF).")
    pdf.add_formula(r"MF = |A1_a - A1_b| / sqrt(sigma_a^2 + sigma_b^2)")
    
    fig2, mf_val = plot_mass_mf(df, model='SIBYLL', energy='17.5', bin_idx=5)
    if fig2: 
        pdf.add_text(rf"Separación Protón vs Hierro observada: {mf_val:.2f} sigma.")
        pdf.add_plot_from_fig(fig2)
    else: pdf.add_text("Faltan datos.")
    
    # PAG 3
    pdf.add_page(); pdf.section_title("3. Modelos Hadrónicos (Helio 17.5)")
    fig3, mf_mod = plot_models_mf(df, primary='Helio', energy='17.5', bin_idx=5)
    if fig3:
        pdf.add_text(rf"Discrepancia entre modelos (QGS vs SIB): {mf_mod:.2f} sigma.")
        pdf.add_plot_from_fig(fig3)
    else: pdf.add_text("Faltan datos.")
    
    # PAG 4
    pdf.add_page(); pdf.section_title("4. Sistemático: Energía")
    tbl_en = special_tables.get('energy')
    if tbl_en is not None and not tbl_en.empty:
        fig4 = plot_systematic_gaussians(tbl_en, 'logE', "Invarianza con Energía")
        pdf.add_plot_from_fig(fig4)
        pdf.add_text("Matriz de Merit Factor (MF) entre energías:")
        df_m = create_mf_matrix_df(tbl_en, 'logE')
        df_m.reset_index(inplace=True); df_m.rename(columns={'index': 'E'}, inplace=True)
        pdf.create_styled_table(df_m)
    else: pdf.add_text("No hay datos de Energía.")
    
    # PAG 5
    pdf.add_page(); pdf.section_title("5. Sistemático: Isotropía")
    tbl_iso = special_tables.get('isotropy')
    if tbl_iso is not None and not tbl_iso.empty:
        fig5 = plot_systematic_gaussians(tbl_iso, 'Phi_In', "Isotropía Azimutal")
        pdf.add_plot_from_fig(fig5)
        pdf.add_text("Matriz de Merit Factor (MF):")
        df_m = create_mf_matrix_df(tbl_iso, 'Phi_In')
        df_m.reset_index(inplace=True); df_m.rename(columns={'index': 'Sec'}, inplace=True)
        pdf.create_styled_table(df_m)
    else: pdf.add_text("No hay datos de Isotropía.")

    out = "Reporte_Global_Final.pdf"
    pdf.output(out)
    print(f"\n REPORTE GENERADO: {out}")

if __name__ == "__main__":
    main()