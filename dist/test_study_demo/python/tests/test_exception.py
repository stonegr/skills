"""
test_exception.py — 异常断言
=============================

覆盖 2 个异常 snippet + 1 个 finalizer snippet：
  - py_test_raises        → pytest.raises(ExceptionType) 捕获
  - py_test_raises_match  → pytest.raises(..., match=r"...") 匹配消息
  - py_test_finalizer     → request.addfinalizer 收尾清理
"""

import pytest

from src.calculator import divide, factorial, load_config


# ─────────────────────────────────────────────────────────────
# py_test_raises：基本异常断言
# ─────────────────────────────────────────────────────────────
def test_raises_division_by_zero():
    """py_test_raises 演示：捕获抛出的异常"""
    with pytest.raises(ValueError):
        divide(10, 0)


def test_raises_and_inspect_exception():
    """pytest.raises 还能拿到异常对象做更细粒度断言"""
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)
    assert "division by zero" in str(exc_info.value)
    assert exc_info.type is ValueError


# ─────────────────────────────────────────────────────────────
# py_test_raises_match：异常消息必须匹配正则
# ─────────────────────────────────────────────────────────────
def test_raises_match_pattern():
    """py_test_raises_match 演示：异常消息要符合正则"""
    with pytest.raises(ValueError, match=r"undefined for negative"):
        factorial(-3)

    # 错误的正则会让用例失败
    # with pytest.raises(ValueError, match=r"WRONG"):
    #     factorial(-3)  # 实际消息不匹配 → Failed


# ─────────────────────────────────────────────────────────────
# py_test_finalizer：request.addfinalizer 收尾清理
# ─────────────────────────────────────────────────────────────
@pytest.fixture
def temp_config_file(request, tmp_path):
    """创建临时配置文件，用 addfinalizer 在用例结束删除。"""
    cfg = tmp_path / "config.json"
    cfg.write_text('{"debug": true}', encoding="utf-8")

    # 注册收尾回调（即便用例失败也会执行）
    def cleanup():
        if cfg.exists():
            cfg.unlink()

    request.addfinalizer(cleanup)
    return cfg


def test_finalizer_creates_and_loads(temp_config_file):
    """py_test_finalizer 演示：用例结束后自动清理资源"""
    data = load_config(str(temp_config_file))
    assert data["debug"] is True
    # 用例结束 → cleanup() 被调用 → 文件被删

    # 验证：再 load 应该失败（文件已被 finalizer 删除）
    # 这里只演示 finalizer 机制，不做断言避免测试间依赖
