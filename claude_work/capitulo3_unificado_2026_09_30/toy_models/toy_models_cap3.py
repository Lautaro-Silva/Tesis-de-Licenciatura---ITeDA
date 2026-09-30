# %% [markdown]
# # Modelos de juguete del Capítulo 3 (fuente puntual + cociente tardío/temprano de Cazón)
#
# Genera las figuras (en ../capitulos/imagenes_capitulos/cap3/) y los números de la Sección "Modelos de juguete" del
# borrador `03_fenomenologia.tex` de esta carpeta. Sólo numpy/matplotlib;
# corre en segundos (no usa datos, no usa Offline).
#
# Modelo: una fuente puntual de muones sobre el eje, a distancia D (medida sobre
# el eje) del núcleo. Una estación en el plano de la lluvia en (r, phi) está a
#   d(phi) = sqrt((D - r tan(theta) cos(phi))^2 + r^2)
# de la fuente, y la ve bajo el ángulo sin(alpha) = r / d.
#
# Factores que se pueden encender/apagar (todos multiplican):
#   dilución       1/d^2
#   angular        f(alpha|p) = k^2/(2 pi Z(k)) cos(alpha) exp(-k sin(alpha)),
#                  k = p/Q,  Z(k) = 1 - (1+k) e^{-k}      (Cazón, dN/dp_t ∝ p_t e^{-p_t/Q})
#   decaimiento    exp(-d / lambda(p)),  lambda = (p/m_mu) c tau_mu   (Armbruster, momento fijo)
#   respuesta      placa horizontal: cos(vartheta) = D cos(theta)/d ; tanque (conteo): A_tanque(vartheta)
#
# A1 se calcula como coeficiente de Fourier del perfil azimutal,
#   A1 = 2 <S cos phi> / <S>,
# que es lo que devuelve un ajuste S0(1 + A1 cos phi) por mínimos cuadrados con
# bines azimutales iguales y pesos iguales.

# %%
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "capitulos" / "imagenes_capitulos" / "cap3"
OUT.mkdir(parents=True, exist_ok=True)

M_MU = 0.10566   # GeV
C_TAU = 658.6    # m
R_TANK, H_TANK = 1.8, 1.2  # m (WCD)

# Punto de referencia (el mismo del memo "Weighting the Angle by Its Probability")
REF = dict(r=1200.0, theta=35.0, D=7500.0, Q=0.20, gamma=2.6)

PHI = np.linspace(-np.pi, np.pi, 361)[:-1]   # grilla azimutal uniforme


def geometria(r, theta_deg, D, phi):
    t = np.radians(theta_deg)
    d = np.sqrt((D - r * np.tan(t) * np.cos(phi)) ** 2 + r ** 2)
    sin_a = r / d
    cos_vt = D * np.cos(t) / d            # cenital local de la trayectoria
    return d, sin_a, cos_vt


def adf(sin_a, p, Q):
    """f(alpha|p) = dN/dOmega normalizada en el hemisferio delantero."""
    k = p / Q
    Z = -np.expm1(-k) - k * np.exp(-k)
    cos_a = np.sqrt(1.0 - sin_a ** 2)
    return k ** 2 / (2 * np.pi * Z) * cos_a * np.exp(-k * sin_a)


def peso(phi, p, r, theta, D, Q, decaimiento=False, respuesta=None):
    """Contribución de muones de momento p que llegan a (r, phi). Arrays con broadcasting."""
    d, sin_a, cos_vt = geometria(r, theta, D, phi)
    w = adf(sin_a, p, Q) / d ** 2
    if decaimiento:
        w = w * np.exp(-d * M_MU / (p * C_TAU))
    if respuesta == "placa":
        w = w * cos_vt
    elif respuesta == "tanque":
        sin_vt = np.sqrt(1 - cos_vt ** 2)
        w = w * (np.pi * R_TANK ** 2 * cos_vt + 2 * R_TANK * H_TANK * sin_vt)
    return w


def a1_fourier(S, phi=PHI):
    return 2 * np.mean(S * np.cos(phi)) / np.mean(S)


def a1_dos_puntos(S_E, S_T):
    return (S_E - S_T) / (S_E + S_T)


# ---------- A1 a momento fijo -------------------------------------------------
def a1_momento_fijo(p, r, theta, D, Q, **kw):
    return a1_fourier(peso(PHI, p, r, theta, D, Q, **kw))


def a1_lineal(p, r, theta, D, Q, decaimiento=False, kappa=0.0):
    """Expansión a primer orden en eps = r/D (Armbruster):
    A1 ≈ [2 - s + D/lambda + kappa] (r/D) tan(theta),  s = k sin(alpha) + tan^2(alpha) (pendiente local de f)."""
    eps = r / D
    sin_a = eps / np.sqrt(1 + eps ** 2)
    s = (p / Q) * sin_a + sin_a ** 2 / (1 - sin_a ** 2)
    att = D * M_MU / (p * C_TAU) if decaimiento else 0.0
    return (2 - s + att + kappa) * eps * np.tan(np.radians(theta))


