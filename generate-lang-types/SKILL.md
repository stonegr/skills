---
name: "generate-lang-types"
description: "学习任意编程语言的类型系统，生成类型定义 + 校验两份详细教学文件，含基础类型、泛型、可选、特色"
---

# lang-types — 语言类型系统学习助手

## 用途

当用户想系统学习某门编程语言的类型系统时，本 skill 生成完整的教学材料：一份讲「怎么定义各种数据类型」，一份讲「怎么校验这些类型」（含静态类型检查 + 运行时校验）。

适用场景：
- 学一门新语言想快速摸清类型系统
- 对比不同语言的类型机制
- 项目里要写复杂数据模型，想参考成熟写法
- 面试前突击类型相关知识点

## 触发方式

```
/lang-types <language> [--skip-outline]
```

参数说明：
- `<language>`（必填）：目标语言，小写、去空格。例：`python`、`typescript`、`go`、`rust`、`java`、`kotlin`、`swift`、`scala`、`cpp` 等
- `--skip-outline`（可选）：跳过大纲生成，直接生成两份详细文件

示例：
- `/lang-types python`
- `/lang-types typescript --skip-outline`
- `/lang-types rust`

## 输出位置

所有生成文件统一存到：

```
./dist/learn_types_<language>/
```

文件结构：

```
learn_types_<language>/
├── outline.md              # 章节大纲（默认生成）
├── data_types.<ext>        # 数据类型定义
└── data_validation.<ext>   # 数据类型校验
```

`<ext>` 根据语言决定：`py` / `ts` / `go` / `rs` / `java` / `kt` / `swift` / `scala` / `cpp` 等。

## 工作流程

### Step 1：解析参数
- 提取 `<language>`，标准化为小写
- 判断是否带 `--skip-outline`
- 确认目标目录是否存在，不存在则 `mkdir -p`

### Step 2：知识准备
- 调取已有知识中该语言类型系统的关键点
- **必要时**联网检索官方文档（如 python.org、typescriptlang.org、doc.rust-lang.org、go.dev 等），确保信息时效性
- 标注信息对应的版本（如「Python 3.12+」「TypeScript 5.x」「Rust Edition 2024」）

### Step 3：生成大纲（除非 `--skip-outline`）
- 在临时目录创建 `outline.md`
- 列出 `data_types.<ext>` 和 `data_validation.<ext>` 的章节结构
- 每节一句话说清楚讲什么
- 完成后停下，告知用户路径，等用户 review 并确认

### Step 4：生成详细文件
- 用户确认大纲后（或带 `--skip-outline` 时直接生成）：
  1. 生成 `data_types.<ext>`
  2. 生成 `data_validation.<ext>`
- 两个文件互相呼应：定义文件中定义的类型，在校验文件中演示如何校验

### Step 5：交付
- 输出三个文件的完整路径
- 总结两份文件主要内容
- 提示用户到目录 review

## 必须覆盖的内容

### `data_types.<ext>` 必须包含

1. **基础类型**：字符串、数字、布尔、字符（如有）
2. **容器类型**：列表/数组、元组、字典/Map、集合/Set
3. **枚举**：enum 的定义与使用
4. **结构类型**：struct / class / interface / trait / protocol / data class 等
5. **泛型**：泛型函数、泛型类、泛型约束
6. **可选与空值**：Optional / nullable / Maybe / void 等
7. **类型别名**：type alias / using
8. **类型推断**：编译器/解释器怎么推导类型
9. **类型转换**：cast / parse / as / 类型断言 / 强转
10. **该语言独有特色**：其他语言没有的独特类型机制（重点标注）：
    - Rust: `Result<T, E>`、生命周期、`?` 操作符、`impl Trait`
    - Go: 隐式接口实现、结构体标签、错误处理
    - TypeScript: 字面量类型、模板字面量类型、判别联合、satisfies
    - Python: `Protocol`、类型守卫、`@override`
    - Java: `sealed`、record、pattern matching
    - Kotlin: data class、sealed class、协程
    - Swift: optional chaining、protocol extension、泛型 where 子句
11. **完整实战模型**：定义真实可用的 `User` / `Order` / `Pet` / `Article` 结构，覆盖基础类型、容器、可选、嵌套、泛型的组合用法

### `data_validation.<ext>` 必须包含

1. **静态类型检查**：编译器 / IDE / 类型注解层面
2. **运行时类型校验**：
   - schema validation
   - decoder / parser
   - assert / require
   - pattern matching
3. **嵌套结构校验**：对象嵌套对象 / 数组如何校验
4. **可选字段校验**：nullable / Optional 字段怎么校验
5. **联合类型校验**：Union / Either / 多类型字段
6. **校验失败处理**：
   - 错误信息格式
   - 异常抛出
   - 自定义错误
   - 错误聚合（多个错误一次报）
7. **完整校验示例**：用 `data_types` 中的实战模型演示完整校验流程
8. **该语言特有校验机制**：标注该语言独有的校验工具或语法

## 风格要求

- **详细+全面**：不偷懒，宁多勿少
- **可运行**：所有代码示例语法必须正确，可直接复制运行
- **真实场景**：用贴近业务的模型（User/Order/Pet/Article）演示，不用 foo/bar
- **重点标注**：语言独有特性要专门标注（`★ Rust 特色`、`★ Go 特色` 等）
- **中文注释为主**：专有名词保留英文
- **版本标注**：关键语法标注对应版本
- **文件大小**：详细但不冗余，单文件建议 800–1500 行

## 联网检索策略

按以下优先级查询：
1. 该语言官方网站（python.org、typescriptlang.org、go.dev 等）
2. 官方 spec / reference / standard library 文档
3. 知名教程（MDN、Microsoft Learn 等）

避免来源：
- 个人观点博客（除非官方引用）
- 过时的 StackOverflow 答案（>3 年的注意核实）

## 错误处理

- 目录创建失败 → 告知用户检查权限
- 不支持的语言 → 告知用户，但允许尝试（知识库可能够用）
- 联网失败 → 退回到已有知识，告知用户「未联网核实，请人工核对最新版本」

## 注意事项

- 中文输出为主，但代码、关键词、版本号保留英文
- 生成前确认 `/etc/code/conf/scripts_ai/` 目录可写
- 不修改飞书 / obsidian，等用户主动要求才同步
- 用户 review 大纲时可修改，确认后再生成详细文件
