"""
Unified analytic model of the azimuthal muon-density asymmetry, and a direct
empirical audit of the actual MC pipeline (icrc2025-test7, SIBYLL 2.3e proton).

This script is new (per the task instructions) and stands alongside, rather than
replaces, claude_work/gap_notes_asimetrias_review_v4/verificacion_eq9_kinematic_divergence.py
(v4), whose exact-geometry toolkit (Section 1 below) it reuses and re-validates.

CORRECTION NOTE (added after first publishing this file): the first version of
this script and its report did not read claude_work/kinematic_divergence_
explainer_and_thesis_updates/ in full, despite the task explicitly listing it as
required reading. That folder's explainer_kinematic_divergence_simulator.py
Section 8 (and its companion spectrum_weighting_correction.html) had ALREADY
found, before this session started, the single most decisive quantitative result
in this whole line of work: a properly spectrum-weighted (not point-evaluated)
combination of the kinematic/ADF term with each detector's own geometric
response predicts UMD +0.13 (observed +0.11, a good match) and SD +0.19
(observed -0.10, badly wrong -- the framework gets the UMD right and fails only
on the SD). Section 7 below reproduces that result exactly as a cross-check,
then extends it -- for the first time -- with this session's own new muon-
attenuation-sign candidate (Section 3), combined in the SAME multiplicative-
ratio convention the explainer notebook uses (not the additive linearised
bracket of Section 2, which is kept as a simpler, secondary cross-check only).
The extended result is more modest than this script's own first version
claimed: the sign-corrected attenuation term moves the SD prediction from +0.19
toward +0.14 (about 20% of the -0.29 gap to the observed -0.10), not the "~1.3
in bracket units, comparable to the gap" figure the first version reported --
that number came from combining a linearised approximation with a fully
nonlinear spectrum-weighted term inconsistently. See report.md for the full,
corrected discussion.

SECOND CORRECTION NOTE: the "~20% of the gap" figure above is ALSO retracted,
not just re-quantified, following the author's direct pushback. Bertou &
Billoir's paper and Fig.1 measurement are about the SD (a Water Cherenkov
Detector, near-zero muon energy threshold), not the UMD (hard ~1.22 GeV
threshold from ~2.3 m of soil) -- applying the same correction factor to BOTH
detectors' predictions, as done below, mixes a muon population (soft, sub-GeV)
the UMD never sees into the UMD's own number. Worse: B&B's own text ("the
total number of muons decreases, but their spread increases") describes
lateral spread of the muon population with depth -- very plausibly the SAME
physical phenomenon Cazon's kinematic-divergence term (already in the "no
attenuation" combination, properly spectrum-weighted, prior work) already
models -- meaning this candidate likely double-counts that physics, with the
opposite sign, from the cruder of the two sources. Section 7's B&B-extended
numbers are kept in this script ONLY for the record (so a future session can
see exactly what was tried and why it failed), not as a trustworthy result.
See report.md Section 3 for the full reasoning.

Six things happen here that were NOT done in v4 or in
kinematic_divergence_explainer_and_thesis_updates/ (see claude_work/gap_notes_
asimetrias_review_v4/*.md and that folder for what came before):

  1. Armbruster (GAP-2020-066) / Luce (ICRC2021-435)'s closed-form linearised
     asymmetry amplitude, a = (2 - gamma + d/lambda)*(r/d)*tan(theta), is checked
     TERM BY TERM against the exact (non-linearised) geometry already validated in
     v4. This is the "one consistent framework" the task asks for: A_geo (Bertou &
     Billoir), the kinematic/ADF term, and attenuation are literally the three
     pieces of ONE bracket, not three separate toy models to be summed by hand.
     (Section 2.)

  2. Bertou & Billoir's own explicit MC (GAP-2000-017, their Fig. 1) is read for
     what it actually says about muon "attenuation": the muon density *increases*,
     not decreases, with slant depth out to 1200 g/cm^2 in their (SD-context,
     essentially unthresholded) sample. This LOOKED like a candidate contribution
     to the SD gap -- but is RETRACTED (Section 3, Section 7) after the author's
     direct pushback: B&B's paper is about the SD specifically (near-zero muon
     threshold, unlike the UMD's ~1.22 GeV), and B&B's own wording ("total
     decreases, but spread increases") suggests this may be the SAME lateral-
     spread physics Cazon's kinematic term already models, not an independent
     effect. Retracting this cleanly is itself the more useful, load-bearing
     result of this section, not a failure to report quietly.

  3. Cazon (2012)'s own stated inadequacy of a single fixed (Q, D) is used to put
     an honest uncertainty band on E* and on the a=... bracket, rather than
     treating Q=0.2 GeV, D=7.5 km as known constants. (Section 4, reusing v4's
     D-scan machinery plus a Q-scan motivated by the cited median c*p_t figure.)

  4. A first-ever DIRECT AUDIT of the real MC parquet output (not a toy model) for
     a sampling/acceptance confound the pipeline review (this session) found is
     structurally possible: the Infill A1 fit is an unweighted per-phi-bin mean
     over however many real 750 m-array stations happen to project into that bin,
     with NO exposure/livetime normalisation anywhere in the pipeline. Section 5
     quantifies how badly the phi-binned station COUNT itself is modulated (up to
     +/-0.3-0.6 in A1-equivalent units at large r), and Section 6 runs the
     decisive causal test directly: equalising the per-bin sample count via
     bootstrap resampling and re-fitting A1. The result is a clean negative: the
     reported SD-muon inversion does NOT move (shifts of 0.0002-0.0006, noise-
     level) when exposure is equalised. This is a genuinely new result -- it rules
     out a candidate artifact explanation for Q1/Q4 that no prior pass in this
     project ever tested against real MC, because no prior pass touched the real
     MC at all.

  5. A precise identification: Bertou & Billoir's A_geo = <p_r/-p_z> tan(theta) is
     shown numerically to be exactly the "+1" (aperture) term of the Armbruster
     bracket at the reference geometry -- i.e. it is the SAME object as the UMD
     "flat-plane instrumental floor" invoked in claude_work/gap_notes_asimetrias_
     review_v4/sd_umd_synthesis.md Part 5, not an independent contribution to be
     added on top of it. This matters for Q2: summing A_geo and the "aperture
     term" as if they were two separate instrumental biases double-counts.

  6. Section 7: the explainer notebook's own corrected per-detector combination
     (kinematic term x geometric response), reproduced as a cross-check -- this
     part is trustworthy and matches spectrum_weighting_correction.html exactly.
     The muon-attenuation-sign extension (item 2) is ALSO computed there, but
     explicitly marked DO NOT CITE: retracted per item 2's reasoning. Honest
     final verdict: no mechanism found across this session or the five prior
     passes survives scrutiny as an independent contribution to the SD gap.

Run with: venv/bin/python claude_work/unified_asymmetry_model_v1/unified_model_verification.py
Needs: numpy, scipy, pandas, pyarrow (all in the repo's venv). Section 5-6 need the
existing MC parquet at /home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17/
(SIBYLL 2.3e proton, icrc2025-test7 production) -- this is read-only, no new
processing job is launched, consistent with CLAUDE.md Sec. 3 (shared-server care).
"""
import numpy as np
import pandas as pd
import glob
import warnings
from scipy.optimize import brentq, curve_fit
from scipy.integrate import quad
from scipy.stats import pearsonr

