"""
Verification of Version_Vieja's Eq. (9) (S_late/S_early kinematic-divergence ratio) and
of GAP-2026-041's replacement "volumetric/track-length" argument (Sec. 6, paragraph 3).

v2 of this script (superseding the version reviewed in the first pass). The original
mixed two different geometric approximations -- Cazon (2012) Eq. 7's alpha(r,D,theta,zeta)
together with Version_Vieja's own small-angle d(phi) ~= D -+ r sin(theta) -- which is
internally inconsistent (Cazon's alpha already implies a specific, different d). This
version instead builds ONE self-consistent exact 3D geometry (production point at
distance D along the shower axis, ground point at shower-plane radius r and azimuth
phi in {0 (early), pi (late)}) and derives d, alpha, and the local zenith angle
theta_loc from it directly, then uses that same geometry for three separate checks:

  1. The pure-kinematic S_late/S_early ratio (Version_Vieja Eqs. 4-9) and its crossover
     energy E*, now with exact geometry and a scan over the production distance D.
  2. A cross-check against the independently published mechanism in Luce et al.
     (ICRC 2021, #435, Sec. 2.2): alpha_asymmetry ~ 2 - gamma + d(theta)/lambda, where
     gamma is the local log-slope of the angular distribution function. Showing this
     reproduces the same E* demonstrates Version_Vieja's Eq. (9) is a re-derivation of
     already-published work, not new physics.
  3. The purely instrumental, purely geometric asymmetry of a physical detector's
     response -- flat horizontal plane (UMD-like) vs. WCD tank particle count vs. WCD
     tank muon VEM signal (path-length weighted) -- using the tank's actual dimensions,
     to check GAP-2026-041 Sec. 6 paragraph 3's claim that the tank's side-wall/
     track-length effect drives a *negative* contribution. Also estimates the purely
     instrumental asymmetry of the UMD's own overburden threshold, which is itself
     azimuthally modulated through theta_loc and which neither GAP note subtracts.

Findings (see claude_work/gap_notes_asimetrias_review/kinematic_divergence_math_check.md
for full discussion):
  - E* (crossover where the pure-kinematic term flips early->late-favoring) is ~2.5 GeV
    at r=1200 m, theta=35 deg, D=7.5 km, Q=0.2 GeV -- above the UMD's own ~1.2 GeV
    threshold at that angle. Population B (E << 1 GeV) sits in the EARLY-favoring
    regime, the opposite of Version_Vieja's Sec. 2.2/4.3 narrative.
  - E* falls with D: by D=2 km it is ~0.6 GeV, so the narrative is not falsified in
    general, only unevaluated -- rescuing it requires an anticorrelation between
    production height and energy that the note never invokes.
  - The Luce (2021) alpha ~ 2 - gamma + d/lambda form reproduces the same E*, confirming
    Version_Vieja's Eq. (9) duplicates already-published prior art without citing it as
    such.
  - The WCD's own geometric response is NOT negative: particle count gives A1 = +0.031
    (positive, suppressed from the flat-plane +0.109 by the tank's 2.4x top/side area
    ratio, exactly as Bertou & Billoir Fig. 6 shows), and the muon VEM (track-length
    weighted) response gives EXACTLY zero, by the Cauchy mean-chord theorem (path length
    through a convex body, integrated over a parallel beam, is F_perp * V / A_top,
    independent of incidence angle -- the track-length gain invoked in GAP-2026-041 Sec.
    6 exactly cancels the aperture-projection loss it is layered on top of).
  - The UMD's own overburden threshold is azimuthally modulated (theta_loc is larger in
    the late region), producing a PURELY INSTRUMENTAL positive A1 of +0.11 to +0.22
    (depending on the assumed muon energy spectral index) at the same reference point --
    comparable to or larger than the entire measured UMD A1 of +0.11. This is not
    accounted for in either GAP note version.

v3 additions (prompted directly by the author's own review, who confirmed the SD/UMD
sign split is physical -- reproduced with both Dense Ring and Infill topologies, MC and
REC geometry -- and pushed back that no positive explanation for the SD had been
offered):

  6. In-flight atmospheric multiple Coulomb scattering (v4, prompted by the author asking
     for a plausible physical mechanism, checked against new bibliography): Grieder
     (2010, "Extensive Air Showers", Sec. 3.1) treats Coulomb scattering of muons DURING
     PROPAGATION as a mechanism distinct from and additive to production-kinematics
     scattering -- something absent from every analytic model used in this whole
     investigation (Cazon's, Version_Vieja's, and this script's Secs. 1-5), all of which
     assume ballistic straight-line propagation. Late-region muons traverse ~25% more
     slant depth than early-region ones at the reference point (two independent
     geometric estimates agree to 3%), so they accumulate more scattering -- which,
     convolved properly (an exponential-tilt argument, verified against direct numerical
     convolution) with Cazon's angular distribution, multiplicatively boosts the
     late/early density ratio. Quantified with the standard Highland RMS (Gaussian-core)
     formula, the boost is only ~1-2% across the relevant energy range -- an order of
     magnitude too small on its own to turn the pure-kinematic term's early-favouring
     prediction into the implied ~-0.13 true-flux inversion. This does NOT rule the
     mechanism out: the Highland formula describes only the Gaussian CORE of the Moliere
     scattering distribution, and Grieder's own text distinguishes this "narrow-angle"
     regime from a separate "wide-angle" tail (rare large single scatters) that the RMS
     estimate cannot capture -- exactly the kind of rare, high-leverage tail population
     that already broke the naive spectrum-weighted integral in point 5 above. Untested
     here; the direct, cheap way to check it is empirical (compare each muon's actual
     simulated ground-arrival direction to Cazon's production-kinematics-only prediction
     in the existing MC), not a fourth analytic toy model.
  4. Because the tank's own geometric term cancels EXACTLY for the muon VEM signal (see
     3. above), the VEM signal is theoretically a clean, undistorted tracer of the true
     incident muon flux ratio -- letting the true-flux A1 be backed out of the reported
     MC-truth COUNT (which is NOT cancelled, only the mild aperture-only bias) by
     dividing out the tank-count-only factor. At the reference point this implies a true
     muon flux A1 of about -0.13 -- MORE inverted than the raw count's reported -0.10,
     since the tank's own aperture bias is early-favoring and was partially masking it.
     This yields a falsifiable prediction: an isolated muon-only VEM signal (not
     currently broken out in either GAP note, only total VEM and muon MC-truth count
     are shown) should show a LARGER inversion than the muon count, not a smaller one.
  5. Spectrum-weighted kinematic term: does the pure-kinematic mechanism (2. above),
     properly averaged over a realistic (power-law) muon energy spectrum rather than
     evaluated pointwise, actually produce a net late-favoring effect? NO, over any
     physically bounded energy range (0.05-20 GeV) it remains early-favoring
     (A1 ~ +0.15 to +0.28) for every (D, spectral index) combination tried. It only
     flips sharply negative when integrated out to unphysical energies (tens to
     hundreds of GeV) -- an artifact of the toy exponential ADF growing faster than any
     power-law spectrum falls (rho(E) ~ exp(k E) for large E), not a real physical
     prediction. This retracts a hypothesis floated in conversation (that a high-energy
     tail above E* might explain the true-flux inversion): it does not survive being
     checked. The true physical origin of the SD's inferred true-flux inversion remains
     UNIDENTIFIED by every analytically-tractable mechanism checked in this script.
"""
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad

