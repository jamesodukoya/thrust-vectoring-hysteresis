# Sources and limits of the public characterization results

Checked against the current Chapter 4 result files on **2026-10-15**.
Paths below are relative to the author's private `thesis_research/` workspace.
No file under `archive/` was used. The current generated results and outline
Chapter 4 take precedence over earlier analysis reports.

The public [aggregate summary](data/characterization_summary.json) records exact
values and source-file SHA-256 hashes. A hash identifies the source version; it
does not make the private measurements publicly reproducible.

## Experiment design and measurement corrections

| Public claim | Source and location | Qualification |
|---|---|---|
| 70 mm fan; six-axis force/torque bench | `thesis_outline.md` §4.1–§4.2 | Bench apparatus, not vehicle architecture |
| Initial 98.7% versus 4.7% vertical thrust share | `calculations/parameters.json::thesis_pipeline_freeze_v5.propulsion.hysteresis.difference.reference` | At the same servo command, 40°, PWM 2000; actual flap position unmeasured; no cause inferred |
| Five sessions, 431,591 retained rows, 1,642 dwells | `calculations/thesis_pipeline/results/ch4/ch4_datasets.json::{v1,S1,S1b,S2,S3}.{rows,n_dwells}` | Rows: 53,543 + 73,067 + 75,400 + 139,391 + 90,190. Dwells: 180 + 485 + 209 + 428 + 340. Repeated values are not independent observations |
| Direct encoder, open-loop/closed-loop distinction and run blocks | `thesis_outline.md` §4.2.1–§4.2.2; `ch4_datasets.json::{blocks,roles}` in the result directory above | Initial instrumented session open-loop; later sessions closed-loop. Rate series, minor loops, thermal soaks and identification trajectory were not run in Chapter 4 |
| 5.2° direction-dependent position gap | `calculations/reports/2026-09-29_bench-v2-test4-servo-map.md` §2–§3 | Independent flap encoder; approximately 93 µs command gap across the assembled drive, not internal servo lash alone. No causal claim about the original force gap |
| 8,741 powered rows without force before clock repair; zero after | `calculations/reports/2026-10-08_ch4-recompute-lever-arm-lift-ceiling.md` §3; `thesis_outline.md` §4.1.3 | 4,609 + 1,976 + 2,156. Some alignment exceptions remain; no claim of perfectly simultaneous acquisition |
| Fresh telemetry frames and settled dwells | `thesis_outline.md` §4.1.3; `calculations/thesis_pipeline/propulsion/ch4_sessions.py::_frame_median` | Fast log rows repeat slower sensor updates; do not count the repeats as fresh measurements |
| Lever arm corrected from 0.186 to 0.44 m; agreement within 4% | `calculations/thesis_pipeline/results/ch4/ch4_wrench.json::{lever_arm,verdict}` | Moment-derived/recorded axial thrust ratios 0.961600–0.990468 over four stand states. Tape tolerance ±0.01 m; moment-origin offset unresolved. Channels share one sensor |
| Lateral-force term removed | `thesis_outline.md` §4.1.4; `ch4_wrench.json::verdict`; `ch4_hysteresis.json::{decision,model}` | Recorded lateral force lacks support from moments. Its cause is not established. Current force model uses the measured-position map and a direction band |

## Prediction and uncertainty results

All JSON files in this table live under `calculations/thesis_pipeline/results/ch4/`.
Thesis session identifiers are retained here only to make the source lookup exact.

| Public result | Source key | What the result does and does not test |
|---|---|---|
| Map fit on S2, test S3: 313 dwells; axial/vertical RMSE 0.1608256 / 0.1640356 N | `ch4_aero_map.json::validation.S2_to_S3.overall` | Map fitted and stop-anchored on the training session. Test uses measured flap position, speed and its own horizontal scale correction |
| Reverse split: 349 dwells; RMSE 0.1835514 / 0.2026770 N | `ch4_aero_map.json::validation.S3_to_S2.overall` | Same conditions. This is a map-shape validation after calibration, not calibration-free controller transfer |
| Validation scale correction | `calculations/thesis_pipeline/propulsion/ch4_aero_map.py::{map_dwells,score,validate}` | Measured horizontal force is brought to the model scale per session; the prediction is converted back for force-error scoring |
| Thrust constant: 1.37% expanded relative uncertainty | `ch4_uncertainty.json::k_T.expanded` = 0.01368097 | Coverage factor 2; fit scatter, zero stability and resolution. Absolute gain and telemetry scales unquantified |
| Thrust prediction: 5.6% expanded relative uncertainty | `ch4_uncertainty.json::thrust_prediction.expanded` = 0.05616549 | Includes model-form mismatch, unlike the fitted-slope budget. Neither is a certified absolute-accuracy bound |
| Re-mount step: 12.4 standard uncertainties | `ch4_uncertainty.json::k_T.vs_scale_step` = 12.44023 | Exceeds the quantified slope budget; the budget omits unverified calibration. Cause remains unresolved |
| Low-throttle bias: 4.4–4.8% high | `ch4_uncertainty.json::thrust_prediction.line_error_pct_by_pwm` | Fitted points at 1500 and 1600 µs; this is model mismatch on fit data, not held-out performance |
| Motor/ESC holdout within 2.0% | `ch4_motor.json::holdout` | Fit on the uninstrumented stand; 13 later-session points at PWM ≥1550 µs. A fourteenth point at 1400 µs is about −7.0% and outside the stated range |
| Rising response: 48.1 ms time constant, 71.4 ms dead time | `ch4_dynamics.json::rotor_summary.up` | Two steps; medians 48.0575 and 71.4243 ms. No independent dynamic validation |
| Falling response: 45.2 ms time constant, 27.5 ms dead time | `ch4_dynamics.json::rotor_summary.down` | Two steps; medians 45.2176 and 27.4607 ms. No independent dynamic validation |
| Remaining limits | `ch4_uncertainty.json::{unquantified,map_grid}`; `thesis_outline.md` §4.1.4 and §4.6 | Unchecked absolute gain, telemetry scales, lever/moment-origin uncertainty, incomplete coverage, speed dependence and dwell independence assumptions |

