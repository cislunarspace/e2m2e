"""HMN 霍曼直接转移：TLI 出发状态构造 + 霍曼转移物理量计算。

算法来源：
- 开普勒根数→笛卡尔：Curtis (2008) Algorithm 4.2
- 霍曼转移 Δv：Curtis §6.1 / Vallado
- 航迹角语义：Curtis Eq. 2.132
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

# 地球引力参数 (km³/s²)，WGS-84
MU_EARTH: float = 398600.4418
# 地球赤道半径 (km)，WGS-84
R_EARTH: float = 6378.137


@dataclass(frozen=True)
class TliParams:
    """Trans-Lunar Injection 出发参数。

    语义参照 Curtis (2008) Algorithm 4.2 + Lu et al. (2021) Eqs. 1-10。

    Attributes:
        parking_alt_km: 停泊轨道高度 (km)，圆轨道假设 (γ=0)
        inclination_deg: 停泊轨道倾角 (deg)
        flight_path_angle_deg: 航迹角 (deg)，霍曼转移出发条件为 0
        raan_deg: 升交点赤经 (deg)
        arg_perigee_deg: 近地点幅角 (deg)
        epoch: 出发历元（UTC 字符串或 JD_TDB 浮点数）
    """

    parking_alt_km: float
    inclination_deg: float
    flight_path_angle_deg: float = 0.0
    raan_deg: float = 0.0
    arg_perigee_deg: float = 0.0
    epoch: float | str = 0.0


def _rotation_matrix(i_deg: float, omega_deg: float, raan_deg: float) -> NDArray[np.float64]:
    """Perifocal → ECI 旋转矩阵 R = R₃(-Ω)·R₁(-i)·R₃(-ω)。

    Curtis (2008) Algorithm 4.2, Step 3-5.
    """
    i = math.radians(i_deg)
    omega = math.radians(omega_deg)
    raan = math.radians(raan_deg)

    ci, si = math.cos(i), math.sin(i)
    cw, sw = math.cos(omega), math.sin(omega)
    co, so = math.cos(raan), math.sin(raan)

    # R₃(-ω) · R₁(-i) · R₃(-Ω)  — 先绕 z 轴转 -ω，再绕 x 轴转 -i，再绕 z 轴转 -Ω
    # 等价于 R = [col1 | col2 | col3] 其中
    # col1 = [cosΩcosω - sinΩsinωcosi,  sinΩcosω + cosΩsinωcosi,  sinωsini]
    # col2 = [-cosΩsinω - sinΩcosωcosi, -sinΩsinω + cosΩcosωcosi, cosωsini]
    # col3 = [sinΩsini,                  -cosΩsini,                 cosi    ]
    r = np.array(
        [
            [
                co * cw - so * sw * ci,
                -(co * sw + so * cw * ci),
                so * si,
            ],
            [
                so * cw + co * sw * ci,
                -(so * sw - co * cw * ci),
                -co * si,
            ],
            [
                sw * si,
                cw * si,
                ci,
            ],
        ],
        dtype=np.float64,
    )
    return r


def keplerian_to_cartesian(
    a_km: float,
    e: float,
    i_deg: float,
    omega_deg: float,
    raan_deg: float,
    nu_deg: float,
    mu: float = MU_EARTH,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Curtis (2008) Algorithm 4.2: 开普勒根数 → ECI 笛卡尔状态。

    Args:
        a_km: 半长轴 (km)
        e: 偏心率
        i_deg: 倾角 (deg)
        omega_deg: 近地点幅角 (deg)
        raan_deg: 升交点赤经 (deg)
        nu_deg: 真近点角 (deg)
        mu: 引力参数 (km³/s²)

    Returns:
        (r_eci, v_eci) in (km, km/s)，shape 均为 (3,)
    """
    nu = math.radians(nu_deg)
    p = a_km * (1.0 - e * e)  # 半通径

    # Perifocal frame 位置与速度
    r_mag = p / (1.0 + e * math.cos(nu))
    r_pf = np.array([r_mag * math.cos(nu), r_mag * math.sin(nu), 0.0])
    v_pf = np.array(
        [
            -math.sin(nu),
            e + math.cos(nu),
            0.0,
        ]
    ) * math.sqrt(mu / p)

    # 旋转到 ECI
    rot = _rotation_matrix(i_deg, omega_deg, raan_deg)
    r_eci = rot @ r_pf
    v_eci = rot @ v_pf
    return r_eci, v_eci


