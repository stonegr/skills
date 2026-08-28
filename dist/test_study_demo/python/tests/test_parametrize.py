"""
test_parametrize.py — 参数化测试
================================

覆盖 4 个 snippet：
  - py_test_param        → @pytest.mark.parametrize 基本
  - py_test_param_ids    → parametrize + ids 自定义用例名
  - py_test_param_stack  → 多个 parametrize 叠加（笛卡尔积）
  - py_test_subtest      → pytest.subtests 动态子测试
"""

import pytest

from src.calculator import add, divide, factorial, is_prime


# ─────────────────────────────────────────────────────────────
# py_test_param：基本参数化
# ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add_parametrized(a, b, expected):
    """py_test_param 演示：4 组参数跑 4 个独立用例"""
    assert add(a, b) == expected


# ─────────────────────────────────────────────────────────────
# py_test_param_ids：自定义用例名（让测试报告更可读）
# ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "n,expected",
    [
        (0, 1),
        (1, 1),
        (2, 2),
        (3, 6),
        (5, 120),
    ],
    ids=["zero", "one", "two", "three", "five"],
)
def test_factorial_with_ids(n, expected):
    """py_test_param_ids 演示：报告里显示 id 名而不是 0/1/2/3/4"""
    assert factorial(n) == expected


# ─────────────────────────────────────────────────────────────
# py_test_param_stack：多个 parametrize 叠加（自动笛卡尔积）
# ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("a", [1, 2])
@pytest.mark.parametrize("b", [10, 100])
def test_param_stack(a, b):
    """py_test_param_stack 演示：2×2 = 4 个用例"""
    # 跑：a=1,b=10 / a=1,b=100 / a=2,b=10 / a=2,b=100
    assert a * b > 0


# ─────────────────────────────────────────────────────────────
# py_test_subtest：运行时动态生成子测试（依赖 pytest-subtests 插件）
# ─────────────────────────────────────────────────────────────
def test_subtest_divide_by_various(subtests):
    """py_test_subtest 演示：用 subtests.test() 动态跑多组数据"""
    cases = [
        (10, 2, 5.0),
        (10, 4, 2.5),
        (10, 5, 2.0),
        (10, 10, 1.0),
    ]
    for a, b, expected in cases:
        with subtests.test(msg=f"divide({a},{b})"):
            assert divide(a, b) == expected


def test_subtest_is_prime(subtests):
    """py_test_subtest 演示：所有小于 20 的素数"""
    for n in range(20):
        with subtests.test(msg=f"n={n}"):
            expected = n in {2, 3, 5, 7, 11, 13, 17, 19}
            assert is_prime(n) == expected
