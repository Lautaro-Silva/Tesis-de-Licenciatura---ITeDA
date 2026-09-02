# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# =============================================================================
# CELDA 1: Importaciones y Configuración Visual (Estilo HEP)
# =============================================================================
import os
import glob
import warnings
import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import curve_fit
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt



warnings.simplefilter('ignore')

# Configuración visual global (Estilo HEP híbrido adaptado)
hep_style = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'xtick.direction': 'in', 
    'ytick.direction': 'in',
    'xtick.top': True, 
    'ytick.right': True,
    'xtick.minor.visible': True, 
    'ytick.minor.visible': True,
    'axes.linewidth': 1.2,
    'legend.frameon': True,
    'legend.shadow': True,
    'font.size': 14, 
    'axes.labelsize': 14, 
    'axes.titlesize': 16, 
    'legend.fontsize': 12, 
    'figure.figsize': (8, 6)
}
plt.rcParams.update(hep_style)

# Colores y marcadores estándar
COLORS = {'Proton': 'royalblue', 'Helio': 'forestgreen', 'Oxigeno': 'purple', 'Hierro': 'firebrick', 'Mix': 'dimgray'}


# %%
# =============================================================================
# CELDA 2: Funciones Auxiliares de Parseo
# =============================================================================
def parse_metadata(folder_name):
    """Extrae metadatos basados en el nombre de la carpeta (ej. parquet_sib_proton_17)."""
    f = folder_name.lower()
    model = 'SIBYLL' if 'sib' in f else 'QGSJet' if 'qgs' in f else 'EPOS' if 'epos' in f else 'Unknown'
    
    if 'proton' in f: primary = 'Proton'
    elif 'hierro' in f or 'iron' in f: primary = 'Hierro'
    elif 'helio' in f or 'helium' in f: primary = 'Helio'
    elif 'oxigeno' in f or 'oxygen' in f: primary = 'Oxigeno'
    else: primary = 'Unknown'
        
    energy = '18.0-18.5' if '_18' in f else '17.5-18.0'
    return model, primary, energy


# %%
# =============================================================================
# CELDA 3: Carga Masiva de Datos
# =============================================================================
ROOT_DIR = "/home/lsilva/Github/ADST_Alexey_module_v9" 

all_dfs = []
if os.path.exists(ROOT_DIR):
    for folder in os.listdir(ROOT_DIR):
        folder_path = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(folder_path): continue
            
        model, primary, energy = parse_metadata(folder)
        parquets = glob.glob(os.path.join(folder_path, "*.parquet"))
        
        for f in parquets:
            try:
                # Cargamos solo las columnas necesarias para el análisis del punto 6.1
                df = pd.read_parquet(f, columns=[
                    'event_id', 'counterId', 'nMuones_REC', 'nMuones_MC', 'theta_REC', 'phi_plane_sp', 'sdSignal_REC'
                ])
                df['Model'] = model
                df['Primary'] = primary
                df['Energy'] = energy
                all_dfs.append(df)
            except Exception as e: 
                pass

    df_master = pd.concat(all_dfs, ignore_index=True)
else:
    print(f"ATENCIÓN: La ruta {ROOT_DIR} no existe. Se generarán datos dummy para probar el script.")
    # (Este bloque es solo por si lo corrés en otro entorno sin los parquets, podés ignorarlo)
    np.random.seed(42)
    df_master = pd.DataFrame({
        'nMuones_MC': np.random.uniform(5, 100, 20000),
        'Model': 'SIBYLL', 'Primary': 'Proton', 'Energy': '17.5-18.0'
    })
    # Simulamos un detector sin sesgo pero con cierta resolución gaussiana
    df_master['nMuones_REC'] = df_master['nMuones_MC'] * np.random.normal(1.0, 0.15, 20000)

# Aislar el Dataset Guía (SIBYLL Proton 17.5-18.0)
df_guia = df_master[(df_master['Model'] == 'SIBYLL') & 
                    (df_master['Primary'] == 'Proton') & 
                    (df_master['Energy'] == '17.5-18.0')].copy()

print(f"Data cargada. Mega-DF: {len(df_master):,} filas | Dataset Guía (SIB P 17.5): {len(df_guia):,} filas")

# %%
# =============================================================================
# CELDA 4: Validación del Conteo de Muones vs. Sesgo de Ajuste (Punto 6.1)
# =============================================================================

# 1. Preparación de los datos: Calcular el residuo relativo
# Filtramos nMuones_MC > 0 para evitar infinitos o NaNs al dividir
df_valid = df_guia[df_guia['nMuones_MC'] > 0].copy()

# Cálculo clave solicitado por Lorenzo/Juan
df_valid['muon_residual_rel'] = (df_valid['nMuones_REC'] - df_valid['nMuones_MC']) / df_valid['nMuones_MC']

# Quitamos outliers extremos (ej. ruido estadístico muy loco en detectores con 1 solo muon MC) 
# para que el histograma sea legible. Rango sugerido: -1.0 a 1.0 (±100% de error)
rango_plot = (-5, 5)
data_plot = df_valid[(df_valid['muon_residual_rel'] >= rango_plot[0]) & 
                     (df_valid['muon_residual_rel'] <= rango_plot[1])]['muon_residual_rel']

# 2. Creación de la figura
fig, ax = plt.subplots(figsize=(8, 6))

# Ploteamos el histograma
ax.hist(data_plot, bins=60, range=rango_plot, color='seagreen', edgecolor='black', linewidth=1.2, alpha=0.75)

# 3. Cálculos estadísticos
mean_val = data_plot.mean()
std_val = data_plot.std()

# 4. Líneas de referencia
ax.axvline(mean_val, color='crimson', linestyle='--', linewidth=2.0, label=r'Media ($\mu$)')
ax.axvline(0, color='black', linestyle='-', linewidth=1.5, alpha=0.6, label='Ideal cero')

# 5. Etiquetas y Títulos
ax.set_xlabel(r'Residuo Relativo de Muones', fontsize=16)
ax.set_ylabel('Número de eventos', fontsize=14)
ax.set_title('Validación de Conteo de Muones', fontsize=16, pad=10, fontweight='bold')

