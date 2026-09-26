"""A clean-room flow-attachment state model in the Goman-Khrabrov form.

Written for this repository from the published idea (Goman & Khrabrov, 1994),
not copied from the thesis code. Every parameter here is ILLUSTRATIVE: the
branch curves only echo the shape of the published bench figure, and none of
them is measured data.

State x in [0, 1]: 1 = jet attached (axial, forward flight),
                   0 = jet separated onto the flap (vertical, VTOL).

    tau * dx/dt + x = x0(theta, x)

The static characteristic x0 is bistable. Above the ascending fold the only
equilibrium is separated (0); below the descending fold it is attached (1);
inside the band the flow stays on whichever sheet it is already on. That last
rule is the memory: the answer depends on where the flap came from.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class GKParams:
    theta_asc: float = 65.0   # servo deg: attached flow snaps to separated going up
    theta_desc: float = 25.0  # servo deg: separated flow snaps back to attached going down
    tau: float = 0.05         # s, relaxation time constant (illustrative)


def x0_bistable(theta: float, x: float, p: GKParams = GKParams()) -> float:
    """Static equilibrium: 0 above the ascending fold, 1 below the descending fold,
    and inside the band the sheet the state is already on."""
    if theta >= p.theta_asc:
        return 0.0
    if theta <= p.theta_desc:
        return 1.0
    return 1.0 if x >= 0.5 else 0.0


def _logistic(theta, center, width):
    return 1.0 / (1.0 + np.exp(-(np.asarray(theta, dtype=float) - center) / width))


def eta_axial(theta):
    """Illustrative vertical efficiency with the jet ATTACHED: the flap barely turns it
    until the flap is nearly fully deflected."""
    return 0.02 + 0.08 * _logistic(theta, 60.0, 4.0)


def eta_vtol(theta):
    """Illustrative vertical efficiency with the jet SEPARATED onto the flap."""
    return 0.02 + 0.97 * _logistic(theta, 30.0, 3.0)


def eta_v(theta, x):
    """Vertical efficiency (share of thrust that points vertically) for state x."""
    return x * eta_axial(theta) + (1.0 - x) * eta_vtol(theta)


def simulate(theta_of_t, t, p: GKParams = GKParams(), x_init: float = 1.0):
    """Integrate the state along a servo-angle history.

    theta_of_t: array of servo angles (deg), same length as t.
    Returns (x, eta) arrays. Uses RK4 with x0 frozen over each step, which is exact
    enough for step sizes well below tau.
    """
    theta = np.asarray(theta_of_t, dtype=float)
    t = np.asarray(t, dtype=float)
    x = np.empty_like(t)
    x[0] = x_init
    for k in range(1, len(t)):
        dt = t[k] - t[k - 1]
        target = x0_bistable(theta[k], x[k - 1], p)
        f = lambda xx: (target - xx) / p.tau  # noqa: E731
        k1 = f(x[k - 1])
        k2 = f(x[k - 1] + 0.5 * dt * k1)
        k3 = f(x[k - 1] + 0.5 * dt * k2)
        k4 = f(x[k - 1] + dt * k3)
        x[k] = np.clip(x[k - 1] + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4), 0.0, 1.0)
    return x, eta_v(theta, x)


def sweep(waypoints, rate_deg_s: float = 20.0, dt: float = 0.005):
    """Piecewise-linear servo sweep through the given angles at a constant rate."""
    thetas, ts, t0 = [waypoints[0]], [0.0], 0.0
    for a, b in zip(waypoints[:-1], waypoints[1:]):
        n = max(2, int(abs(b - a) / rate_deg_s / dt))
        seg = np.linspace(a, b, n)[1:]
        thetas.extend(seg)
        ts.extend(t0 + dt * np.arange(1, n))
        t0 = ts[-1]
    return np.array(ts), np.array(thetas)
