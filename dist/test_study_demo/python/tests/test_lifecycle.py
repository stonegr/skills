"""
test_lifecycle.py — 测试生命周期钩子
====================================

覆盖 4 个 snippet：
  - py_test_setup         → setup_module / setup_function（模块/函数级 setup）
  - py_test_teardown      → teardown_function（函数级 teardown）
  - py_test_class_setup   → setup_class / teardown_class（类级 setup/teardown）
  - py_test_finalizer     → 同 test_exception.py，本文件演示类内 finalizer

注：xUnit-style 的 setup/teardown 在 pytest 中仍可用，但推荐用 fixture（见 test_fixture.py）。
"""

import pytest

from src.calculator import divide


# ─────────────────────────────────────────────────────────────
# 模块级 setup_module：整个模块第一个测试前执行一次
# ─────────────────────────────────────────────────────────────
def setup_module(module):
    """py_test_setup 演示：模块加载后第一个用例前执行"""
    print("\n[lifecycle] setup_module → 模块初始化")


def teardown_module(module):
    """模块所有用例结束后执行一次"""
    print("\n[lifecycle] teardown_module → 模块清理")


# ─────────────────────────────────────────────────────────────
# 函数级 setup_function / teardown_function：每个用例前后都执行
# ─────────────────────────────────────────────────────────────
def setup_function(function):
    """py_test_setup 函数级：每个测试函数前执行"""
    print(f"\n[lifecycle] setup_function → 准备 {function.__name__}")


def teardown_function(function):
    """py_test_teardown 函数级：每个测试函数后执行"""
    print(f"[lifecycle] teardown_function → 收尾 {function.__name__}")


def test_divide_normal():
    """用例 1：受 setup_function / teardown_function 包裹"""
    assert divide(10, 2) == 5


def test_divide_negative():
    """用例 2：再次 setup + teardown"""
    assert divide(-10, 2) == -5


# ─────────────────────────────────────────────────────────────
# 类级 setup_class / teardown_class
# ─────────────────────────────────────────────────────────────
class TestDivideClass:
    """py_test_class_setup 演示：整个测试类前后各执行一次 setup_class / teardown_class"""

    @classmethod
    def setup_class(cls):
        print("\n[lifecycle] setup_class → 类共享资源初始化")

    @classmethod
    def teardown_class(cls):
        print("\n[lifecycle] teardown_class → 类共享资源清理")

    def test_divide_by_one(self):
        assert divide(42, 1) == 42

    def test_divide_returns_float(self):
        result = divide(10, 4)
        assert result == 2.5


# ─────────────────────────────────────────────────────────────
# 类内 setup_method / teardown_method：每个方法前后
# ─────────────────────────────────────────────────────────────
class TestPerMethod:
    """类内 setup_method / teardown_method：每个方法都执行"""

    def setup_method(self, method):
        print(f"\n[lifecycle] setup_method → {method.__name__}")

    def teardown_method(self, method):
        print(f"[lifecycle] teardown_method → {method.__name__}")

    def test_one(self):
        assert True

    def test_two(self):
        assert True
