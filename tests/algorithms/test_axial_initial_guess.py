"""Axial 轨道初始猜测模块测试。

覆盖 compute_axial_initial_guess 的返回结构、x 轴对称初始条件、
面外速度非零与错误处理。
"""

import numpy as np
import pytest

from e2m2e.algorithm.dynamics import CR3BP_System, LibrationPoint
from e2m2e.algorithm.family.axial_initial_guess import compute_axial_initial_guess

MU_EM = 1.215058560962404e-2


def _earth_moon_system() -> CR3BP_System:
    system = CR3BP_System(mu=MU_EM, primary="Earth", secondary="Moon")
    system.set_characteristic_scales(distance=384405.0, period=27.32 * 86400.0)
    return system


# =============================================================================
# Module identity
# =============================================================================


class TestModuleImport:
    """验证模块可直接导入，函数可直接调用。"""

    def test_module_importable(self):
        """axial_initial_guess 模块应可直接导入。"""
        assert compute_axial_initial_guess is not None

    def test_function_has_docstring(self):
        """公共函数应有文档字符串。"""
        assert compute_axial_initial_guess.__doc__ is not None


# =============================================================================
# compute_axial_initial_guess
# =============================================================================


class TestAxialInitialGuess:
    """compute_axial_initial_guess 的正确性。"""

    def test_returns_state_and_period(self):
        """应返回 (state, period) 元组。"""
        system = _earth_moon_system()
        result = compute_axial_initial_guess(system, 2, 0.01)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_state_shape_is_6(self):
        """状态向量形状应为 (6,)。"""
        system = _earth_moon_system()
        state0, _ = compute_axial_initial_guess(system, 2, 0.01)
        assert np.asarray(state0).shape == (6,)

    def test_period_is_positive(self):
        """标称周期应为正值。"""
        system = _earth_moon_system()
        _, T = compute_axial_initial_guess(system, 2, 0.01)
        assert T > 0

    @pytest.mark.parametrize("L", [1, 2, 3])
    def test_z0_is_zero(self, L: int):
        """初始 z 坐标应为 0（x 轴对称，Type B）。"""
        system = _earth_moon_system()
        state0, _ = compute_axial_initial_guess(system, L, 0.01)
        assert state0[2] == pytest.approx(0.0, abs=1e-15)

    @pytest.mark.parametrize("L", [1, 2, 3])
    def test_y0_is_zero(self, L: int):
        """初始 y 坐标应为 0（x 轴上）。"""
        system = _earth_moon_system()
        state0, _ = compute_axial_initial_guess(system, L, 0.01)
        assert state0[1] == pytest.approx(0.0, abs=1e-15)

    @pytest.mark.parametrize("L", [1, 2, 3])
    def test_xdot0_is_zero(self, L: int):
        """初始 x 方向速度应为 0（x 轴垂直穿越）。"""
        system = _earth_moon_system()
        state0, _ = compute_axial_initial_guess(system, L, 0.01)
        assert state0[3] == pytest.approx(0.0, abs=1e-15)

    @pytest.mark.parametrize("L", [1, 2, 3])
    def test_vz0_nonzero(self, L: int):
        """初始 z 方向速度应非零（Type B 特征）。"""
        system = _earth_moon_system()
        state0, _ = compute_axial_initial_guess(system, L, 0.01)
        assert abs(state0[5]) > 1e-10

    def test_vz0_sign_follows_input(self):
        """vz0 符号应与输入一致（正上族、负下族）。"""
        system = _earth_moon_system()
        state_pos, _ = compute_axial_initial_guess(system, 1, 0.01)
        state_neg, _ = compute_axial_initial_guess(system, 1, -0.01)
        assert state_pos[5] > 0
        assert state_neg[5] < 0

    def test_anchor_near_libration_point(self):
        """初始 x 坐标应在 L1 附近。"""
        system = _earth_moon_system()
        state0, _ = compute_axial_initial_guess(system, 1, 0.01)
        lp = system.get_libration_point(LibrationPoint.L1)
        assert abs(state0[0] - lp[0]) < 0.01

    @pytest.mark.parametrize("L", [1, 2, 3])
    def test_state_finite(self, L: int):
        """状态所有分量应为有限值。"""
        system = _earth_moon_system()
        state0, T = compute_axial_initial_guess(system, L, 0.01)
        assert np.all(np.isfinite(state0))
        assert np.isfinite(T)

    @pytest.mark.parametrize("L", [1, 2])
    def test_period_reasonable_range(self, L: int):
        """L1/L2 面内周期应在 Lyapunov 量级（约 2-4 无量纲时间）。"""
        system = _earth_moon_system()
        _, T = compute_axial_initial_guess(system, L, 0.01)
        assert 1.5 < T < 5.0
