---
name: generate-func-snippets
description: 为具体的库（pandas/numpy/requests/fastapi/gin/gorm/axios 等）生成 vscode code-snippets，支持多语言，先出大纲再生成
---

# generate-func-snippets — 库级 VSCode snippets 生成器

## 用途

为某个**具体库**生成 30-50 个常用 API 的 VSCode snippets。区别于 `generate-lang-snippets`（按语言维度组织 通用编程动作），本 skill 按**库维度**组织 库特有 API 的常用写法。

适用场景：
- 日常用某个库写代码，想快速补全高频 API（不需要再翻文档）
- 项目里反复用到某个库的固定模式（读 CSV、读 Excel、groupby+agg、merge 等）
- 学习一个库，想用 snippets 倒逼自己掌握核心 API

## 触发方式

```
/generate-func-snippets <library> [--lang=<lang>] [--max=N]
```

参数说明：
- `<library>`：**必填**，库名。例：`pandas` / `numpy` / `requests` / `fastapi` / `gin` / `gorm` / `axios`
- `--lang=<lang>`：可选，默认 `python`。支持 `python / typescript / javascript / go / rust`
- `--max=N`：snippet 上限，默认 40，范围 30-50

示例：
```
/generate-func-snippets pandas
/generate-func-snippets numpy --max=35
/generate-func-snippets axios --lang=typescript
/generate-func-snippets gin --lang=go
```

## 输出位置

生成文件统一放：
```
.vscode/<library>.code-snippets
```

中间产物（大纲）**不落盘**，直接在对话里展示给用户 review。

## 工作流程

### Step 1：解析参数
- 提取 `<library>`，标准化为小写
- 提取 `--lang`（默认 `python`）
- 提取 `--max`（默认 40）
- 确认 `.vscode/` 目录存在，不存在则创建

### Step 2：生成大纲（强制停在这里等用户 review）

**这一步必须停**，不能直接生成 snippets。

1. **列出 30-50 个 snippet，按分类组织（8-12 个分类）**
2. 大纲**直接在对话里输出**，不写入任何文件
3. 每个 snippet 一行：`prefix | 中文描述 | 关键 API/调用模式`
4. 大纲格式示例（pandas）：

```markdown
# pandas snippets 大纲（40 个）

## IO 读写（8）
- pd_read_csv | 读取 CSV | pd.read_csv(path, encoding='utf-8')
- pd_read_excel | 读取 Excel | pd.read_excel(path, sheet_name)
- pd_read_json | 读取 JSON | pd.read_json(path)
- pd_read_sql | 读 SQL | pd.read_sql(sql, conn)
- pd_read_parquet | 读 Parquet | pd.read_parquet(path)
- pd_to_csv | 写 CSV | df.to_csv(path, index=False)
- pd_to_excel | 写 Excel | df.to_excel(path, sheet_name)
- pd_to_sql | 写数据库 | df.to_sql(name, conn, if_exists)

## 创建 DataFrame（4）
- pd_create_df_dict | 字典创建 | pd.DataFrame({col: [..]})
...

## 数据查看（4）
- pd_head | 看前 N 行 | df.head(n)
...
```

5. 大纲输出后停下，**等用户确认/修改后再进入 Step 3**

### Step 3：生成 .code-snippets
- 按确认后的大纲，逐个生成 snippet
- **key / description 一律中文**，prefix 严格遵循下面的命名规范（英文）
- 每个 body 头部都写完整 `import`（独立可用原则）
- 生成完写入 `.vscode/<library>.code-snippets`

### Step 4：校验（生成完必跑）

```bash
# 1. JSON 合法
python3 -c "import json; json.load(open('.vscode/<library>.code-snippets'))"

# 2. 用 expand.py 模拟 VSCode 展开所有 snippet
python3 references/expand.py .vscode/<library>.code-snippets
```

如果展开结果出现：
- `$$` 变成空 → `\\` 写少了
- `$1` 变成字面 `$` → 占位符语法写错
- 占位符默认值丢失 → `:` 后内容没正确闭合

### Step 5：交付
- 输出 snippets 文件路径 + snippet 总数 + 校验结果
- 提示用户到产物 review

---

## prefix 命名规范

格式：`{abbrev}_{func}`，全部小写，下划线分隔。

### 内置缩写表（找不到时问用户）

