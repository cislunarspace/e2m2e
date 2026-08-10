"""e2m2e/data/constants/ 单元测试。"""

import math

import pytest

from e2m2e.data.constants import (
    AU_KM,
    EARTH,
    EMB,
    GRAVITATIONAL_CONSTANT,
    KM_TO_M,
    MOON,
    SECONDS_PER_DAY,
    SECONDS_PER_JULIAN_YEAR,
    SOLAR_FLUX_TSI_W_M2,
    SOLAR_FLUX_W_M2,
    SOLAR_PRESSURE_1AU,
    SPEED_OF_LIGHT_KMS,
    SUN,
    Datum,
)

pytestmark = pytest.mark.data


class TestUniversalConstants:
    def test_speed_of_light(self):
        assert SPEED_OF_LIGHT_KMS == 299792.458

    def test_gravitational_constant(self):
        assert GRAVITATIONAL_CONSTANT == 6.67430e-20

    def test_astronomical_unit(self):
        assert AU_KM == 149597870.7

    def test_time_constants(self):
        assert SECONDS_PER_DAY == 86400.0
        assert SECONDS_PER_JULIAN_YEAR == 365.25 * 86400.0

    def test_unit_conversion(self):
        assert KM_TO_M == 1000.0

    def test_solar_flux_and_pressure(self):
        assert SOLAR_FLUX_W_M2 == 1367.0
        assert SOLAR_FLUX_TSI_W_M2 == 1361.0
        expected_pressure = SOLAR_FLUX_W_M2 / (SPEED_OF_LIGHT_KMS * KM_TO_M)
        assert pytest.approx(SOLAR_PRESSURE_1AU) == expected_pressure


class TestDatumValues:
    def test_de421_values(self):
        assert Datum.DE421.mu == 0.012150585350562453
        assert Datum.DE421.earth_gm == 398600.4415
        assert Datum.DE421.moon_gm == 4902.8005821478
        assert Datum.DE421.sun_gm == 1.32712428e11
        assert Datum.DE421.emb_gm == 403503.242083
        assert Datum.DE421.char_length_km == 384400.0
        assert Datum.DE421.char_time_s == 375190.2588926273

    def test_de440_values(self):
        assert Datum.DE440.mu == 0.012150584394709708
        assert Datum.DE440.earth_gm == 398600.435507
        assert Datum.DE440.moon_gm == 4902.800118
        assert Datum.DE440.sun_gm == 1.32712440018e11
        assert Datum.DE440.emb_gm == 403503.235502

    def test_wgs84_values(self):
        assert Datum.WGS84.earth_gm == 398600.4418
        assert Datum.WGS84.earth_radius_km == 6378.137
        assert Datum.WGS84.earth_flattening == pytest.approx(1.0 / 298.257223563)


class TestDatumConsistency:
    def test_de421_mu_matches_gm_ratio(self):
        mu_computed = Datum.DE421.moon_gm / (Datum.DE421.earth_gm + Datum.DE421.moon_gm)
        assert Datum.DE421.mu == pytest.approx(mu_computed, rel=1e-15)

    def test_de421_char_time_matches_definition(self):
        total_gm = Datum.DE421.earth_gm + Datum.DE421.moon_gm
        char_time_computed = math.sqrt(Datum.DE421.char_length_km**3 / total_gm)
        assert Datum.DE421.char_time_s == pytest.approx(char_time_computed, rel=1e-12)

    def test_de440_mu_matches_gm_ratio(self):
        mu_computed = Datum.DE440.moon_gm / (Datum.DE440.earth_gm + Datum.DE440.moon_gm)
        assert Datum.DE440.mu == pytest.approx(mu_computed, rel=1e-15)


class TestBodies:
    def test_earth(self):
        assert EARTH.naif_id == 399
        assert EARTH.mean_radius_km == 6378.137
        assert EARTH.gravity_ref_radius_km == 6378.1363
        assert EARTH.rotation_rate_iers_rad_s == 7.292115146706979e-5
        assert EARTH.rotation_rate_gmat_rad_s == 7.29211585530e-5

    def test_moon(self):
        assert MOON.naif_id == 301
        assert MOON.mean_radius_km == 1737.4
        assert MOON.gravity_ref_radius_km == 1738.0

    def test_sun(self):
        assert SUN.naif_id == 10
        assert SUN.mean_radius_km == 696000.0

    def test_emb(self):
        assert EMB.naif_id == 3
        assert EMB.gm_by_datum["DE421"] == 403503.242083
        assert EMB.gm_by_datum["DE440"] == 403503.235502

    def test_planet_naif_ids(self):
        from e2m2e.data.constants import (
            JUPITER,
            MARS,
            MERCURY,
            NEPTUNE,
            PLUTO,
            SATURN,
            URANUS,
            VENUS,
        )

        assert MERCURY.naif_id == 199
        assert VENUS.naif_id == 299
        assert MARS.naif_id == 499
        assert JUPITER.naif_id == 599
        assert SATURN.naif_id == 699
        assert URANUS.naif_id == 799
        assert NEPTUNE.naif_id == 899
        assert PLUTO.naif_id == 999
