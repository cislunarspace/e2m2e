"""Facade 结果翻译和 JSON 兼容序列化测试。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from e2m2e.api.facade import (
    _control_result_to_response,
    _design_result_to_response,
    _details_to_dict,
    _ephemeris_to_dict,
)
from e2m2e.data.constants import Datum
from e2m2e.data.templates import ConvergenceState, FailureCause
from e2m2e.data.types.maneuver import ManeuverTable
from e2m2e.data.types.sk_statistic import SKStatistic
from e2m2e.data.types.trajectory import EphemerisTable

pytestmark = pytest.mark.interface


def _make_ephemeris(n: int = 3, with_jd: bool = False) -> EphemerisTable:
    return EphemerisTable(
        year=np.full(n, 2024, dtype=int),
        month=np.full(n, 1, dtype=int),
        day=np.full(n, 1, dtype=int),
        hour=np.arange(n, dtype=int),
        minute=np.zeros(n, dtype=int),
        second=np.zeros(n, dtype=float),
        position_km=np.arange(n * 3, dtype=float).reshape(n, 3),
        velocity_mps=np.full((n, 3), 1000.0),
        synodic_position=np.full((n, 3), 0.5),
        times_jd_tdb=np.linspace(2460310.0, 2460311.0, n) if with_jd else None,
    )


def _make_design_result(*, with_system: bool = True):
    system = SimpleNamespace(mu=Datum.DE421.mu) if with_system else None
    return SimpleNamespace(
        orbit_type="DRO",
        epoch_utc="2024-01-01T00:00:00.000",
        duration_day=365.25,
        initial_state=np.zeros(6),
        ephemeris=_make_ephemeris(),
        cr3bp_orbit=SimpleNamespace(
            states=np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 0.1, 0.1, 0.1]]),
            times=np.array([0.0, 1.234]),
            system=system,
        ),
        cr3bp_jacobi=3.16,
        correction=SimpleNamespace(iterations=4),
        force_config={"sun_body": 1},
        status="converged",
        cause="none",
        message="任务完成",
        drift_e=None,
        drift_aop_deg=None,
        drift_rp_km=None,
        secular_aop_rate_deg_per_year=None,
    )


def _make_control_result(*, controlled: bool):
    return SimpleNamespace(
        num_failed=1,
        status="converged" if controlled else "failed",
        cause="none" if controlled else "unknown",
        message="任务完成" if controlled else "全部蒙特卡洛样本失败",
        sk_statistic=SKStatistic(rows=np.zeros((2, 3)), num_failed=1),
        maneuvers=ManeuverTable(mjd_tdb=np.array([60000.0]), delta_v_mps=np.array([1.0])),
        controlled_ephemeris=_make_ephemeris(n=2) if controlled else None,
    )


class TestDetailsSerialization:
    def test_serializes_nested_numpy_values(self):
        result = _details_to_dict(
            {"array": np.array([1.0, 2.0]), "nested": {"tuple": (np.array([3.0]), 4.0)}}
        )
        assert result == {"array": [1.0, 2.0], "nested": {"tuple": [[3.0], 4.0]}}

    def test_serializes_dataclass_and_none(self):
        details = _details_to_dict(
            ManeuverTable(mjd_tdb=np.array([60000.0]), delta_v_mps=np.array([1.0]))
        )
        assert details["mjd_tdb"] == [60000.0]
        assert _details_to_dict(None) == {}


class TestEphemerisSerialization:
    def test_preserves_all_public_columns_as_json_values(self):
        result = _ephemeris_to_dict(_make_ephemeris(n=2))
        assert result is not None
        assert result["position_km"] == [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]]
        assert result["velocity_mps"] == [[1000.0, 1000.0, 1000.0]] * 2
        assert set(result) == {
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
            "position_km",
            "velocity_mps",
            "synodic_position",
            "times_jd_tdb",
        }
        assert result["times_jd_tdb"] is None

    def test_serializes_optional_jd_and_none_input(self):
        result = _ephemeris_to_dict(_make_ephemeris(with_jd=True))
        assert result is not None
        assert result["times_jd_tdb"] == pytest.approx([2460310.0, 2460310.5, 2460311.0])
        assert _ephemeris_to_dict(None) is None


class TestDesignResponseTranslation:
    def test_translates_geometry_and_status(self):
        response = _design_result_to_response(_make_design_result())
        assert response.orbit_type == "DRO"
        assert response.status is ConvergenceState.CONVERGED
        assert response.cause is FailureCause.NONE
        assert response.initial_state == [0.0] * 6
        assert response.states[1] == [1.0, 1.0, 1.0, 0.1, 0.1, 0.1]
        assert response.times == [0.0, 1.234]
        assert response.mu == pytest.approx(Datum.DE421.mu)
        assert response.correction_iterations == 4

    def test_translates_missing_system_as_optional_mu(self):
        response = _design_result_to_response(_make_design_result(with_system=False))
        assert response.mu is None
        assert len(response.states) == 2


class TestControlResponseTranslation:
    def test_translates_controlled_ephemeris(self):
        response = _control_result_to_response(
            _make_control_result(controlled=True), mu=Datum.DE421.mu
        )
        assert response.status is ConvergenceState.CONVERGED
        assert response.cause is FailureCause.NONE
        assert response.num_failed == 1
        assert response.controlled_ephemeris is not None
        assert response.mu == pytest.approx(Datum.DE421.mu)

    def test_preserves_missing_ephemeris_for_all_failed_samples(self):
        response = _control_result_to_response(_make_control_result(controlled=False), mu=None)
        assert response.status is ConvergenceState.FAILED
        assert response.cause is FailureCause.UNKNOWN
        assert response.controlled_ephemeris is None
        assert response.mu is None