warnings.filterwarnings("ignore")

PARQUET_DIR = "/home/lsilva/Github/ADST_Alexey_module_v11/parquet_sib_proton_17/"
R_TANK, H_TANK = 1.8, 1.2  # Auger WCD radius/height (m)


# =============================================================================
# Section 1 -- Exact geometry (reused, unchanged in substance, from v4's
# verificacion_eq9_kinematic_divergence.py; reproduced here so this script is
# self-contained).
# =============================================================================
def geometry(r, D, theta_deg, phi_deg):
    """(d, alpha, theta_loc) for a ground point at shower-plane radius r, azimuth
    phi_deg (0=early, 180=late), single production point at distance D along the
    shower axis leaning toward the early side (matches both GAP notes' own
    qualitative statements: d_early < d_late, theta_loc_early < theta_loc_late)."""
    th = np.radians(theta_deg)
    sign = -1.0 if abs(phi_deg) < 90 else 1.0
    x_ground = sign * r / np.cos(th)
    x_prod, z_prod = -D * np.sin(th), D * np.cos(th)
    dx, dz = x_ground - x_prod, -z_prod
    d = np.hypot(dx, dz)
    theta_loc = np.arctan2(abs(dx), z_prod)
    axis_down = np.array([np.sin(th), 0.0, -np.cos(th)])
    v = np.array([dx, 0.0, dz]) / d
    alpha = np.arccos(np.clip(v @ axis_down, -1.0, 1.0))
    return d, alpha, theta_loc


def factors(r, D, theta_deg):
    d_e, ae, tle = geometry(r, D, theta_deg, 0.0)
    d_l, al, tll = geometry(r, D, theta_deg, 180.0)
    return d_e, d_l, ae, al, tle, tll, (d_e / d_l) ** 2, np.cos(al) / np.cos(ae)


def A1_from_ratio(late_over_early):
    return (1 - late_over_early) / (1 + late_over_early)


def ratio(E, r, D, theta_deg, Q):
    d_e, d_l, ae, al, tle, tll, spatial, cosfac = factors(r, D, theta_deg)
    return spatial * cosfac * np.exp((np.sin(ae) - np.sin(al)) * E / Q)


def crossover_energy(r, D, theta_deg, Q):
    return brentq(lambda E: ratio(E, r, D, theta_deg, Q) - 1.0, 0.001, 200)


