"""GMAT-compatible 时间尺度与 IAU XYS 链路测试。"""

import numpy as np
import pytest

from e2m2e.algorithm.coordinate.gmat_time import TimeSystemConverter
from e2m2e.algorithm.coordinate.xys import ErfaXysProvider
from e2m2e.data.frames import CoordinateDataError, TaiUtcTable, gmat_fixture_path

pytestmark = pytest.mark.data


def _tai_utc_table() -> TaiUtcTable:
    return TaiUtcTable.from_file(gmat_fixture_path("tai-utc.dat"))


def test_time_converter_preserves_utc_tai_tt_definitions():
    converter = TimeSystemConverter(_tai_utc_table())

    for utc_mjd, tai_minus_utc in [(51544.0, 32.0), (57754.0, 37.0), (61203.0, 37.0)]:
        tai_mjd = converter.utc_mjd_to_tai_mjd(utc_mjd)
        assert tai_mjd == pytest.approx(utc_mjd + tai_minus_utc / 86400.0)
        assert converter.tai_mjd_to_utc_mjd(tai_mjd) == pytest.approx(utc_mjd)
        assert converter.utc_mjd_to_a1_mjd(utc_mjd) == pytest.approx(
            utc_mjd + (tai_minus_utc + 0.0343817) / 86400.0
        )
        assert converter.utc_mjd_to_tt_mjd(utc_mjd) == pytest.approx(
            utc_mjd + (tai_minus_utc + 32.184) / 86400.0
        )


def test_time_converter_keeps_et_as_its_public_epoch():
    converter = TimeSystemConverter(_tai_utc_table())

    assert converter.et_to_tt_mjd(0.0) == pytest.approx(51544.5, abs=1e-8)


@pytest.mark.parametrize(
    ("tt_mjd", "expected"),
    [
        (51544.5, (-2.694638014904722e-05, -2.8004721164764934e-05, -1.0133965177563803e-08)),
        (57754.0, (0.0016391211394910907, -4.7004517266413526e-05, 3.543052006656307e-08)),
        (61203.0, (0.002582493526172671, 2.9498181435383408e-05, -3.3505790903890935e-08)),
    ],
)
def test_erfa_xys_matches_iau_2006_2000a_reference(tt_mjd, expected):
    """参考值来自 SOFA iauXys06a，是 IAU 模型定义而非软件输出基线。"""
    assert ErfaXysProvider().xys(tt_mjd) == pytest.approx(expected)


def test_erfa_xys_rejects_non_finite_epoch():
    provider = ErfaXysProvider()

    with pytest.raises(CoordinateDataError):
        provider.xys(np.nan)

    with pytest.raises(CoordinateDataError):
        provider.xys(np.inf)
