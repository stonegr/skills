"""
test_smoke.py — 冒烟测试：覆盖 py_test_func / py_test_class / py_test_skip / py_test_xfail
=====================================================================================

最基础的 4 个测试 snippet：
  - py_test_func      → def test_xxx() 顶层测试函数
  - py_test_class     → class TestXxx 用类组织一组相关测试
  - py_test_skip      → @pytest.mark.skip(reason=...) 主动跳过
  - py_test_xfail     → @pytest.mark.xfail(reason=...) 预期失败（已知 bug）
"""

import pytest

from src.calculator import add, is_prime, multiply


# ─────────────────────────────────────────────────────────────
# py_test_func：顶层 def test_xxx() 函数（最常见的 pytest 写法）
# ─────────────────────────────────────────────────────────────
def test_add_two_positives():
    """py_test_func 演示：基本测试函数"""
    result = add(2, 3)
    assert result == 5


def test_multiply_by_zero():
    """py_test_func 演示：函数名 test_ 开头即可被 pytest 自动发现"""
    assert multiply(5, 0) == 0


# ─────────────────────────────────────────────────────────────
# py_test_class：用类组织一组相关测试（共享 setup 或仅作分组）
# ─────────────────────────────────────────────────────────────
class TestIsPrime:
    """py_test_class 演示：一个测试类里放多个相关用例"""

    def test_prime_2(self):
        assert is_prime(2) is True

    def test_prime_7(self):
        assert is_prime(7) is True

    def test_composite_4(self):
        assert is_prime(4) is False

    def test_below_two_is_not_prime(self):
        assert is_prime(1) is False
        assert is_prime(0) is False
        assert is_prime(-5) is False


# ─────────────────────────────────────────────────────────────
# py_test_skip：跳过测试（功能还没实现 / 临时禁用）
# ─────────────────────────────────────────────────────────────
@pytest.mark.skip(reason="功能尚未实现，等后端联调")
def test_not_implemented_yet():
    """py_test_skip 演示：跳过，pytest 输出显示 SKIPPED"""
    assert add(1, 1) == 3  # 这行不会执行


# ─────────────────────────────────────────────────────────────
# py_test_xfail：预期失败（已知 bug / 预期会抛错的边界用例）
# ─────────────────────────────────────────────────────────────
@pytest.mark.xfail(reason="已知 bug：is_prime 对负数抛错而非返回 False")
def test_known_bug_negative_input():
    """py_test_xfail 演示：预期失败，跑过即 XFAIL（不算失败）"""
    assert is_prime(-5) is False  # 实际抛 ValueError → 符合预期