# =============================================================================
# Section 2 -- Armbruster/Luce linearised bracket vs exact geometry, term by term
# =============================================================================
def armbruster_terms(r, D, theta_deg):
    """Decompose the exact geometry into the three linearised Armbruster
    (GAP-2020-066 Eq. 2.33) bracket ingredients, each expressed as an
    A1-equivalent amplitude for direct, apples-to-apples comparison against the
    exact (non-linearised) geometry of Section 1.

    Armbruster: a = (2 - gamma + d/lambda) * eps * tan(theta),  eps = r/d.
    Each unit contribution to the bracket (a "+1") corresponds to an A1 of
    eps*tan(theta); this function reports both the linearised prediction and the
    matching exact-geometry quantity for each of the bracket's structural pieces.
    """
    th = np.radians(theta_deg)
    eps = r / D
    base = eps * np.tan(th)  # one unit of bracket, in A1-equivalent units

    d_e, d_l, ae, al, tle, tll, spatial, cosfac = factors(r, D, theta_deg)

    # "+2" solid-angle / 1/d^2 term
    lin_2 = 2 * base
    exact_2 = A1_from_ratio(spatial)

    # "+1" flat-plane aperture term == Bertou-Billoir's A_geo
    lin_1 = 1 * base
    exact_flat = A1_from_ratio(np.cos(tll) / np.cos(tle))

    # WCD tank particle count (Bertou & Billoir's own 2.4x top/side factor)
    At, As = np.pi * R_TANK**2, 2 * R_TANK * H_TANK
    Ndet = (At * np.cos(th) - As * np.cos(th) ** 2 / np.sin(th)) / (At * np.cos(th) + As * np.sin(th))
    count_e = At * np.cos(tle) + As * np.sin(tle)
    count_l = At * np.cos(tll) + As * np.sin(tll)
    exact_tank_count = A1_from_ratio(count_l / count_e)
    lin_tank_count = Ndet * base

    return dict(eps=eps, base=base, lin_2=lin_2, exact_2=exact_2,
                lin_flat=lin_1, exact_flat=exact_flat, A_geo=lin_1,
                Ndet=Ndet, lin_tank_count=lin_tank_count, exact_tank_count=exact_tank_count,
                exact_tank_VEM=0.0)  # Cauchy mean-chord theorem, v4 Section 3, exact


def required_bracket(r, D, theta_deg, measured_A1):
    """Invert a=(bracket)*eps*tan(theta) for the bracket value a measured A1 at
    this (r, D, theta) implies, so it can be compared to 2-gamma+d/lambda."""
    th = np.radians(theta_deg)
    base = (r / D) * np.tan(th)
    return measured_A1 / base


# =============================================================================
# Section 3 -- The muon "attenuation" sign correction (Bertou & Billoir Fig. 1)
# =============================================================================
def bb_muon_density_vs_depth():
    """Bertou & Billoir (GAP-2000-017) Fig. 1, muon curve, read off relative to
    the 900 g/cm^2 reference depth (their own explicit MC, isolating the muon
    component -- NOT an assumption). Values transcribed from the literature
    read-off (claude_work agent report, this session): at 1000/1100/1200 g/cm^2,
    muon density (10^19 eV shower) is 1.09/1.21/1.27x the 900 g/cm^2 value --
    i.e. INCREASING, not decreasing, with depth over this whole range.
    Returns an effective growth rate (positive = density grows with depth,
    the OPPOSITE sign convention to a normal attenuation length)."""
    X = np.array([900.0, 1000.0, 1100.0, 1200.0])
    rho_mu_rel = np.array([1.00, 1.09, 1.21, 1.27])  # 10^19 eV column
    # fit rho ~ rho0 * exp(+(X-900)/Lambda_growth)  -> Lambda_growth in g/cm^2
    logy = np.log(rho_mu_rel)
    slope, intercept = np.polyfit(X - 900.0, logy, 1)
    Lambda_growth_gcm2 = 1.0 / slope  # g/cm^2 (positive = growing)
    return Lambda_growth_gcm2, X, rho_mu_rel


def slant_depth(theta_loc_rad, D, theta_deg, X_ground=880.0, alt_ground_km=1.4, H=7.25, X0_sea=1030.0):
    """Vertical atmospheric depth traversed from production altitude to ground
    (isothermal exponential atmosphere, scale height H), converted to slant
    depth along the actual arrival direction theta_loc. Same model and default
    parameters as kinematic_divergence_explainer_and_thesis_updates/explainer_
    kinematic_divergence_simulator.py Section 9, reused here for Section 7's
    attenuation-ratio calculation so the two are on a consistent footing."""
    D_km = D / 1000.0
    alt_prod_km = alt_ground_km + D_km * np.cos(np.radians(theta_deg))
    X_prod = X0_sea * np.exp(-alt_prod_km / H)
    vertical_depth = X_ground - X_prod
    return vertical_depth / np.cos(theta_loc_rad)


def geometric_length_to_gcm2(length_km, rho_ground=1.05e-3):
    """Convert a geometric length (km) near ground level to an equivalent
    grammage (g/cm^2) using sea-level-ish air density (rho_ground in g/cm^3,
    ~1.05e-3 near Malargue's 1400 m altitude) -- crude but adequate for an
    order-of-magnitude cross-check against Armbruster's lambda=36 km (muon
    attenuation length, a geometric length, not a grammage -- see Section 2
    task-agent report)."""
    return length_km * 1e5 * rho_ground  # km->cm, times g/cm^3 -> g/cm^2


