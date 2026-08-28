# Python pytest 测试 snippets 示例

> 配套 `.vscode/python.code-snippets` 里 **30 条** 测试 snippets 的可运行 demo。

## 快速开始

```bash
cd dist/test_study_demo/python

# 1) 安装依赖
pip install pytest pytest-subtests

# 2) 跑全部测试
pytest

# 3) 看每个用例详情
pytest -v

# 4) 看覆盖率（py_test_cov snippet）
pip install pytest-cov
pytest --cov=src --cov-report=term-missing
```

预期看到：
- **54 passed**（含 24 个 subtest 子用例）
- **1 skipped**（py_test_skip 演示）
- **1 xpassed**（py_test_xfail 演示，预期失败的用例实际失败，符合预期）

---

## 30 条 snippet 一句话总结

### 测试函数
| prefix | 一句话 | 适用场景 |
|---|---|---|
| `py_test_func` | `def test_xxx()` 顶层函数 | 绝大多数用例的默认写法 |
| `py_test_class` | `class TestXxx` 分组 | 共享 setup 或仅做语义分组 |
| `py_test_subtest` | `pytest.subtests()` 动态子测试 | 循环里跑多组数据，失败不中断后续 |
| `py_test_skip` | `@pytest.mark.skip` 跳过 | 临时禁用 / 功能未实现 |
| `py_test_xfail` | `@pytest.mark.xfail` 预期失败 | 已知 bug，跑过即通过 |

### 断言
| prefix | 一句话 |
|---|---|
| `py_test_assert_eq` | `assert a == b` |
| `py_test_assert_ne` | `assert a != b` |
| `py_test_assert_true` | `assert 条件` |
| `py_test_assert_in` | `assert x in container` |
| `py_test_assert_approx` | `pytest.approx(值)` 处理浮点精度 |

### 异常
| prefix | 一句话 |
|---|---|
| `py_test_raises` | `with pytest.raises(ExcType):` |
| `py_test_raises_match` | `pytest.raises(ExcType, match=r"...")` |

### 生命周期
| prefix | 一句话 |
|---|---|
| `py_test_setup` | `setup_module` / `setup_function` |
| `py_test_teardown` | `teardown_function` |
| `py_test_class_setup` | `setup_class` / `teardown_class` |
| `py_test_finalizer` | `request.addfinalizer(cleanup)` |

### Fixture
| prefix | 一句话 |
|---|---|
| `py_test_fixture` | `@pytest.fixture` 基本 |
| `py_test_fixture_yield` | yield 风格（setup+teardown 一体） |
| `py_test_fixture_param` | `params=[1,2,3]` 参数化 fixture |
| `py_test_fixture_scope` | `scope="session"` 跨文件共享 |

### 参数化
| prefix | 一句话 |
|---|---|
| `py_test_param` | `@pytest.mark.parametrize("a,b", [...])` |
| `py_test_param_ids` | `parametrize(..., ids=["x","y"])` |
| `py_test_param_stack` | 多个 `@parametrize` 叠加（笛卡尔积） |

### Mock
| prefix | 一句话 |
|---|---|
| `py_test_mock` | `Mock()` 替身对象 |
| `py_test_patch` | `patch("module.func")` 替换函数 |
| `py_test_spy` | `MagicMock(wraps=原方法)` 监视并保留行为 |
| `py_test_mock_return` | `mock.method.return_value = 值` |
| `py_test_mock_side` | `Mock(side_effect=[...])` 多次返回/抛错 |

### 工具
| prefix | 一句话 |
|---|---|
| `py_test_cov` | `pytest --cov=src` 覆盖率命令 |
| `py_test_tmp` | `tmp_path` 临时目录 fixture |

---

## 常用 pytest 命令

```bash
# 跑全部
pytest

# 详细输出
pytest -v

# 跑某个文件
pytest tests/test_mock.py

# 跑某个测试类或函数
pytest tests/test_mock.py::test_mock_basic

# 按名字过滤
pytest -k "fixture"

# 遇到失败立即停
pytest -x

# 看 print 输出（默认会被捕获）
pytest -s

# 覆盖率（py_test_cov）
pytest --cov=src --cov-report=html

# 并行（pytest-xdist）
pip install pytest-xdist
pytest -n auto

# 标记运行（按 tag 过滤）
pytest -m "not slow"
```

---

## 文件结构

```
python/
├── pytest.ini                    # pytest 配置
├── outline.md                    # 30 条 snippet 分组学习路径
├── README.md                     # 本文件
├── src/
│   └── calculator.py             # 被测代码（加/减/乘/除/阶乘/素数/JSON IO）
└── tests/
    ├── __init__.py
    ├── conftest.py               # 共享 fixture（sample_data / app_config / db_connection）
    ├── test_smoke.py             # 5 个 snippet：func/class/skip/xfail
    ├── test_assertion.py         # 5 个 snippet：eq/ne/true/in/approx
    ├── test_exception.py         # 3 个 snippet：raises/match/finalizer
    ├── test_lifecycle.py         # 4 个 snippet：setup/teardown/class_setup
    ├── test_fixture.py           # 4 个 snippet：fixture/yield/param/scope
    ├── test_parametrize.py       # 4 个 snippet：param/ids/stack/subtest
    ├── test_mock.py              # 5 个 snippet：mock/patch/spy/return/side
    └── test_tmp.py               # 1 个 snippet：tmp_path
```
