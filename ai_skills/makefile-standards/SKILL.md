---
name: makefile-standards
description: 规范项目 Makefile 的命令集合、命名与组织方式，适用于新建/改造模板项目时生成或审阅 Makefile，覆盖 Python/Go/前端/移动端的开发、测试、构建、Docker、清理等通用命令。
---

# Makefile Standards

规范项目 Makefile 的命令集合、命名与组织方式，让任何模板项目（Python / Go / 前端 / 移动端）只要带 Makefile，就拥有一致的命令集合、命名风格与帮助输出。

## 用途与触发

**适用场景**：
- 创建新的项目模板时，生成符合规范的 Makefile
- 审阅/改造现有 Makefile，使其符合规范
- 统一多个项目的 Makefile 命令集合与帮助输出格式

**不适用**：
- 单文件脚本、临时 demo（无需 Makefile）
- 纯文档站点（无构建/测试流程）

## 一、通用规范（所有语言栈都遵守）

### 1.1 核心命令清单

**核心 6 个命令**——所有项目类型都强制包含，缺一不可：

| # | 命令 | 作用 | 说明 |
|---|---|---|---|
| 1 | `help` | 自描述帮助，解析 `## 描述` 自动列出 | 必须为 Makefile 第一个可读目标 |
| 2 | `dev` | 本地开发启动（含热重载） | 解释型语言=热重载 server；前端=`pnpm dev`；移动端=`metro run`/`flutter run` |
| 3 | `test` | 运行单元测试 | 不带覆盖率；覆盖率走 `test-cov` |
| 4 | `lint` | 静态检查 | 必须修复后才能视为完成 |
| 5 | `fmt` | 自动格式化 | 与 lint 解耦，可单独跑 |
| 6 | `clean` | 清理缓存与构建产物 | 必须覆盖该语言的缓存目录 |

**编译型语言额外必需**：`build`（Go / 移动端 / 前端 bundle）。**解释型语言（Python / Node 服务端）不强制 `build`**。

> 解释型语言如确需"构建步骤"占位，应在注释中说明"无需构建，install 即同步依赖"。

### 1.2 按需命令清单（默认不包含，遇到场景再加）

#### 通用扩展

| 命令 | 触发条件 | 作用 |
|---|---|---|
| `install` | 项目首次使用需装依赖 | 同步依赖（`uv sync` / `pnpm install` / `go mod tidy`） |
| `start` | 区别于 `dev` 的生产模式启动 | 用 Gunicorn/PM2/打包产物启动 |
| `test-cov` | 需要覆盖率报告 | 带 `--cov` 或 `-coverprofile` |
| `preview` | 前端项目（Vite/Nuxt/Next） | 本地预览 `dist/` |
| `run` | Go 项目 | `go run` 启动入口（可与 `dev` 等价） |
| `typecheck` | TypeScript 项目 | `tsc --noEmit` 类型检查 |

#### Docker 套件（含 `docker-compose.yml` 时启用）

| 命令 | 是否默认 | 作用 |
|---|---|---|
| `docker-build` | ✅ 默认 | 构建所有服务镜像 |
| `docker-up` | ✅ 默认 | 后台启动 docker compose 栈 |
| `docker-down` | ✅ 默认 | 停止并移除容器、网络（**保留**数据卷和镜像） |
| `docker-logs` | ✅ 默认 | 查看日志（支持 `make docker-logs s=app` 指定服务） |
| `docker-clean` | ✅ 默认 | 彻底清理容器、网络、数据卷（含 `-v --remove-orphans`） |
| `docker-build-cn` | ⚪ 可选 | 国内构建（清华源 / 中科大源 / goproxy.cn） |

> `docker-build-cn` 默认**不**生成，需要的人手动从 `references/Makefile.go.template` 复制。

#### 数据库迁移（项目含 alembic / migrate / GORM AutoMigrate 时）

| 命令 | 作用 |
|---|---|
| `migrate` | 应用迁移到最新版本 |
| `revision` | 生成新迁移版本（`make revision m="message"`） |
| `downgrade` | 回滚一个版本 |

#### 国际化（项目含 i18n / babel 时）

