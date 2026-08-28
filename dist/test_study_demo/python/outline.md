# Python 测试 snippets 学习大纲

> 配套示例：`dist/test_study_demo/python/`
> 总计 **30 条** pytest snippet，覆盖 pytest 90% 的日常用法。

---

## 推荐学习路径

按下面顺序读，每读完一组就 `pytest tests/<file>.py -v` 跑一遍：

```
1. test_smoke.py        → 测试的 4 种基本形态（10 分钟）
2. test_assertion.py    → 5 种断言（5 分钟）
3. test_exception.py    → 异常 + 收尾（10 分钟）
4. test_lifecycle.py    → setup/teardown（10 分钟）
5. test_fixture.py      → fixture 灵魂 4 件套（20 分钟）
6. test_parametrize.py  → 参数化 + 子测试（15 分钟）
7. test_mock.py         → mock 隔离依赖（20 分钟）
8. test_tmp.py          → tmp_path 临时文件（5 分钟）
```

---

## 30 条 snippet 分组速查

### ① 测试函数（5 条）

| prefix | snippet | 演示位置 |
|---|---|---|
| `py_test_func` | def test_xxx() | `test_smoke.py::test_add_two_positives` |
| `py_test_class` | class TestXxx | `test_smoke.py::TestIsPrime` |
| `py_test_subtest` | subtests.test() | `test_parametrize.py::test_subtest_divide_by_various` |
| `py_test_skip` | @pytest.mark.skip | `test_smoke.py::test_not_implemented_yet` |
| `py_test_xfail` | @pytest.mark.xfail | `test_smoke.py::test_known_bug_negative_input` |

> 注：`py_test_subtest` 依赖 `pytest-subtests` 插件。函数签名需带 `subtests` 参数。

### ② 断言（5 条）

| prefix | snippet | 演示位置 |
|---|---|---|
| `py_test_assert_eq` | assert == | `test_assertion.py::test_assert_eq` |
| `py_test_assert_ne` | assert != | `test_assertion.py::test_assert_ne` |
| `py_test_assert_true` | assert truthy | `test_assertion.py::test_assert_true` |
| `py_test_assert_in` | assert x in y | `test_assertion.py::test_assert_in` |
| `py_test_assert_approx` | pytest.approx | `test_assertion.py::test_assert_approx` |

### ③ 异常断言（2 条）

| prefix | snippet | 演示位置 |
|---|---|---|
| `py_test_raises` | pytest.raises | `test_exception.py::test_raises_division_by_zero` |
| `py_test_raises_match` | raises(match=) | `test_exception.py::test_raises_match_pattern` |

### ④ 生命周期（4 条）

| prefix | snippet | 演示位置 |
|---|---|---|
| `py_test_setup` | setup_module/setup_function | `test_lifecycle.py`（模块顶部） |
| `py_test_teardown` | teardown_function | `test_lifecycle.py`（模块顶部） |
| `py_test_class_setup` | setup_class/teardown_class | `test_lifecycle.py::TestDivideClass` |
| `py_test_finalizer` | request.addfinalizer | `test_exception.py::temp_config_file` |

### ⑤ Fixture（4 条）

| prefix | snippet | 演示位置 |
|---|---|---|
| `py_test_fixture` | @pytest.fixture 基本 | `test_fixture.py::test_fixture_basic` |
| `py_test_fixture_yield` | yield 风格 | `test_fixture.py::workdir` / `conftest.py::db_connection` |
| `py_test_fixture_param` | params= 参数化 | `test_fixture.py::number` |
| `py_test_fixture_scope` | scope=session/module | `conftest.py::app_config` |

### ⑥ 参数化（3 条）

| prefix | snippet | 演示位置 |
|---|---|---|
| `py_test_param` | @pytest.mark.parametrize | `test_parametrize.py::test_add_parametrized` |
| `py_test_param_ids` | parametrize + ids | `test_parametrize.py::test_factorial_with_ids` |
| `py_test_param_stack` | 多 parametrize 叠加 | `test_parametrize.py::test_param_stack` |

### ⑦ Mock（5 条）

| prefix | snippet | 演示位置 |
|---|---|---|
| `py_test_mock` | Mock() | `test_mock.py::test_mock_basic` |
| `py_test_patch` | patch() | `test_mock.py::test_patch_replace_function` |
| `py_test_spy` | wraps= 原方法 | `test_mock.py::test_spy_wraps_original` |
| `py_test_mock_return` | return_value | `test_mock.py::test_mock_return_value` |
| `py_test_mock_side` | side_effect | `test_mock.py::test_mock_side_effect_iterable` |

### ⑧ 工具（2 条）

| prefix | snippet | 演示位置 |
|---|---|---|
| `py_test_cov` | pytest --cov | 见 `README.md` 的运行命令 |
| `py_test_tmp` | tmp_path | `test_tmp.py::test_tmp_path_basic` |

---

## 在 VSCode 里用 snippet 写测试

打开任意 `test_*.py`，输入触发词（如 `py_test_func`），按 Tab，就能插入对应模板：

```
test_       → py_test_func（基本测试函数）
@pytest.    → py_test_raises（异常断言）
@pytest.fix → py_test_fixture（基本 fixture）
@pytest.mar → py_test_param（参数化）
```

snippet 的占位符用 `${1:变量名}` 标记，光标会自动跳到第一个占位符，填完按 Tab 跳到下一个。