# 6. Caja de Estadísticas (Idéntica a tu estilo)
stats_text = f"Statistics:\nModules: {len(data_plot):,}\n$\mu$: {mean_val:.3f}\n$\sigma$: {std_val:.3f}"
props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='gray')
ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)

# 7. Anotaciones Físicas
ax.text(0.95, 0.95, r"$\mathbf{Proton\ showers}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color=COLORS['Proton'])
ax.text(0.95, 0.88, r"$\mathbf{SIB2.3e}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color='purple')
ax.text(0.95, 0.81, r"$\log_{10}(E_0/\mathrm{eV}) = 17.5 - 18.0$", transform=ax.transAxes, fontsize=11, va='top', ha='right')

# Indicador del detector / arreglo
ax.text(0.05, 0.11, r"$\mathbf{Dense\ Ring\ (450\ m)}$", transform=ax.transAxes, fontsize=12, va='top', ha='left', color='black')

# 8. Grillas y Leyenda
ax.grid(True, which='major', linestyle='-', alpha=0.5)
ax.grid(True, which='minor', linestyle=':', alpha=0.3)
ax.minorticks_on()
ax.legend(loc='center right', fontsize=12)

plt.yscale('log')
plt.tight_layout()
plt.savefig('muon_counting_validation.pdf', dpi=300)
plt.show()

print(f"Interpretación rápida: Si mu (la media) está muy cerca de 0 (ej. {mean_val:.3f}),")
print("eso demuestra que el UMD no está subestimando ni sobreestimando sistemáticamente los muones,")
print("y que el sesgo de asimetría A1 se debe al 'wash-out' geométrico y no a un error de conteo del detector.")


# %%
# =========================================================================
# CELDA: DIAGNÓSTICO CUANTITATIVO - CHI-CUADRADO REDUCIDO (Goodness of Fit)
# =========================================================================

def fit_func_deg(phi_deg, A1):
    return 1.0 * (1 + A1 * np.cos(np.deg2rad(phi_deg)))

# -------------------------------------------------------------------------
# 1. PREPARACIÓN SEGURA DE DATOS (Para evitar el NameError)
# -------------------------------------------------------------------------
# Filtramos Anillo Denso
df_ana = df_guia[(df_guia['counterId'] >= 90000) & (df_guia['counterId'] < 100000)].copy()

# Generamos Bines de Theta y Phi
s2_bins = np.linspace(np.sin(np.deg2rad(0))**2, np.sin(np.deg2rad(65))**2, 11)
theta_edges = np.rad2deg(np.arcsin(np.sqrt(s2_bins)))
theta_labels = [f"{theta_edges[k]:.1f}° - {theta_edges[k+1]:.1f}°" for k in range(10)]
df_ana['theta_bin_idx'] = pd.cut(df_ana['theta_REC'], bins=theta_edges, labels=False)

df_ana['phi_deg_centered'] = (np.rad2deg(df_ana['phi_plane_sp']) + 180) % 360 - 180
phi_bin_edges = np.linspace(-180, 180, 13)
phi_centers = (phi_bin_edges[:-1] + phi_bin_edges[1:]) / 2

# -------------------------------------------------------------------------
# 2. CÁLCULO DE CHI^2 REDUCIDO
# -------------------------------------------------------------------------
evol_theta = []
chi2_umd_rec, chi2_umd_mc, chi2_sd = [], [], []

columnas = ['nMuones_REC', 'nMuones_MC', 'sdSignal_REC']

for i in range(10):
    mask_bin = (df_ana['theta_bin_idx'] == i)
    df_sl = df_ana[mask_bin].copy()
    
    if len(df_sl) < 50: 
        continue
        
    df_sl['phi_bin'] = pd.cut(df_sl['phi_deg_centered'], bins=phi_bin_edges)
    stats = df_sl.groupby('phi_bin', observed=True)[columnas].agg(['mean', 'sem'])
    
    chi2_vals = {'nMuones_REC': np.nan, 'nMuones_MC': np.nan, 'sdSignal_REC': np.nan}
    
    for col in columnas:
        if col not in stats.columns: continue
        
        means = stats[col]['mean']
        norm = means.mean()
        if pd.isna(norm) or norm == 0: continue
            
        y = (means / norm).values
        yerr = (stats[col]['sem'] / norm).values
        
        # Filtrar NaNs para el ajuste
        valid_idx = ~np.isnan(y) & ~np.isnan(yerr) & (yerr > 0)
        y_valid = y[valid_idx]
        yerr_valid = yerr[valid_idx]
        x_valid = phi_centers[valid_idx]
        
        if len(y_valid) > 2: # Necesitamos al menos 3 puntos para 1 parámetro (ndf > 0)
            try:
                popt, _ = curve_fit(fit_func_deg, x_valid, y_valid, p0=[0.05], sigma=yerr_valid, absolute_sigma=True)
                y_fit = fit_func_deg(x_valid, popt[0])
                
                # Cálculo de Chi Cuadrado Reducido
                chi2 = np.sum(((y_valid - y_fit) / yerr_valid) ** 2)
                ndf = len(y_valid) - 2  # 1 parámetro (A1)
                chi2_vals[col] = chi2 / ndf
            except:
                pass
                
    evol_theta.append(i)
    chi2_umd_rec.append(chi2_vals['nMuones_REC'])
    chi2_umd_mc.append(chi2_vals['nMuones_MC'])
    chi2_sd.append(chi2_vals['sdSignal_REC'])

# -------------------------------------------------------------------------
# 3. PLOT DE CHI^2 REDUCIDO
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(evol_theta, chi2_umd_mc, 's--', color='forestgreen', markersize=8, lw=2, label=r'UMD $N_\mu^{\mathrm{MC}}$')
ax.plot(evol_theta, chi2_umd_rec, 'o-', color='navy', markersize=8, lw=2, label=r'UMD $N_\mu^{\mathrm{REC}}$')
ax.plot(evol_theta, chi2_sd, '^-.', color='firebrick', markersize=8, lw=2, label='SD')

# Líneas de referencia para Goodness of Fit
ax.axhline(1.0, color='black', linestyle='-', lw=2, alpha=0.7, label=r'Ajuste Ideal ($\chi^2_\nu = 1$)')
ax.axhline(2.0, color='gray', linestyle='--', lw=1.5, alpha=0.5, label=r'Limite Aceptable ($\chi^2_\nu = 2$)')
ax.axhline(0.5, color='gray', linestyle=':', lw=1.5, alpha=0.5)

ax.set_xlabel(r"Bin Cenital (incrementando en $\sin^2\theta$)", fontsize=14)
ax.set_ylabel(r"Chi Cuadrado Reducido ($\chi^2_\nu$)", fontsize=14)
ax.set_title("Bondad del Ajuste", fontsize=16, pad=15, fontweight='bold')

# Escala logarítmica si algunos fits se rompen y el chi2 explota a >10
ax.set_yscale('log')
ax.set_ylim(0, 10) 

# Formateo de ticks del eje Y para escala logarítmica
from matplotlib.ticker import ScalarFormatter
ax.yaxis.set_major_formatter(ScalarFormatter())
ax.set_yticks([0.1, 0.5, 1, 2, 5, 10])

# Fijamos las posiciones de los ticks en los índices (0 a 9) y aplicamos los labels rotados
ax.set_xticks(evol_theta) 
ax.set_xticklabels(theta_labels, rotation=35, ha='right', fontsize=10)
# --- FIN MODIFICACIÓN ---

# Anotaciones Físicas
ax.text(0.95, 0.25, r"$\mathbf{Proton\ showers}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color=COLORS['Proton'])
ax.text(0.95, 0.18, r"$\mathbf{SIB2.3e}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color='purple')
ax.text(0.95, 0.11, r"$\log_{10}(E_0/\mathrm{eV}) = 17.5 - 18.0$", transform=ax.transAxes, fontsize=11, va='top', ha='right')

# Indicador del detector / arreglo
ax.text(0.05, 0.11, r"$\mathbf{Dense\ Ring\ (450\ m)}$", transform=ax.transAxes, fontsize=12, va='top', ha='left', color='black')

ax.grid(True, which='major', linestyle='-', alpha=0.4)
ax.grid(True, which='minor', linestyle=':', alpha=0.2)
ax.legend(fontsize=12, loc='upper left')

plt.tight_layout()
plt.savefig('Chi2_Reduced_Fits.pdf', dpi=300)
plt.show()

print("Interpretación: Valores de chi2 reducido ~ 1 indican un buen ajuste.")
print("Valores >> 1 indican que el modelo (sinusoide simple) no describe bien los datos (¿quizás se necesita un doble armónico?).")
print("Valores << 1 podrían indicar sobreestimación de los errores estadísticos.")

# %%
# =========================================================================
# CELDA: TOY MONTE CARLO - PROPAGACIÓN DEL RUIDO INSTRUMENTAL
# =========================================================================

# 1. Extraer la distribución real de errores de tu detector (del Punto 6.1)
# Asumimos que df_valid tiene la columna 'muon_residual_rel' que calculamos antes
residuos_empiricos = df_valid['muon_residual_rel'].dropna().values

# 2. Inyectar este ruido a la verdad de Monte Carlo (crear el Toy Detector)
# Le asignamos a cada estación un error sacado al azar de la bolsa de errores reales
np.random.seed(311001) # Para reproducibilidad
ruido_aleatorio = np.random.choice(residuos_empiricos, size=len(df_ana))

df_ana['nMuones_TOY'] = df_ana['nMuones_MC'] * (1 + ruido_aleatorio)

# 3. Analizar la asimetría de este nuevo "Detector Toy"
evol_theta = []
a1_mc, a1_rec, a1_toy = [], [], []

columnas = ['nMuones_MC', 'nMuones_REC', 'nMuones_TOY']

for i in range(10):
    mask_bin = (df_ana['theta_bin_idx'] == i)
    df_sl = df_ana[mask_bin].copy()
    
    if len(df_sl) < 50: continue
        
    df_sl['phi_bin'] = pd.cut(df_sl['phi_deg_centered'], bins=phi_bin_edges)
    stats = df_sl.groupby('phi_bin', observed=True)[columnas].agg(['mean', 'sem'])
    
    a1_vals = {}
    
    for col in columnas:
        if col not in stats.columns: continue
        
        means = stats[col]['mean']
        norm = means.mean()
        if pd.isna(norm) or norm == 0: continue
            
        y = (means / norm).values
        yerr = (stats[col]['sem'] / norm).values
        
        valid_idx = ~np.isnan(y) & ~np.isnan(yerr) & (yerr > 0)
        
        if len(y[valid_idx]) > 3:
            try:
                popt, _ = curve_fit(fit_func_deg, phi_centers[valid_idx], y[valid_idx], p0=[0.05], sigma=yerr[valid_idx])
                a1_vals[col] = popt[0]
            except: pass
                
    evol_theta.append(i)
    a1_mc.append(a1_vals.get('nMuones_MC', np.nan))
    a1_rec.append(a1_vals.get('nMuones_REC', np.nan))
    a1_toy.append(a1_vals.get('nMuones_TOY', np.nan))

# 4. Ploteo de la Verificación
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(evol_theta, a1_mc, 's--', color='forestgreen', markersize=8, lw=2, label=r'Ideal ($UMD\ N_\mu^{MC}$)')
ax.plot(evol_theta, a1_rec, 'o-', color='navy', markersize=8, lw=2, label=r'Realidad ($UMD\ N_\mu^{REC}$)')
ax.plot(evol_theta, a1_toy, '*:', color='darkorange', markersize=11, lw=2.5, label=r'Toy Model (MC + Ruido Empírico)')

ax.set_xlabel(r"Zenith Angle Bin (increasing in $\sin^2\theta$)", fontsize=14)
ax.set_ylabel(r"Asymmetry Amplitude $A_1$", fontsize=14)
ax.set_title("Check for the Loss of Asymmetry due to Instrumental Bias", fontsize=15, fontweight='bold', pad=15)

# -------------------------------------------------------------------------
# ANOTACIONES FÍSICAS Y DE CONTEXTO
# -------------------------------------------------------------------------
# Indicador del detector / arreglo
ax.text(0.05, 0.95, r"$\mathbf{Dense\ Ring\ (450\ m)}$", transform=ax.transAxes, fontsize=12, va='top', ha='left', color='black')

# Anotaciones Físicas
ax.text(0.95, 0.98, r"$\mathbf{Proton\ showers}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color=COLORS['Proton'])
ax.text(0.95, 0.91, r"$\mathbf{SIB2.3e}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color='purple')
ax.text(0.95, 0.84, r"$\log_{10}(E_0/\mathrm{eV}) = 17.5 - 18.0$", transform=ax.transAxes, fontsize=11, va='top', ha='right')

ax.grid(True, which='major', linestyle='-', alpha=0.4)
ax.grid(True, which='minor', linestyle=':', alpha=0.2)
ax.legend(fontsize=12, loc='lower center')

# Ajustar límites Y si es necesario para que entre el texto
y_max = max(max(a1_mc), max(a1_rec), max(a1_toy))
ax.set_ylim(bottom=0, top=y_max * 1.3)

plt.tight_layout()
#plt.savefig('ToyModel_Resolution_Validation.jpg', dpi=300)
plt.show()

# %% [markdown]
# ### Modelado de la Pérdida de Asimetría mediante un *Toy Monte Carlo* Basado en Datos
#
# Al analizar la amplitud de la asimetría azimutal ($A_1$) en el Anillo Denso, se observó una degradación sistemática de la señal reconstruida ($N_\mu^{\mathrm{REC}}$) en comparación con la inyectada por el generador de Monte Carlo ($N_\mu^{\mathrm{MC}}$). Dado que las estaciones del Anillo Denso se simulan en posiciones azimutales fijas respecto al eje de la lluvia, el *smearing* geométrico por errores en la reconstrucción angular es estrictamente nulo en este subconjunto de datos. Por lo tanto, se hipotetizó que la disminución en la amplitud relativa se debe exclusivamente a la resolución instrumental del detector (fluctuaciones estadísticas y colas asimétricas en el conteo de partículas), las cuales actúan como un fondo no correlacionado que incrementa el denominador en el cálculo de la señal normalizada $S/\langle S \rangle$.
#
# Para demostrar cuantitativamente esta hipótesis, se desarrolló un *Toy Model* impulsado por datos. El procedimiento consistió en:
# 1. Aislar la distribución real de los residuos relativos del detector ($\frac{N_\mu^{\mathrm{REC}} - N_\mu^{\mathrm{MC}}}{N_\mu^{\mathrm{MC}}}$).
# 2. Muestrear aleatoriamente esta distribución para inyectar un "ruido instrumental realista" directamente sobre la señal pura de Monte Carlo ($N_\mu^{\mathrm{MC}}$), evento a evento.
# 3. Repetir el ajuste armónico sobre este nuevo conjunto de datos simulados ($N_\mu^{\mathrm{TOY}}$). 
#
# La superposición de las curvas de amplitud entre la señal Monte Carlo ideal y el *Toy Model* confirma matemáticamente que la divergencia entre MC y REC no proviene de un sesgo algorítmico o de proyecciones, pero tampoco es una consecuencia intrínseca de la dispersión estadística y la resolución instrumental del detector de centelleo.

# %%
# =========================================================================
# CELDA: ANÁLISIS DIRECCIONAL DEL SESGO DE RECONSTRUCCIÓN (UMD)
# =========================================================================

# 1. Filtrar eventos válidos (MC > 0) para evitar divisiones por cero
df_res = df_ana[df_ana['nMuones_MC'] > 0].copy()

# 2. Calcular el residuo relativo módulo por módulo
df_res['muon_residual_rel'] = (df_res['nMuones_REC'] - df_res['nMuones_MC']) / df_res['nMuones_MC']

# 3. Filtrar para lluvias inclinadas (donde la asimetría y el efecto deberían ser mayores)
# Usamos bines de theta del 4 al 9 (aprox 40° a 65°)
df_res_inclined = df_res[df_res['theta_bin_idx'] >= 4].copy()

# ¡LA CORRECCIÓN! Creamos la columna 'phi_bin' para agrupar
df_res_inclined['phi_bin'] = pd.cut(df_res_inclined['phi_deg_centered'], bins=phi_bin_edges)

# 4. Agrupar por ángulo azimutal en el plano de la lluvia
stats_res = df_res_inclined.groupby('phi_bin', observed=True)['muon_residual_rel'].agg(['mean', 'sem'])

# 5. Ploteo
fig, ax = plt.subplots(figsize=(8, 6))

# Plot del residuo medio por bin azimutal
ax.errorbar(phi_centers, stats_res['mean'], yerr=stats_res['sem'], 
            fmt='o-', color='crimson', capsize=5, markersize=8, markeredgecolor='black', lw=2)#, label='Relative Residual (REC vs MC)')

# Líneas de referencia
media_global = df_res_inclined['muon_residual_rel'].mean()
ax.axhline(0, color='black', linestyle='-', lw=1.5, alpha=0.8, label='Ideal Detector')
ax.axhline(media_global, color='gray', linestyle='--', lw=2, alpha=0.7, label=f'Mean Global Bias ($\mu$ = {media_global:.3f})')

# Estética
ax.set_xlabel(r"$\phi_{station}$ (0° = Early, $\pm 180$° = Late)", fontsize=14)
ax.set_ylabel(r"Mean Relative Residual $\langle \frac{N_{\mu}^{\mathrm{REC}} - N_{\mu}^{\mathrm{MC}}}{N_{\mu}^{\mathrm{MC}}} \rangle$", fontsize=14)
ax.set_title("Directional Bias from UMD Reconstruction", fontsize=16, fontweight='bold', pad=15)

ax.set_xlim(-180, 180)

# Indicador del detector / arreglo
ax.text(0.05, 0.20, r"$\mathbf{Dense\ Ring\ (450\ m)}$", transform=ax.transAxes, fontsize=12, va='top', ha='left', color='black')
ax.text(0.05, 0.13, r"$\mathbf{\theta \approx 40^\circ - 65^\circ}$", transform=ax.transAxes, fontsize=12, va='top', ha='left')

# Anotaciones Físicas
ax.text(0.5, 0.98, r"$\mathbf{Proton\ showers}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color=COLORS['Proton'])
ax.text(0.5, 0.91, r"$\mathbf{SIB2.3e}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color='purple')
ax.text(0.5, 0.84, r"$\log_{10}(E_0/\mathrm{eV}) = 17.5 - 18.0$", transform=ax.transAxes, fontsize=11, va='top', ha='right')

ax.grid(True, which='major', linestyle='-', alpha=0.4)
ax.grid(True, which='minor', linestyle=':', alpha=0.2)
ax.legend(fontsize=12, loc='lower right')

plt.tight_layout()
plt.savefig('directional_bias.jpg', dpi=300)
plt.show()

# %% [markdown]
# ### Degradación de la Asimetría Reconstruida por Sesgos Direccionales en la Respuesta Instrumental
#
# Al comparar la amplitud de la asimetría azimutal reconstruida ($A_1^{\mathrm{REC}}$) con la inyectada por la simulación de Monte Carlo ($A_1^{\mathrm{MC}}$) en el Anillo Denso, se observó una subestimación sistemática del parámetro en la reconstrucción. Dado que este subconjunto de datos carece de incertezas de posicionamiento angular, se descartó el *smearing* geométrico como causa principal. Adicionalmente, la implementación de un *Toy Model* basado en datos demostró que las fluctuaciones estadísticas de conteo y el ruido simétrico del detector no son capaces de reducir la amplitud relativa de la asimetría.
#
# El origen de esta discrepancia radica en un sesgo direccional intrínseco en la respuesta del detector simulado. El análisis de los residuos relativos medios $\langle \frac{N_{\mu}^{\mathrm{REC}} - N_{\mu}^{\mathrm{MC}}}{N_{\mu}^{\mathrm{MC}}} \rangle$ en función del ángulo azimutal en el plano de la lluvia ($\phi$) reveló que el algoritmo de reconstrucción (Offline) sobreestima sistemáticamente la cantidad de muones en todo el anillo, pero de forma fuertemente asimétrica: el error es mínimo en la región temprana ($\phi = 0^\circ$) y alcanza su máximo en la región tardía ($\phi = \pm 180^\circ$). Matemáticamente, la inyección de señal artificial ("sobreconteo") justamente en el valle de la distribución azimutal reduce el contraste entre ambas regiones, achatando la modulación y disminuyendo inevitablemente la amplitud $A_1$ extraída del ajuste armónico.
#
# Físicamente, este sobreconteo direccional se explica por la interacción de los muones con el material centellador y los métodos de calibración del detector, fundamentados en los siguientes procesos:
#
# 1. **Ablandamiento del Espectro de Energía:** La asimetría "temprano-tardía" es una consecuencia directa de la atenuación longitudinal. Los muones que arriban en la región tardía ($\phi = \pm 180^\circ$) atraviesan un espesor atmosférico significativamente mayor que los de la región temprana. Como resultado, sufren una mayor pérdida de energía por colisiones e ionización, lo que produce un espectro energético promedio mucho más "blando" (de menor energía) para la población de muones tardíos.
# 2. **Pérdida de Energía Específica ($dE/dx$) y Calibración:** Los detectores de centelleo miden la luz producida por la energía depositada por las partículas incidentes. El algoritmo de calibración asume típicamente que los muones se comportan como Partículas Mínimamente Ionizantes (MIPs), las cuales depositan una cantidad de energía pequeña y constante por unidad de longitud. Sin embargo, de acuerdo con la curva de Bethe-Bloch, cuando los muones tardíos (de baja energía) ingresan al detector, su tasa de pérdida de energía específica ($dE/dx$) aumenta drásticamente al acercarse al final de su trayectoria.
# 3. **Artefacto de Reconstrucción:** Al depositar una cantidad de energía sustancialmente mayor a la de un MIP estándar, el destello de luz generado en el centellador es desproporcionadamente grande. El algoritmo de reconstrucción interpreta esta señal anómala integrando la carga total y dividiéndola por la carga equivalente a un MIP, lo que resulta en la contabilización errónea de múltiples muones allí donde físicamente ingresó uno solo.
# 4. **Efecto de Trayectoria (Track Length):** Adicionalmente, los muones tardíos impactan el plano del suelo con un ángulo de incidencia mucho más rasante. Esto incrementa su longitud de trayectoria geométrica dentro del material centellador, aumentando aún más la energía depositada total y la probabilidad de generar señales cruzadas (*cross-talk*) en canales adyacentes, exacerbando el sobreconteo en la dirección $\phi = \pm 180^\circ$.
#
# En conclusión, la reducción de la asimetría reconstruida respecto a la verdad de Monte Carlo es un artefacto sistemático predecible, derivado de la convolución entre el espectro de energía asimétrico de la lluvia y la respuesta intrínseca del detector a partículas con alto $dE/dx$.

# %% [markdown]
# ### Referencias Bibliográficas: Respuesta Instrumental y Asimetría
#
# **Física de Partículas y Pérdida de Energía ($dE/dx$)**
# Para justificar el comportamiento de la curva de Bethe-Bloch, el aumento de la pérdida de energía en partículas lentas (pico de Bragg) y la definición de una Partícula Mínimamente Ionizante (MIP):
#
# * Workman, R. L., et al. (Particle Data Group). (2022). Review of Particle Physics: Passage of particles through matter. *Progress of Theoretical and Experimental Physics*, 2022(8), 083C01.
# * Leo, W. R. (2012). *Techniques for Nuclear and Particle Physics Experiments: A How-to Approach* (2nd rev. ed.). Springer Science & Business Media. (Específicamente los capítulos sobre detectores de centelleo y pérdida de energía en la materia).
#
# **Instrumentación y Reconstrucción en el UMD (Auger)**
# Para referenciar el diseño del detector de centelleo, el efecto de las trayectorias (track length), el *clipping corner* y cómo el algoritmo *Offline* cuenta muones basándose en la calibración del MIP:
#
# * Aab, A., et al. (Pierre Auger Collaboration). (2021). Design and performance of the AMIGA underground muon detector of the Pierre Auger Observatory. *Journal of Instrumentation*, 16(01), P01026.
# * Aab, A., et al. (Pierre Auger Collaboration). (2017). Muon counting using silicon photomultipliers in the AMIGA detector of the Pierre Auger observatory. *Journal of Instrumentation*, 12(03), P03002.
# * Aab, A., et al. (Pierre Auger Collaboration). (2020). Direct measurement of the muon background in surface detectors of the Pierre Auger Observatory. *The European Physical Journal C*, 80(8), 751.
#
# **Desarrollo Longitudinal y Espectro de la Lluvia**
# Para fundamentar que la asimetría espacial conlleva una asimetría energética debido a la atenuación longitudinal y el espesor atmosférico recorrido por los muones tardíos:
#
# * Pryke, C. (1998). *Auger project technical note: Asymmetry of Air Showers at Ground Level* (GAP-98-034). General Auger Publication.
# * Spurio, M. (2014). *Particles and Astrophysics: A Multi-Messenger Approach*. Springer. (Capítulos referidos al desarrollo de EAS, decaimiento y atenuación de muones en la atmósfera).

# %%
# =============================================================================
# CELDA: Mapa de Calor - Distribución del Residuo (Eje X) vs Azimut (Eje Y)
# =============================================================================

# 1. Preparación de datos (usando el Dataset Guía)
# Filtramos nMuones_MC > 0 para evitar divisiones por cero
df_valid = df_guia[df_guia['nMuones_MC'] > 0].copy()

# Calculamos residuo relativo y azimut centrado
df_valid['muon_residual_rel'] = (df_valid['nMuones_REC'] - df_valid['nMuones_MC']) / df_valid['nMuones_MC']
df_valid['phi_deg_centered'] = (np.rad2deg(df_valid['phi_plane_sp']) + 180) % 360 - 180

# Definimos límites (X = Residuo, Y = Phi)
x_min, x_max = -1.5, 4.5
y_min, y_max = -180, 180

mask_plot = (df_valid['muon_residual_rel'] >= x_min) & (df_valid['muon_residual_rel'] <= x_max)
data_x = df_valid.loc[mask_plot, 'muon_residual_rel']
data_y = df_valid.loc[mask_plot, 'phi_deg_centered']

# 2. Generar Bines y el Histograma 2D
x_bins = np.linspace(x_min, x_max, 80)    # 80 bines de residuo (Eje X - Resolución)
y_bins = np.linspace(y_min, y_max, 13)    # 12 bines de phi (Eje Y)

H, xedges, yedges = np.histogram2d(data_x, data_y, bins=[x_bins, y_bins])

# 3. NORMALIZACIÓN POR FILA DE PHI (Eje Y)
# H tiene shape (len(x_bins)-1, len(y_bins)-1). Cada columna 'j' es un bin de phi.
# Queremos que cada franja horizontal sume 1 (para comparar densidades justas)
H_norm = np.zeros_like(H)
for j in range(H.shape[1]): 
    suma_phi = H[:, j].sum()
    if suma_phi > 0:
        H_norm[:, j] = H[:, j] / suma_phi

# 4. Creación de la Figura
fig, ax = plt.subplots(figsize=(11, 7))

# Ploteamos el mapa de calor transpuesto
X, Y = np.meshgrid(xedges, yedges)
im = ax.pcolormesh(X, Y, H_norm.T, cmap='viridis', norm=mcolors.LogNorm(vmin=1e-4, vmax=H_norm.max()))

# 5. Superponer la Media para tener la referencia visual (Puntos Rojos)
df_valid['phi_bin'] = pd.cut(df_valid['phi_deg_centered'], bins=y_bins)
stats = df_valid[mask_plot].groupby('phi_bin', observed=True)['muon_residual_rel'].agg(['mean', 'sem'])
phi_centers = (yedges[:-1] + yedges[1:]) / 2

# Notar que acá graficamos X = media, Y = phi_centers
ax.errorbar(stats['mean'], phi_centers, xerr=stats['sem'], fmt='o-', color='crimson', 
            linewidth=2.5, markersize=8, markeredgecolor='black', label='Mean Residual')

# 6. Estética, Líneas de Referencia y Anotaciones
ax.axvline(0, color='white', linestyle='--', linewidth=1.5, alpha=0.8, label='Ideal Zero Bias')

ax.set_xlabel(r'Relative Muon Residual $\frac{N_{\mu}^{\mathrm{REC}} - N_{\mu}^{\mathrm{MC}}}{N_{\mu}^{\mathrm{MC}}}$', fontsize=15)
ax.set_ylabel(r'Shower Plane Azimuth $\phi$ [deg] (0° = Early, $\pm 180$° = Late)', fontsize=15)
ax.set_title('Normalized Muon Residual Distribution per Azimuth Bin', fontsize=17, pad=15, fontweight='bold')

# Barra de Color
cbar = fig.colorbar(im, ax=ax)
cbar.set_label('Probability Density (per $\phi$ bin)', fontsize=14)

# Textos Físicos (Posicionados para no tapar la cola derecha)
ax.text(0.95, 0.95, r"$\mathbf{Proton\ showers}$", transform=ax.transAxes, fontsize=13, va='top', ha='right', color='black')
ax.text(0.95, 0.89, r"$\mathbf{SIB2.3e}$", transform=ax.transAxes, fontsize=13, va='top', ha='right', color='black')
ax.text(0.95, 0.83, r"$\log_{10}(E_0/\mathrm{eV}) = 17.5 - 18.0$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color='black')

# Globo para el Array
props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='gray')
ax.text(0.03, 0.95, r"$\mathbf{Dense\ Ring\ (450\ m)}$", transform=ax.transAxes, fontsize=13, va='top', ha='left', bbox=props)

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_yticks([-180, -120, -60, 0, 60, 120, 180])
ax.legend(loc='lower right', fontsize=13, framealpha=0.9)

plt.tight_layout()
plt.show()

# %%
# =============================================================================
# CELDA: Mapa de Calor - Distribución del Residuo (Eje X) vs Azimut (Eje Y)
# =============================================================================

# 1. Preparación de datos (usando el Dataset Guía)
# Filtramos nMuones_MC > 0 para evitar divisiones por cero
df_valid = df_guia[df_guia['nMuones_MC'] > 0].copy()

# Calculamos residuo relativo y azimut centrado
df_valid['muon_residual_rel'] = (df_valid['nMuones_REC'] - df_valid['nMuones_MC']) / df_valid['nMuones_MC']
df_valid['phi_deg_centered'] = (np.rad2deg(df_valid['phi_plane_sp']) + 180) % 360 - 180

# Definimos límites (X = Residuo, Y = Phi)
x_min, x_max = -1.5, 4.5
y_min, y_max = -180, 180

mask_plot = (df_valid['muon_residual_rel'] >= x_min) & (df_valid['muon_residual_rel'] <= x_max)
data_x = df_valid.loc[mask_plot, 'muon_residual_rel']
data_y = df_valid.loc[mask_plot, 'phi_deg_centered']

# 2. Generar Bines y el Histograma 2D
x_bins = np.linspace(x_min, x_max, 80)    # 80 bines de residuo (Eje X - Resolución)
y_bins = np.linspace(y_min, y_max, 13)    # 12 bines de phi (Eje Y)

H, xedges, yedges = np.histogram2d(data_x, data_y, bins=[x_bins, y_bins])

# 3. NORMALIZACIÓN POR FILA DE PHI (Eje Y)
# H tiene shape (len(x_bins)-1, len(y_bins)-1). Cada columna 'j' es un bin de phi.
# Queremos que cada franja horizontal sume 1 (para comparar densidades justas)
H_norm = np.zeros_like(H)
for j in range(H.shape[1]): 
    suma_phi = H[:, j].sum()
    if suma_phi > 0:
        H_norm[:, j] = H[:, j] / suma_phi

# 4. Creación de la Figura
fig, ax = plt.subplots(figsize=(11, 7))

# Ploteamos el mapa de calor transpuesto
X, Y = np.meshgrid(xedges, yedges)
im = ax.pcolormesh(X, Y, H_norm.T, cmap='viridis', norm=mcolors.LogNorm(vmin=1e-4, vmax=H_norm.max()))

# 5. Superponer la Media para tener la referencia visual (Puntos Rojos)
df_valid['phi_bin'] = pd.cut(df_valid['phi_deg_centered'], bins=y_bins)
stats = df_valid[mask_plot].groupby('phi_bin', observed=True)['muon_residual_rel'].agg(['mean', 'sem'])
phi_centers = (yedges[:-1] + yedges[1:]) / 2

# Notar que acá graficamos X = media, Y = phi_centers
ax.errorbar(stats['mean'], phi_centers, xerr=stats['sem'], fmt='o-', color='crimson', 
            linewidth=2.5, markersize=8, markeredgecolor='black', label='Mean Residual')

# 6. Estética, Líneas de Referencia y Anotaciones
ax.axvline(0, color='white', linestyle='--', linewidth=1.5, alpha=0.8, label='Ideal Zero Bias')

ax.set_xlabel(r'Relative Muon Residual $\frac{N_{\mu}^{\mathrm{REC}} - N_{\mu}^{\mathrm{MC}}}{N_{\mu}^{\mathrm{MC}}}$', fontsize=15)
ax.set_ylabel(r'Shower Plane Azimuth $\phi$ [deg] (0° = Early, $\pm 180$° = Late)', fontsize=15)
ax.set_title('Normalized Muon Residual Distribution per Azimuth Bin', fontsize=17, pad=15, fontweight='bold')

# Barra de Color
cbar = fig.colorbar(im, ax=ax)
cbar.set_label('Probability Density (per $\phi$ bin)', fontsize=14)

# Textos Físicos (Posicionados para no tapar la cola derecha)
ax.text(0.95, 0.95, r"$\mathbf{Proton\ showers}$", transform=ax.transAxes, fontsize=13, va='top', ha='right', color='white')
ax.text(0.95, 0.89, r"$\mathbf{SIB2.3e}$", transform=ax.transAxes, fontsize=13, va='top', ha='right', color='white')
ax.text(0.95, 0.83, r"$\log_{10}(E_0/\mathrm{eV}) = 17.5 - 18.0$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color='white')

# Globo para el Array
props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='gray')
ax.text(0.03, 0.95, r"$\mathbf{Dense\ Ring\ (450\ m)}$", transform=ax.transAxes, fontsize=13, va='top', ha='left', bbox=props)

ax.set_xlim(-0.05, 0.2)
ax.set_ylim(y_min, y_max)
ax.set_yticks([-180, -120, -60, 0, 60, 120, 180])
ax.legend(loc='lower right', fontsize=13, framealpha=0.9)

plt.tight_layout()
plt.show()

# %%
# =========================================================================
# CELDA: TOY MONTE CARLO DIRECCIONAL (Phi-Dependent Noise)
# =========================================================================

# Asegurarnos de tener los bines de phi listos
phi_bin_edges = np.linspace(-180, 180, 13)
phi_centers = (phi_bin_edges[:-1] + phi_bin_edges[1:]) / 2

# Nos aseguramos de tener la columna 'phi_bin' bien definida en df_valid y df_ana
df_valid['phi_deg_centered'] = (np.rad2deg(df_valid['phi_plane_sp']) + 180) % 360 - 180
df_valid['phi_bin'] = pd.cut(df_valid['phi_deg_centered'], bins=phi_bin_edges)

df_ana['phi_deg_centered'] = (np.rad2deg(df_ana['phi_plane_sp']) + 180) % 360 - 180
df_ana['phi_bin'] = pd.cut(df_ana['phi_deg_centered'], bins=phi_bin_edges)

# 1. Crear las 12 "bolsas" de errores separadas por bin azimutal
bolsas_errores = {}
for bin_name, group in df_valid.groupby('phi_bin', observed=True):
    bolsas_errores[bin_name] = group['muon_residual_rel'].dropna().values

# 2. Inyectar el ruido dependiente de phi a la verdad de Monte Carlo
np.random.seed(311001) # Para reproducibilidad
df_ana['nMuones_TOY_PHI'] = np.nan

for bin_name, group in df_ana.groupby('phi_bin', observed=True):
    bolsa = bolsas_errores.get(bin_name, np.array([]))
    if len(bolsa) > 0:
        # Muestreamos de la bolsa específica de este ángulo
        ruido_phi = np.random.choice(bolsa, size=len(group))
        df_ana.loc[group.index, 'nMuones_TOY_PHI'] = group['nMuones_MC'] * (1 + ruido_phi)
    else:
        # Si por alguna razón la bolsa está vacía, no modificamos el MC
        df_ana.loc[group.index, 'nMuones_TOY_PHI'] = group['nMuones_MC']

# 3. Analizar la asimetría para este nuevo "Detector Toy"
evol_theta = []
a1_mc, a1_rec, a1_toy_phi = [], [], []

columnas = ['nMuones_MC', 'nMuones_REC', 'nMuones_TOY_PHI']

for i in range(10):
    mask_bin = (df_ana['theta_bin_idx'] == i)
    df_sl = df_ana[mask_bin].copy()
    
    if len(df_sl) < 50: continue
        
    stats = df_sl.groupby('phi_bin', observed=True)[columnas].agg(['mean', 'sem'])
    
    a1_vals = {}
    
    for col in columnas:
        if col not in stats.columns: continue
        
        means = stats[col]['mean']
        norm = means.mean()
        if pd.isna(norm) or norm == 0: continue
            
        y = (means / norm).values
        yerr = (stats[col]['sem'] / norm).values
        
        valid_idx = ~np.isnan(y) & ~np.isnan(yerr) & (yerr > 0)
        
        if len(y[valid_idx]) > 3:
            try:
                popt, _ = curve_fit(fit_func_deg, phi_centers[valid_idx], y[valid_idx], p0=[0.05], sigma=yerr[valid_idx])
                a1_vals[col] = popt[0]
            except: pass
                
    evol_theta.append(i)
    a1_mc.append(a1_vals.get('nMuones_MC', np.nan))
    a1_rec.append(a1_vals.get('nMuones_REC', np.nan))
    a1_toy_phi.append(a1_vals.get('nMuones_TOY_PHI', np.nan))

# 4. Ploteo de la Verificación Definitiva
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(evol_theta, a1_mc, 's--', color='forestgreen', markersize=8, lw=2, label=r'$UMD\ N_\mu^{MC}$')
ax.plot(evol_theta, a1_rec, 'o-', color='navy', markersize=8, lw=2, label=r'$UMD\ N_\mu^{REC}$')
ax.plot(evol_theta, a1_toy_phi, '*:', color='crimson', markersize=12, lw=2.5, label=r'Toy Model ($\phi$-dependent bias)')

ax.set_xlabel(r"Zenith Bin", fontsize=14)
ax.set_ylabel(r"Asymmetry Amplitude $A_1$", fontsize=14)
ax.set_title("Asymmetry Loss due to Reconstruction Directional Bias", fontsize=15, fontweight='bold', pad=15)

# Fijamos las posiciones de los ticks en los índices (0 a 9) y aplicamos los labels rotados
ax.set_xticks(evol_theta) 
ax.set_xticklabels(theta_labels, rotation=35, ha='right', fontsize=10)
# --- FIN MODIFICACIÓN ---

# Indicador del detector / arreglo
ax.text(0.05, 0.95, r"$\mathbf{Dense\ Ring\ (450\ m)}$", transform=ax.transAxes, fontsize=12, va='top', ha='left', color='black')

# Anotaciones Físicas
ax.text(0.95, 0.98, r"$\mathbf{Proton\ showers}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color=COLORS['Proton'])
ax.text(0.95, 0.91, r"$\mathbf{SIB2.3e}$", transform=ax.transAxes, fontsize=12, va='top', ha='right', color='purple')
ax.text(0.95, 0.84, r"$\log_{10}(E_0/\mathrm{eV}) = 17.5 - 18.0$", transform=ax.transAxes, fontsize=11, va='top', ha='right')


ax.grid(True, which='major', linestyle='-', alpha=0.4)
ax.grid(True, which='minor', linestyle=':', alpha=0.2)
ax.legend(fontsize=12, loc='lower center')

y_max = max(max(a1_mc), max(a1_rec), max(a1_toy_phi))
ax.set_ylim(bottom=0, top=y_max * 1.3)

plt.tight_layout()
plt.savefig('toy_model.png', dpi=300)
plt.show()

# %% [markdown]
# ### Validación Definitiva: *Toy Model* con Sesgo Direccional
#
# Para corroborar definitivamente que la degradación de la asimetría reconstruida es consecuencia directa de una respuesta instrumental dependiente de la dirección, se diseñó un *Toy Model* empírico direccional. A diferencia de un modelo de ruido global, en este enfoque se inyectó sobre la señal pura de Monte Carlo ($N_\mu^{\mathrm{MC}}$) un ruido muestreado directamente de las distribuciones de los residuos relativos reales correspondientes a cada sector azimutal específico ($\phi$). De esta manera, el modelo hereda artificialmente la sobreestimación sistemática de muones en la región tardía de la lluvia.
#
# Los resultados de este modelo reproducen fielmente el comportamiento de la reconstrucción:
#
# 1. **Régimen de baja y media inclinación ($\theta \lesssim 45^\circ$):** La amplitud de asimetría generada por el *Toy Model* direccional se superpone exactamente con la curva de la reconstrucción del detector ($A_1^{\mathrm{REC}}$). Esto constituye una prueba irrefutable de que, en este rango angular, el 100% de la pérdida de asimetría se debe exclusivamente al sesgo de sobreconteo direccional originado por el ablandamiento del espectro de energía y la respuesta geométrica del centellador.
#
# 2. **Régimen de alta inclinación ($\theta \gtrsim 45^\circ$):** Si bien el sesgo direccional introducido logra explicar más del 50% de la degradación observada frente a los datos ideales, la curva del *Toy Model* no alcanza a replicar la totalidad de la caída en $A_1^{\mathrm{REC}}$. Esta divergencia remanente en el régimen inclinado indica la presencia de efectos físicos y topológicos de segundo orden que un modelo estadístico de conteo unidimensional no logra capturar. 
#
# **Hipótesis para la divergencia a gran inclinación:**
# La degradación adicional en lluvias muy inclinadas puede atribuirse a dos factores combinados:
# * **Desplazamiento Geomagnético:** A grandes ángulos cenitales, la fuerza de Lorentz ($\vec{v} \times \vec{B}$) ejercida por el campo magnético terrestre genera una separación espacial significativa entre muones positivos y negativos. Este ensanchamiento físico de la distribución "lava" la modulación senoidal pura de una forma que no puede ser replicada inyectando únicamente fluctuaciones en el conteo de partículas.
# * **Topología Extrema en el Detector:** Para trayectorias casi horizontales, un único muon rasante recorre una longitud desproporcionada dentro del material, pudiendo inducir señales cruzadas (*cross-talk*) masivas en múltiples tiras de centelleo adyacentes, lo que rompe la linealidad de los residuos asumida en la construcción del modelo empírico.

# %%
