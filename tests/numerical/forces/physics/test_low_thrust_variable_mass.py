import numpy as np
import pytest

from e2m2e.algorithm.forces import (
    ForceModel,
    GravityField,
    VariableMassFiniteBurn,
)
from tests.numerical.forces.conftest import EARTH_RE, keplerian_to_cartesian

pytestmark = [pytest.mark.force, pytest.mark.low_thrust]


def _build_lowthrust_problem(system, thrust, isp, mass, direction_kind="velocity"):
    """构造沿速度方向、可变质量的低推力 ForceModel。

    direction_kind:
        - "velocity": 固定方向向量无法跟随速度，故用 (t, state) -> v/|v| 可调用；
          可调用方向使 to_rust_spec 返回 None，走 Python 回退路径。
        - "fixed": 固定方向向量 [0,1,0]，to_rust_spec 非 None，走 Rust 7D 路径。
    """
    mu = system.gravitational_parameter("EARTH")
    r_earth = EARTH_RE
    a0 = r_earth + 300.0
    y0_6 = keplerian_to_cartesian(a0, 0.0, 0.0, 0.0, 0.0, 0.0, mu)

    if direction_kind == "velocity":

        def direction(_t: float, state: np.ndarray) -> np.ndarray:
            v = state[3:6]
            return v / np.linalg.norm(v)
    elif direction_kind == "fixed":
        direction = np.array([0.0, 1.0, 0.0])  # 与圆轨道初速方向一致
    else:
        raise ValueError(direction_kind)

    burn = VariableMassFiniteBurn(thrust=thrust, isp=isp, initial_mass=mass, direction=direction)
    gravity = GravityField(body="EARTH", degree=0, order=0)
    fm = ForceModel(system, forces=[gravity, burn])
    y0 = np.concatenate([y0_6, [mass]])
    return fm, y0


@pytest.mark.spice
def test_variable_mass_callable_direction_rust_rejects_unsupported_force(earth_icrf_system):
    """Rust 不支持可调用方向时显式拒绝，不隐式回退 Python。"""
    system = earth_icrf_system

    thrust = 0.1
    mass = 1000.0
    isp = 3000.0
    duration_s = 0.25 * 86400.0

    fm, y0 = _build_lowthrust_problem(system, thrust, isp, mass, direction_kind="velocity")
    # 可调用方向不能序列化为 Rust force spec，必须显式拒绝。
    burn = next(e.force for e in fm._entries if isinstance(e.force, VariableMassFiniteBurn))
    assert burn.to_rust_spec(system) is None

    et0 = system.spice.utc_to_et("2025-06-21T11:00:06")
    t_span = (et0, et0 + duration_s)
    t_eval = np.array([et0, et0 + duration_s])

    with pytest.raises(NotImplementedError, match="callable direction.*Rust"):
        fm.propagate(y0, t_span, t_eval=t_eval, max_steps=200_000)