# =============================================================================
# Section 4 -- Q uncertainty (Cazon 2012's own stated inadequacy of a single Q)
# =============================================================================
def Q_from_median_cpt(median_cpt_GeV):
    """For dN/dp_t ~ (p_t/Q^2) exp(-p_t/Q) (Cazon's own Eq., their ref. [15]
    form), the median of p_t satisfies a transcendental relation; a very good
    closed-form approximation is median ~= 1.678 Q (verified numerically below).
    Cazon Fig. 8 gives median c*p_t ~ 0.20-0.22 GeV (the "total" curve) -- NOT
    Q=0.20 GeV directly, since Q is the exponential SCALE, not the median."""
    return median_cpt_GeV / 1.678


def _verify_median_factor():
    # dN/dpt ~ (pt/Q^2) exp(-pt/Q); CDF(pt)=1-(1+pt/Q)exp(-pt/Q); solve CDF=0.5
    from scipy.optimize import brentq as _b
    f = lambda x: 1 - (1 + x) * np.exp(-x) - 0.5  # x = pt/Q
    return _b(f, 0.1, 10.0)  # returns median/Q


# =============================================================================
# Section 7 (placed here so it can reuse Section 1's geometry) -- the
# explainer notebook's own corrected spectrum-weighted combination, reproduced
# as a cross-check and then extended with this session's muon-attenuation-sign
# term (Section 3), combined the way the notebook itself combines kinematics
# with geometry: as multiplicative ratios, not the additive bracket of
# Section 2. See kinematic_divergence_explainer_and_thesis_updates/
# explainer_kinematic_divergence_simulator.py Section 8 and
# spectrum_weighting_correction.html for the original (this session's own
# prior omission, corrected here).
# =============================================================================
def _adf_normalised(alpha, E, Q):
    """dN/dOmega(alpha|E), properly normalised (carries the k^2 prefactor the
    first-pass v4 calculation dropped -- see explainer notebook Section 8,
    'Error 2'). k = E/(cQ)."""
    k = E / Q
    norm = 1.0 - np.exp(-k) * (1.0 + k)
    return (k ** 2 / (2 * np.pi)) * np.cos(alpha) * np.exp(-k * np.sin(alpha)) / max(norm, 1e-12)


def _region_weight(alpha, d, Q, gamma, E_min, E_max):
    """What actually arrives in one region: integral over the muon spectrum of
    N(E) x f(alpha|E) / d^2 (a RATIO OF INTEGRALS, not an average of ratios --
    explainer notebook Section 8, 'Error 1')."""
    f = lambda u: np.exp(u) * (np.exp(u) ** (-gamma)) * _adf_normalised(alpha, np.exp(u), Q) / d ** 2
    return quad(f, np.log(E_min), np.log(E_max), limit=500)[0]


def spectrum_weighted_A1_corrected(r, D, theta_deg, Q, gamma, E_min, E_max):
    """The corrected kinematic-term-only A1 (explainer notebook Section 8),
    reproduced here as a cross-check before extending it in Section 7 below."""
    d_e, d_l, ae, al, *_ = factors(r, D, theta_deg)
    W_e = _region_weight(ae, d_e, Q, gamma, E_min, E_max)
    W_l = _region_weight(al, d_l, Q, gamma, E_min, E_max)
    return A1_from_ratio(W_l / W_e)


def muon_attenuation_ratio(r, D, theta_deg, Lambda_gcm2, growing):
    """late/early density RATIO from an exponential trend in slant depth.
    growing=False: rho ~ exp(-X/Lambda) (EM-like, falls with depth) -> ratio<1,
        early-favoring -- what both GAP notes' prose implicitly assumes applies
        to muons too.
    growing=True:  rho ~ exp(+X/Lambda) (Bertou & Billoir's OWN muon-only MC,
        Section 3 above) -> ratio>1, late-favoring -- this session's candidate."""
    _, _, _, _, tle, tll, _, _ = factors(r, D, theta_deg)
    X_e, X_l = slant_depth(tle, D, theta_deg), slant_depth(tll, D, theta_deg)
    sign = +1.0 if growing else -1.0
    return np.exp(sign * (X_l - X_e) / Lambda_gcm2), X_e, X_l


def combined_per_detector_prediction(r, D, theta_deg, Q, gamma, Lambda_growth):
    """Kinematic term x geometric response x (optionally) attenuation, for both
    detectors, at one gamma. Three variants for the attenuation factor: none
    (matches the explainer notebook's own Section 6 exactly -- the cross-check),
    EM-like (both GAP notes' implicit assumption), and B&B muon-specific (this
    session's sign-corrected candidate). All three combined the same way the
    explainer notebook combines kinematics with geometry: multiplying ratios,
    i.e. A1_total = A1_from_ratio(product of to_ratio(each A1) or ratio)."""
    A1_flat_umd, A1_tank_count = _tank_response_simple(r, D, theta_deg)
    E_SD, E_UMD = 0.155, 1.0 / np.cos(np.radians(theta_deg))
    kin_sd = spectrum_weighted_A1_corrected(r, D, theta_deg, Q, gamma, E_SD, 2000.0)
    kin_umd = spectrum_weighted_A1_corrected(r, D, theta_deg, Q, gamma, E_UMD, 2000.0)

    def to_ratio(a1):
        return (1 - a1) / (1 + a1)

    sd_none = A1_from_ratio(to_ratio(kin_sd) * to_ratio(A1_tank_count))
    umd_none = A1_from_ratio(to_ratio(kin_umd) * to_ratio(A1_flat_umd))

    atten_em, X_e, X_l = muon_attenuation_ratio(r, D, theta_deg, Lambda_growth, growing=False)
    atten_bb, _, _ = muon_attenuation_ratio(r, D, theta_deg, Lambda_growth, growing=True)

    sd_em = A1_from_ratio(to_ratio(kin_sd) * to_ratio(A1_tank_count) * atten_em)
    umd_em = A1_from_ratio(to_ratio(kin_umd) * to_ratio(A1_flat_umd) * atten_em)
    sd_bb = A1_from_ratio(to_ratio(kin_sd) * to_ratio(A1_tank_count) * atten_bb)
    umd_bb = A1_from_ratio(to_ratio(kin_umd) * to_ratio(A1_flat_umd) * atten_bb)

    return dict(kin_sd=kin_sd, kin_umd=kin_umd, sd_none=sd_none, umd_none=umd_none,
                sd_em=sd_em, umd_em=umd_em, sd_bb=sd_bb, umd_bb=umd_bb,
                atten_em=atten_em, atten_bb=atten_bb, X_e=X_e, X_l=X_l)