| 库 | 缩写 | prefix 示例 |
|---|---|---|
| pandas | `pd` | `pd_read_csv` / `pd_groupby` / `pd_merge` |
| numpy | `np` | `np_array` / `np_linspace` / `np_dot` |
| requests | `req` | `req_get` / `req_post` / `req_session` |
| fastapi | `fa` | `fa_route` / `fa_pydantic` / `fa_dep` |
| flask | `fk` | `fk_route` / `fk_blueprint` |
| pydantic | `pd2`（避开 pandas） | `pd2_basemodel` / `pd2_validator` |
| sqlalchemy | `sa` | `sa_session` / `sa_query` |
| pillow | `pil` | `pil_open` / `pil_resize` |
| pytest | `pt` | `pt_test` / `pt_fixture` / `pt_param` |
| httpx | `hx` | `hx_get` / `hx_async_client` |
| aiohttp | `ah` | `ah_get` / `ah_session` |
| loguru | `lg` | `lg_add` / `lg_logger` |
| typer | `tp` | `tp_app` / `tp_command` |
| rich | `rc` | `rc_print` / `rc_console` |
| beautifulsoup4 | `bs` | `bs_soup` / `bs_find` |
| selenium | `se` | `se_driver` / `se_find_element` |
| scrapy | `sc` | `sc_spider` / `sc_item` |
| click | `cl` | `cl_command` / `cl_group` |
| axios | `ax` | `ax_get` / `ax_interceptor` |
| lodash | `ld` | `ld_debounce` / `ld_groupby` |
| express | `ex` | `ex_route` / `ex_middleware` |
| react | `rc2`（避开 rich） | `rc2_component` / `rc2_hook` |
| vue | `vu` | `vu_component` / `vu_ref` |
| prisma | `pr` | `pr_schema` / `pr_client` |
| gin | `gn` | `gn_route` / `gn_middleware` |
| gorm | `gm` | `gm_model` / `gm_query` |
| cobra | `cb` | `cb_command` / `cb_flag` |
| zap | `zp` | `zp_logger` / `zp_sugar` |
| sqlx | `sx` | `sx_query` / `sx_tx` |
| serde | `sd` | `sd_derive` / `sd_serialize` |
| tokio | `tk` | `tk_spawn` / `tk_channel` |

**缩写冲突规则**：已注册的库优先，新库追加数字后缀（`pd2` / `rc2`）。

---

## body 规范

### 通用模板

```json
"<中文 key>": {                           // JSON 字典的 key：中文
  "prefix": "<abbrev>_<func>",           // 触发词：英文（按缩写表）
  "body": [
    "import <lib> as <abbrev>",
    "${1:result} = <abbrev>.<api>(${2:arg})"
  ],
  "description": "<中文描述>"            // 中文（去掉库名前缀，括号备注可保留）
}
```

三个字段的语种分工：

| 字段 | 语种 | 规则 |
|---|---|---|
| **key** | **中文** | 简短描述，去掉括号备注。与 description 保持中文一致 |
| **prefix** | **英文** | 按下方缩写表 `<abbrev>_<func>` |
| **description** | **中文** | 去掉库名前缀（如 `pandas`、`fastapi`、`gin`），括号备注可保留 |

### 占位符规范

| 用途 | 写法 | 说明 |
|---|---|---|
| 普通占位 | `${1:变量名}` | 提示用户这里要填什么 |
| 多占位 | `${1:arg1}, ${2:arg2}` | 按 tab 顺序填 |
| 选项列表 | `${1\|utf-8,gbk\|}` | 用 `\|...\|` 包起来，逗号分隔 |
| 默认值 | `${2:10}` | 占位符 N 的默认是 `10` |
| 终末位置 | `${0}` | 光标最后落点 |
| 同占位符 | `${1:var}` 出现多次 | 多处联动改 |

### import 写入规则

- 每个 snippet **都写完整 import**（独立可用，不依赖 IDE auto-import）
- 多 import 的库（如 sqlalchemy + pandas）按字母序写
- 同库已有 snippet 的 import，**不要再加注释说明**（避免 snippet 重复噪音）

### description 规范

