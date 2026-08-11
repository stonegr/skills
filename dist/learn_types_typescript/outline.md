# TypeScript 类型系统学习大纲

> 覆盖版本：TypeScript 4.9 ~ 7.0（推荐 5.4+ 享受 NoInfer / 类型谓词推断）
> 文件基于「TypeScript 静态类型 + 类型编程 + 类型工具」
> 风格：详细 + 可运行 + 真实业务模型（User/Order/Pet/Article）

---

## 文件 1：`data_types.ts` —— 数据类型定义

### 1. 类型系统全景
- TS = JavaScript 的超集，加静态类型 + 编译期检查
- 运行时**不检查**类型（编译后类型擦除，类型仅用于 IDE / tsc）
- 结构化类型（structural typing）—— 不需要 nominal 兼容
- 类型分类：基础类型 / 容器 / 对象 / 函数 / 字面量 / 高级类型

### 2. 基础类型
- boolean / number / string / bigint / symbol
- null / undefined / void / never
- unknown（安全的 any，反向不可赋值）
- 字面量类型："draft"、42、true

### 3. 容器类型
- 数组 T[] / Array<T>
- 元组 [T1, T2, T3] —— 长度与位置类型固定
- 对象 object / Record<K, V>
- Map<K, V> / Set<T> / WeakMap / WeakSet

### 4. 联合与交叉
- 联合类型 A | B
- 交叉类型 A & B
- 类型守卫 narrowing（typeof / in / instanceof / 等式）

### 5. 字面量类型与 as const
- 字面量联合：type Status = "draft" | "published"
- as const —— 把字面量冻结成 readonly 字面量
- 字面量类型在 union 中的字面量扩展效果

### 6. 枚举
- enum Direction { Up, Down } 数字枚举
- enum Status { Active = "active" } 字符串枚举
- const enum（编译期擦除）
- 与字面量联合的对比

### 7. 接口与类型别名
- interface —— 描述对象形状
- type —— 更通用的类型定义
- 声明合并（declaration merging）—— interface 特有
- extends 接口继承
- 交叉 / 联合

### 8. 类（class）
- 字段 + 构造函数
- 访问修饰符：public / private / protected
- readonly 字段
- implements 接口
- abstract 抽象类
- 静态字段 + 静态方法
- private fields（#name）—— 编译期硬私有
- 装饰器（5.0+）

### 9. 函数类型
- 函数声明与函数表达式
- 可选参数 / 默认参数
- 剩余参数
- void 返回类型
- 函数重载签名

### 10. 泛型（Generics）
- 泛型函数
- 泛型接口
- 泛型类
- 泛型约束 T extends X
- 多泛型 + 关系约束
- 泛型默认值
- const 泛型（5.0+）

### 11. 可选与空值
- T | undefined / T | null
- strictNullChecks 模式
- 可选链 ?.
- 空值合并 ??
- 非空断言 x!

### 12. 类型别名（type）
- type UserID = string
- type User = { ... }
- 模板字面量类型（4.1+）
- 工具类型：Partial、Required、Pick、Omit、Record、Exclude、Extract、ReturnType、Parameters、Awaited

### 13. 类型断言与类型守卫
- 类型断言 as T
- as const 字面量断言
- 类型守卫：typeof / in / instanceof / 等式
- 自定义类型守卫：x is T
- 断言函数 asserts x is T（3.7+）

### 14. 高级类型编程
- 条件类型 T extends U ? X : Y
- 映射类型 {[K in keyof T]: ...}
- infer 关键字
- keyof / typeof
- 索引访问类型 T[K]
- 分布式条件类型
- 模板字面量类型
- satisfies 操作符（4.9+）—— 校验形状但保留具体类型

### 15. 类型推断
- 上下文类型推断
- 推断算法
- ReturnType / Parameters 工具类型自动推断

### 16. 模块与命名空间
- ES Modules：import / export
- 默认导出与命名导出
- 类型导入：import type
- namespace（旧风格，新项目不推荐）

### 17. 声明文件
- .d.ts 文件
- declare module
- declare global
- 第三方库类型

### 18. TypeScript 独有特色汇总
- 结构化类型
- 联合 + 判别联合
- 条件类型 + infer
- 映射类型
- 模板字面量类型
- satisfies 操作符
- const 泛型
- 类型守卫 + 断言函数
- 工具类型体系

### 19. 完整实战模型
- 定义 User / Address / Pet / Article / Order 五个类型
- 配套：枚举 / 字面量联合 / 判别联合 / 泛型 / 工具类型 / 类型守卫
- 业务层用 class 实现，类型层用 interface 描述

---

## 文件 2：`data_validation.ts` —— 数据类型校验

### 1. 校验全景
- 静态层：tsc 编译器 + IDE（红线）
- 运行时层：
  - JSON.parse + 自定义校验（最轻量）
  - Zod（当前主流推荐）
  - Yup / Joi（老牌）
  - io-ts（FP 风格）
  - Valibot（轻量新秀）
  - ArkType（性能最佳）
