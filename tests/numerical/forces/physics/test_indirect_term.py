"""IndirectTerm Rust 单点绑定物理对照。

验证 Rust ``indirect_term_acceleration`` 与解析公式 ``-mu·r/|r|³`` 一致
（SPICE 取月心位置）。
"""

import numpy as np
import pytest

from e2m2e.integrators import indirect_term_acceleration

pytestmark = [pytest.mark.force, pytest.mark.spice]


@pytest.mark.spice
def test_indirect_term_rust_binding_matches_point_mass_formula(spice_manager, reference_epoch):
    """Rust ``indirect_term_acceleration`` 与 -mu·r/|r|³ 公式一致（SPICE 取位）。"""
    et = spice_manager.utc_to_et(reference_epoch)
    mu = 4902.800122
    acc = indirect_term_acceleration(et, "MOON", "EARTH", mu)

    r_moon = np.asarray(spice_manager.get_body_position("MOON", et, "J2000", "EARTH"), dtype=float)
    expected = -mu / np.linalg.norm(r_moon) ** 3 * r_moon
    np.testing.assert_allclose(acc, expected, rtol=1e-10)