# ---------- A1 de una población con espectro ----------------------------------
P_GRID = np.logspace(np.log10(0.05), np.log10(2000.0), 1500)


def perfil_poblacion(p_umbral, r, theta, D, Q, gamma, umbral_local=False, **kw):
    """S(phi) = ∫_{p_umbral} p^-gamma W(phi,p) dp  (cociente de integrales, no promedio de cocientes).
    umbral_local=True: el umbral depende del cenital local de cada trayectoria,
    p_umbral(phi) = p_umbral / cos(vartheta(phi))  (espesor de suelo atravesado, UMD)."""
    p = P_GRID[P_GRID >= min(p_umbral, P_GRID.max())]
    G = p ** (-gamma)
    W = peso(PHI[:, None], p[None, :], r, theta, D, Q, **kw)
    if umbral_local:
        _, _, cos_vt = geometria(r, theta, D, PHI)
        W = np.where(p[None, :] >= (p_umbral / cos_vt)[:, None], W, 0.0)
    return np.trapezoid(G[None, :] * W, p, axis=1)


def a1_poblacion(p_umbral, r, theta, D, Q, gamma, **kw):
    return a1_fourier(perfil_poblacion(p_umbral, r, theta, D, Q, gamma, **kw))


def a1_promedio_de_cocientes(p_umbral, r, theta, D, Q, gamma):
    """La versión INCORRECTA (memo, 'Error 1' + 'Error 2'): promedia el cociente
    tardío/temprano con el espectro de producción y sin el prefactor k^2/Z."""
    p = P_GRID[P_GRID >= p_umbral]
    G = p ** (-gamma)
    dE, sE, _ = geometria(r, theta, D, 0.0)
    dT, sT, _ = geometria(r, theta, D, np.pi)
    cE, cT = np.sqrt(1 - sE ** 2), np.sqrt(1 - sT ** 2)
    rho = (dE / dT) ** 2 * (cT / cE) * np.exp(p / Q * (sE - sT))
    rho_m = np.trapezoid(G * rho, p) / np.trapezoid(G, p)
    return (1 - rho_m) / (1 + rho_m)


