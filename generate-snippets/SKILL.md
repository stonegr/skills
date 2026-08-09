---
name: generate-snippets
description: 批量生成vscode的code-snippets，为各种语言生成相同功能的代码片段
---

# $ 转义速查（重点）

shell/js/python 的 snippet body 里 `$` 转义是出错率最高的点。**口诀：想要插入的代码里有字面 `$` 时，JSON 文件里写 `\\$`**。

## 三层模型

snippet body 的 `$` 要"穿过"两层解析才到目标代码：

```
你想插入的代码:    $var                 ← 用户最终看到的
                   ↑ 渲染自
snippet 看到:      \$var               ← JSON 解码后的 body
                   ↑ 来源于
JSON 文件 raw:    \\$var              ← 文件里实际写的字符
```

每一层的规则：
- **JSON 文本层**：写 `\\` 表示一个 `\`（反斜杠）。`$` 在 JSON 里**没有特殊含义，直接写 `$`**，不要写 `\$`（会报 invalid escape）。
- **JSON 解码后**：得到 `\$` / `$var` / `${1:default}` 等。
- **snippet 引擎层**：`\$` 渲染成字面 `$`；`$N` / `${N:default}` 是占位符；其他 `$` 直接渲染。

## 4 个高频模式

| 想插入的代码 | JSON 文件里写 | 说明 |
|---|---|---|
| `$var`（字面） | `\\$var` | snippet 看到 `\$var` → 渲染为 `$var` |
| `$$`（PID） | `\\$\\$` | snippet 看到 `\$\$` → 渲染为 `$$` |
| `${var:-default}` | `\\${var:-default}` | snippet 看到 `\${...}` → 整段渲染为字面 |
| `${1:var}`（占位符） | `${1:var}` | snippet 直接当占位符处理 |

**不需要转义的**：单/双引号 `'` `"`、`(` `)`、`$` 以外的其他字符、`$(command)` 命令替换、`$((expr))` 算术展开。

## 容易踩的坑

**坑 1：shell 默认值语法和占位符语法冲突**

❌ `kill ${1:-TERM} \\$pid`  
`${1:-TERM}` 看起来像 shell 默认值 `:-`，但 VSCode 把它当占位符，遇到 `:-` 会解析失败。

✅ `kill ${1:TERM} \\$${2:pid}`  
拆成两个占位符，让用户填 TERM/KILL 和 pid 变量名。

**坑 2：占位符值嵌进 `${var:-default}` 里**

❌ `${1:VAR}="\\${$1:-${2:default}}"`  
`$1` 紧跟 `\$` 时 snippet 解析混乱。

✅ `${1:VAR}="\\${${1:VAR}:-${2:default}}"`  
`${1:VAR}` 写两次即可——第一次是左值赋值，第二次嵌进 shell 参数展开。

**坑 3：`$` 后面直接跟占位符**

❌ `\\$$1` → snippet 看到 `\$` + `$1`（会渲染成 `$` + 占位符 1 的值，但容易写错）。  
✅ 统一用 `\\$${1:var}`，语义更清楚。

**坑 4：JSON 里写 `\$`**

❌ `"\$var"`  
JSON 解析器会报 "Invalid \escape"。

✅ `"\\$var"`

## 验证清单（生成完必跑）

```bash
# 1. JSON 合法
python3 -c "import json; json.load(open('shell.code-snippets'))"

# 2. 用 python 模拟 snippet 展开（参考 references/expand.py）
python3 references/expand.py shell.code-snippets
```

如果展开结果有 `$$` 变成空、或 `$1` 变成字面 `$`，说明 `\\` 写少了。

# vscode snippets 示例
```jsonc
{
	// Place your snippets for skill here. Each snippet is defined under a snippet name and has a prefix, body and 
	// description. The prefix is what is used to trigger the snippet and the body will be expanded and inserted. Possible variables are:
	// $1, $2 for tab stops, $0 for the final cursor position, and ${1:label}, ${2:another} for placeholders. Placeholders with the 
	// same ids are connected.
	// Example:
	// "Print to console": {
	// 	"prefix": "log",
	// 	"body": [
	// 		"console.log('$1');",
	// 		"$2"
	// 	],
	// 	"description": "Log output to console"
	// }
}
```

# 提示语言和选项

- **提示语言**（让用户知道这里要填什么）：`${1:变量名}`
- **选项列表**（用户用 tab 切换）：`${1|选项1,选项2,选项3|}`

# 用户输入
- 获取目标语言
- 如果调用skill的传入了就直接使用，不要询问
	- 例如：`/generate-snippets go` 则代表生成go语言的

# 需要生成的模块
- 循环(数组，range)
- 错误捕获（错误定义、错误抛出、错误捕获）
- if判断逻辑
- 读取文件
- 读取env
- 执行shell命令
- 获取程序运行耗时
- 获取当前目录
- 命令行参数获取
- 获取用户输入
- 多线程(包括lock, rlock, Semaphore, condition, event, Barrier, 这几个功能都要有))
- 多进程
- 日志打印
- 读取json配置文件
- 程序退出监听，比如sighup这种，要做推出前的清理或者处理

> 上面的是我想生成的功能名称，`prefix` 要保证是英文,`Print to console`和`description`是中文

# 文件格式
- 以python为例子
  - 文件名: python.code-snippets 放在当前项目的.vscode目录下
  - prefix: 如果是if -> py_if 用-连接