| 命令 | 作用 |
|---|---|
| `i18n-extract` | 从源码提取翻译到 `.pot` |
| `i18n-init` | 初始化新语言（`make i18n-init lang=ja_JP`） |
| `i18n-update` | 根据 `.pot` 更新各语言 `.po` |
| `i18n-compile` | 编译 `.po` → `.mo` |

#### 代码生成（按工具选）

| 命令 | 触发条件 |
|---|---|
| `swag` | Go 项目用 swagger |
| `proto` | 项目含 Protobuf |
| `gen` | 其他代码生成（mock/sqlc/ent 等） |
| `seed` | Go/Node 项目种子数据 |

### 1.3 不纳入的命令

下列命令**不**纳入本 skill 的按需清单，使用者自行决定：

- ❌ `docs`（文档站点）
- ❌ `bench`（基准测试）
- ❌ `profile`（性能分析）
- ❌ `release`（发版打包——更适合 CI 流水线）
- ❌ `deps-update`（升级依赖）
- ❌ `security`（安全扫描）
- ❌ `precommit`（pre-commit 框架）

### 1.4 命名规范

- 全部小写字母 + 中划线（`docker-build-cn`），**不**用驼峰或下划线
- `docker-*` 前缀统一管理容器相关命令
- 业务生成命令用动词原形（`migrate` / `revision`），不写 `db-migrate`
- 所有非文件目标必须 `.PHONY` 声明
- 变量定义在文件顶部，全大写下划线（`APP_NAME`、`BUILD_DIR`、`COMPOSE_FILE`）

### 1.5 help 命令标准模板（必背）

每个 Makefile 顶部第一段必须是：

```makefile
.DEFAULT_GOAL := help

.PHONY: help
help: ## 显示所有命令
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
```

要点：
- `.DEFAULT_GOAL := help` 让 `make` 不带参数时显示帮助
- 解析 `## 中文描述`，按目标名排序，ANSI 青色左对齐 20 列
- 不需要再单独写 README 命令清单

### 1.6 注释规范

- 每个目标行末必须有 `## 中文描述`（help 命令解析依赖此格式）
- 段标题用 `# ===== Section =====`（如 Docker、Database、i18n）
- 复杂命令上方 1-2 行注释解释**为什么**这么做（参考 Flask Makefile 中 HOST/PORT 的注释）
- 参数化命令附 `usage:` 说明（如 `make revision m="message"`）

### 1.7 变量与可覆盖参数

- 工具路径用 `?=`（`PYTHON ?= python3`、`UV ?= uv`、`PNPM ?= pnpm`）
- 端口、主机用 `?=` 但**配合 shell 兜底**，避免继承系统环境变量坑：

```makefile
HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: dev
dev: ## 启动开发服务 (HOST/PORT override via `make dev HOST=... PORT=...`)
	@HOST=$${HOST:-$(HOST)}; \
	PORT=$${PORT:-$(PORT)}; \
	$(UV) run uvicorn app.main:app --reload --host $$HOST --port $$PORT
```

> **为什么用 shell 兜底**：macOS 终端继承 `HOST=192.168.x.x`，如果只用 make 的 `HOST?=`，会被系统环境覆盖，导致绑定失败。`$${HOST:-$(HOST)}` 让命令行参数优先级最高。

---

## 二、按语言/技术栈的最小可用清单

### 2.1 Python（FastAPI / Flask / Django / 通用）

**必含**：核心 6 个 + `install`
**推荐按需**：`start` / `test-cov` / `migrate` / `revision` / `downgrade` / `i18n-*` / `docker-*`

**工具链参考**：

```makefile
$(UV) run pytest -v
$(UV) run pytest --cov=app --cov-report=html
$(UV) run ruff check .
$(UV) run pyright .
$(UV) run ruff format .
$(UV) run alembic upgrade head
```

参考模板：`references/Makefile.python.template`

### 2.2 Go（Gin / CLI / 通用）

**必含**：核心 6 个 + `build`
**推荐按需**：`install` / `seed` / `swag` / `proto` / `docker-*`

**工具链参考**：

