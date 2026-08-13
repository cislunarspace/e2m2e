"""CR3BP 运动方程、Jacobi 不变量与传播接口测试。"""

import numpy as np
import pytest
from numpy.testing import assert_allclose

pytestmark = pytest.mark.theory


@pytest.fixture
def dynamics(earth_moon_dynamics):
    return earth_moon_dynamics


@pytest.fixture
def sample_state():
    return np.array([0.8, 0.0, 0.0, 0.0, 0.1, 0.0])


def test_state_equations_have_kinematic_position_derivatives(dynamics):
    state = np.array([0.5, -0.2, 0.1, 1.0, 2.0, 3.0])
    derivative = dynamics.equations_of_motion(0.0, state)
    assert_allclose(derivative[:3], state[3:])


def test_zero_z_state_stays_in_the_xy_plane(dynamics):
    state = np.array([0.8, 0.0, 0.0, 0.0, 0.0, 0.0])
    derivative = dynamics.equations_of_motion(0.0, state)
    assert derivative[2] == 0.0
    assert derivative[5] == 0.0


def test_pseudo_potential_acceleration_is_symmetric_under_y_reflection(dynamics):
    state_plus = np.array([0.8, 0.1, 0.0, 0.0, 0.0, 0.0])
    state_minus = np.array([0.8, -0.1, 0.0, 0.0, 0.0, 0.0])
    derivative_plus = dynamics.equations_of_motion(0.0, state_plus)
    derivative_minus = dynamics.equations_of_motion(0.0, state_minus)

    assert derivative_plus[3] == pytest.approx(derivative_minus[3])
    assert derivative_plus[4] == pytest.approx(-derivative_minus[4])
    assert derivative_plus[5] == pytest.approx(derivative_minus[5])


def test_equations_remain_finite_at_machine_scale_singularity(dynamics):
    mu = dynamics.system.mu
    for x in (-mu, 1.0 - mu):
        derivative = dynamics.equations_of_motion(0.0, np.array([x, 0.0, 0.0, 0.0, 0.1, 0.0]))
        assert np.all(np.isfinite(derivative))


def test_jacobi_constant_is_conserved_during_propagation(dynamics, sample_state):
    result = dynamics.propagate(sample_state, (0.0, 2.0), with_jacobi=True)
    assert result["jacobi_error"] < 1e-4
    assert len(result["jacobi"]) == len(result["states"])


def test_jacobi_constant_implementation_agrees_with_system(dynamics, sample_state):
    assert dynamics.compute_jacobi_constant(sample_state) == pytest.approx(
        dynamics.system.get_jacobi_constant(sample_state)
    )
