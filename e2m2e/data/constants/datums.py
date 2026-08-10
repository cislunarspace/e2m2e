"""基准集定义。

以"基准（datum）"为一等概念，每套基准内部 GM、μ、特征长度、特征时间
来自同一来源，保持自洽。阶段 1 先包含 DE421、DE440、WGS-84 三套现成
数据；后续阶段再补充 DE430、IAU2015 等基准。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .sources import ConstantSource
from .universal import SECONDS_PER_DAY


@dataclass(frozen=True)
class _DatumSpec:
    """单个基准集的内部字段。

    所有 GM 量单位均为 km³/s²；特征长度单位为 km；特征时间单位为 s。
    字段标注 ``source`` 给出每个值的原始出处（可能与基准本身不同，如
    WGS-84 基准中的地球半径来自 WGS-84，但基准标签仍是 WGS-84）。
    """

    source: ConstantSource
    # 地月系统质量比（无量纲）。
    mu: float | None = None
    # 地月特征长度 l*（km）。
    char_length_km: float | None = None
    # 地月特征时间 t*（s）。
    char_time_s: float | None = None
    # 地球引力参数（km³/s²）。
    earth_gm: float | None = None
    # 月球引力参数（km³/s²）。
    moon_gm: float | None = None
    # 太阳引力参数（km³/s²）。
    sun_gm: float | None = None
    # 地月系质心（EMB）引力参数（km³/s²）。
    emb_gm: float | None = None
    # 地球赤道半径（km）。
    earth_radius_km: float | None = None
    # 地球扁率（无量纲）。
    earth_flattening: float | None = None

    # 每个字段的出处元数据（字段名 → ConstantSource）。
    field_sources: dict[str, ConstantSource] = field(default_factory=dict)


class _DatumEnumMeta(type):
    """支持 ``Datum.DE421.mu`` 形式的命名空间访问。"""

    _members: dict[str, _DatumSpec] = {}

    def __getattr__(cls, name: str) -> _DatumSpec:
        try:
            return cls._members[name]
        except KeyError as exc:
            raise AttributeError(f"Datum 没有名为 {name!r} 的基准") from exc

    def __iter__(cls):
        return iter(cls._members.items())

    def __contains__(cls, name: object) -> bool:
        return name in cls._members


class Datum(metaclass=_DatumEnumMeta):
    """物理常数基准集。

    用法示例::

        from e2m2e.data.constants import Datum
        print(Datum.DE421.mu)
        print(Datum.DE440.earth_gm)
        print(Datum.WGS84.earth_radius_km)
    """

    # 来源：Folta 2022 Table 2；NASA JPL DE421。
    DE421 = _DatumSpec(
        source=ConstantSource.DE421,
        mu=0.012150585350562453,
        char_length_km=384400.0,
        char_time_s=375190.2588926273,
        earth_gm=398600.4415,
        moon_gm=4902.8005821478,
        sun_gm=1.32712428e11,
        emb_gm=403503.242083,
        field_sources={
            "mu": ConstantSource.DE421,
            "char_length_km": ConstantSource.LITERATURE,
            "char_time_s": ConstantSource.LITERATURE,
            "earth_gm": ConstantSource.DE421,
            "moon_gm": ConstantSource.DE421,
            "sun_gm": ConstantSource.DE421,
            "emb_gm": ConstantSource.DE421,
        },
    )

    # 来源：JPL DE440 星历。
    # 特征长度/特征时间由 GM 与星历历元推导，当前阶段未提供，避免编造。
    DE440 = _DatumSpec(
        source=ConstantSource.DE440,
        mu=0.012150584394709708,
        earth_gm=398600.435507,
        moon_gm=4902.800118,
        sun_gm=1.32712440018e11,
        emb_gm=403503.235502,
        field_sources={
            "mu": ConstantSource.DE440,
            "earth_gm": ConstantSource.DE440,
            "moon_gm": ConstantSource.DE440,
            "sun_gm": ConstantSource.DE440,
            "emb_gm": ConstantSource.DE440,
        },
    )

    # 来源：WGS-84 / GMAT R2026a 默认地球形状模型。
    WGS84 = _DatumSpec(
        source=ConstantSource.WGS84,
        earth_gm=398600.4418,
        earth_radius_km=6378.137,
        earth_flattening=1.0 / 298.257223563,
        field_sources={
            "earth_gm": ConstantSource.WGS84,
            "earth_radius_km": ConstantSource.WGS84,
            "earth_flattening": ConstantSource.WGS84,
        },
    )

    # DE430 与 DE440 使用相同的 GM 表作为占位；阶段 1 未细分。
    DE430 = DE440


Datum._members = {  # type: ignore[attr-defined]
    "DE421": Datum.DE421,
    "DE430": Datum.DE430,
    "DE440": Datum.DE440,
    "WGS84": Datum.WGS84,
}

# 预计算 SECONDS_PER_DAY 在派生量中可能用到；避免 lint 报告未使用。
_ = SECONDS_PER_DAY