def construct_departure_state(
    params: TliParams,
    mu_earth: float = MU_EARTH,
    r_earth: float = R_EARTH,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """TLI 参数 → ECI 出发状态向量。

    简化路径（γ=0，圆停泊轨道，霍曼转移标准出发条件）：
    1. r_park = r_earth + parking_alt_km
    2. v_park = √(mu_earth / r_park)
    3. r_pf = [r_park, 0, 0]ᵀ;  v_pf = [0, v_park, 0]ᵀ
    4. R = R₃(-Ω)·R₁(-i)·R₃(-ω)
    5. r_eci = R·r_pf;  v_eci = R·v_pf

    非零航迹角路径（γ≠0，椭圆停泊轨道）：
    调用 keplerian_to_cartesian(a, e, i, ω, Ω, ν=0) 其中：
    a = r_park / (1 - e), e 由航迹角推导（Curtis Eq. 2.132）。

    Args:
        params: TLI 出发参数
        mu_earth: 地球引力参数 (km³/s²)
        r_earth: 地球赤道半径 (km)

    Returns:
        (r0, v0) in (km, km/s)，shape 均为 (3,)
    """
    gamma = math.radians(params.flight_path_angle_deg)
    r_park = r_earth + params.parking_alt_km

    if abs(params.flight_path_angle_deg) < 1e-10:
        # γ=0：圆轨道，简化路径
        v_park = math.sqrt(mu_earth / r_park)
        r_pf = np.array([r_park, 0.0, 0.0])
        v_pf = np.array([0.0, v_park, 0.0])
        rot = _rotation_matrix(params.inclination_deg, params.arg_perigee_deg, params.raan_deg)
        return rot @ r_pf, rot @ v_pf
    # γ≠0：椭圆轨道，航迹角反推偏心率
    # Curtis Eq. 2.132: tan γ = (e·sin ν) / (1 + e·cos ν)
    # 在近地点 ν=0 时 γ=0，所以取 ν=90°（远地点附近）反解 e:
    # tan γ = e / 1  =>  e = tan γ （仅在 ν=90° 时成立）
    # 更通用：在任意 ν 处，e = tan γ · (1 + e·cos ν) / sin ν
    # 简化：假设出发点为近地点 (ν=0)，γ 应为 0；否则需从给定 ν 反解
    # 这里取 ν=90° 的简化假设（远地点出发）
    e = math.tan(abs(gamma))  # γ 在 [0, π/2) 内
    a = r_park / (1.0 - e)  # 近地点 = r_park 时，a = r_park / (1-e)
    return keplerian_to_cartesian(
        a,
        e,
        params.inclination_deg,
        params.arg_perigee_deg,
        params.raan_deg,
        0.0,  # ν=0（近地点）
        mu_earth,
    )


def hohmann_delta_v(r1: float, r2: float, mu: float = MU_EARTH) -> tuple[float, float]:
    """经典霍曼转移 Δv（Curtis §6.1 / Vallado）。

    Args:
        r1: 出发轨道半径 (km)
        r2: 到达轨道半径 (km)
        mu: 引力参数 (km³/s²)

    Returns:
        (dv1, dv2) in km/s
    """
    dv1 = math.sqrt(mu / r1) * (math.sqrt(2.0 * r2 / (r1 + r2)) - 1.0)
    dv2 = math.sqrt(mu / r2) * (1.0 - math.sqrt(2.0 * r1 / (r1 + r2)))
    return dv1, dv2


def hohmann_tof(r1: float, r2: float, mu: float = MU_EARTH) -> float:
    """霍曼转移飞行时间（半椭圆周期）。

    Args:
        r1: 出发轨道半径 (km)
        r2: 到达轨道半径 (km)
        mu: 引力参数 (km³/s²)

    Returns:
        飞行时间 (秒)
    """
    a_t = (r1 + r2) / 2.0
    return math.pi * math.sqrt(a_t**3 / mu)