```makefile
go mod tidy
go run ./cmd/server/main.go
CGO_ENABLED=0 go build -ldflags="-s -w" -o ./bin/$(APP_NAME) ./cmd/server/main.go
go test -v -coverprofile=coverage.out ./...
golangci-lint run --fix ./...   # 未安装时自动 go install
gofmt -w .                       # 可选 goimports
```

> Go 项目的 `lint` 命令推荐在工具未安装时自动 `go install`（参考 Go-Gin Makefile）。

参考模板：`references/Makefile.go.template`

### 2.3 前端（Vue3 / Next.js / Nuxt / 通用）

**必含**：核心 6 个 + `build` + `preview`
**推荐按需**：`install` / `test-cov` / `typecheck`（TS 项目）/ `docker-*`

**工具链参考**：

```makefile
pnpm install
pnpm dev
pnpm build
pnpm preview
pnpm test
pnpm lint
pnpm format
pnpm exec tsc --noEmit
```

> 前端的 `clean` 必须清理 `dist/` `.nuxt/` `.next/` `.cache/` `.turbo/`，**不**清理 `node_modules/`。

参考模板：`references/Makefile.frontend.template`

### 2.4 移动端（Android + iOS 双套）

**Android 必含**：核心 6 个 + `build`
**iOS 必含**：核心 6 个 + `build`
**推荐按需**：`release` / `install`

**工具链参考**：

```makefile
# Android
./gradlew assembleDebug
./gradlew assembleRelease
./gradlew test
./gradlew lintDebug
ktlint --format

# iOS
xcodebuild -workspace App.xcworkspace -scheme AppName -configuration Debug build
xcodebuild test -workspace App.xcworkspace -scheme AppName -destination 'platform=iOS Simulator,name=iPhone 15'
swiftlint
swiftlint --fix
mint bootstrap
```

> 移动端推荐用 `platform=android|ios` 参数切换，避免 Makefile 翻倍。参考 `references/Makefile.mobile.template`。

---

## 三、工作流程

生成或审阅 Makefile 时按以下步骤执行：

```
Step 1 识别项目类型
       ├─ 语言：Python / Go / TypeScript / Kotlin / Swift / ...
       ├─ 框架：FastAPI / Gin / Vue3 / Next.js / ...
       └─ 特性：是否有 docker-compose / DB 迁移 / i18n / 代码生成？

Step 2 选定必含命令
       ├─ 解释型 → 核心 6 个
       └─ 编译型 → 核心 6 个 + build

Step 3 按需追加
       ├─ 含 docker-compose → docker-build / up / down / logs / clean（默认 5 个）
       ├─ 含 DB 迁移 → migrate / revision / downgrade
       ├─ 含 i18n → i18n-extract / init / update / compile
       └─ 含代码生成 → swag / proto / gen / seed

Step 4 填入工具链命令
       └─ 按语言栈"工具链参考"填入具体命令

Step 5 添加 help 模板与 .DEFAULT_GOAL
       └─ 放在 Makefile 顶部

Step 6 标注所有 .PHONY + 中文注释
       └─ 每个目标行末 ## 描述，参数化命令附 usage 说明

Step 7 校验
       ├─ make help 输出整齐对齐
       ├─ make lint / make fmt 可跑通
       └─ 端口/主机参数化且不被系统环境变量污染
```

---

## 四、验证清单

审阅或生成完成后，逐项检查：

- [ ] 核心 6 个命令齐全（`help` / `dev` / `test` / `lint` / `fmt` / `clean`）
- [ ] 编译型语言额外含 `build`
- [ ] 所有目标都有 `.PHONY`
- [ ] `.DEFAULT_GOAL := help`（位于 help 上方）
- [ ] 每个目标都有 `## 中文描述`
- [ ] `make help` 输出按名称对齐且有颜色（青色 20 列宽）
- [ ] Docker 命令（若适用）齐全：build / up / down / logs / clean；`docker-build-cn` 仅在用户需要时加入
- [ ] 工具命令可通过 `make xxx` 直接运行（不依赖手动 source venv）
- [ ] 端口/主机参数化且不被系统环境变量污染（shell 兜底）
- [ ] `clean` 命令覆盖该语言的缓存目录（Python: `__pycache__` / `.pytest_cache` / `.ruff_cache`；前端: `dist/` / `.nuxt/` / `.next/`；Go: `bin/` / `coverage.*`）

