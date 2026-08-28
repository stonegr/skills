"""
test_assertion.py — 断言 5 件套
==============================

覆盖 5 个断言 snippet：
  - py_test_assert_eq      → assert actual == expected
  - py_test_assert_ne      → assert actual != expected
  - py_test_assert_true    → assert condition
  - py_test_assert_in      → assert item in container
  - py_test_assert_approx  → pytest.approx（处理浮点精度）
"""

import pytest

from src.calculator import add, factorial, is_prime


def test_assert_eq():
    """py_test_assert_eq：相等断言（最常用）"""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    # 浮点比较见 test_assert_approx（用 pytest.approx 而非 ==）


def test_assert_ne():
    """py_test_assert_ne：不等断言"""
    assert add(2, 3) != 6
    assert is_prime(4) is not True  # 也可写成 != True


def test_assert_true():
    """py_test_assert_true：真值断言"""
    assert is_prime(7)
    assert is_prime(2)
    assert not is_prime(1)
    assert not is_prime(9)


def test_assert_in():
    """py_test_assert_in：包含断言"""
    primes_under_20 = [2, 3, 5, 7, 11, 13, 17, 19]
    assert 7 in primes_under_20
    assert 100 not in primes_under_20
    # 字符串包含
    assert "snippet" in "py_test_snippet_xxx"


def test_assert_approx():
    """py_test_assert_approx：浮点近似（解决 0.1+0.2 != 0.3 问题）"""
    # 直接 == 会失败：0.1 + 0.2 == 0.30000000000000004
    # 用 pytest.approx 比较，默认 rel=1e-6
    assert add(0.1, 0.2) == pytest.approx(0.3)
    assert add(0.1, 0.2) == pytest.approx(0.3, rel=1e-9)  # 自定义精度

    # 数学常量
    import math
    assert math.pi == pytest.approx(3.14159265, abs=1e-5)  # abs 绝对误差