try:
    import sympy as sp
    _HAVE_SYMPY = True
except ImportError:
    _HAVE_SYMPY = False  # not part of this repo's venv (see CLAUDE.md Sec. 10) -- fall
                          # back to the equivalent hand-derived closed form below rather
                          # than installing an extra package into the shared environment.


# ---------------------------------------------------------------------------
# 0. Symbolic re-derivation of Version_Vieja Eqs. (4)-(9)
# ---------------------------------------------------------------------------
def symbolic_check():
    if _HAVE_SYMPY:
        E, Q, alpha, alpha_e, alpha_l = sp.symbols('E Q alpha alpha_e alpha_l', positive=True)
        pt = E * sp.sin(alpha)
        dN_dpt = pt * sp.exp(-pt / Q)
        dOmega_dpt = sp.sin(alpha) / (E * sp.cos(alpha))
        dN_dOmega = sp.simplify(dN_dpt / dOmega_dpt)
        print("dN/dOmega =", dN_dOmega, "  (matches Version_Vieja's Eq. 8 up to an E^2 prefactor)")

        expfac = sp.exp(E * (sp.sin(alpha_e) - sp.sin(alpha_l)) / Q)
        dfac_dE = sp.simplify(sp.diff(expfac, E))
        print("d/dE[exp((sin ae - sin al) E / Q)] =", dfac_dE)
    else:
        print("(sympy not installed in this venv -- reproducing the hand derivation instead)")
        print("dN/dpt = pt*exp(-pt/Q), pt = E*sin(alpha), dOmega/dpt = sin(alpha)/(E*cos(alpha))")
        print("=> dN/dOmega = dN/dpt / (dOmega/dpt) = E^2 * cos(alpha) * exp(-E sin(alpha)/Q)")
        print("  (matches Version_Vieja's Eq. 8 up to the E^2 prefactor, dropped there)")
        print("d/dE[exp((sin ae - sin al) E / Q)] = ((sin ae - sin al)/Q) * exp((sin ae - sin al) E/Q)")
    print(" -> strictly positive whenever sin(alpha_e) > sin(alpha_l): the exponential")
    print("    'gain' factor is MONOTONICALLY INCREASING in E -- it is small/negligible")
    print("    near E=0 and only matters once E is large. It does not intrinsically")
    print("    favour low-energy (Population B) muons; the paper's own algebra says")
    print("    the opposite of its prose.\n")


