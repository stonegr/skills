"""
test_fixture.py — Fixture 完整演示
==================================

fixture 是 pytest 的灵魂。本文件覆盖 4 个 snippet（基本 fixture 也在 conftest.py）：
  - py_test_fixture         → @pytest.fixture 基本
  - py_test_fixture_yield   → yield 风格（setup + teardown 一体）
  - py_test_fixture_param   → params=[...] 参数化 fixture
  - py_test_fixture_scope   → scope="session"/"module"/"class"

详见 conftest.py 里的 sample_data / app_config / db_connection 三个 fixture。
"""

import pytest

from src.calculator import save_config


# ─────────────────────────────────────────────────────────────
# py_test_fixture：基本 fixture（function 级，每个用例独立创建）
# ─────────────────────────────────────────────────────────────
@pytest.fixture
def greeting():
    """简单 fixture：返回值作为参数注入用例"""
    return "hello pytest"


def test_fixture_basic(greeting):
    """py_test_fixture 演示：参数名与 fixture 名一致即可注入"""
    assert greeting == "hello pytest"


# ─────────────────────────────────────────────────────────────
# py_test_fixture_yield：yield 风格（setup+teardown 一体写）
# ─────────────────────────────────────────────────────────────
@pytest.fixture
def workdir(tmp_path):
    """yield 风格：yield 前的代码是 setup，yield 后是 teardown。"""
    work = tmp_path / "work"
    work.mkdir()
    print(f"\n[fixture_yield] setup: 创建 {work}")

    yield work  # 这里把 work 注入给用例

    # teardown（用例结束后执行，即便失败也跑）
    print(f"[fixture_yield] teardown: 清理 {work}")
    # 注意：tmp_path 本身是 pytest 自带清理，无需手动删


def test_yield_fixture_creates_file(workdir):
    """py_test_fixture_yield 演示：yield 风格 fixture"""
    cfg = workdir / "app.json"
    save_config(str(cfg), {"v": 1})
    assert cfg.exists()
    assert cfg.read_text(encoding="utf-8") == '{\n  "v": 1\n}'


# ─────────────────────────────────────────────────────────────
# py_test_fixture_param：参数化 fixture（同一 fixture 多组数据）
# ─────────────────────────────────────────────────────────────
@pytest.fixture(params=[1, 2, 3])
def number(request):
    """参数化 fixture：每个 param 值都跑一次用例"""
    return request.param


def test_param_fixture_is_positive(number):
    """py_test_fixture_param 演示：3 个参数跑 3 次"""
    assert number > 0
    assert number <= 3


# ─────────────────────────────────────────────────────────────
# py_test_fixture_scope：session 级 fixture（整个测试会话共享）
# ─────────────────────────────────────────────────────────────
# session 级 fixture 定义在 conftest.py（app_config）
def test_session_fixture_path(app_config):
    """py_test_fixture_scope 演示：session 级 fixture 只创建一次"""
    assert app_config.exists()
    assert app_config.name == "app.json"
    # 多个用例共享同一份 app_config（不会重复创建）


def test_session_fixture_path_again(app_config):
    """另一个用例也用 app_config，复用同一实例"""
    import json
    data = json.loads(app_config.read_text(encoding="utf-8"))
    assert data["env"] == "test"


# ─────────────────────────────────────────────────────────────
# 综合：db_connection yield fixture 来自 conftest.py
# ─────────────────────────────────────────────────────────────
def test_yield_db_connection(db_connection):
    """py_test_fixture_yield 综合演示：跨文件共享的 yield fixture"""
    assert db_connection["connected"] is True
    assert db_connection["tx_id"] == "tx-001"
    # 用例结束后 → db_connection fixture 的 teardown 把 connected 置 False
