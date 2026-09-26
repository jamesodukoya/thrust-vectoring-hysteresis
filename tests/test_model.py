import json
from pathlib import Path

import numpy as np

from tvh import GKParams, eta_v, simulate
from tvh.model import sweep

P = GKParams()
ROOT = Path(__file__).resolve().parents[1]


def _hold(theta, x_init, seconds=2.0, dt=0.005):
    t = np.arange(0, seconds, dt)
    return simulate(np.full_like(t, theta), t, P, x_init=x_init)


def test_bistable_hold_keeps_its_sheet():
    mid = 0.5 * (P.theta_asc + P.theta_desc)
    x_att, _ = _hold(mid, 1.0)
    x_sep, _ = _hold(mid, 0.0)
    assert x_att[-1] == 1.0 and x_sep[-1] == 0.0


def test_snap_through_at_each_fold():
    dt = 0.001
    t = np.arange(0, 5 * P.tau, dt)
    x_up, _ = simulate(np.full_like(t, P.theta_asc + 1), t, P, x_init=1.0)
    x_dn, _ = simulate(np.full_like(t, P.theta_desc - 1), t, P, x_init=0.0)
    assert x_up[-1] < 0.01 and x_dn[-1] > 0.99


def test_direction_dependence_inside_band():
    theta = 40.0
    t, th_up = sweep([0, theta], dt=0.005)
    _, eta_up = simulate(th_up, t, P, x_init=1.0)
    t, th_dn = sweep([80, theta], dt=0.005)
    _, eta_dn = simulate(th_dn, t, P, x_init=0.0)
    assert eta_dn[-1] > 5 * eta_up[-1]


def test_return_point_memory():
    t, th = sweep([80, 40, 60, 40], dt=0.005)
    _, eta = simulate(th, t, P, x_init=0.0)
    first = eta[int(np.argmax(th <= 40.0))]  # end of the first leg, 80 -> 40
    assert abs(eta[-1] - first) < 1e-6


def test_eta_bounds():
    th = np.linspace(0, 100, 101)
    for x in (0.0, 0.5, 1.0):
        e = eta_v(th, x)
        assert np.all(e >= 0) and np.all(e <= 1)


def test_hover_yaw_data_matches_thesis_results():
    d = json.loads((ROOT / "data" / "hover_yaw.json").read_text())
    g, f, r = d["conditions"]["landing_gate"], d["conditions"]["full_pack"], d["requirements"]
    assert (g["motors_only_floor"], g["flight_design"], g["after_bench_v2"]) == (0.840, 1.011, 1.447)
    assert (f["motors_only_floor"], f["flight_design"], f["after_bench_v2"]) == (1.392, 1.569, 2.073)
    assert (r["calm_air_minimum"], r["nose_into_wind"], r["beam_wind_design"]) == (0.430, 0.776, 1.669)


def test_figures_smoke(tmp_path):
    from tvh.figures import main
    for p in main(str(tmp_path)):
        assert p.exists() and p.stat().st_size > 1000