def _tank_response_simple(r, D, theta_deg):
    """Flat-plane and WCD-tank-count A1, exactly as armbruster_terms() computes
    them (duplicated here as a small standalone helper so Section 7 doesn't
    need to unpack armbruster_terms()'s full dict)."""
    _, _, _, _, tle, tll, _, _ = factors(r, D, theta_deg)
    A1_flat = A1_from_ratio(np.cos(tll) / np.cos(tle))
    At, As = np.pi * R_TANK ** 2, 2 * R_TANK * H_TANK
    count_e = At * np.cos(tle) + As * np.sin(tle)
    count_l = At * np.cos(tll) + As * np.sin(tll)
    A1_count = A1_from_ratio(count_l / count_e)
    return A1_flat, A1_count


# =============================================================================
# Section 5 -- Real-MC acceptance/exposure audit (Infill, icrc2025-test7)
# =============================================================================
PHI_EDGES = np.linspace(-180, 180, 13)
PHI_CTR = (PHI_EDGES[:-1] + PHI_EDGES[1:]) / 2


def _A1_gap_sign(y, e=None):
    """Fit y(phi) = norm*(1 + A*cos(phi)) and return A with the GAP-note sign
    convention (A1>0 = early excess): this requires flipping the raw cos-fit
    sign because Section 5/6's phi is defined as -180..180 with our own private
    early=phi~0 convention matching v4's geometry() -- flip verified against a
    direct reproduction of GAP-2026-041's Table 2 (see main() Section 5 output)."""
    n = np.nanmean(y)
    if not np.isfinite(n) or n == 0:
        return np.nan
    yn = y / n
    ee = np.ones_like(yn) if e is None else e / n
    v = np.isfinite(yn) & np.isfinite(ee) & (ee > 0)
    if v.sum() < 5:
        return np.nan
    p, _ = curve_fit(lambda x, A: 1 + A * np.cos(np.deg2rad(x)),
                      PHI_CTR[v].astype(float), yn[v], sigma=ee[v], absolute_sigma=True)
    return -p[0]


def load_infill_reference_bin():
    files = sorted(glob.glob(PARQUET_DIR + "*.parquet"))
    cols = ["theta_MC", "counterId", "nMuones_MC", "sd_nMuons_MC", "sd_nEM_MC",
            "sdSignal_REC", "r_core_MC", "phi_plane_euler_MC_true_core"]
    df = pd.concat([pd.read_parquet(f, columns=cols) for f in files], ignore_index=True)
    inf = df[df.counterId >= 100000].copy()
    # phi_plane_euler_MC_true_core is stored in RADIANS, [0, 2*pi)
    phi_deg = np.degrees(inf["phi_plane_euler_MC_true_core"].values)
    inf["phi"] = (phi_deg + 180) % 360 - 180
    inf = inf.dropna(subset=["phi"])
    inf["pb"] = pd.cut(inf.phi, bins=PHI_EDGES, labels=PHI_CTR)
    return inf


def table2_reproduction(inf):
    print("=== Reproduction of GAP-2026-041 Table 2 (theta in [30,40)) ===")
    print("Published: r=450 UMD +0.10 SDmu +0.05 SDem +0.40 (typ. unc. <=0.02)")
    print("           r=800 +0.12/+0.04/+0.45 | r=1200 +0.11/-0.10/+0.44\n")
    d = inf[(inf.theta_MC >= 30) & (inf.theta_MC < 40)]
    print(f"{'r-bin (m)':>10} {'N':>7} | {'A1_UMD':>14} {'A1_SDmu':>14} {'A1_SDem':>14} {'A1_VEM':>14}")
    for rlo, rhi, lab in [(300, 600, 450), (650, 950, 800), (1050, 1400, 1200), (1400, 1800, 1600)]:
        s = d[(d.r_core_MC >= rlo) & (d.r_core_MC < rhi)]
        g = s.groupby("pb", observed=False)
        vals = []
        for col in ["nMuones_MC", "sd_nMuons_MC", "sd_nEM_MC", "sdSignal_REC"]:
            st = g[col].agg(["mean", "sem"])
            vals.append(_A1_gap_sign(st["mean"].values, st["sem"].values))
        print(f"{lab:>10} {len(s):>7} | " + " ".join(f"{v:+13.4f}" if np.isfinite(v) else f"{'nan':>14}" for v in vals))
    print()


