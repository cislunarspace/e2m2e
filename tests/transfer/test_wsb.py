"""WSB 太阳引力辅助转移测试（物理定义验证）。

测试策略：按物理定义验证，不用黄金样本。
BCR4BP 纯数值测试不需要 SPICE，用 BCR4BPSystem.earth_moon() 构造。
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from e2m2e.algorithm.dynamics import BCR4BP_Dynamics, BCR4BPSystem, CR3BP_Dynamics, CR3BP_System
from e2m2e.algorithm.transfer import (
    TransferDesignResult,
    WsbSearchParams,
    WsbTransferDetails,
    transfer_orbit,
)
from e2m2e.algorithm.transfer.hohmann import TliParams
from e2m2e.algorithm.transfer.wsb import (
    compute_kepler_energy_moon,
)

# 地月 CR3BP 参数
MU = 1.21506683e-2
DU = 384405.0  # km


def _make_bcr4bp_system(sun_phase0: float = 0.0):
    """创建标准地月 BCR4BP 系统。"""
    return BCR4BPSystem.earth_moon(sun_phase0=sun_phase0)


def _make_cr3bp_system():
    """创建地月 CR3BP 系统并初始化特征尺度。"""
    system = CR3BP_System(mu=MU, primary="Earth", secondary="Moon")._with_default_scales()
    dynamics = CR3BP_Dynamics(system)
    return system, dynamics


def _make_departure_state(system):
    """构造典型 LEO 出发态的旋转系无量纲态。"""
    from e2m2e.algorithm.transfer.hohmann import MU_EARTH, R_EARTH

    r_park = R_EARTH + 200.0
    v_circ = math.sqrt(MU_EARTH / r_park)
    r0 = np.array([r_park, 0.0, 0.0])
    v0 = np.array([0.0, v_circ, 0.0])
    departure_phys = np.concatenate([r0, v0])
    return system.physical_to_dimensionless(departure_phys)


def _make_target_state(system):
    """构造近月轨道目标态的旋转系无量纲态。"""
    mu = system.mu
    moon_x = 1.0 - mu
    r_target_km = 2000.0
    r_target_du = r_target_km / DU
    x_target = moon_x + r_target_du
    v_circ_dim = math.sqrt(mu / r_target_du)
    return np.array([x_target, 0.0, 0.0, 0.0, v_circ_dim, 0.0])


# ---------------------------------------------------------------------------
# TestWsbSearchParams：搜索参数验证
# ---------------------------------------------------------------------------


class TestWsbSearchParams:
    """搜索参数验证。"""

    def test_default_params_valid(self):
        """默认参数范围合理。"""
        params = WsbSearchParams()
        assert params.sun_phase_range == (0.0, 2.0 * math.pi)
        assert params.n_sun_phase > 0
        assert params.tof_range == (5.0, 45.0)
        assert params.perilune_alt_min == 100.0
        assert params.perilune_alt_max == 10000.0
        assert params.max_total_dv == 25.0
        assert params.h2_energy_threshold == 0.0
        assert params.n_departure_phase > 0
        assert params.n_tof > 0

    def test_frozen_dataclass(self):
        """WsbSearchParams 是 frozen dataclass。"""
        params = WsbSearchParams()
        with pytest.raises(AttributeError):
            params.n_sun_phase = 16  # type: ignore[misc]

    def test_custom_params(self):
        """自定义参数可正确构造。"""
        params = WsbSearchParams(
            sun_phase_range=(0.0, math.pi),
            n_sun_phase=4,
            departure_phase_range=(0.0, math.pi),
            n_departure_phase=20,
            tof_range=(10.0, 30.0),
            n_tof=20,
            perilune_alt_min=200.0,
            perilune_alt_max=5000.0,
            max_total_dv=30.0,
            h2_energy_threshold=0.01,
        )
        assert params.sun_phase_range == (0.0, math.pi)
        assert params.n_sun_phase == 4
        assert params.max_total_dv == 30.0
        assert params.h2_energy_threshold == 0.01


# ---------------------------------------------------------------------------
# TestComputeKeplerEnergyMoon：H2 计算验证
# ---------------------------------------------------------------------------


class TestComputeKeplerEnergyMoon:
    """compute_kepler_energy_moon H2 计算验证。"""

    def test_circular_orbit_near_moon_negative_energy(self):
        """月球附近圆轨道 H2 < 0（受月球约束）。"""
        mu = MU
        r_orbit = 2000.0 / DU  # 2000 km 高度（月球上方）
        moon_x = 1.0 - mu
        x = moon_x + r_orbit
        v_circ = math.sqrt(mu / r_orbit)
        state = np.array([x, 0.0, 0.0, 0.0, v_circ, 0.0])
        h2 = compute_kepler_energy_moon(state, mu)
        assert h2 < 0, f"圆轨道 H2 应为负，得到 {h2}"

    def test_zero_velocity_at_moon_negative_energy(self):
        """月心处零速度：势能主导，H2 为很大的负数。"""
        mu = MU
        moon_x = 1.0 - mu
        r_offset = 0.01  # 距月心 0.01 DU
        state = np.array([moon_x + r_offset, 0.0, 0.0, 0.0, 0.0, 0.0])
        h2 = compute_kepler_energy_moon(state, mu)
        assert h2 < 0, f"静止近月态 H2 应为负，得到 {h2}"

    def test_fast_flyby_positive_energy(self):
        """高速飞越：H2 > 0（超逃逸速度）。"""
        mu = MU
        moon_x = 1.0 - mu
        r_flyby = 5000.0 / DU  # 远处飞越
        x = moon_x + r_flyby
        v_escape = math.sqrt(2.0 * mu / r_flyby)
        v_flyby = v_escape * 2.0  # 2 倍逃逸速度
        # 旋转系速度：vy + x - moon_x = v_flyby，取 vx=0, vy=v_flyby
        state = np.array([x, 0.0, 0.0, 0.0, v_flyby + moon_x - x, 0.0])
        h2 = compute_kepler_energy_moon(state, mu)
        assert h2 > 0, f"高速飞越 H2 应为正，得到 {h2}"

    def test_velocity_correction_applied(self):
        """验证旋转系→惯性系速度修正已正确应用。

        检查旋转系静止物体（vx=vy=vz=0）在月心处的相对速度不为零
        （旋转系效应）。
        """
        mu = MU
        moon_x = 1.0 - mu
        state_stationary = np.array([moon_x + 0.1, 0.0, 0.0, 0.0, 0.0, 0.0])
        h2 = compute_kepler_energy_moon(state_stationary, mu)
        # 旋转系静止 → 惯性系有速度 → v_rel_moon 不为零
        # 动能应为正，但势能主导，H2 < 0
        assert h2 < 0
        # 纯势能（无速度）应给出更小的 H2（更负）
        # 因为动能是正的，所以 H2 > 纯势能
        r_rel = 0.1
        pe_only = -mu / r_rel
        assert h2 > pe_only, "旋转系静止态应有正的动能贡献"

    def test_far_from_moon_approaches_zero(self):
        """远离月球时 H2 → 0⁺（相对速度趋近逃逸速度）。"""
        mu = MU
        moon_x = 1.0 - mu
        r_far = 50000.0 / DU
        x = moon_x + r_far
        v_escape = math.sqrt(2.0 * mu / r_far)
        # 恰好逃逸速度
        state = np.array([x, 0.0, 0.0, 0.0, v_escape + moon_x - x, 0.0])
        h2 = compute_kepler_energy_moon(state, mu)
        assert abs(h2) < 1e-3, f"逃逸速度处 H2 应接近 0，得到 {h2}"


# ---------------------------------------------------------------------------
# TestWsbPhysics：物理不变量验证
# ---------------------------------------------------------------------------


class TestWsbPhysics:
    """WSB 物理不变量验证。"""

    def test_cr3bp_jacobi_conservation(self):
        """CR3BP Jacobi 常数沿轨道守恒（验证传播工具正确性）。"""
        from e2m2e.algorithm.transfer.lga import _compute_jacobi

        system, dynamics = _make_cr3bp_system()
        dep_state = _make_departure_state(system)
        mu = system.mu

        t_span = (0.0, 1.0)
        result = dynamics.propagate(dep_state, t_span, t_eval=np.linspace(0.0, 1.0, 100))
        states = result["states"]

        c_start = _compute_jacobi(states[0], mu)
        c_end = _compute_jacobi(states[-1], mu)
        assert abs(c_start - c_end) < 1e-8, (
            f"Jacobi 常数不守恒：C_start={c_start:.10e}, C_end={c_end:.10e}"
        )

    def test_bcr4bp_no_jacobi(self):
        """BCR4BP 无 Jacobi 积分（时间周期系统）。"""
        system = _make_bcr4bp_system()
        dynamics = BCR4BP_Dynamics(system)
        dep_state = _make_departure_state(system)
        with pytest.raises(NotImplementedError, match="Jacobi"):
            dynamics.compute_jacobi_constant(dep_state)

    def test_bcr4bp_system_initialization(self):
        """BCR4BPSystem.earth_moon() 正确初始化特征尺度和太阳参数。"""
        system = _make_bcr4bp_system(math.pi / 4)
        assert system.is_initialized
        assert system.characteristic_length is not None
        assert system.characteristic_time is not None
        assert system.characteristic_velocity is not None
        assert system.sun_phase0 == math.pi / 4
        assert system.sun_mass > 0
        assert system.sun_distance > 0

    def test_bcr4bp_propagation_differs_by_sun_phase(self):
        """不同太阳相位角的 BCR4BP 传播结果不同。"""
        dep_state = _make_departure_state(_make_bcr4bp_system())
        t_dim = 5.0 * 86400.0 / _make_bcr4bp_system().characteristic_time

        result_0 = BCR4BP_Dynamics(_make_bcr4bp_system(0.0)).propagate(
            dep_state, (0.0, t_dim), t_eval=np.array([t_dim])
        )
        result_pi = BCR4BP_Dynamics(_make_bcr4bp_system(math.pi)).propagate(
            dep_state, (0.0, t_dim), t_eval=np.array([t_dim])
        )
        state_0 = result_0["states"][-1]
        state_pi = result_pi["states"][-1]
        diff = np.linalg.norm(state_0 - state_pi)
        assert diff > 1e-6, f"不同太阳相位的传播结果应有差异，diff={diff}"


# ---------------------------------------------------------------------------
# TestWsbTransferOrbit：transfer_orbit("WSB") 编排器测试
# ---------------------------------------------------------------------------


class TestWsbTransferOrbit:
    """transfer_orbit("WSB") 编排器测试。"""

    def _make_target_ephemeris(self):
        system = _make_bcr4bp_system()
        target_state = _make_target_state(system)
        du = system.characteristic_length
        vu = system.characteristic_velocity
        target_phys = np.array(
            [
                target_state[0] * du,
                target_state[1] * du,
                target_state[2] * du,
                target_state[3] * vu,
                target_state[4] * vu,
                target_state[5] * vu,
            ]
        )
        return target_phys.reshape(1, 6)

    @pytest.mark.slow
    def test_returns_transfer_design_result(self):
        """transfer_orbit("WSB", ...) 返回 TransferDesignResult，transfer_type == "WSB"。"""
        tli_params = TliParams(parking_alt_km=200.0, inclination_deg=0.0)
        target_ephemeris = self._make_target_ephemeris()
        search_params = WsbSearchParams(
            n_sun_phase=1,
            n_departure_phase=5,
            n_tof=3,
            max_total_dv=50.0,
        )

        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = transfer_orbit(
                "WSB",
                tli_params=tli_params,
                target_ephemeris=target_ephemeris,
                wsb_search_params=search_params,
            )

        assert isinstance(result, TransferDesignResult)
        assert result.transfer_type == "WSB"

    @pytest.mark.slow
    def test_wsb_details_populated(self):
        """details 包含 WsbTransferDetails 全部字段。"""
        tli_params = TliParams(parking_alt_km=200.0, inclination_deg=0.0)
        target_ephemeris = self._make_target_ephemeris()
        search_params = WsbSearchParams(
            n_sun_phase=1,
            n_departure_phase=5,
            n_tof=3,
            max_total_dv=50.0,
        )

        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = transfer_orbit(
                "WSB",
                tli_params=tli_params,
                target_ephemeris=target_ephemeris,
                wsb_search_params=search_params,
            )

        details = result.details
        assert isinstance(details, WsbTransferDetails)
        assert isinstance(details.tof_sec, float)
        assert isinstance(details.perilune_alt_km, float)
        assert isinstance(details.perilune_vel_km_s, float)
        assert isinstance(details.dv_departure_km_s, float)
        assert isinstance(details.dv_arrival_km_s, float)
        assert isinstance(details.h2_energy, float)
        assert isinstance(details.n_candidates_searched, int)
        assert isinstance(details.n_candidates_feasible, int)
        assert isinstance(details.converged, bool)
        assert isinstance(details.search_params, WsbSearchParams)

    def test_wsb_missing_params_raises(self):
        """transfer_orbit("WSB") 缺少必要参数时报错。"""
        with pytest.raises(ValueError, match="tli_params"):
            transfer_orbit("WSB", target_ephemeris=np.zeros((1, 6)))

        with pytest.raises(ValueError, match="target_ephemeris"):
            transfer_orbit("WSB", tli_params=TliParams(parking_alt_km=200.0, inclination_deg=0.0))

    def test_unsupported_type_still_raises(self):
        """transfer_orbit("low_thrust") 仍抛出 NotImplementedError。"""
        with pytest.raises(NotImplementedError, match="low_thrust"):
            transfer_orbit("low_thrust")
