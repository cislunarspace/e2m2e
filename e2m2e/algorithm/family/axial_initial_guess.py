"""Axial 轨道一阶解析初猜（Gómez Type B 分岔族）。

Axial 轨道从 planar Lyapunov 轨道通过 pitchfork 分岔产生（Gómez Type B），
关于 x 轴对称。与 Halo（Type A, xz 平面对称）的区别：

- Halo: 初始 (x₀, 0, z₀, 0, ẏ₀, 0) — 从 xz 平面出发，ż₀=0
- Axial: 初始 (x₀, 0, 0, 0, ẏ₀, ż₀) — 从 xy 平面出发，z₀=0，ż₀≠0

Axial 轨道从 xy 平面获得面外速度后，在半周期返回 xy 平面
（z 翻转：z(t) = -z(T-t)）。面外振幅由 |ż₀| 控制。

初猜构造：面内部分取 Lyapunov 模态（x 轴上穿越点），面外部分
施加一个小垂直速度 ż₀。

References:
    Gómez, G., et al. (2001). Dynamics and mission design near libration
    points, Vol. III, Sec. 3.3. Type B 垂直临界分岔。
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from ..dynamics import CR3BP_System
from .lissajous_initial_guess import _linear_modes


def compute_axial_initial_guess(
    system: CR3BP_System,
    collinear_point: int,
    vz0: float,
) -> tuple[npt.NDArray[np.floating], float]:
    """构造 Axial 轨道一阶初猜状态。

    初始状态在 x 轴上：(x_L, 0, 0, 0, 0, vz0)，叠加小量面内模态。

    Args:
        system: CR3BP 系统（含已计算的平动点）。
        collinear_point: 共线点编号 1/2/3。
        vz0: 初始 z 方向速度（无量纲 DU/TU），带符号区分上/下族。

    Returns:
        (state0, nominal_period)：t=0 的 6 维状态（无量纲 synodic），
        与面内标称周期 2π/ω_xy。
    """
    if not system.has_L_points:
        system.compute_libration_points()

    omega_xy, _v_xy, _omega_z, _v_z, x_L = _linear_modes(system, collinear_point)

    # 初始状态：从平动点出发，x 轴上，带面外速度
    state0 = np.zeros(6)
    state0[0] = x_L
    state0[5] = vz0

    nominal_period = 2.0 * np.pi / omega_xy
    return state0, nominal_period
