---
name: generate-snippets
description: 批量生成vscode的code-snippets，为各种语言生成相同功能的代码片段
---

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

# vscode snippets 容易犯的错
- $的转义
例如你在实际的代码中需要生成`$1`, 这个和vscode的snippet中的占位符重复，所以在body中需要写成`\\$1`，如果是`${a}`，那么应该写成：`\\${a}`
- 提示语言
如果你要提示用户此时输入的是什么，可以写成：${1:你要提示的内容}
- 可供选项
如果你要在用户输入的时候给他一些选择项: ${1|选项1,选项2,选项3|}

# 用户输入
- 获取目标语言
- 如果调用skill的传入了就直接使用，不要询问
	- 例如：`/generate-snippets go` 则代表生成go语言的

# 需要生成的模块
- 循环
- 错误捕获
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