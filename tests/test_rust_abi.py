"""Python↔Rust ABI 版本戳散度与行为测试。

验证 Rust 侧 ``_py_abi_version()`` 与 Python 侧 ``_MIN_REQUIRED_RUST_ABI``
一致（CI 散度兜底），以及过期/缺失二进制下的正确失败模式。

本文件标 ``pytest.mark.spice``：需编译扩展（非内核）；无二进制时整文件跳过。
行为测试（monkeypatch 注入，不依赖真实二进制）仍在此文件内，但因模块级
``importorskip`` 会一并跳过；如需无二进制环境运行行为测试，请移至
``tests/data/test_rust_signature_guard.py``（该文件已有等价的缺失/过期测试）。
"""

from __future__ import annotations

import pytest

from e2m2e import integrators as gw

pytestmark = pytest.mark.spice

# 模块级 gate：无编译扩展时跳过全文件（CI 有 .pyd，不跳过）
_py_abi_version = pytest.importorskip(
    "e2m2e._integrators", reason="compiled Rust extension not available"
)._py_abi_version


class TestRustAbiVersion:
    """ABI 版本戳散度与行为契约。"""

    def test_rust_reports_abi_version(self):
        """Rust 扩展暴露 _py_abi_version()，返回正整数。"""
        v = _py_abi_version()
        assert isinstance(v, int)
        assert v >= 1

    def test_divergence_check(self):
        """Rust ABI 版本 >= Python 所需最低版本（防只改一边）。"""
        actual = _py_abi_version()
        assert actual >= gw._MIN_REQUIRED_RUST_ABI, (
            f"ABI 散度：Rust 报 v{actual}，Python 要求 >= v{gw._MIN_REQUIRED_RUST_ABI}。"
            "请同步 bump 两侧常量（见 CONTRIBUTING / docs/plans）。"
        )

    def test_expected_version_matches(self):
        """当前版本已知值断言（等值检查，防忘 bump 任一侧）。"""
        # ── 更新：每次 bump RUST_PY_ABI / _MIN_REQUIRED_RUST_ABI 时同步此处 ──
        assert _py_abi_version() == 1
        assert gw._MIN_REQUIRED_RUST_ABI == 1

    def test_stale_binary_raises_runtime_error(self, monkeypatch):
        """过期二进制（模拟 version < min）→ RuntimeError + maturin 提示。"""
        monkeypatch.setattr(gw, "_MIN_REQUIRED_RUST_ABI", 9999)
        # Reset the cache so the check runs again
        monkeypatch.setattr(gw, "_abi_ok", False)

        with pytest.raises(RuntimeError, match="maturin"):
            gw._check_rust_abi()

    def test_absent_extension_degrades_silently(self, monkeypatch):
        """扩展缺失 → 静默跳过（_abi_ok = True，不抛）。"""
        import sys

        monkeypatch.setitem(sys.modules, "e2m2e._integrators", None)
        monkeypatch.setattr(gw, "_abi_ok", False)
        gw._check_rust_abi()
        assert gw._abi_ok is True
