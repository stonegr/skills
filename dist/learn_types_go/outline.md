# Go 类型系统学习大纲

> 覆盖版本：Go 1.18 ~ 1.26（推荐 1.21+ 享受 slices/maps 包，1.22+ cmp.Ordered，1.23+ iter）
> 文件基于「Go 静态类型 + 类型声明 + 1.18 泛型」
> 风格：详细 + 可运行 + 真实业务模型（User/Order/Pet/Article）

---

## 文件 1：`data_types.go` —— 数据类型定义

### 1. 类型系统全景
- Go 是**静态强类型** + **编译期检查**（无运行时类型注解）
- 类型分类：基础类型 / 复合类型 / 类型声明 / 类型字面量
- Go 1.18 引入泛型：类型参数 + 类型约束
- 命名类型 vs 类型别名（`type X T` vs `type X = T`）
- 零值机制：每个类型都有默认零值

### 2. 基础类型
- `bool`（`true` / `false`）
- 整数：`int` / `int8` / `int16` / `int32` / `int64` / `uint` 系列
- 字节：`byte`（`uint8` 别名）/ `rune`（`int32` 别名）
- 浮点：`float32` / `float64`
- 复数：`complex64` / `complex128`
- 字符串：`string`（不可变字节序列）

### 3. 复合类型
- **数组** `[N]T` —— 长度是类型的一部分
- **切片** `[]T` —— 动态长度，引用语义
- **映射** `map[K]V` —— 无序键值对
- **结构体** `struct { ... }` —— 字段聚合
- **指针** `*T` —— 显式指针
- **函数** `func(...) (...)` —— 一等公民
- **接口** `interface { ... }` —— 方法集
- **通道** `chan T` —— 并发通信

### 4. 类型声明
- `type X T` —— 定义新类型（与 T 不兼容）
- `type X = T`（1.9+）—— 类型别名（与 T 完全相同）
- ★ 命名类型 vs 别名：业务建模用新类型，迁移/重构用别名

### 5. 常量与 iota
- `const` 声明
- `iota` 自动递增枚举常量
- 无类型常量（untyped constant）的隐式转换

### 6. 结构体（struct）
- 字段定义、字段标签（struct tag）
- ★ struct tag：`json:"name,omitempty"`、`validate:"required,email"`
- 字段嵌入（embedding）—— 「组合优于继承」
- 匿名字段（嵌入类型）方法提升（promoted methods）
- 构造函数惯例（NewXxx）

### 7. 方法（method）
- 值接收者 vs 指针接收者
- 方法集规则
- 嵌入类型的方法提升
- 接口实现（隐式）

### 8. 接口（interface）
- ★ **隐式实现**：不写 `implements`，方法集对了就是实现
- 空接口 `interface{}` / `any`（1.18+）
- 嵌入接口
- 类型断言：`x.(T)` / `x, ok := i.(T)`
- type switch：`switch v := i.(type) { ... }`
- 常用接口：`error`（`Error() string`）、`Stringer`、`Reader`/`Writer`、`Sort.Interface`

### 9. ★ 泛型（Generics，1.18+）
- 类型参数列表：`[T any]` / `[T comparable]`
- 类型约束：`interface { ... }` 现在是「类型集合」而不只是「方法集合」
- 联合类型元素：`int | float64`
- 底层类型元素：`~int`（匹配所有 int 的命名类型）
- 预定义约束：`any`（1.18）、`comparable`（1.18）、`cmp.Ordered`（1.22）
- 泛型函数 + 泛型类型
- 类型推断（type inference）

### 10. 切片与映射的泛型
- 1.21+ `slices` 包：`slices.Sort`、`slices.Contains`、`slices.Compact`
- 1.21+ `maps` 包：`maps.Keys`、`maps.Values`、`maps.Collect`
- 1.21+ 内置 `min` / `max` / `clear`
- 1.23+ `iter` 包 + `range over func`

### 11. 通道（chan）
- 无缓冲通道 `make(chan T)` vs 有缓冲 `make(chan T, n)`
- 方向：`chan<-`（只发送）/ `<-chan`（只接收）
- `close` 与 `range` 配合遍历通道

### 12. 函数与多返回值
- 多返回值（Go 特色）
- 命名返回值
- 变参 `...T`
- 闭包
- `defer` / `panic` / `recover`
- `init()` 函数

### 13. 错误处理
- `error` 接口（`Error() string`）
- 自定义错误类型
- `errors.New` / `fmt.Errorf` / `errors.Join`（1.20+）
- 错误包装：`%w`
- 错误判定：`errors.Is` / `errors.As`（1.13+）

### 14. 类型断言与类型转换
- 类型转换 `T(x)`（显式）
- 类型断言 `x.(T)`（运行时检查）
- 类型 switch `switch v := i.(type)`

### 15. 反射（reflect）
- `reflect.TypeOf` / `reflect.ValueOf`
- 动态读取 struct tag
- 动态调用方法
- 性能开销，仅在必要时使用

### 16. ★ Go 独有特色汇总
- 接口隐式实现（structural typing 的轻量版）
- 类型嵌入模拟继承
- 多返回值 + 显式 error 处理
- struct tag 元数据机制
- 1.18 泛型
- 1.21 slices/maps 标准库
- 1.22 cmp.Ordered
- 1.23 iter 包 + range over func
- defer / panic / recover 错误恢复