# ---------------------------------------------------------------------------
# 1. Unified exact geometry
# ---------------------------------------------------------------------------
# Convention (validated against both GAP notes' own qualitative statements: d_early <
# d_late, theta_loc_early < theta_loc_late): shower core at ground origin; axis unit
# vector from ground upward to the production point is (-sin th, 0, cos th), i.e. the
# production point leans toward the EARLY side (phi=0, x<0). A ground point at
# shower-plane radius r in the early/late direction sits at ground-plane position
# x = -r/cos(th) (early) or x = +r/cos(th) (late) -- the standard 1/cos(theta)
# foreshortening between shower-plane and ground-plane radius along the tilt direction.
def geometry(r, D, theta_deg, phi_deg):
    """Return (d, alpha, theta_loc) for a ground point at shower-plane radius r,
    azimuth phi_deg (0=early, 180=late), production point at distance D along the axis."""
    th = np.radians(theta_deg)
    sign = -1.0 if abs(phi_deg) < 90 else 1.0  # early: -1, late: +1
    x_ground = sign * r / np.cos(th)
    x_prod, z_prod = -D * np.sin(th), D * np.cos(th)

    dx, dz = x_ground - x_prod, 0.0 - z_prod  # vector production -> ground
    d = np.hypot(dx, dz)
    theta_loc = np.arctan2(abs(x_ground - x_prod), z_prod)  # angle from vertical at ground

    # emission angle alpha: angle between (ground - production) and the downward axis
    # direction (sin th, 0, -cos th)
    axis_down = np.array([np.sin(th), 0.0, -np.cos(th)])
    v = np.array([dx, 0.0, dz]) / d
    cos_alpha = np.clip(np.dot(v, axis_down), -1.0, 1.0)
    alpha = np.arccos(cos_alpha)
    return d, alpha, theta_loc


def factors(r, D, theta_deg):
    d_e, ae, tle = geometry(r, D, theta_deg, 0.0)
    d_l, al, tll = geometry(r, D, theta_deg, 180.0)
    spatial = (d_e / d_l) ** 2
    cosfac = np.cos(al) / np.cos(ae)
    return d_e, d_l, ae, al, tle, tll, spatial, cosfac


