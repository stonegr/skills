---
name: pdf-inspector
description: 处理 PDF 文件的统一入口——检测类型、转 Markdown、抽文本/表格、调试渲染。**任何 PDF 任务（检测类型、抽文字、转 Markdown、读表格）都优先用本 skill，不要用 markitdown 处理 PDF**。三个子命令：detect-pdf（判断 text-based/scanned/image-based/mixed，给出 OCR 建议）、pdf2md（PDF 转 Markdown，保留表格/列/页码）、dump_ops（导出原始 content stream 操作）。本 skill 专门覆盖本机 cargo 安装的 pdf-inspector 二进制。
---

# pdf-inspector 使用指南

`pdf-inspector` 是 Firecrawl 团队用 Rust 写的 PDF 检视/分类/转 Markdown 工具，速度快（lopdf + rayon），内置智能 OCR 路由判断。本 skill 假设你已经在本机通过 `cargo install pdf-inspector` 安装好了三个二进制：`detect-pdf`、`pdf2md`、`dump_ops`，位置在 `~/.cargo/bin/`。

## 何时用哪个命令

| 你想做的事 | 用哪个 |
|---|---|
| 这个 PDF 能不能直接抽文字？要不要 OCR？ | `detect-pdf` |
| 把 PDF 转成 Markdown（带表格/列/页码） | `pdf2md` |
| 只想要纯文本、不要表格/页眉 | `pdf2md --raw` 或 `--compact` |
| 拿到坐标/字体信息做进一步处理 | `pdf2md --items-json` |
| 加密 PDF | `pdf2md --password PW` |
| 只想看前几页 | `pdf2md --select-pages 1,3,5-10` |
| PDF 渲染/排版异常，排查 content stream | `dump_ops` |

## 1. `detect-pdf` — 检测 PDF 类型

判断 PDF 属于四种类型之一，并给出置信度和 OCR 建议：

- **TEXT-BASED**：可直接抽文字（最快）
- **SCANNED**：扫描件，必须 OCR
- **IMAGE-BASED**：以图片为主，OCR 可能有用
- **MIXED**：部分文字部分图片

### 基础用法

```bash
detect-pdf path/to/file.pdf
```

输出示例：

```
PDF Type Detection Results
==========================
File: file.pdf

Type: TEXT-BASED (extractable text)
Confidence: 100%

Page count: 2
Pages sampled: 2
Pages with text: 2
OCR recommended: NO
Title: Agent Quote PDF

Detection time: 7ms

Recommendation: Use direct text extraction (fast)
```

### 常用 flag

| flag | 作用 |
|---|---|
| `--json` | 输出 JSON，方便脚本解析 |
| `--analyze` | 在检测基础上再做布局分析（是否含表格/列） |

### 脚本化判断

```bash
# 只拿类型字符串
detect-pdf file.pdf --json | jq -r .pdf_type

# 判断是否需要 OCR（true/false）
detect-pdf file.pdf --json | jq -r .ocr_recommended
```

## 2. `pdf2md` — PDF 转 Markdown

智能判断 PDF 类型，文本型直接抽文字+布局还原，扫描型/图片型会建议改用 OCR 工具（不会自动 OCR）。

### 基础用法

```bash
# 输出到 stdout
pdf2md file.pdf

# 输出到文件
pdf2md file.pdf output.md
```

`stdout` 是 Markdown 正文，`stderr` 是元信息（页数、布局复杂度、耗时）。这是 Firecrawl 的设计：方便管道组合。

### 常用 flag

| flag | 作用 |
|---|---|
| `--raw` | 只输出 markdown，不要任何头部（适合直接管道给后续工具） |
| `--compact` | 压缩点状分隔符等冗余格式 |
| `--json` | 输出 JSON（含 markdown 字段、元信息） |
| `--items-json` | 输出带坐标/字体/加粗等元信息的 TextItem 数组（适合做结构化提取） |
| `--pages` | 在 markdown 中插入页码标记 `<!-- Page N -->` |
| `--select-pages 1,3,5-10` | 只处理指定页（逗号分隔 + 范围） |
| `--password PW` | 解密 PDF |
| `--detect-only` | 只检测类型不抽文字 |
| `--analyze` | 检测 + 抽文字 + 布局分析，不输出 markdown |

### OCR 相关（需 `ocr` feature）

默认安装 **不包含** OCR（不会自动 OCR 扫描型 PDF）。如果你自己用 `cargo install pdf-inspector --features ocr` 重装了，可以：

```bash
pdf2md file.pdf --ocr auto          # 自动判断哪些页走 OCR
pdf2md file.pdf --ocr force         # 全部页走 OCR
pdf2md file.pdf --ocr auto --ocr-dpi 300   # 提高渲染分辨率
pdf2md file.pdf --ocr auto --ocr-offline   # 禁止下载模型
```