- 选择策略：边界（API 入参、localStorage、URL query）必须做运行时校验

### 2. 编译期类型检查
- tsc 严格模式
- 常见编译错误：类型不匹配、属性缺失、可空处理
- 演示：故意写错代码，看 tsc 报错

### 3. JSON.parse 隐式校验
- JSON.parse(text) 返回 any
- 必须先校验再使用
- 演示：解析一段 JSON → 校验 → 拿到 User

### 4. Zod（主流推荐）
- 安装：npm install zod
- 基础 schema：z.object({...})
- 常用验证器：z.string().min(1).email()、z.number().int().positive()
- 可选字段 .optional() / .nullable()
- 字面量联合：z.union([z.literal("a"), z.literal("b")])
- 判别联合：z.discriminatedUnion("type", [...])
- 嵌套校验：z.object({ pet: PetSchema })
- 数组校验：z.array(X)
- 转换 / 预处理：.transform() / .preprocess()
- 错误处理：safeParse 返回 { success, data, error } / parse 抛 ZodError
- 类型推断：z.infer<typeof Schema> 直接从 schema 拿类型
- 自定义校验：.refine() / .superRefine()
- Partial / Pick / Omit：.partial() / .pick({...})

### 5. z.infer 与类型联动
- type User = z.infer<typeof UserSchema> —— schema 是单一真相源
- 避免「类型和校验规则双重维护」

### 6. 嵌套结构校验
- Zod 嵌套对象自动递归
- 数组元素校验
- 复杂容器：z.record(z.string(), z.array(z.number()))

### 7. 可选与可空字段
- .optional() —— 字段可以缺失
- .nullable() —— 字段可以是 null
- .default(value) —— 默认值

### 8. 联合类型校验
- z.union([A, B]) —— 按顺序尝试
- z.discriminatedUnion("type", [...]) —— 按 type 字段精确分发（更快、更准）

### 9. 校验失败处理
- safeParse 风格（不抛异常）
- parse 风格（失败抛 ZodError）
- 错误信息格式化：.format() / .flatten()
- 错误聚合：Zod 默认一次报所有错误
- 自定义错误消息

### 10. 与 data_types.ts 联动
- 把 data_types.ts 的 User/Order/Pet/Article 引入
- 用 Zod 写对应的 *Schema 校验层
- 演示：JSON → safeParse → 拿到 User
- 演示：故意构造非法数据，看 Zod 错误输出
- 演示：z.infer 把 schema 转为业务类型

### 11. TypeScript 独有校验机制
- z.infer —— schema 即类型
- discriminatedUnion —— 判别联合比 union 更精确
- safeParse —— 不抛异常，符合 FP 风格
- 判别联合 + type guard 收窄（编译期 + 运行时联动）
- 自定义类型守卫做运行时类型推断
- 装饰器校验（实验性）

### 12. 实战校验示例
- 演示解析一段 JSON（模拟 API 响应）→ 校验 → 拿到 User
- 故意构造非法数据 → 演示错误聚合
- 用 discriminatedUnion 解析 Pet 的 Cat | Dog
- 边界校验：API 入参 + localStorage 读取 + URL query
- 完整链路：unknown → schema → type-safe

---

## 关键版本对照表

| 版本 | 特性 |
|------|------|
| 3.7  | 断言函数 asserts x is T、递归类型 |
| 4.0  | 可变元组、标签元组、short-circuiting 赋值 |
| 4.1  | 模板字面量类型、key remapping |
| 4.3  | separate write types、override 关键字 |
| 4.4  | Control flow analysis of aliased conditions |
| 4.5  | Awaited 类型、type modifier on import names |
| 4.7  | extends constraints on infer、optional variance annotations |
| 4.8  | Improved inference for infer、unconstrained type parameter |
| 4.9  | satisfies 操作符、in 算子收窄、auto-accessors |
| 5.0  | const 类型参数、装饰器（标准）、const enums |
| 5.1  | JSX 类型简化、getter/setter 类型分离 |
| 5.2  | using 声明、装饰器元数据 |
| 5.3  | import attributes、resolve JSON modules |
| 5.4  | NoInfer 工具类型、Object.groupBy |
| 5.5  | 类型谓词推断、regular expression syntax |
| 5.6  | disallowed nullish / truthy checks |
| 5.7  | 嵌套函数声明类型推断 |
| 6.0+ | 性能改进、新 strict 选项 |
| 7.0  | 最新稳定版（2026） |

---

## 学习顺序建议

1. 先看 data_types.ts：建立「TS 类型系统能表达什么」的认知
2. 再看 data_validation.ts：学习「怎么在运行时落地校验」
3. 重点章节：联合与判别联合（§4）、类与接口（§7-8）、泛型（§10）、条件类型 + infer（§14）、satisfies（§14）、Zod + z.infer（校验 §4-5）