def ratio(E, r, D, theta_deg, Q):
    d_e, d_l, ae, al, tle, tll, spatial, cosfac = factors(r, D, theta_deg)
    expfac = np.exp((np.sin(ae) - np.sin(al)) * E / Q)
    return spatial * cosfac * expfac


def crossover_energy(r, D, theta_deg, Q):
    return brentq(lambda E: ratio(E, r, D, theta_deg, Q) - 1.0, 0.001, 100)


def A1_from_ratio(late_over_early):
    return (1 - late_over_early) / (1 + late_over_early)


# ---------------------------------------------------------------------------
# 2. Luce et al. (ICRC 2021, #435) Sec. 2.2 cross-check: alpha ~ 2 - gamma + d/lambda
# ---------------------------------------------------------------------------
def luce_gamma_eff(E, r, D, theta_deg, Q):
    """Local log-slope of the exponential ADF at the mean of the early/late emission
    angles: gamma_eff = E * alpha / (c Q), the effective power-law index an exponential
    tail mimics locally. Luce's Eq. (see their Sec. 2.2, alpha ~ 2 - gamma + d/lambda,
    attenuation term d/lambda dropped here to isolate the pure geometric/kinematic part,
    matching what Version_Vieja's Eq. (9) computes)."""
    _, _, ae, al, *_ = factors(r, D, theta_deg)
    alpha_mean = 0.5 * (ae + al)
    gamma_eff = E * alpha_mean / Q
    return 2.0 - gamma_eff  # pure geometric+kinematic term, attenuation excluded


# ---------------------------------------------------------------------------
# 3. Tank vs. flat-plane geometric response, and the UMD's own threshold modulation
# ---------------------------------------------------------------------------
R_TANK, H_TANK = 1.8, 1.2  # Auger WCD radius/height (m); top/side area ratio ~2.36,
                           # matching Bertou & Billoir's quoted 2.4


def tank_response(r, D, theta_deg):
    """A1 of a detector's purely geometric response at a fixed shower-plane radius r,
    for three detector models: flat horizontal plane (count ~ cos(theta_loc), UMD-like),
    WCD tank particle count (~ projected aperture), WCD tank muon VEM (~ mean path
    length in water, i.e. aperture x mean-chord -- by the Cauchy formula this equals
    F_perp * V / A_top exactly, independent of theta_loc)."""
    _, _, _, _, tle, tll, _, _ = factors(r, D, theta_deg)

    flat_e, flat_l = np.cos(tle), np.cos(tll)
    A1_flat = A1_from_ratio(flat_l / flat_e)

    Atop, Aside_proj = np.pi * R_TANK ** 2, 2 * R_TANK * H_TANK
    count_e = Atop * np.cos(tle) + Aside_proj * np.sin(tle)
    count_l = Atop * np.cos(tll) + Aside_proj * np.sin(tll)
    A1_count = A1_from_ratio(count_l / count_e)

    # Cauchy mean-chord: total path length crossed by a parallel beam of unit flux F_perp
    # through a convex body of volume V is F_perp * V, independent of incidence angle.
    # -> VEM signal per unit incident flux is angle-independent -> A1 = 0 exactly.
    A1_VEM = 0.0

    return A1_flat, A1_count, A1_VEM, Atop, Aside_proj, tle, tll


def umd_threshold_A1(r, D, theta_deg, beta):
    """Purely instrumental A1 induced by the UMD's overburden threshold being
    azimuthally modulated through theta_loc: E_thr(theta_loc) = 1 GeV / cos(theta_loc).
    Assuming a power-law muon flux dN/dE ~ E^-beta at the relevant energies (beta in
    [2.0, 3.0] bracketing Cazon's quoted E^-2.6 production spectrum and typical ground
    spectra after propagation losses), N(>E_thr) ~ E_thr^-(beta-1)."""
    _, _, _, _, tle, tll, _, _ = factors(r, D, theta_deg)
    Ethr_e, Ethr_l = 1.0 / np.cos(tle), 1.0 / np.cos(tll)
    Nsurv_e, Nsurv_l = Ethr_e ** -(beta - 1), Ethr_l ** -(beta - 1)
    return A1_from_ratio(Nsurv_l / Nsurv_e), Ethr_e, Ethr_l


