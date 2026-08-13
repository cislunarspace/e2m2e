"""segmented 星历时间轴对齐回归测试。

回归 bug：``ForceModel._prepare_t_eval`` 在 t_eval 末尾自动追加段终点 tf，
``design_orbit`` 的 segmented 逐段积分把每段的 tf 端点状态一并拼进
``states_dense``，位置数组（756 点）比时间网格 ``et_grid``（731 点）多出
段数个点；``batch_j2000_to_synodic`` 按索引把位置与旋转时刻配对，错位逐段
累积，星历会合系曲线一圈一圈偏离 Halo 轨道（GUI 观感"慢慢发散"）。

用 GUI 默认参数的 30 天 Halo（L2、30000 km、phase 0）端到端回归：
长度一致判据直接对应根因（位置-时间错位），y 对称判据直接对应症状
（错位把 y 拉到单侧 -0.266，正常 ±0.107）。
"""

from __future__ import annotations

import os

import numpy as np
import pytest

from e2m2e.algorithm.design import design_orbit
from e2m2e.api.models import DesignOrbitRequest

_SPICE_KERNEL_DIR = os.environ.get(
    "SPICE_KERNEL_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "kernels"),
)
_SPICE_AVAILABLE = os.path.isdir(_SPICE_KERNEL_DIR) and any(
    f.endswith(".bsp") for f in os.listdir(_SPICE_KERNEL_DIR)
)

pytestmark = [
    pytest.mark.orchestration,
    pytest.mark.spice,
    pytest.mark.skipif(not _SPICE_AVAILABLE, reason="SPICE kernels not available"),
]

DURATION_SEC = 30 * 86400.0
OUTPUT_STEP_SEC = 3600.0
# et_grid = et0 + arange(0, duration + 0.5·step, step)，含首末点
N_EXPECTED = int(DURATION_SEC / OUTPUT_STEP_SEC) + 1


@pytest.fixture(scope="module")
def halo_result():
    """GUI 默认参数的 30 天 Halo segmented 设计，模块内复用一次。"""
    return design_orbit(
        DesignOrbitRequest(
            orbit_type="HALO",
            collinear_point=2,
            amplitude=30000.0,
            phase=0.0,
            duration=DURATION_SEC,
            output_step=OUTPUT_STEP_SEC,
        )
    )


def test_ephemeris_fields_aligned_with_time_grid(halo_result):
    """星历位置/速度/会合系点数必须与时间字段一致（位置-时间错位回归）。"""
    eph = halo_result.ephemeris
    assert len(eph) == N_EXPECTED
    assert len(eph.position_km) == N_EXPECTED
    assert len(eph.velocity_mps) == N_EXPECTED
    assert len(eph.synodic_position) == N_EXPECTED


def test_synodic_y_symmetric(halo_result):
    """会合系 y 振幅对称（错位回归：逐段累积的时间错位把 y 拉到单侧）。"""
    syn = np.asarray(halo_result.ephemeris.synodic_position)
    y = syn[:, 1]
    # 正常 Halo y ∈ ±0.107，|max+min| ≈ 0；错位时 y ∈ [-0.266, 0.010]，
    # |max+min| ≈ 0.256。阈值 0.05 远小于错位特征、远大于正常残差。
    assert abs(y.max() + y.min()) < 0.05, f"会合系 y 不对称: max={y.max():.4f} min={y.min():.4f}"
