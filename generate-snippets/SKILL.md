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

# 用户输入
- 获取目标语言

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

> 上面的是我想生成的功能名称，`prefix` 要保证是英文,`Print to console`和`description`是中文

# 文件格式
- 以python为例子
  - 文件名: python.code-snippets 放在当前项目的.vscode目录下
  - prefix: 如果是if -> py_if 用-连接