"""天体参数目录。

按天体组织，每个天体提供各基准下的 GM、半径、扁率、NAIF ID、自转角速度等。
半径区分两种语义：
- ``mean_radius_km``：平均/赤道半径，用于阴影、SRP、相对论等几何计算；
- ``gravity_ref_radius_km``：重力场参考半径，来自系数文件头，用于球谐、
  固潮等重力模型。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .sources import ConstantSource


@dataclass(frozen=True)
class Body:
    """天体参数。

    ``gm_by_datum`` 为各基准下的引力参数（km³/s²）；``mean_radius_km`` 为
    几何/制图平均半径；``gravity_ref_radius_km`` 为重力场系数文件给出的
    参考半径；``naif_id`` 为 SPICE/NAIF 整数 ID；``rotation_rate_rad_s`` 为
    自转角速度（rad/s），按场景分别命名。
    """

    name: str
    gm_by_datum: dict[str, float] = field(default_factory=dict)
    mean_radius_km: float | None = None
    mean_radius_source: ConstantSource | None = None
    gravity_ref_radius_km: float | None = None
    gravity_ref_radius_source: ConstantSource | None = None
    flattening: float | None = None
    flattening_source: ConstantSource | None = None
    naif_id: int | None = None
    rotation_rate_iers_rad_s: float | None = None
    rotation_rate_iers_source: ConstantSource | None = None
    rotation_rate_gmat_rad_s: float | None = None
    rotation_rate_gmat_source: ConstantSource | None = None


#: 太阳。
SUN = Body(
    name="SUN",
    gm_by_datum={
        "DE421": 1.32712428e11,
        "DE440": 1.32712440018e11,
    },
    mean_radius_km=696000.0,
    mean_radius_source=ConstantSource.LITERATURE,
    naif_id=10,
)

#: 地球。
EARTH = Body(
    name="EARTH",
    gm_by_datum={
        "DE421": 398600.4415,
        "DE440": 398600.435507,
        "WGS84": 398600.4418,
    },
    mean_radius_km=6378.137,
    mean_radius_source=ConstantSource.WGS84,
    gravity_ref_radius_km=6378.1363,
    gravity_ref_radius_source=ConstantSource.GMAT,
    flattening=1.0 / 298.257223563,
    flattening_source=ConstantSource.WGS84,
    naif_id=399,
    rotation_rate_iers_rad_s=7.292115146706979e-5,
    rotation_rate_iers_source=ConstantSource.IERS,
    rotation_rate_gmat_rad_s=7.29211585530e-5,
    rotation_rate_gmat_source=ConstantSource.GMAT,
)

#: 月球。
MOON = Body(
    name="MOON",
    gm_by_datum={
        "DE421": 4902.8005821478,
        "DE440": 4902.800118,
    },
    mean_radius_km=1737.4,
    mean_radius_source=ConstantSource.IAU2015,
    gravity_ref_radius_km=1738.0,
    gravity_ref_radius_source=ConstantSource.GMAT,
    naif_id=301,
)

#: 地月系质心（Earth-Moon Barycenter）。
EMB = Body(
    name="EMB",
    gm_by_datum={
        "DE421": 403503.242083,
        "DE440": 403503.235502,
    },
    naif_id=3,
)

#: 水星。
MERCURY = Body(
    name="MERCURY",
    gm_by_datum={},
    naif_id=199,
)

#: 金星。
VENUS = Body(
    name="VENUS",
    gm_by_datum={},
    naif_id=299,
)

#: 火星。
MARS = Body(
    name="MARS",
    gm_by_datum={},
    naif_id=499,
)

#: 木星。
JUPITER = Body(
    name="JUPITER",
    gm_by_datum={},
    naif_id=599,
)

#: 土星。
SATURN = Body(
    name="SATURN",
    gm_by_datum={},
    naif_id=699,
)

#: 天王星。
URANUS = Body(
    name="URANUS",
    gm_by_datum={},
    naif_id=799,
)

#: 海王星。
NEPTUNE = Body(
    name="NEPTUNE",
    gm_by_datum={},
    naif_id=899,
)

#: 冥王星。
PLUTO = Body(
    name="PLUTO",
    gm_by_datum={},
    naif_id=999,
)