- 中文，简洁（不超过 30 字）
- 名词为主，不加"用于"等冗余词
- **去掉库名前缀**：写 `读取 CSV 文件` 而不是 `pandas 读取 CSV 文件`、写 `定义 GET 路由` 而不是 `gin 定义 GET 路由`（库名已隐含在 prefix/文件名里）
- **括号备注可保留**：实现细节、依赖包等关键提示写在括号里（如 `信号监听（程序退出前清理）`）
- 例：`读取 CSV 文件` / `定义 GET 路由` / `信号监听（程序退出前清理）`

### key 规范

- **key 一律中文**，与 description 保持中文一致
- key 是 description 去掉所有括号备注后的简短版（如 `description="信号监听（程序退出前清理）"` → `key="信号监听"`）
- key 名直接对应一个 snippet，VSCode 补全面板里会显示这个中文名

---

## $ 转义速查（复用 generate-lang-snippets 经验）

snippet body 的 `$` 要"穿过"两层解析：

```
你想插入的代码:    $var
                   ↑ 渲染自
snippet 看到:      \$var        ← JSON 解码后的 body
                   ↑ 来源于
JSON 文件 raw:    \\$var        ← 文件里实际写的字符
```

| 想插入的代码 | JSON 文件里写 |
|---|---|
| `$var`（字面） | `\\$var` |
| `$$`（PID） | `\\$\\$` |
| `${var:-default}` | `\\${var:-default}` |
| `${1:var}`（占位符） | `${1:var}` |

**绝对不要在 JSON 里写 `\$`**（会报 invalid escape）。

---

## 必须覆盖的功能分类（按库类型）

> 不是每个分类都必出现在大纲里，按库实际功能挑 8-12 个，确保总数 30-50。

### 数据分析类（pandas / numpy / polars）

| 分类 | 覆盖示例 |
|---|---|
| IO 读写 | read_csv/excel/json/sql/parquet + to_csv/excel/sql |
| 创建 | DataFrame/Series/数组创建 |
| 查看 | head/tail/info/describe/shape/dtypes |
| 选择过滤 | loc/iloc/where/query/bool 索引 |
| 列操作 | 增加/删除/重命名/类型转换/apply |
| 变形 | sort/drop/rename/astype/fillna/dropna |
| 聚合 | groupby/agg/transform/aggregate |
| 合并 | merge/join/concat/append/combine |
| 透视 | pivot/pivot_table/melt/stack/unstack |
| 缺失值 | isnull/notnull/dropna/fillna/interpolate |
| 重复值 | duplicated/drop_duplicates/value_counts |
| 时间序列 | to_datetime/resample/rolling/shift/dt 访问器 |
| 字符串 | str.contains/replace/split/extract |
| 统计 | mean/std/corr/cov/cumsum/value_counts |

### 网络请求类（requests / httpx / aiohttp / axios / fetch）

| 分类 | 覆盖示例 |
|---|---|
| 基本方法 | GET/POST/PUT/DELETE/PATCH |
| 参数 | query params / body json / form-data |
| Headers & Cookies | 自定义 headers / cookies 传递 |
| Session & 客户端 | Session/Client/连接池 |
| 文件 | 文件上传（multipart）/下载（stream） |
| 异常 | 超时设置 / 异常捕获 / 重试 |
| 鉴权 | Bearer Token / Basic Auth / 自定义 |

### Web 框架类（fastapi / flask / gin / express / koa）

| 分类 | 覆盖示例 |
|---|---|
| 路由 | GET/POST/PUT/DELETE 路由定义 |
| 请求解析 | path/query/body 参数解析 |
| 响应 | JSONResponse / 模板渲染 / 文件响应 |
| 中间件 | 全局中间件 / 路由级中间件 |
| 异常处理 | 全局异常 / 自定义异常类 |
| 依赖注入 | fastapi Depends / gin 中间件链 |
| 数据校验 | Pydantic 模型 / gin binding / express validator |
| 异步 | async 路由 / 异步处理 |
| 启动配置 | 应用创建 / 配置加载 / 启动监听 |

### ORM 类（sqlalchemy / gorm / prisma / typeorm）

| 分类 | 覆盖示例 |
|---|---|
| 连接配置 | engine/session/客户端创建 |
| 模型定义 | Model/Entity/Schema 定义 |
| CRUD | create / read / update / delete |
| 查询 | filter/where/order_by/limit |
| 关联关系 | 一对多 / 多对多 / 预加载 |
| 事务 | 事务开启/提交/回滚/with 块 |
| 迁移 | alembic / 自动迁移 / 手动迁移 |
| 原始 SQL | text() / Raw SQL 执行 |