# ---------------------------------------------------------------------------
# 4. True-flux inversion implied by factoring the tank's own count-only bias out of
#    the reported MC-truth count (see docstring point 4).
# ---------------------------------------------------------------------------
def implied_true_flux_A1(r, D, theta_deg, reported_count_A1):
    """Given the reported MC-truth tank-boundary COUNT asymmetry (which retains the
    tank's own mild aperture-only geometric bias, NOT cancelled the way VEM is), back
    out what the true incident muon flux ratio must be. count_ratio = flux_ratio *
    aperture_ratio  =>  flux_ratio = count_ratio / aperture_ratio."""
    A1_flat, A1_count, A1_VEM, *_ = tank_response(r, D, theta_deg)
    ratio_count_reported = (1 - reported_count_A1) / (1 + reported_count_A1)
    ratio_aperture = (1 - A1_count) / (1 + A1_count)
    ratio_flux = ratio_count_reported / ratio_aperture
    return A1_from_ratio(ratio_flux), A1_count


# ---------------------------------------------------------------------------
# 5. Spectrum-weighted kinematic term: does the pure-kinematic mechanism survive
#    averaging over a realistic muon energy spectrum, rather than being evaluated at a
#    single point? (prompted directly by the author's review -- see docstring point 5)
# ---------------------------------------------------------------------------
def spectrum_weighted_kinematic_A1(r, D, theta_deg, Q, gamma, E_min, E_max):
    """Number-weighted average of the pure-kinematic ratio(E) over a power-law muon
    spectrum dN/dE ~ E^-gamma on [E_min, E_max]. Assumes the EARLY-region density at
    each E is simply proportional to N(E) (i.e. 'early' is just a directional label for
    otherwise-identical particles, absent the late/early asymmetry itself) so that
    total_late/total_early = <ratio(E)>_{N(E)-weighted} exactly."""
    num = quad(lambda E: E ** (-gamma) * ratio(E, r, D, theta_deg, Q), E_min, E_max, limit=200)[0]
    den = quad(lambda E: E ** (-gamma), E_min, E_max, limit=200)[0]
    rho_avg = num / den
    return A1_from_ratio(rho_avg), rho_avg


def kinematic_growth_rate(r, D, theta_deg, Q):
    """The exponential's asymptotic growth rate k in ratio(E) ~ C * exp(k E) at large E
    (k = (sin ae - sin al)/Q > 0), which is what makes the spectrum-weighted integral
    formally divergent for an unbounded power-law spectrum -- confirming the divergence
    seen numerically above is a real analytic feature of the toy model, not a fluke."""
    _, _, ae, al, *_ = factors(r, D, theta_deg)
    return (np.sin(ae) - np.sin(al)) / Q


# ---------------------------------------------------------------------------
# 6. In-flight atmospheric multiple-Coulomb-scattering hypothesis (v4)
# ---------------------------------------------------------------------------
X0_AIR = 36.62      # g/cm^2, radiation length of air (standard value)
M_MU = 0.10566      # GeV, muon rest mass


def slant_depth(theta_loc_rad, D, theta_deg, X_ground=880.0, alt_ground_km=1.4,
                 H=7.25, X0_sea=1030.0):
    """Vertical atmospheric depth traversed from production altitude to ground
    (isothermal exponential atmosphere, scale height H), converted to slant depth
    along the actual arrival direction theta_loc. Cross-checked against the exact
    geometry's own d_early/d_late ratio in the docstring/notes -- the two agree to ~3%,
    an independent sanity check of this simplified atmosphere model."""
    D_km = D / 1000.0
    alt_prod_km = alt_ground_km + D_km * np.cos(np.radians(theta_deg))
    X_prod = X0_sea * np.exp(-alt_prod_km / H)
    vertical_depth = X_ground - X_prod
    return vertical_depth / np.cos(theta_loc_rad)


