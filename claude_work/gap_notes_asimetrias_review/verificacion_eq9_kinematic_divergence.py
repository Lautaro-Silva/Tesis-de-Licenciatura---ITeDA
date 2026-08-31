"""
Verification of Version_Vieja's Eq. (9) (S_late/S_early kinematic-divergence ratio),
prompted by the advisor's comment questioning whether the exponential "gain" term is
actually large for Population B (low-energy) muons.

Symbolic part reproduces Eqs. (4)-(8) from dN/dpt ~ pt*exp(-pt/Q) and sin(alpha)=pt/E,
confirming dN/dOmega ~ E^2 cos(alpha) exp(-E sin(alpha)/Q), matching the paper's Eq. (8)
up to the E^2 prefactor (absorbed/dropped there).

Numeric part evaluates the full ratio (spatial x cosine x exponential factors) using
Cazon (2012) Eq. (7) for the exact alpha(r, D, theta, zeta) relation (more precise than
Version_Vieja's small-angle d(phi) approximation), with Q ~ 0.2 GeV taken from Cazon
(2012) Figs. 7-9 / their "1 GeV muon spans 10 deg, 10 GeV spans 1 deg" statement, and
D ~ 5-10 km from Cazon's own worked example ("muon produced at z=10 km") and
Bertou & Billoir (GAP-2000-017)'s "~5 km altitude" statement.

Finding: at r=1200 m, theta=35 deg (Version_Vieja/GAP2026_041 Table 2's disputed point),
the *net* kinematic term (all three factors combined) is EARLY-favoring (positive A1) for
E below a crossover E* ~ 1.1-4.1 GeV depending on (Q, D), and only turns LATE-favoring
above that -- straddling the UMD's own effective threshold (~1.0-1.5 GeV depending on
theta). This contradicts the "Population B (E << 1 GeV) drives the late excess, UMD
filters it out" narrative in Version_Vieja Sec. 2.2/4.3, since Population B's own energy
range sits mostly *below* E*, where the term is early-favoring, same sign as attenuation.
"""
import numpy as np
from scipy.optimize import brentq
import sympy as sp


def symbolic_check():
    E, Q, alpha, alpha_e, alpha_l = sp.symbols('E Q alpha alpha_e alpha_l', positive=True)
    pt = E * sp.sin(alpha)
    dN_dpt = pt * sp.exp(-pt / Q)
    dOmega_dpt = sp.sin(alpha) / (E * sp.cos(alpha))
    dN_dOmega = sp.simplify(dN_dpt / dOmega_dpt)
    print("dN/dOmega =", dN_dOmega, "  (matches paper's Eq. 8 up to E^2 prefactor)")

    expfac = sp.exp(E * (sp.sin(alpha_e) - sp.sin(alpha_l)) / Q)
    dfac_dE = sp.simplify(sp.diff(expfac, E))
    print("d/dE[exp((sin ae - sin al) E / Q)] =", dfac_dE)
    print(" -> strictly positive whenever sin(alpha_e) > sin(alpha_l): exponential factor")
    print("    is MONOTONICALLY INCREASING in E, i.e. it requires E to be large to matter.\n")


def alpha_rad(r, D, theta_rad, zeta_rad):
    """Cazon (2012) Eq. 7, solved for alpha: r = z / (cos(zeta) tan(theta) + 1/tan(alpha))."""
    tan_alpha = r / (D - r * np.cos(zeta_rad) * np.tan(theta_rad))
    return np.arctan(tan_alpha)


def factors(r, D, theta_deg, Q):
    theta = np.radians(theta_deg)
    ae = alpha_rad(r, D, theta, 0.0)
    al = alpha_rad(r, D, theta, np.pi)
    d_early = D - r * np.sin(theta)
    d_late = D + r * np.sin(theta)
    spatial = (d_early / d_late) ** 2
    cosfac = np.cos(al) / np.cos(ae)
    return ae, al, spatial, cosfac


def ratio(E, r, D, theta_deg, Q):
    ae, al, spatial, cosfac = factors(r, D, theta_deg, Q)
    expfac = np.exp((np.sin(ae) - np.sin(al)) * E / Q)
    return spatial * cosfac * expfac


def crossover_energy(r, D, theta_deg, Q):
    return brentq(lambda E: ratio(E, r, D, theta_deg, Q) - 1.0, 0.01, 50)


def main():
    symbolic_check()

    r, theta_deg = 1200.0, 35.0
    print(f"=== r={r} m, theta={theta_deg} deg (Table 2's disputed far-core point) ===\n")
    print("Crossover energy E* (pure-kinematic A1 flips + -> -):")
    for Q in (0.15, 0.20, 0.25, 0.30):
        for D in (5000.0, 7500.0, 10000.0):
            Estar = crossover_energy(r, D, theta_deg, Q)
            print(f"  Q={Q:.2f} GeV, D={D/1000:.1f} km  ->  E* = {Estar:.2f} GeV")
        print()

    theta_rad = np.radians(theta_deg)
    print(f"UMD effective threshold at theta={theta_deg} deg: "
          f"E_mu >~ 1 GeV/cos(theta) = {1.0/np.cos(theta_rad):.2f} GeV")
    print("SD effective threshold (WCD, ~100 MeV kinetic, per GAP2026_041 Sec. 5): ~0.1-0.15 GeV\n")

    print("=== Sanity check at r=450 m (near-core reference point), Q=0.20 GeV ===")
    for D in (5000.0, 7500.0, 10000.0):
        ae, al, spatial, cosfac = factors(450.0, D, theta_deg, 0.20)
        print(f"D={D/1000:.1f} km: alpha_e={np.degrees(ae):.2f} deg, alpha_l={np.degrees(al):.2f} deg, "
              f"spatial={spatial:.3f}, cosfac={cosfac:.4f}")
        for E in (0.1, 0.3, 1.0, 1.22, 3.0):
            full = ratio(E, 450.0, D, theta_deg, 0.20)
            A1 = (1 - full) / (1 + full)
            print(f"    E={E:5.2f} GeV -> S_late/S_early={full:.3f}, implied A1={A1:+.3f}")
        print()
    print("(Matches sign and rough magnitude of the observed SD-Muon(MC) A1=+0.05 at r=450 m,"
          " Table 2 of both GAP notes -- the model is not broken, it just tells a different"
          " story than the Sec. 2.2/4.3 prose at r=1200 m.)")


if __name__ == "__main__":
    main()
