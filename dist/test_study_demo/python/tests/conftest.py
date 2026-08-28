"""
conftest.py — 跨 test_*.py 共享的 fixture

演示：
  - py_test_fixture（基本 fixture）
  - py_test_fixture_scope（scope=session）
  - py_test_fixture_yield（yield 风格的 setup+teardown）
"""

import pytest

from src.calculator import save_config


@pytest.fixture
def sample_data():
    """每个用例独立的简单数据 fixture（py_test_fixture）。"""
    return {"name": "alice", "age": 30}


@pytest.fixture(scope="session")
def app_config(tmp_path_factory):
    """session 级 fixture，整个测试会话只创建一次（py_test_fixture_scope）。

    用 tmp_path_factory 而非 tmp_path 是因为后者是 function 级。
    """
    cfg_path = tmp_path_factory.mktemp("config") / "app.json"
    save_config(str(cfg_path), {"env": "test", "debug": True, "max": 100})
    return cfg_path


@pytest.fixture
def db_connection():
    """yield 风格 fixture：setup 创资源 → yield 给用例 → teardown 关闭（py_test_fixture_yield）。"""
    conn = {"connected": True, "tx_id": "tx-001"}
    print(f"\n[setup] open connection {conn['tx_id']}")
    yield conn
    print(f"\n[teardown] close connection {conn['tx_id']}")
    conn["connected"] = False