### 测试类（pytest / jest / go testing）

| 分类 | 覆盖示例 |
|---|---|
| 测试函数 | 基本测试 / 子测试 |
| Fixture | pytest fixture / jest beforeEach |
| 参数化 | parametrize / test.each |
| Mock | mock/patch / jest.mock |
| 异常断言 | assertRaises / rejects.toThrow |
| 钩子 | setup/teardown / beforeAll/afterAll |
| 覆盖率 | 配置运行 / 报告生成 |

### 工具类（pydantic / loguru / click / typer / pillow / rich）

按各自核心 API 选 5-8 个分类，每个分类 3-5 个 snippet。例如：

- **pydantic**：BaseModel / Field / validator / model_config / model_dump / nested model
- **loguru**：logger.add / logger.info / rotation / filter / exception
- **pillow**：Image.open / resize / crop / convert / thumbnail / save
- **rich**：Console / Table / Progress / Syntax / Panel

---

## 联网检索策略

按以下优先级补充知识：
1. 库官方文档（如 pandas.pydata.org、docs.python-requests.com、fastapi.tiangolo.com）
2. 官方 quickstart / cookbook / cheatsheet
3. 知名教程（RealPython、Effective Go 等）

避免：
- 个人博客（除非官方引用）
- 过时 StackOverflow 答案（>3 年需核实版本）

**联网失败时**，退回到已有知识，标注「未联网核实，请人工核对最新版本」。

---

## 错误处理

| 场景 | 处理 |
|---|---|
| 库名不存在 | 询问用户：基于知识库生成，还是取消 |
| 缩写冲突 | 按 `pd2` / `rc2` 规则追加数字后缀 |
| 大纲未确认 | 拒绝进入 Step 3，提示先 review |
| `.vscode/` 不存在 | 自动 `mkdir -p` |
| JSON 不合法 | 回滚未写入的文件，告知哪一行报错 |
| 展开校验失败 | 输出失败 snippet 名 + diff，**不删除文件**让用户排查 |

---

## 风格要求

- **全面不冗余**：覆盖核心 API，不堆冷门方法
- **可独立运行**：每个 snippet 复制到空文件即可工作
- **占位符语义清晰**：默认值要让用户秒懂该填什么
- **key 和 description 一律中文**：key 是中文简短版，description 是中文详情（去掉库名前缀，括号备注可保留）。**只有 prefix 保留英文**
- **不发明新缩写**：库里没出现的缩写先去查表，没查到问用户
- **snippet 总数 30-50**：少了说明覆盖不全，多了说明喧宾夺主

---

## 完整示例（pandas 一个 snippet）

```json
"读取 CSV 文件": {                              // key: 中文（与 description 一致）
  "prefix": "pd_read_csv",                      // prefix: 英文（按缩写表）
  "body": [
    "import pandas as pd",
    "${1:df} = pd.read_csv(${2:path}, encoding=${3|'utf-8','gbk','gb2312'|}, sep=${4:','})"
  ],
  "description": "读取 CSV 文件"                // description: 中文（去掉"pandas"前缀）
}
```

展开后（模拟）：
```python
import pandas as pd

df = pd.read_csv(path, encoding='utf-8', sep=',')
```

---

## 验证清单（生成完必跑）

```bash
# 1. JSON 合法
python3 -c "import json; json.load(open('.vscode/<library>.code-snippets'))"

# 2. 模拟展开
python3 references/expand.py .vscode/<library>.code-snippets

# 3. snippet 总数检查（应在 30-50 之间）
python3 -c "import json; d=json.load(open('.vscode/<library>.code-snippets')); print(f'snippet 总数: {len(d)}')"
```

输出示例：
```
snippet 总数: 42
✓ JSON 合法
✓ 42 个 snippet 全部展开成功
```

---

## 注意事项

- 中文输出为主，但代码、prefix、API 名保留英文
- **key 和 description 都用中文**（key 是简短中文名，description 是中文详情）；只有 prefix 保留英文
- 生成前确认 `.vscode/` 目录可写
- **不在大纲未确认时直接生成文件**
- 用户 review 大纲时可增删改，确认后再生成详细 snippet
- 每次生成覆盖前先 `diff` 旧文件，确认无误后再覆盖（避免误删历史版本）