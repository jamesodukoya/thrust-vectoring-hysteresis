# Sources for every number in README.md

All paths are in the author's thesis workspace (`thesis_research/`), which is not public. Values were read on 2026-09-26.

| README number | Source | Key |
|---|---|---|
| 98.7% vs 4.7% at 40°, PWM 2000 (gap 0.94) | `calculations/parameters.json` | `thesis_pipeline_freeze_v5.propulsion.hysteresis.difference.reference` (`eta_V_desc` 0.98696, `eta_V_asc` 0.04716, `d_eta_V` 0.93980) |
| median gap 0.61, max 1.04, 33 matched points | same | `...hysteresis.difference.median` 0.60697, `.max` 1.03894, `...hysteresis.n_points` 33 |
| 9 throttle levels, 11 servo angles, 58,828 samples, 70 mm EDF | `calculations/parameters.json` | `dataset.pwm_setpoints_note`, `dataset.angle_setpoints_deg`, `dataset.n_samples`, `quadplane_architecture.edf_diameter_mm` |
| folds about 25° and 65° | `figures/gk/fig5_3_gk_duffing_potential.png` (fitted folds, merged branches, PWM ≥ 1600) | pipeline stage `gk.fit` |
| side force κ = 0.468 (~47%) | `calculations/parameters.json` | `thesis_pipeline_freeze_v5.propulsion.constants.kappa.axial` 0.46790 |
| 200 Monte Carlo runs | `figures/gk/fig5_5_langevin_sde_buffeting.png` legend | pipeline stage `gk.sde` |
| hover yaw 0.84 / 1.01 / 1.45 (landing gate), 1.39 / 1.57 / 2.07 (full pack) | `calculations/thesis_pipeline/results/control/qa23_results.json` | `configs.<frozen design>.headline.{landing_gate_best_ir,full_pack_mean_ir}.{floor_motors_only_nm,flight_design_nm,v2_conditional_nm}` |
| requirements 0.43 / 0.78 / 1.67 | same | `configs.<frozen design>.requirement.{n_req_min_nm,n_req_weathervane_nm,n_req_design_nm}` |
| "about 20% more" | derived | 1.011 / 0.840 = 1.204 |
| force sensor ~10 Hz; v1 angle changes were steps | `thesis_research/AGENTS.md`; `calculations/thesis_pipeline/gk/ode.py` header | |