OCR 选项：`--ocr {off,auto,force}`、`--ocr-dpi N`（默认 150）、`--ocr-min-confidence N`、`--ocr-hosted-threshold N`、`--ocr-model-dir DIR`、`--ocr-offline`。

> ⚠️ 当前默认 `cargo install pdf-inspector` 出来的二进制不支持 `--ocr`，运行会报 `this pdf2md build does not include OCR`。

### 退出码

- `0`：成功
- `1`：解析错误（文件损坏等）
- `2`：PDF 类型为 SCANNED/IMAGE-BASED，需要 OCR（仅 `--raw` 模式）

## 3. `dump_ops` — 导出 PDF 原始操作

低层调试工具，把 PDF content stream 里的绘图操作（`gs`、`cs`、`cm`、`q/Q`、`re`、`f`、`Tj` 等）逐行打印到 stdout。用于排查渲染异常、字体问题、坐标错乱等。

### 用法

```bash
# 打印第 1 页全部操作
dump_ops file.pdf

# 打印第 5 页
dump_ops file.pdf 5

# 只打印包含 "Tj" 的操作（文本绘制），找到首个匹配后输出 60 行
dump_ops file.pdf 1 Tj
```

第三个参数是子字符串过滤，命中后从该位置开始输出 60 行并停止。常用来定位某段文字/某个图形的绘制上下文。

> ⚠️ **必须给文件参数**，否则会 panic：`called Result::unwrap() on an Err value`。这个工具不像其他两个有 usage 输出。

## 典型工作流

### 流程 A：拿到一个 PDF，先判断怎么处理

```bash
# 第一步：检测类型
detect-pdf file.pdf

# 如果 Type: TEXT-BASED
pdf2md file.md --raw > file.md

# 如果 Type: SCANNED / IMAGE-BASED / MIXED（且需要图片内容）
# pdf-inspector 帮不了你，转用 markitdown/MinerU/PaddleOCR 等其他工具
```

### 流程 B：批量处理一批 PDF

```bash
for f in *.pdf; do
  type=$(detect-pdf "$f" --json | jq -r .pdf_type)
  if [ "$type" = "text_based" ] || [ "$type" = "mixed" ]; then
    pdf2md "$f" --raw > "${f%.pdf}.md"
  else
    echo "Skip $f (type=$type, needs OCR)" >&2
  fi
done
```

### 流程 C：提取带坐标的结构化文本

```bash
pdf2md file.pdf --items-json | jq '.items[] | select(.is_bold) | {text, page, x, y}'
```

返回每个加粗文本项的坐标，可用于定位标题/小节等。

### 流程 D：抽取加密 PDF 某几页

```bash
pdf2md secret.pdf --password mypass --select-pages 1,3-5
```

## 与其他 skill 的分工

| 场景 | 用哪个 skill |
|---|---|
| 想用 Python 库（pypdf/pdfplumber/pypdfium2）写脚本处理 PDF | `pdf` skill |
| 想用 markitdown 通用转换（含 PDF→MD） | `markitdown` skill |
| 想快速分类/检测/转 MD，且本机有 pdf-inspector 二进制 | **本 skill** |

## 注意事项

1. **三个二进制都不带 `--help`**。参数错了会 panic 或者静默忽略某个 flag。直接看源码 `~/.cargo/registry/src/index.crates.io-*/pdf-inspector-*/src/bin/` 或本 skill 的"常用 flag"表。
2. **`pdf2md` 把元信息打到 stderr**，Markdown 打到 stdout。可以放心用 `> out.md` 重定向，不会丢失元信息。
3. **OCR 不会自动启用**。扫描型 PDF 用 `pdf2md` 会得到 `Exit code 2`，并提示"Consider using MinerU or similar OCR tool"。要 OCR 必须重装带 feature 的版本。
4. **`dump_ops` 是低层工具**，正常提取请用 `pdf2md`。只有遇到"为什么这个 PDF 渲染出来是这样"的诡异问题时才用它。
5. **`detect-pdf` 速度快**（典型 7ms），可以放心在任何管道最前面跑一次作为预判。
6. **元信息（标题/作者等）通过 `detect-pdf` 的 `Title:` 字段拿到**，不会出现在 `pdf2md` 输出里。

## 升级

```bash
cargo install pdf-inspector --force

# 带 OCR 支持（首次会下载模型）
cargo install pdf-inspector --features ocr --force
```

OCR 模型会下载到系统标准缓存目录（macOS: `~/Library/Caches/`），如果不想下载可加 `--ocr-offline`。