def highland_theta0(E_GeV, X_gcm2, X0=X0_AIR):
    """Highland (Gaussian-core) multiple-Coulomb-scattering RMS angle, general to any
    charged particle via its own momentum/velocity (standard PDG-level formula; Grieder
    2010 Eq. 4.34-4.35 gives the same result derived for electrons, but the formula only
    depends on the SCATTERED particle's own p, beta, not its identity)."""
    p = np.sqrt(max(E_GeV ** 2 - M_MU ** 2, 1e-9))
    beta = p / E_GeV
    t = X_gcm2 / X0
    return (0.0136 / (beta * p)) * np.sqrt(t) * (1 + 0.038 * np.log(t))  # radians


def scattering_boost_factor(E_GeV, r, D, theta_deg, Q):
    """Multiplicative boost to the late/early kinematic ratio from the DIFFERENCE in
    scattering width between regions (derived via an exponential-tilt/convolution
    argument on Cazon's locally-exponential angular distribution, k = E/Q):
    boost = exp(k^2 (sigma_late^2 - sigma_early^2) / 2). Verified against a direct
    numerical Gaussian convolution (see kinematic_divergence_math_check.md / this
    session's chat record for the cross-check)."""
    _, _, ae, al, tle, tll, _, _ = factors(r, D, theta_deg)
    X_e = slant_depth(tle, D, theta_deg)
    X_l = slant_depth(tll, D, theta_deg)
    sigma_e = highland_theta0(E_GeV, X_e)
    sigma_l = highland_theta0(E_GeV, X_l)
    k = E_GeV / Q
    boost = np.exp(k ** 2 * (sigma_l ** 2 - sigma_e ** 2) / 2)
    return boost, X_e, X_l, sigma_e, sigma_l