### 17. 完整实战模型
- 定义 `User`、`Address`、`Pet`、`Article`、`Order` 五个结构体
- 配套：常量（状态枚举）、接口（业务接口）、泛型容器、type switch
- 覆盖：基础类型、切片、映射、指针、嵌入、struct tag、泛型、接口、错误处理
- 提供构造函数、`String()` 方法（实现 Stringer 接口）

---

## 文件 2：`data_validation.go` —— 数据类型校验

### 1. 校验全景
- 静态层：Go 编译器本身（强类型）
- 运行时层：
  - 标准库 `encoding/json`（隐式类型转换 + 字段校验）
  - `reflect` 手写校验器
  - 第三方：`go-playground/validator`（最主流）
  - 第三方：`go-ozzo/ozzo-validation`（规则链式）
- 业务层：自定义 Validate() 方法

### 2. 编译期类型检查
- 强类型：int 和 string 不能混
- 命名类型严格区分：`type UserID int`，不能把 int 当 UserID 用
- 泛型约束在编译期生效

### 3. encoding/json 反序列化校验
- 字段必须存在（用 `[]byte` 缺失字段会报错）
- 类型不匹配会返回 `*json.UnmarshalTypeError`
- struct tag 控制 JSON 字段名
- `json.Number` 保留数字精度
- 嵌套结构自动递归

### 4. 类型断言与 type switch
- `x.(T)` 安全断言：`val, ok := x.(T)`
- `switch v := i.(type) { case T: ... }` 做形状判断
- 错误处理：`fmt.Errorf("unexpected type: %T", v)`

### 5. reflect 手动校验
- `reflect.TypeOf(obj)` / `reflect.ValueOf(obj)`
- 遍历 struct 字段读 tag
- 检查字段值（zero value / 范围 / pattern）
- 演示：用 reflect 写一个简单的「必填字段」校验

### 6. ★ go-playground/validator（主流推荐）
- 安装：`go get github.com/go-playground/validator/v10`
- 常用 tag：`required`、`min`、`max`、`len`、`email`、`url`、`uuid`、`oneof`
- 嵌套校验：`dive` 关键字
- 跨字段校验：`eqfield`、`gtfield`
- 自定义验证器：`RegisterValidation`
- 错误处理：`validator.ValidationErrors`

### 7. 自定义 Validate() 方法
- 业务层校验入口：实现 `Validate() error` 接口
- 调用基础校验 + 业务规则
- 与 go-playground/validator 配合：`func (u *User) Validate() error { return validate.Struct(u) }`

### 8. 嵌套结构校验
- 嵌套 struct 自动校验
- slice / map 元素校验
- pointer 解引用校验

### 9. 可选与零值字段
- Go 没有 nullable 类型，用指针 `*T` 表示可空
- `omitempty` JSON tag：零值不序列化
- sql.NullString / sql.NullInt64 标准库模式

### 10. 联合类型校验
- Go 1.18+ 的「类型联合约束」是编译期概念，运行时用 interface + type switch
- 反序列化时用 `json.RawMessage` + 自定义 UnmarshalJSON
- 演示：`UnmarshalJSON` 解析判别联合（按 `type` 字段分发）

### 11. 校验失败处理
- error 接口返回
- `errors.Join`（1.20+）聚合多个错误
- 错误包装：`fmt.Errorf("user validation: %w", err)`
- 自定义错误类型带字段信息

### 12. 与 `data_types.go` 联动
- 把 `data_types.go` 里的 `User` / `Address` / `Pet` / `Article` / `Order` 引入
- 演示：
  - 解析 JSON 字符串 → User 结构体
  - 校验失败时打印详细错误
  - 用 type switch 处理 `interface{}` 字段
  - 反射读取 struct tag

### 13. ★ Go 独有校验机制
- `json.Unmarshal` 的隐式类型校验（最轻量）
- `validator` 库的 tag 驱动校验（最主流）
- 反射手写校验（最灵活）
- 自定义 `UnmarshalJSON` 处理 union type
- `errors.Join`（1.20+）错误聚合

### 14. 实战校验示例
- 演示解析一段 JSON 字符串（模拟 API 响应）→ 校验 → 拿到 `User`
- 故意构造一段非法数据 → 演示错误聚合输出
- 用 type switch 校验 `interface{}` 字段
- 用 `UnmarshalJSON` 实现判别联合（Union by type tag）

---

## 关键版本对照表

| 版本 | 特性 |
|------|------|
| 1.0  | 基础类型系统、接口、map、slice、chan |
| 1.4  | go generate |
| 1.9  | 类型别名 `type X = T` |
| 1.13 | 错误包装 `errors.Wrap` / `errors.Is` / `errors.As` |
| 1.17 | 有序 map 遍历（虽然语义上仍不保证） |
| 1.18 | **泛型**、类型约束、`any`、`comparable` |
| 1.20 | `errors.Join` |
| 1.21 | `slices` / `maps` 包、内置 `min` / `max` / `clear` |
| 1.22 | `cmp.Ordered`、range over integer、for-range loop 变量作用域 |
| 1.23 | **iter 包**、range over func |
| 1.25 | sync.WaitGroup.Go、`slices.Sorted`、`maps.Insert` |

---

## 学习顺序建议

1. 先看 `data_types.go`：建立「Go 类型系统能表达什么」的认知
2. 再看 `data_validation.go`：学习「怎么在运行时落地校验」
3. 重点章节：类型声明（§4）、struct tag（§6）、接口与隐式实现（§8）、泛型（§9）、错误处理（§13）、reflect 校验（校验 §5）、go-playground/validator（校验 §6）