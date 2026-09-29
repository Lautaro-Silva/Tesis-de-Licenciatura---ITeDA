"""
Independent check (Phase 3, point 4 of the review plan): does the has_rec
selection effect (and the resulting A1 sign flip) depend on zenith theta and
energy logE the way it should if the proposed EM-help/muon-enrichment
mechanism is real? No prior document in scope tested this explicitly.

Input: claude_work/revision_asimetrias_sd_umd/04_soporte/tablas/adst_counts_fast.csv
(already-executed raw-ADST station-level extraction, 106281 rows, 20 SIBYLL 2.3e
proton files, icrc2025-test7, produced and audited by the reviewed work itself;
this script only re-reads it and performs a fresh, independent aggregation).
"""
import pandas as pd
import numpy as np

df = pd.read_csv('claude_work/revision_asimetrias_sd_umd/04_soporte/tablas/adst_counts_fast.csv')

# restrict to the far bin used for the headline result
far = df[(df.r >= 1050) & (df.r < 1400) & (df.theta >= 30) & (df.theta < 40)].copy()
print(f"Far bin (1050-1400m, 30-40deg) rows: {len(far)}")
print(f"has_rec fraction overall in far bin: {far.has_rec.mean():.3f}")

def a1_fit(sub, phi_col='phi', val_col='mu', nbins=12):
    sub = sub.dropna(subset=[val_col])
    if len(sub) < 50:
        return np.nan, len(sub)
    edges = np.linspace(-180, 180, nbins+1)
    sub = sub.copy()
    sub['bin'] = pd.cut(sub[phi_col], edges, include_lowest=True)
    means = sub.groupby('bin', observed=True)[val_col].mean()
    centers = np.deg2rad([ (e.left+e.right)/2 for e in means.index ])
    y = means.values
    # weighted linear least squares for rho0*(1+A1 cos phi): y = rho0 + rho0*A1*cos(phi)
    X = np.column_stack([np.ones_like(centers), np.cos(centers)])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    rho0, rho0A1 = coef
    A1 = rho0A1/rho0 if rho0 != 0 else np.nan
    return A1, len(sub)

print("\n--- theta dependence (whole dataset, far radius fixed at 1050-1400m) ---")
for lo, hi in [(20,30),(30,40),(40,50),(50,65)]:
    sub = df[(df.r>=1050)&(df.r<1400)&(df.theta>=lo)&(df.theta<hi)]
    a1_all, n_all = a1_fit(sub)
    a1_sel, n_sel = a1_fit(sub[sub.has_rec == 1])
    frac = sub.has_rec.mean() if len(sub) else np.nan
    print(f"theta [{lo:2d},{hi:2d}): retain_frac={frac:.3f}  A1_all={a1_all:+.4f} (n={n_all:6d})  A1_selected={a1_sel:+.4f} (n={n_sel:6d})  delta={a1_sel-a1_all:+.4f}" if not np.isnan(a1_all) else f"theta [{lo:2d},{hi:2d}): insufficient stats")

print("\n--- energy dependence (30-40 deg, r 1050-1400m fixed) ---")
if 'logE' in df.columns:
    for lo, hi in [(17.5,17.75),(17.75,18.0),(18.0,18.5)]:
        sub = far[(far.logE>=lo)&(far.logE<hi)]
        a1_all, n_all = a1_fit(sub)
        a1_sel, n_sel = a1_fit(sub[sub.has_rec == 1])
        frac = sub.has_rec.mean() if len(sub) else np.nan
        if not np.isnan(a1_all):
            print(f"logE [{lo},{hi}): retain_frac={frac:.3f}  A1_all={a1_all:+.4f} (n={n_all:6d})  A1_selected={a1_sel:+.4f} (n={n_sel:6d})  delta={a1_sel-a1_all:+.4f}")
        else:
            print(f"logE [{lo},{hi}): insufficient stats (n={len(sub)})")
else:
    print("no logE column")

print("\n--- retention fraction vs phi decile, far bin only (early=0, late=+-180) ---")
far2 = far.copy()
far2['phibin'] = pd.cut(far2.phi, np.linspace(-180,180,13), include_lowest=True)
g = far2.groupby('phibin', observed=True).agg(retain=('has_rec','mean'), mean_mu_all=('mu','mean'),
                                               mean_mu_sel=('mu', lambda s: s[far2.loc[s.index,"has_rec"] == 1].mean()),
                                               n=('mu','size'))
print(g)