---

## 五、反模式（禁止事项）

- ❌ 目标名用驼峰（`RunTests` / `RunDev`）
- ❌ 注释用 `##` 但 help 命令缺失或不解析
- ❌ 用空格缩进（makefile 缩进必须是**真实 Tab**）
- ❌ 把 docker 命令命名为 `d-up` / `compose-start`（破坏 `docker-*` 命名一致性）
- ❌ 不声明 `.PHONY`，导致与同名文件冲突
- ❌ 把硬编码端口写在脚本里，不暴露给命令行
- ❌ 注释语言混用（中英夹杂且不一致）
- ❌ 在解释型项目里硬塞 `build` 命令却什么都不做
- ❌ 把 `docker-build-cn` 默认放进所有 docker 项目的 Makefile
- ❌ `clean` 命令误删 `node_modules/` / `.venv/` / 源码目录

---

## 六、references/ 使用方式

`references/` 目录包含 4 份精简骨架模板，可直接复制到项目根目录后按需扩展：

| 文件 | 适用场景 | 命令数 |
|---|---|---|
| `Makefile.python.template` | Python 项目（FastAPI / Flask / Django） | ~15（含按需注释） |
| `Makefile.go.template` | Go 项目（Gin / CLI） | ~18（含按需注释） |
| `Makefile.frontend.template` | 前端项目（Vue3 / Next / Nuxt） | ~13 |
| `Makefile.mobile.template` | Android + iOS 双端（用 platform 参数切换） | ~20 |

**使用方式**：
1. 选最匹配项目类型的模板
2. 复制到项目根目录改名为 `Makefile`
3. 修改变量（`APP_NAME`、`SCHEME`、`PORT` 等）
4. 按需启用注释掉的可选命令（去掉行首 `#`）
5. 跑 `make help` 确认输出整齐

---

## 七、与现有 skill 的协作

| Skill | 协作点 |
|---|---|
| `config-management` | 涉及 `.env` / `config.yaml` / `config.jsonc` 的项目，配合该 skill 确保配置格式一致 |
| `template_code/AGENTS.md` | 模板项目规范：改动 Makefile 后需同步 lint/fmt 流水线 |

---

## 八、常见问题

### Q1: 为什么解释型语言不强制 `build`？

A: Python / Node 服务端通常不需要构建步骤，依赖同步即视为"构建"。硬塞一个空 `build` 会污染 help 输出。如果团队需要"打包步骤"（如 PyInstaller、npm pack），应单独命名（如 `bundle` / `package`）而不是 `build`。

### Q2: `dev` 和 `start` 的区别？

A: `dev` = 开发模式（带热重载、debug 日志、绑定 localhost）；`start` = 生产模式（多 worker、生产日志、绑定 0.0.0.0）。两者必须分开，不能合并。

### Q3: 为什么 `.PHONY` 必不可少？

A: 如果 Makefile 中存在与目标同名的文件/目录（如 `test` 目录、`build` 目录），make 会认为目标"已最新"而跳过。`.PHONY` 强制每次都执行命令。

### Q4: `docker-logs` 如何支持指定服务？

A: 利用 shell 判断 `$(s)` 变量：

```makefile
.PHONY: docker-logs
docker-logs: ## 查看日志（默认所有服务; make docker-logs s=app）
	@if [ -n "$(s)" ]; then \
		$(COMPOSE) logs -f $(s); \
	else \
		$(COMPOSE) logs -f; \
	fi
```

### Q5: 移动端为什么用 `platform` 参数而不是分两个 Makefile？

A: 双端项目通常共享 CI 流水线、共享文档，分两个 Makefile 维护成本高。`platform=android|ios` 参数让一份 Makefile 覆盖两端，且 `make help` 只显示当前平台的目标。

---

## 九、变更记录

- v1.0：初始版本。核心 6 命令 + 编译型 +build；按需覆盖 Docker / DB 迁移 / i18n / 代码生成；含 4 份 references 模板。