# %%
if __name__ == "__main__":
    r, th, D, Q, g = REF["r"], REF["theta"], REF["D"], REF["Q"], REF["gamma"]
    dE, sE, cvE = geometria(r, th, D, 0.0)
    dT, sT, cvT = geometria(r, th, D, np.pi)
    print("=== Punto de referencia r=1200 m, theta=35°, D=7.5 km, Q=0.2 GeV/c, gamma=2.6")
    print(f"d_E = {dE:.0f} m, d_T = {dT:.0f} m, (d_E/d_T)^2 = {(dE/dT)**2:.3f}")
    print(f"alpha_E = {np.degrees(np.arcsin(sE)):.2f}°, alpha_T = {np.degrees(np.arcsin(sT)):.2f}°")
    print(f"vartheta_E = {np.degrees(np.arccos(cvE)):.1f}°, vartheta_T = {np.degrees(np.arccos(cvT)):.1f}°")
    print(f"d_T - d_E = {dT-dE:.0f} m  (2 r tan(theta) = {2*r*np.tan(np.radians(th)):.0f} m)")

    # respuesta del detector sola (flujo isótropo en f/L^2 apagado): A1 de cos(vartheta) y del tanque
    a_placa = a1_dos_puntos(cvE, cvT)
    AE = np.pi*R_TANK**2*cvE + 2*R_TANK*H_TANK*np.sqrt(1-cvE**2)
    AT = np.pi*R_TANK**2*cvT + 2*R_TANK*H_TANK*np.sqrt(1-cvT**2)
    print(f"A1 sólo respuesta: placa {a_placa:+.3f}, tanque (conteo) {a1_dos_puntos(AE, AT):+.3f}, tanque (señal VEM) +0.000")

    # E* exacto (dos puntos) y lineal
    ps = np.logspace(-1, 1.5, 4000)
    R = [(dE/dT)**2 * np.sqrt(1-sT**2)/np.sqrt(1-sE**2) * np.exp(p/Q*(sE-sT)) for p in ps]
    p_star = ps[np.argmin(np.abs(np.log(R)))]
    print(f"p* (cociente tardío/temprano = 1): {p_star:.2f} GeV/c ; aproximación 2QD/r = {2*Q*D/r:.2f} GeV/c")
    Rd = [Ri*np.exp(-(dT-dE)*M_MU/(p*C_TAU)) for Ri, p in zip(R, ps)]
    p_star_d = ps[np.argmin(np.abs(np.log(Rd)))]
    print(f"p* con decaimiento: {p_star_d:.2f} GeV/c")
    for p in [0.2, 0.5, 1, 2, 8]:
        fr = adf(sT, p, Q)/adf(sE, p, Q)
        print(f"  p={p:>4} GeV/c: f(aT)/f(aE) = {fr:.3f}, cociente total Ec.3.4 = {(dE/dT)**2*fr:.3f}, "
              f"A1(p) exacto = {a1_momento_fijo(p, r, th, D, Q):+.3f}, lineal = {a1_lineal(p, r, th, D, Q):+.3f}")

    print("\n=== Población con espectro p^-2.6, cociente de integrales")
    for pth in [0.155, 0.3, 0.5, 1.0/np.cos(np.radians(th)), 2.0, 3.0]:
        print(f"  p_umbral={pth:5.3f}: Ec.3.4 sola {a1_poblacion(pth, r, th, D, Q, g):+.3f} | "
              f"+decaim. {a1_poblacion(pth, r, th, D, Q, g, decaimiento=True):+.3f} | "
              f"+decaim.+placa {a1_poblacion(pth, r, th, D, Q, g, decaimiento=True, respuesta='placa'):+.3f} | "
              f"+decaim.+tanque {a1_poblacion(pth, r, th, D, Q, g, decaimiento=True, respuesta='tanque'):+.3f} | "
              f"promedio de cocientes (incorrecto) {a1_promedio_de_cocientes(pth, r, th, D, Q, g):+.3f}")
    # comparación con el memo (dos puntos)
    SE = perfil_poblacion(0.155, r, th, D, Q, g)
    print(f"  (control memo, 2 puntos, umbral 0.155) A1 = "
          f"{a1_dos_puntos(SE[np.argmin(np.abs(PHI))], SE[0]):+.3f}  (memo: +0.160)")

    # ---------------- Figura 1: f(alpha|p) y A1 a momento fijo ----------------
    plt.rcParams.update({"font.family": "serif", "font.size": 11, "axes.labelsize": 12,
                         "legend.fontsize": 9.5, "mathtext.fontset": "cm"})
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    al = np.radians(np.linspace(0, 30, 600))
    cols = plt.cm.viridis(np.linspace(0.05, 0.85, 4))
    for p, c in zip([0.2, 0.5, 2.0, 8.0], cols):
        f = adf(np.sin(al), p, Q)
        ax[0].plot(np.degrees(al), f / f.max(), color=c, lw=2, label=fr"$p = {p:g}$ GeV/$c$")
    aE, aT = np.degrees(np.arcsin(sE)), np.degrees(np.arcsin(sT))
    for a, lab in [(aT, r"$\alpha_{T}$"), (aE, r"$\alpha_{E}$")]:
        ax[0].axvline(a, color="0.3", ls="--", lw=1)
        ax[0].text(a + 0.3, 1.02, lab, fontsize=11)
    ax[0].set_xlabel(r"ángulo de emisión $\alpha$ [°]")
    ax[0].set_ylabel(r"$f(\alpha\,|\,p)$ normalizada al máximo")
    ax[0].set_ylim(0, 1.12); ax[0].set_xlim(0, 30)
    ax[0].legend(loc="upper right")
    ax[0].set_title("(a) Distribución angular de emisión", fontsize=11)

    pp = np.logspace(-1, np.log10(30), 300)
    ax[1].plot(pp, [a1_momento_fijo(p, r, th, D, Q) for p in pp], color="C0", lw=2,
               label=r"dilución $\times$ emisión angular")
    ax[1].plot(pp, a1_lineal(pp, r, th, D, Q), color="C0", ls=":", lw=1.5, label="aproximación lineal")
    ax[1].plot(pp, [a1_momento_fijo(p, r, th, D, Q, decaimiento=True) for p in pp], color="C3", lw=2,
               label=r"$+$ decaimiento $e^{-d/\lambda(p)}$")
    ax[1].plot(pp, a1_lineal(pp, r, th, D, Q, decaimiento=True), color="C3", ls=":", lw=1.5)
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].axvline(p_star, color="C0", ls="--", lw=1)
    ax[1].text(p_star * 1.08, 0.55, fr"$p^*\simeq{p_star:.1f}$", color="C0")
    ax[1].set_xscale("log"); ax[1].set_ylim(-0.6, 0.9)
    ax[1].set_xlabel(r"momento del muón en producción $p$ [GeV/$c$]")
    ax[1].set_ylabel(r"$A_1$ a momento fijo")
    ax[1].text(12, -0.14, "exceso\ntardío", fontsize=10, color="0.3")
    ax[1].text(12, 0.04, "exceso\ntemprano", fontsize=10, color="0.3")
    ax[1].legend(loc="lower left")
    ax[1].set_title(r"(b) $A_1$ de muones de un único momento", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "toy_momento_fijo.pdf")

    # ---------------- Figura 2: A1 de la población vs umbral ----------------
    pth = np.logspace(np.log10(0.1), np.log10(5), 60)
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    curvas = [
        (dict(), "C0", "-", r"dilución $\times$ emisión angular"),
        (dict(decaimiento=True), "C3", "-", r"$+$ decaimiento"),
        (dict(decaimiento=True, respuesta="placa"), "C2", "-", r"$+$ decaimiento $+$ placa horizontal"),
        (dict(decaimiento=True, respuesta="tanque"), "C1", "--", r"$+$ decaimiento $+$ tanque (conteo)"),
    ]
    for kw, c, ls, lab in curvas:
        ax.plot(pth, [a1_poblacion(x, r, th, D, Q, g, **kw) for x in pth], color=c, ls=ls, lw=2, label=lab)
    ax.axhline(0, color="k", lw=0.8)
    for x, lab in [(0.2, "SD"), (1 / np.cos(np.radians(th)), "UMD")]:
        ax.axvline(x, color="0.5", ls="--", lw=1)
        ax.text(x * 1.04, 0.38, lab, color="0.3")
    ax.set_xscale("log"); ax.set_ylim(-0.45, 0.45)
    ax.set_xlabel(r"umbral en momento $p_{\rm umbral}$ [GeV/$c$]")
    ax.set_ylabel(r"$A_1$ de la población")
    ax.set_title(r"$r=1200$ m, $\theta=35^\circ$, $D=7.5$ km, $Q=0.2$ GeV/$c$, $\gamma=2.6$", fontsize=10)
    ax.legend(loc="lower left", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "toy_umbral.pdf")

    # ---------------- Figura 3: A1 vs r, toy completo por detector ----------------
    rr = np.linspace(200, 1800, 33)
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for thv, ls in [(35.0, "-"), (50.0, "--")]:
        ax.plot(rr, [a1_poblacion(0.2, x, thv, D, Q, g, decaimiento=True, respuesta="tanque") for x in rr],
                color="C1", ls=ls, lw=2, label=fr"SD: conteo en tanque, $p>0.2$ GeV/$c$, $\theta={thv:.0f}^\circ$")
        ax.plot(rr, [a1_poblacion(1.0, x, thv, D, Q, g, decaimiento=True, respuesta="placa", umbral_local=True)
                     for x in rr],
                color="C0", ls=ls, lw=2, label=fr"UMD: placa, $p>1\,{{\rm GeV}}/(c\cos\vartheta)$, $\theta={thv:.0f}^\circ$")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylim(-0.02, 0.75)
    ax.set_xlabel(r"radio en el plano de la lluvia $r$ [m]")
    ax.set_ylabel(r"$A_1$ del modelo de juguete completo")
    ax.legend(fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "toy_radio.pdf")

    print("\n=== Umbral UMD global (1/cos theta) vs local (1/cos vartheta), placa + decaimiento, r=1200, theta=35")
    print(f"  global {a1_poblacion(1/np.cos(np.radians(th)), r, th, D, Q, g, decaimiento=True, respuesta='placa'):+.3f}"
          f"  local {a1_poblacion(1.0, r, th, D, Q, g, decaimiento=True, respuesta='placa', umbral_local=True):+.3f}")
    print("\n=== A1 vs r, toy completo (SD: tanque, p>0.2 ; UMD: placa, p>1/cos(vartheta))")
    for thv in [35, 50]:
        for x in [450, 750, 1200, 1600]:
            print(f"  theta={thv} r={x}: SD {a1_poblacion(0.2, x, thv, D, Q, g, decaimiento=True, respuesta='tanque'):+.3f}, "
                  f"UMD {a1_poblacion(1.0, x, thv, D, Q, g, decaimiento=True, respuesta='placa', umbral_local=True):+.3f}"
                  f"  | sólo Ec.3.4+dec: SD-like {a1_poblacion(0.2, x, thv, D, Q, g, decaimiento=True):+.3f}")
    print("\n=== Linealización: contribución de cada término a A1/(eps tan theta) en r=1200, theta=35, p=1 y p=3 GeV/c")
    eps = r / D
    for p in [1.0, 3.0]:
        s_ = p / Q * eps / np.sqrt(1 + eps**2)
        print(f"  p={p}: dilución +2, angular -{s_:.2f}, decaimiento D/lambda=+{D*M_MU/(p*C_TAU):.2f}, placa +1"
              f"  -> eps tan theta = {eps*np.tan(np.radians(th)):.3f}")
    print(f"  atenuación sola: A1_att ≈ r tan(theta)/lambda = {r*np.tan(np.radians(th))/(1/M_MU*C_TAU):.3f} para p=1 GeV/c")
    print("\nFiguras en", OUT)