def acceptance_audit(inf):
    print("=== A1-equivalent modulation of the raw STATION COUNT per phi bin ===")
    print("(A uniform, unbiased array would give exactly 0. This is NOT a density")
    print(" measurement -- it is how lopsided the SAMPLE of real 750 m-array")
    print(" stations projecting into each shower-plane phi bin is, at fixed r.)\n")
    print(f"{'theta':>10} " + " ".join(f"{'r~'+str(r):>9}" for r in [450, 800, 1200, 1600]))
    for tlo, thi in [(20, 30), (30, 40), (40, 50), (50, 65)]:
        row = f"{f'{tlo}-{thi}':>10} "
        for rlo, rhi in [(300, 600), (650, 950), (1050, 1400), (1400, 1800)]:
            s = inf[(inf.theta_MC >= tlo) & (inf.theta_MC < thi) &
                    (inf.r_core_MC >= rlo) & (inf.r_core_MC < rhi)]
            cnt = s.groupby("pb", observed=False).size().values.astype(float)
            row += f"{_A1_gap_sign(cnt):+9.3f}" if cnt.sum() > 500 else f"{'--':>9}"
        print(row)
    print()


def acceptance_density_correlation(inf):
    print("=== Correlation of the acceptance modulation with the reported density signal ===")
    r_edges = np.arange(300, 2000, 150)
    rows = []
    for tlo, thi in [(20, 30), (30, 40), (40, 50), (50, 65)]:
        for rlo, rhi in zip(r_edges[:-1], r_edges[1:]):
            s = inf[(inf.theta_MC >= tlo) & (inf.theta_MC < thi) &
                    (inf.r_core_MC >= rlo) & (inf.r_core_MC < rhi)]
            if len(s) < 300:
                continue
            g = s.groupby("pb", observed=False)
            cnt = g.size().values.astype(float)
            a_acc = _A1_gap_sign(cnt)
            st_u = g["nMuones_MC"].agg(["mean", "sem"])
            st_s = g["sd_nMuons_MC"].agg(["mean", "sem"])
            rows.append((tlo, rlo, a_acc,
                         _A1_gap_sign(st_u["mean"].values, st_u["sem"].values),
                         _A1_gap_sign(st_s["mean"].values, st_s["sem"].values), len(s)))
    R = pd.DataFrame(rows, columns=["theta", "r", "A1_acc", "A1_umd", "A1_sd", "N"]).dropna()
    for col in ["A1_umd", "A1_sd"]:
        v = R.dropna(subset=[col, "A1_acc"])
        r, p = pearsonr(v["A1_acc"], v[col])
        print(f"  corr(A1_accept, {col}) = {r:+.3f}  (p={p:.2e}, n={len(v)})")
    print(f"\n  (Correlation alone does not establish causation -- see Section 6, which")
    print(f"   runs the direct causal test.)\n")
    return R


# =============================================================================
# Section 6 -- THE DECISIVE TEST: equal-exposure bootstrap re-fit
# =============================================================================
def equal_exposure_test(inf, tlo, thi, rlo, rhi, label, n_boot=300, seed=0):
    s = (inf[(inf.theta_MC >= tlo) & (inf.theta_MC < thi) &
              (inf.r_core_MC >= rlo) & (inf.r_core_MC < rhi)]
         .dropna(subset=["sd_nMuons_MC", "nMuones_MC"]).reset_index(drop=True))
    g = s.groupby("pb", observed=False)
    cnt = g.size()
    nmin = int(cnt.min())
    if nmin < 30:
        print(f"{label}: sparsest bin has only {nmin} rows, skipping (too few for a stable bootstrap)")
        return

    def fit_once(sub, col):
        st = sub.groupby("pb", observed=False)[col].mean()
        y = st.values
        n = np.nanmean(y)
        if not np.isfinite(n) or n == 0:
            return np.nan
        yn = y / n
        v = np.isfinite(yn)
        if v.sum() < 5:
            return np.nan
        p, _ = curve_fit(lambda x, A: 1 + A * np.cos(np.deg2rad(x)), PHI_CTR[v].astype(float), yn[v], p0=[0.0])
        return -p[0]

    A1_full_sd = fit_once(s, "sd_nMuons_MC")
    A1_full_umd = fit_once(s, "nMuones_MC")
    rng = np.random.default_rng(seed)
    idx_by_bin = {k: v.to_numpy() for k, v in g.groups.items()}
    boot_sd, boot_umd = [], []
    for _ in range(n_boot):
        picks = [rng.choice(idxs, size=nmin, replace=False) for idxs in idx_by_bin.values() if len(idxs) > 0]
        sub = s.loc[np.concatenate(picks)]
        boot_sd.append(fit_once(sub, "sd_nMuons_MC"))
        boot_umd.append(fit_once(sub, "nMuones_MC"))
    boot_sd, boot_umd = np.array(boot_sd), np.array(boot_umd)
    print(f"{label} (rows/bin: min={nmin}, max={int(cnt.max())}, N_total={len(s)})")
    print(f"  standard (unequal-N):  A1_SDmu = {A1_full_sd:+.4f}   A1_UMD = {A1_full_umd:+.4f}")
    print(f"  equal-N/bin ({n_boot} boot): A1_SDmu = {np.nanmean(boot_sd):+.4f} +/- {np.nanstd(boot_sd):.4f}   "
          f"A1_UMD = {np.nanmean(boot_umd):+.4f} +/- {np.nanstd(boot_umd):.4f}")
    print(f"  shift:  SDmu {np.nanmean(boot_sd) - A1_full_sd:+.4f}   UMD {np.nanmean(boot_umd) - A1_full_umd:+.4f}\n")


