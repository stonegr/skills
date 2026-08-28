"""
test_tmp.py — 临时文件/目录 fixture
====================================

覆盖 1 个 snippet：
  - py_test_tmp → tmp_path（function 级）/ tmp_path_factory（session 级）
"""

from src.calculator import load_config, save_config


def test_tmp_path_basic(tmp_path):
    """py_test_tmp 演示：tmp_path 是 pytest 自带的 function 级 fixture

    用例结束后，整个目录树自动删除，无需手动清理。
    """
    # tmp_path 是 pathlib.Path 对象
    assert tmp_path.exists()
    assert tmp_path.is_dir()

    # 在临时目录里创建文件
    text_file = tmp_path / "hello.txt"
    text_file.write_text("hello pytest", encoding="utf-8")

    # 断言文件存在 + 内容正确
    assert text_file.exists()
    assert text_file.read_text(encoding="utf-8") == "hello pytest"


def test_tmp_path_for_json_config(tmp_path):
    """py_test_tmp 实战：测试 load_config / save_config"""
    cfg = tmp_path / "config.json"

    # 写
    save_config(str(cfg), {"debug": True, "max_users": 100})

    # 读
    data = load_config(str(cfg))
    assert data == {"debug": True, "max_users": 100}
