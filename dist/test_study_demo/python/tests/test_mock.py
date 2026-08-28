"""
test_mock.py — Mock 全家桶
==========================

unittest.mock 是隔离依赖、验证调用的核心。本文件覆盖 5 个 snippet：
  - py_test_mock        → Mock() 基本对象
  - py_test_patch       → patch 替换模块/对象的方法
  - py_test_spy         → spy（保留原行为 + 记录调用）
  - py_test_mock_return → Mock().return_value 设定返回值
  - py_test_mock_side   → Mock().side_effect 多次返回/抛错
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.calculator import divide, load_config


# ─────────────────────────────────────────────────────────────
# py_test_mock：Mock 基本对象
# ─────────────────────────────────────────────────────────────
def test_mock_basic():
    """py_test_mock 演示：Mock 是万能替身"""
    mock = Mock(return_value=42)
    result = mock()
    assert result == 42
    # 调用历史
    assert mock.called is True
    assert mock.call_count == 1


# ─────────────────────────────────────────────────────────────
# py_test_mock_return：return_value 设定方法返回值
# ─────────────────────────────────────────────────────────────
def test_mock_return_value():
    """py_test_mock_return 演示：方法级 return_value"""
    mock = Mock()
    mock.fetch_user.return_value = {"id": 1, "name": "alice"}

    # 调用 mock.fetch_user(任意参数) 都返回上面设的值
    assert mock.fetch_user(1) == {"id": 1, "name": "alice"}
    assert mock.fetch_user(999) == {"id": 1, "name": "alice"}


# ─────────────────────────────────────────────────────────────
# py_test_mock_side：side_effect 多次返回 / 抛错
# ─────────────────────────────────────────────────────────────
def test_mock_side_effect_iterable():
    """py_test_mock_side 演示：side_effect=列表 时，每次调用依次返回一个值"""
    mock = Mock(side_effect=[1, 2, 3])
    assert mock() == 1
    assert mock() == 2
    assert mock() == 3
    # 第四次再调，列表耗尽 → 抛 StopIteration


def test_mock_side_effect_exception():
    """py_test_mock_side 演示：side_effect=异常 时，调用时直接抛"""
    mock = Mock(side_effect=ValueError("boom"))
    with pytest.raises(ValueError, match="boom"):
        mock()


# ─────────────────────────────────────────────────────────────
# py_test_patch：替换真实函数 / 方法
# ─────────────────────────────────────────────────────────────
def test_patch_replace_function():
    """py_test_patch 演示：临时替换 src.calculator.divide（影响所有引用）"""
    with patch("src.calculator.divide") as mock_divide:
        mock_divide.return_value = 999

        # 即使从其他模块调用 divide，也会拿到 mock 的值
        from src.calculator import divide
        assert divide(10, 2) == 999  # 不是 5.0！

        mock_divide.assert_called_once_with(10, 2)


def test_patch_as_decorator():
    """py_test_patch 也可作装饰器"""
    import src.calculator
    with patch.object(src.calculator, "divide", return_value=-1) as mock_div:
        # 用 src.calculator.divide 而非顶部的 from-import 引用
        result = src.calculator.divide(7, 3)
        assert result == -1
        mock_div.assert_called()


# ─────────────────────────────────────────────────────────────
# py_test_spy：spy（保留原行为 + 记录调用）
# ─────────────────────────────────────────────────────────────
def test_spy_wraps_original():
    """py_test_spy 演示：用 wraps 包裹原方法，调用既执行原逻辑又能被断言"""
    real_divide = divide
    divide_obj = MagicMock(wraps=divide)  # wraps 保留真实实现

    # 这里为了演示 spy 概念，临时替换
    # 实际用法：spy 在测试中监视对象方法
    spy = MagicMock(wraps=lambda a, b: real_divide(a, b))

    assert spy(10, 2) == 5.0
    assert spy.call_count == 1
    assert spy.call_args == ((10, 2), {})


def test_spy_on_method():
    """py_test_spy 演示：监视 dict.get 这种内置方法（场景：验证被调用次数）"""
    d = {"a": 1, "b": 2}
    spy = MagicMock(wraps=d.get)
    spy("a")  # 不会真的修改 d，但 spy 记录了调用
    spy.assert_called_once_with("a")
