"""通用物理常量（全库一套）。

单位统一采用 km / s / kg 系；来源标注在每个常量上方。
"""

from __future__ import annotations

# 真空中的光速（km/s）。SI 定义值，精确。
SPEED_OF_LIGHT_KMS: float = 299792.458

# 万有引力常数 G（km³ / (kg · s²)）。CODATA 2018 推荐值。
GRAVITATIONAL_CONSTANT: float = 6.67430e-20

# 天文单位（km）。IAU 2012 决议 B2。
AU_KM: float = 149597870.7

# 一天的秒数。定义值。
SECONDS_PER_DAY: float = 86400.0

# 儒略年的天数。定义值。
DAYS_PER_JULIAN_YEAR: float = 365.25

# 儒略世纪的天数。定义值。
DAYS_PER_JULIAN_CENTURY: float = 36525.0

# 儒略年的秒数。由定义派生。
SECONDS_PER_JULIAN_YEAR: float = DAYS_PER_JULIAN_YEAR * SECONDS_PER_DAY

# 千米 → 米换算因子。定义值。
KM_TO_M: float = 1000.0

# 太阳辐射通量（W/m²）。工程默认值，GMAT/IERS 1996 兼容。
SOLAR_FLUX_W_M2: float = 1367.0

# 太阳辐射通量（W/m²）。现代 TSI 备选值（Pesce 2023）。
SOLAR_FLUX_TSI_W_M2: float = 1361.0

# 1 AU 处太阳辐射压（N/m²）。由 SOLAR_FLUX_W_M2 / (c · 1000) 派生。
SOLAR_PRESSURE_1AU: float = SOLAR_FLUX_W_M2 / (SPEED_OF_LIGHT_KMS * KM_TO_M)