# ---------------------------------------------------------------------------
def main():
    symbolic_check()

    r, theta_deg = 1200.0, 35.0
    print(f"=== 1. Pure-kinematic crossover energy E*, r={r} m, theta={theta_deg} deg ===")
    print("(exact unified geometry; Table 2's disputed far-core reference point)\n")
    for Q in (0.15, 0.20, 0.25, 0.30):
        for D in (5000.0, 7500.0, 10000.0):
            Estar = crossover_energy(r, D, theta_deg, Q)
            print(f"  Q={Q:.2f} GeV, D={D/1000:.1f} km  ->  E* = {Estar:.2f} GeV")
        print()

    theta_rad = np.radians(theta_deg)
    print(f"UMD effective threshold at theta={theta_deg} deg (E_mu >~ 1 GeV/cos theta): "
          f"{1.0/np.cos(theta_rad):.2f} GeV\n")

    print("=== D-scan at Q=0.20 GeV: does E* ever drop into Population B's range? ===")
    for D in (2000.0, 3000.0, 5000.0, 7500.0, 10000.0):
        Estar = crossover_energy(r, D, theta_deg, 0.20)
        print(f"  D={D/1000:5.1f} km  ->  E* = {Estar:.2f} GeV")
    print("  (E* falls below the UMD threshold only for D <~ 2-3 km: the narrative is")
    print("   not falsified for ALL production heights, only unevaluated -- it would")
    print("   require unusually LOW production, anticorrelated with low E, that neither")
    print("   GAP note invokes.)\n")

    print("=== 2. Cross-check against Luce et al. (ICRC 2021) alpha ~ 2 - gamma + d/lambda ===")
    D = 7500.0
    for E in (0.3, 1.0, 1.22, 2.48, 3.0, 5.0):
        g = luce_gamma_eff(E, r, D, theta_deg, 0.20)
        print(f"  E={E:5.2f} GeV -> 2 - gamma_eff = {g:+.3f}  "
              f"({'early-favouring' if g > 0 else 'late-favouring'}, pure geom/kinematic term)")
    print("  (Sign flips near the same E* found in Sec. 1 above -- confirms Version_Vieja's")
    print("   Eq. (9) is a re-derivation of Luce's already-published Sec. 2.2 model.)\n")

    print("=== Sanity check at r=450 m (near-core reference point), Q=0.20 GeV ===")
    for D in (5000.0, 7500.0, 10000.0):
        d_e, d_l, ae, al, tle, tll, spatial, cosfac = factors(450.0, D, theta_deg)
        print(f"D={D/1000:.1f} km: alpha_e={np.degrees(ae):.2f} deg, alpha_l={np.degrees(al):.2f} deg, "
              f"spatial={spatial:.3f}, cosfac={cosfac:.4f}")
        for E in (0.1, 0.3, 1.0, 1.22, 3.0):
            full = ratio(E, 450.0, D, theta_deg, 0.20)
            print(f"    E={E:5.2f} GeV -> S_late/S_early={full:.3f}, implied A1={A1_from_ratio(full):+.3f}")
        print()
    print("(Matches sign and rough magnitude of the observed SD-Muon(MC) A1=+0.05 at r=450 m,"
          " Table 2 of both GAP notes -- the model is not broken, it just tells a different"
          " story than the Sec. 2.2/4.3 prose at r=1200 m.)\n")

    print("=== 3. Tank vs. flat-plane geometric response (GAP-2026-041 Sec. 6, para. 3) ===")
    for (r_, D_) in [(1200.0, 7500.0), (800.0, 7500.0), (450.0, 7500.0)]:
        A1_flat, A1_count, A1_VEM, Atop, Aside, tle, tll = tank_response(r_, D_, theta_deg)
        print(f"r={r_:6.0f} m, D={D_/1000:.1f} km, theta={theta_deg} deg: "
              f"theta_loc(early/late)={np.degrees(tle):.1f}/{np.degrees(tll):.1f} deg")
        print(f"    A1_flat(UMD-like)   = {A1_flat:+.3f}")
        print(f"    A1_tank,count       = {A1_count:+.3f}")
        print(f"    A1_tank,muon-VEM    = {A1_VEM:+.3f}  (exact, Cauchy mean-chord theorem)")
    print(f"\n  Tank Atop/Aside_proj = {np.pi*R_TANK**2/(2*R_TANK*H_TANK):.2f} "
          "(Bertou & Billoir quote 2.4 for the real WCD geometry -- matches)")
    print("  Neither tank response is negative: the tank SUPPRESSES the flat-plane")
    print("  geometric term toward zero (count) or exactly to zero (VEM), it does not")
    print("  reverse its sign. GAP-2026-041 Sec. 6 para. 3's claim that the track-length")
    print("  term 'contributes negatively' is not supported by this calculation.\n")

    print("=== UMD's own instrumental threshold-modulation A1 (neither GAP note subtracts this) ===")
    for beta in (2.0, 2.6, 3.0):
        A1_thr, Ee, El = umd_threshold_A1(r, 7500.0, theta_deg, beta)
        print(f"  beta={beta:.1f}: E_thr(early)={Ee:.2f} GeV, E_thr(late)={El:.2f} GeV "
              f"-> A1_threshold = {A1_thr:+.3f}")
    print("  (Comparable to or larger than the measured UMD A1 ~ +0.11 at this point --")
    print("   the claim that UMD A1 is purely attenuation-driven is not established.)\n")

    print("=== 4. True-flux A1 implied by factoring the tank-count bias out of Table 2's -0.10 ===")
    A1_flux, A1_count_only = implied_true_flux_A1(r, 7500.0, theta_deg, reported_count_A1=-0.10)
    print(f"  tank-count-only geometric bias  = {A1_count_only:+.3f}  (early-favouring, masks the true signal)")
    print(f"  reported SD-Muon(MC) count A1   = -0.100  (Table 2, both GAP notes)")
    print(f"  implied TRUE incident flux A1   = {A1_flux:+.3f}")
    print("  Prediction: an isolated muon-only VEM signal should show a LARGER inversion")
    print("  than the muon count, not a smaller one -- directly testable in the existing MC.\n")

    print("=== 5. Spectrum-weighted kinematic term: does it survive averaging over a real spectrum? ===")
    k = kinematic_growth_rate(r, 7500.0, theta_deg, 0.20)
    print(f"  asymptotic growth rate k = {k:.4f} /GeV  (ratio(E) ~ exp(k E) at large E --")
    print(f"  beats ANY power-law spectrum eventually: the integral below is genuinely")
    print(f"  divergent for an unbounded spectrum, not just numerically awkward)\n")
    for D in (5000.0, 7500.0, 10000.0):
        print(f"  -- D = {D/1000:.1f} km --")
        for gamma in (2.0, 2.6, 3.0):
            for Emax in (5.0, 20.0, 100.0):
                A1s, rho_avg = spectrum_weighted_kinematic_A1(r, D, theta_deg, 0.20, gamma, 0.05, Emax)
                print(f"     gamma={gamma:.1f}  E in [0.05,{Emax:5.1f}] GeV  ->  <rho>={rho_avg:8.3g}  A1={A1s:+.3f}")
        print()
    print("  Over any physically bounded range (<= 20 GeV) the spectrum-weighted term stays")
    print("  EARLY-favouring for every (D, gamma) tried -- it only flips at unphysical")
    print("  energies, where the exponential's unbounded growth (see k above) overwhelms")
    print("  the power-law falloff. This retracts the hypothesis that a high-energy tail")
    print("  above E* explains the true-flux inversion in point 4 above: it does not survive")
    print("  spectrum-weighting. The true origin of that inversion is NOT identified by any")
    print("  mechanism checked in this script.\n")

    print("=== 6. In-flight atmospheric scattering: does it supply the missing boost? ===")
    D6 = 7500.0
    _, _, ae6, al6, tle6, tll6, _, _ = factors(r, D6, theta_deg)
    X_e6 = slant_depth(tle6, D6, theta_deg)
    X_l6 = slant_depth(tll6, D6, theta_deg)
    print(f"  theta_loc: early={np.degrees(tle6):.1f} deg, late={np.degrees(tll6):.1f} deg")
    print(f"  production-kinematic alpha: early={np.degrees(ae6):.2f} deg, late={np.degrees(al6):.2f} deg")
    print(f"  slant depth traversed: early={X_e6:.0f} g/cm2, late={X_l6:.0f} g/cm2, "
          f"ratio={X_l6/X_e6:.3f}\n")
    print(f"  {'E_mu (GeV)':>10} {'sigma_e (deg)':>14} {'sigma_l (deg)':>14} {'boost factor':>14}")
    for E in (0.3, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0):
        boost, Xe, Xl, se, sl = scattering_boost_factor(E, r, D6, theta_deg, 0.20)
        print(f"  {E:10.1f} {np.degrees(se):14.2f} {np.degrees(sl):14.2f} {boost:14.4f}")
    print("\n  Boost factors are ~1.01-1.02 across the whole relevant energy range -- an")
    print("  order of magnitude too small to turn the pure-kinematic term's early-favouring")
    print("  prediction into the implied ~-0.13 true-flux inversion (point 4) on its own.")
    print("  This is the Gaussian-CORE (Highland RMS) estimate only -- it does not capture")
    print("  the non-Gaussian wide-angle Moliere tail (Grieder 2010, Sec. 3.1: 'narrow-angle")
    print("  multiple scattering accounts for the bulk of the [deflections]', implying a")
    print("  separate, rarer wide-angle population exists) which could still matter, given")
    print("  this investigation has twice already found rare high-leverage tails break naive")
    print("  bulk/RMS estimates (see point 5). Untested here -- the direct, cheap check is")
    print("  empirical: compare each muon's actual simulated ground-arrival direction to")
    print("  Cazon's production-kinematics-only prediction in the existing MC.")


if __name__ == "__main__":
    main()