## What changed from the earlier public account

- **Command versus measured position:** the initial stand did not measure flap position. Its direction-dependent force result cannot establish aerodynamic bistability by itself.
- **Dataset size:** 58,828 is the first session's raw row count. The old 436,876 total mixed raw first-session rows with retained later-session rows. Current Chapter 4 retains 431,591 rows.
- **Force errors:** the 0.14–0.17 N wording came from before the corrected joins and force treatment. The current two-direction session comparison is reported above.
- **Timing:** the earlier 48.5/61.8 ms rising response values predate the corrected joins. The current values are 48.1/71.4 ms.
- **Uncertainty:** fitted-constant uncertainty and prediction uncertainty are different. Neither includes unverified absolute sensor gain.
- **Lateral force:** the approximately 47% physical side-force interpretation is withdrawn; the moment consistency check does not support it.
- **State model and buffeting:** the illustrative code demonstrates a possible mathematical behavior. It is not a measured explanation or the Chapter 4 force map. Earlier significance and buffeting figures are not retained as current evidence.
- **Hover yaw:** the old allocator figures are superseded and removed. This case study makes no new vehicle-performance claim.

## Visual sources and disclosure boundaries

| Visual | Source | Interpretation and limits |
|---|---|---|
| `figures/investigation.gif` and `investigation_overview.png` | Initial 98.7%/4.7% observation above; grouped force validation below; Chapter 4 experiment protocol | Actuator, controller and protocol drawings are schematic. The animation presents flow hysteresis as the initial hypothesis, then shows measurement, position feedback and a separately tested map. It does not identify the original gap's sole cause or claim all direction dependence vanished |
| `figures/test_stand.png` | Exterior housing from `cad/airframe_6u3p/mesh/render_unit/housing__nozzle_housing.ply`; apparatus context from `figures/bench/{encoder_view,servo_view}.jpg` and outline §4.1.1 | The mesh was replaced privately by a closed convex envelope before rendering. No flap, linkage, gear or flow-path mesh was loaded into the render. Inlet/outlet detail is opaque. Stand, encoder placement, electronics and signal routes are schematic. Only the flat raster `figures/assets/test_stand_exterior.png` is distributed, without CAD, hidden layers or mechanism dimensions |
| `figures/force_validation.png` | `data/validation_bins.json`; private `propulsion/ch4_aero_map.py::{fitted_map,map_dwells,predict,score}`; same result-file hashes as the public characterization summary | Predictions use the exact session splits and scale correction of the scored map. Begin with 16 equal-width measured-force bins and merge sparse neighbors so every public group contains at least five dwells. Plot grouped means, retain summed squared residuals, and compute headline RMSE over all 313/349 dwells. Residual shading is an observed 10th–90th percentile range, not a confidence interval. No individual dwell or position-indexed map is exported |
| `figures/characterization_results.png` | `data/characterization_summary.json::uncertainty` | Retains the parameter-versus-prediction comparison; force-error bars are replaced by the agreement and residual plots |

## Public reproduction boundary

`tvh/figures.py` redraws the public visuals from aggregate JSON and the exterior
raster. `tvh/investigation_animation.py`, `test_stand_figure.py` and
`validation_figure.py` implement the new figures; `tvh/model.py` remains a separate
synthetic demonstration. Grouped statistics preserve all dwell counts and squared
errors, which tests compare with the previously published RMSE. Tests do not rerun
the private characterization analysis. Source hashes preserve provenance but do
not make the underlying records publicly reproducible. The original exterior
render is a supplied raster asset; recreating it in 3D requires the private CAD.

The two AIAA DOI references in the README support test-stand design and baseline
EDF performance. They are not substitutes for the source records of the later
Chapter 4 corrections and validation.