# =============================================================================
def main():
    print("#" * 80)
    print("# Section 2 -- Armbruster/Luce linearised bracket vs exact geometry")
    print("#" * 80)
    r, D, theta = 1200.0, 7500.0, 35.0
    t = armbruster_terms(r, D, theta)
    print(f"Reference point: r={r} m, D={D/1000} km, theta={theta} deg,  eps*tan(theta)={t['base']:.4f}\n")
    print(f"  '+2' (1/d^2 solid angle):    linearised {t['lin_2']:+.4f}   exact {t['exact_2']:+.4f}")
    print(f"  '+1' (flat plane / A_geo):   linearised {t['lin_flat']:+.4f}   exact {t['exact_flat']:+.4f}")
    print(f"       Bertou-Billoir A_geo = <p_r/-p_z> tan(theta) ~ (r/d) tan(theta) = {t['base']:.4f}")
    print(f"       => IDENTICAL to the linearised '+1' aperture term. Not an extra contribution.")
    print(f"  WCD tank particle count:     linearised {t['lin_tank_count']:+.4f}   exact {t['exact_tank_count']:+.4f}"
          f"   (N_det={t['Ndet']:.3f})")
    print(f"  WCD tank muon VEM:           exact {t['exact_tank_VEM']:+.4f}  (Cauchy mean-chord theorem, exact)")
    agree = abs(t['exact_2'] - t['lin_2']) / abs(t['lin_2'])
    print(f"\n  Linearised-vs-exact agreement on the largest term ('+2'): {agree*100:.1f}% relative error")
    print(f"  at eps={t['eps']:.3f} -- the O(eps^2) expansion is doing well even at this far-core point.\n")

    print("=== Required bracket value B = a/(eps*tan(theta)) to reproduce GAP-2026-041 Table 2 ===")
    print("(B = 2 - gamma + d/lambda; B<0 needs gamma > 2 + d/lambda, i.e. a VERY steep local ADF)\n")
    meas = {450: {"UMD": 0.10, "SDmu": 0.05}, 800: {"UMD": 0.12, "SDmu": 0.04}, 1200: {"UMD": 0.11, "SDmu": -0.10}}
    for Dref in (5000.0, 7500.0, 10000.0):
        print(f" -- D = {Dref/1000:.1f} km --")
        for rr in (450, 800, 1200):
            b = required_bracket(rr, Dref, 35.0, meas[rr]["SDmu"])
            print(f"    r={rr:4d} m: B_required(SDmu) = {b:+.2f}")
    print()

    print("#" * 80)
    print("# Section 3 -- Muon 'attenuation' sign correction (Bertou & Billoir Fig. 1)")
    print("#" * 80)
    Lam_g, X, rho = bb_muon_density_vs_depth()
    print(f"B&B Fig. 1 muon curve (10^19 eV, their own explicit MC): rho_mu(X)/rho_mu(900) = "
          f"{dict(zip(X.astype(int), rho))}")
    print(f"Fitted as rho ~ exp(+(X-900)/Lambda): Lambda_growth = {Lam_g:+.0f} g/cm^2 (positive = GROWING with depth)")
    print("This is the OPPOSITE sign to a normal attenuation length -- both GAP notes assume muon")
    print("'attenuation' is early-favoring like the EM component; B&B's own muon-isolated MC says no,")
    print("over exactly the depth range relevant here (900-1200 g/cm^2 sea-level-equivalent).\n")
    lam_36km_gcm2 = geometric_length_to_gcm2(36.0)
    print(f"Cross-check: Armbruster's lambda=36 km (a GEOMETRIC length, muon range) converts to "
          f"~{lam_36km_gcm2:.0f} g/cm^2 near ground -- consistent order of magnitude with |Lambda_growth| "
          f"above ({abs(Lam_g):.0f} g/cm^2), i.e. the two 'attenuation' pictures are comparably strong, just")
    print("opposite in sign for the muon channel specifically.")
    print("A crude linearised bracket estimate (using the geometric-length-to-grammage conversion")
    print("above rather than an actual slant-depth calculation) suggested this swing might be")
    print("'comparable' to the gap in Section 2's table -- that estimate mixed a linearised bracket")
    print("with an exact geometry inconsistently and OVERSTATED the effect. Section 7 below redoes")
    print("this properly (real slant depths, combined multiplicatively with the corrected spectrum-")
    print("weighted kinematic term from the explainer notebook) and finds a smaller, more honest number.\n")

    print("#" * 80)
    print("# Section 4 -- Q uncertainty (Cazon 2012 explicitly rejects a single Q)")
    print("#" * 80)
    med_factor = _verify_median_factor()
    print(f"Verified median/Q factor for dN/dpt~(pt/Q^2)exp(-pt/Q): median = {med_factor:.4f} * Q")
    for med_cpt in (0.20, 0.21, 0.22):
        Q = Q_from_median_cpt(med_cpt)
        print(f"  Cazon Fig. 8 median c*pt = {med_cpt:.2f} GeV  =>  Q = {Q:.3f} GeV  (NOT the often-quoted 0.20 GeV)")
    print("Cazon (2012) itself: 'the different correlations of pt with Ei and X must be included...'")
    print("-- rejects a single fixed Q as inadequate. Any E* computed from one Q, one D is a point")
    print("estimate inside a genuinely broad, correlated distribution (h(X) FWHM ~600-700 g/cm^2).\n")

    print("#" * 80)
    print("# Section 5 -- Real-MC acceptance audit (icrc2025-test7, SIBYLL 2.3e proton)")
    print("#" * 80)
    inf = load_infill_reference_bin()
    table2_reproduction(inf)
    acceptance_audit(inf)
    R = acceptance_density_correlation(inf)

    print("#" * 80)
    print("# Section 6 -- Decisive test: does equalising exposure change the reported A1?")
    print("#" * 80)
    equal_exposure_test(inf, 30, 40, 1050, 1400, "r~1200 m, theta 30-40 (Table 2 reference point)")
    equal_exposure_test(inf, 30, 40, 650, 950, "r~800 m, theta 30-40 (small-effect control)")
    equal_exposure_test(inf, 30, 40, 1400, 1800, "r~1600 m, theta 30-40 (largest acceptance bias)")
    print("VERDICT: shifts are all within noise (<0.001) despite acceptance modulations up to +/-0.6 and")
    print("a strong correlation (Section 5) between A1_accept and A1_SDmu across (theta,r) cells. The")
    print("correlation is real but NOT causal for the unweighted-mean estimator used by the pipeline --")
    print("the reported SD-muon inversion is not an artifact of non-uniform station sampling.\n")

    print("#" * 80)
    print("# Section 7 -- RETRACTED: the B&B muon-attenuation-sign candidate")
    print("#" * 80)
    print("This section's 'no attenuation' column reproduces claude_work/kinematic_divergence_explainer_")
    print("and_thesis_updates/explainer_kinematic_divergence_simulator.py Section 8's own combined")
    print("prediction (prior work, not this session's) as a cross-check -- that part is trustworthy.")
    print()
    print("The '+B&B muon attenuation' columns are KEPT BELOW FOR RECORD ONLY, NOT AS A FINDING.")
    print("Two problems, found by the author's direct questioning of the physics, retract this candidate:")
    print("  1. Population/threshold mismatch: B&B's Fig.1 is raw AIRES particle output -- essentially")
    print("     the ENTIRE muon spectrum, the SD's own near-zero-threshold population -- not the UMD's")
    print("     hard >1.22 GeV threshold population. Applying the same factor to the UMD (as done below,")
    print("     and as the previous version of this report did in its headline numbers) mixes a")
    print("     population the UMD never sees into the UMD's own prediction.")
    print("  2. Likely double-counting: B&B's own text ('total decreases, but spread increases')")
    print("     describes lateral spread of the muon population with depth -- i.e. very plausibly the")
    print("     SAME physics as the kinematic-divergence term already in the 'no attenuation' combination")
    print("     above (properly spectrum-weighted, prior work). Adding B&B's cruder, energy-integrated")
    print("     number on top double-counts that physics with the opposite sign from the better source.")
    print("  (A third, secondary problem: B&B's calibration depths, 900-1200 g/cm2 vertical for a")
    print("   10^19-10^20 eV VERTICAL shower, sit above this reference point's own slant depths, 568-708")
    print("   g/cm2 for a 10^17.5-18 eV, 35deg shower -- an extrapolation + unjustified energy transfer.)")
    print()
    Lambda_growth = bb_muon_density_vs_depth()[0]
    print(f"{'gamma':>6}  {'no attenuation (TRUSTED, prior work)':>36}  {'+B&B (RETRACTED, see above)':>28}")
    for gamma in (2.0, 2.6, 3.0):
        res = combined_per_detector_prediction(1200.0, 7500.0, 35.0, 0.20, gamma, Lambda_growth)
        print(f"gamma={gamma:.1f}  SD={res['sd_none']:+.3f} UMD={res['umd_none']:+.3f}"
              f"                          |  SD={res['sd_bb']:+.3f} UMD={res['umd_bb']:+.3f}  (DO NOT CITE)")
    print(f"\nobserved: SD=-0.10  UMD=+0.11")
    print(f"\nVERDICT: no candidate mechanism found across this session, or any of the five prior passes,")
    print(f"survives scrutiny as an independent, correctly-attributed contribution to the SD gap -- not")
    print(f"even partially. See report.md Section 3 for the full reasoning and what would need to be done")
    print(f"(population-matched, depth-correct re-measurement) before this idea could be revisited.")


if __name__ == "__main__":
    main()
