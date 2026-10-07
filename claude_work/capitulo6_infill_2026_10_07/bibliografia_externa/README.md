# External literature search for Chapter 6 (2026-10-07)

Quick web search (not exhaustive) for work related to the three new results of Chapter 6:
station-selection bias at large distance, the reconstructed-core shift caused by the asymmetry,
and the muon azimuthal asymmetry in inclined showers. **None of this is in the chapter yet.**
Candidate BibTeX entries are in `candidatas.bib`; check every field before copying them into
`Tesis - Latex/bibliografia.bib`.

**No work was found that shows station selection inverting the SD muon asymmetry.** With the
caveat that the search was short, the HasStation result of Chapter 6 looks new.

## 1. Pierre Auger Collaboration, "Reconstruction of events recorded with the surface detector of the Pierre Auger Observatory", JINST 15 (2020) P10021, arXiv:2007.09035

The most useful one; sections 5.2.1–5.2.2 were read in full.

- **Core shift (supports `subsec:lavado_nucleo` and Ch. 5 `subsubsec:corrimiento_nucleo`).**
  - Quote: "Both LDF models used within the Auger Collaboration assume that the deposited signals in the stations are rotationally symmetric around the shower axis. In truth, the showers are asymmetric due to a combination of the longitudinal evolution and geometrical effects…"
  - The Herald reconstruction corrects each signal with S_symm = S / (1 + α(r) cos ζ) (their Eq. 5.8), with α(r) taken from simulations. Observer applies no correction.
  - The paper attributes the systematic core-position difference between the two reconstructions (~40 m) to this correction: "the corresponding shift of the impact-point".
  - This is the same physics as ΔA1 ≈ −βb/r: the Collaboration knows the shift exists, but regards it as small for S(1000) (< 0.2 %).
  - Open check: confirm that the thesis simulations were reconstructed with Observer/Offline (no asymmetry correction). If so, the measured b = 9–21 m is this effect.
- **Selection (supports `subsec:seleccion_estaciones`).**
  - Non-triggered stations enter the LDF likelihood through a trigger probability p_trig(S(r_i)) that depends on the **total** expected signal (their item (d), p. 16).
  - Quote: "Without consideration of the non-triggered stations, deviations of the shower size on the order of up to 8% are observed."
  - The standard LDF fit therefore corrects for the trigger threshold. An A1 computed as a plain average over triggered stations does not, and Ch. 6 shows what that does to the asymmetry.

## 2. N. Arsene, M. Roth, O. Sima, "Restoration of azimuthal symmetry of muon densities in extended air showers", arXiv:2004.04461

- Studies, for Auger conditions, the ground-level azimuthal asymmetry of the muon density in inclined showers. It is caused by geometry plus attenuation/decay, with amplitude up to ~35 %.
- Projecting muons along their own direction, with attenuation weights, restores the symmetry. The choice of projection changes X_max^μ by up to 32 g/cm².
- Fits Ch. 3 best, or the Ch. 6 introduction.
- The journal reference is not verified.

## 3. Pierre Auger Collaboration, "Azimuthal asymmetry in the risetime of the surface detector signals of the Pierre Auger Observatory", PRD 93 (2016) 072006

The SD risetime asymmetry used as a composition observable above 3×10^18 eV. It is the closest published precedent for using an azimuthal asymmetry for mass composition. Fits Ch. 1, 3 or 5.

## 4. T. Huege, F. Schlüter, "Reconstructing inclined extensive air showers from radio measurements", ICRC2021 (PoS 395, 209), arXiv:2208.14258

In radio, uncorrected early-late asymmetries bias the reconstructed core position and arrival direction. It is an independent analogue of the core shift (one sentence in `subsec:lavado_nucleo`).

## 5. S. Müller for the Pierre Auger Collaboration, "Direct Measurement of the Muon Density in Air Showers with the Pierre Auger Observatory", EPJ Web Conf. 210 (2019) 02013 (UHECR 2018)

AMIGA over-counting depends on the muon azimuth relative to the module orientation (their Fig. 2). Relevant to the directional counting bias of Ch. 5 (`subsec:bias_direccional`).

## Proposed sentences (Spanish, not inserted)

- **End of `subsec:lavado_nucleo`:**
  "Este efecto es conocido en la reconstrucción estándar del SD: las LDF utilizadas por la Colaboración suponen señales con simetría rotacional, y la corrección de la asimetría mediante $S/(1+\alpha(r)\cos\zeta)$, aplicada sólo en una de las dos reconstrucciones oficiales, desplaza el punto de impacto en $\sim 40$~m \cite{auger2020sdreco}."
- **`subsec:seleccion_estaciones`, after the hypothesis paragraph:**
  "La probabilidad de que una estación dispare depende de su señal total esperada, y la reconstrucción estándar incluye las estaciones sin disparo en el ajuste de la LDF precisamente para no sesgar el tamaño de la lluvia \cite{auger2020sdreco}; un promedio de la asimetría sobre las estaciones disparadas no incorpora esa corrección."
- **Ch. 6 introduction or Ch. 3:** cite Arsene et al. next to Bertou–Billoir for the ground-level geometric asymmetry of the muon density.
