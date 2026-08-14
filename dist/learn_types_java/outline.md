# Java 类型系统教学大纲

> 版本基线：**Java 21 LTS**（涵盖 Java 8 ~ 21 的核心特性，标注引入版本）
> 输出文件：`data_types.java` + `data_validation.java`
> 风格：详细、全面、可直接运行、业务模型驱动（User / Order / Pet / Article）

---

## 一、`data_types.java` —— 数据类型定义

### 1. 基础类型（Primitive Types）
- 8 种基础类型：`byte` / `short` / `int` / `long` / `float` / `double` / `boolean` / `char`
- 取值范围、默认值、字面量后缀（`L` / `F` / `D`）
- 基础类型 vs 包装类型（Wrapper）的差异
- 自动装箱 / 拆箱（Auto-boxing / Unboxing）及陷阱（NullPointerException）
- 字符串字面量与 `String` 池

### 2. 数组（Array）
- 一维数组、 多维数组、不规则数组
- 数组协变（Array Covariance）及其安全隐患
- `Arrays` 工具类常用方法

### 3. 容器类型（Collection Framework）
- `Collection` 体系总览：`List` / `Set` / `Queue` / `Deque`
- `Map` 体系：`HashMap` / `LinkedHashMap` / `TreeMap` / `ConcurrentHashMap`
- `ArrayList` / `LinkedList` / `HashSet` / `TreeSet` / `PriorityQueue` 选择策略
- 不可变集合：`List.of` / `Set.of` / `Map.of`（Java 9+）
- 流式操作 `Stream`（Java 8+）

### 4. 枚举（enum）
- 基础 enum 定义（Java 5+）
- 带字段、方法、构造器的枚举（enum + 行为）
- `EnumSet` / `EnumMap` 高性能容器
- 在 switch 中的使用（传统 + 箭头语法）

### 5. 类与对象（class）
- 类的声明、字段、方法、构造器
- 访问修饰符：`public` / `protected` / `private` / package-private
- `static` / `final` / `abstract` 修饰符
- 初始化顺序、实例初始化块、静态初始化块
- 不可变类的设计原则

### 6. 抽象类与接口
- 抽象类（`abstract class`）的定义与使用场景
- 接口（`interface`）的演进：常量 → 抽象方法 → 默认方法（Java 8）→ 静态方法 → `private` 方法（Java 9）
- 函数式接口（`@FunctionalInterface`）与 Lambda
- 抽象类 vs 接口的选择

### 7. 嵌套类与内部类
- 静态嵌套类
- 成员内部类
- 局部内部类
- 匿名内部类（Lambda 替代场景）

### 8. ★ Record（Java 14 预览 / 16 正式）
- 不可变数据载体的简洁写法
- 自动生成：构造器、访问器、`equals`、`hashCode`、`toString`
- 紧凑构造器（Compact Constructor）做数据校验
- Record 与 Lombok 的对比
- Record 组件上添加注解

### 9. ★ Sealed Class / Interface（Java 17 正式）
- 封闭类型：`permits` 子类型白名单
- 与 `record` + `pattern matching` 配合实现代数数据类型（ADT）
- 模式匹配穷尽性检查

### 10. 泛型（Generics）
- 泛型类、泛型接口、泛型方法
- 类型擦除（Type Erasure）与桥接方法
- 有界类型参数：`<T extends Comparable<T>>`
- 通配符：`?` / `? extends T`（上界）/ `? super T`（下界）
- PECS 原则（Producer Extends Consumer Super）

### 11. Optional 与空值处理
- `Optional<T>`（Java 8+）的创建：`of` / `ofNullable` / `empty`
- 链式操作：`map` / `flatMap` / `filter` / `orElse` / `orElseGet` / `orElseThrow`
- Optional 的反模式（不要用作字段、不要序列化）
- `@Nullable` / `@NonNull` 注解（JSR 305 / JSpecify / Checker Framework）

### 12. 注解（Annotation）
- 内置注解：`@Override` / `@Deprecated` / `@SuppressWarnings` / `@FunctionalInterface`
- 元注解：`@Target` / `@Retention` / `@Inherited` / `@Repeatable` / `@Documented`
- 自定义注解的定义与使用
- 类型注解（Type Annotation, Java 8+）：`@NonNull String`

### 13. ★ 类型推断
- `var` 关键字（Java 10+）：局部变量类型推断
- 菱形操作符 `<>`（Java 7+）
- Lambda 形参类型推断
- 模式匹配中的 `var`（Java 21）：`case Box(var x) -> ...`

### 14. 类型转换
- 隐式转换（自动类型提升）：`int → long → double`
- 强制类型转换（窄化）：`(int) doubleValue`
- 自动装箱 / 拆箱
- `instanceof` 模式匹配（Java 16+）：`if (obj instanceof String s) { ... }`
- switch 模式匹配（Java 21）

### 15. ★ Pattern Matching 模式匹配（Java 16 ~ 21）
- `instanceof` 模式匹配
- `switch` 模式匹配（Java 21 正式）
- 记录模式（Record Pattern）：`case User(String name, int age) -> ...`
- 嵌套模式匹配与密封类型

### 16. Switch 表达式（Java 14 正式）
- 箭头语法：`case X -> ...`
- `yield` 返回值
- 穷尽性检查（与 sealed 配合）

### 17. Text Blocks 文本块（Java 13 预览 / 15 正式）
- 三引号字符串 `"""..."""`
- 缩进处理与转义

### 18. Java 独有特色总结
- 强类型 + 静态类型 + 名义类型（Nominal Typing）
- 类型擦除（与 C# 具化泛型对比）
- 单继承 + 多实现接口
- 注解即类型元数据（运行时可反射）

### 19. 完整实战模型
- **`User`**：基础字段 + Optional + 嵌套 Address + List 角色
- **`Order`**：泛型容器 + enum 状态 + sealed PaymentMethod
- **`Pet`**：抽象类 + record 子类（Dog / Cat / Bird 用 record 实现）
- **`Article`**：Text Blocks + Map 元数据 + 嵌套 List

---

## 二、`data_validation.java` —— 数据类型校验

### 1. 静态类型检查
- `javac` 编译期类型检查
- IDE 实时类型检查（IntelliJ IDEA）
- 注解处理器（Annotation Processor）的编译期检查
- Checker Framework（可选强类型检查）

### 2. 运行时校验基础
- `Objects.requireNonNull` / `requireNonNullElse`
- `assert` 断言（`-ea` 启用）
- 自定义前置校验工具方法

### 3. ★ instanceof 模式匹配校验
- 类型守卫：`if (obj instanceof String s)`
- 在 switch 中进行多类型分支校验

### 4. Objects 工具类
- `Objects.equals` / `Objects.hash` / `Objects.isNull` / `Objects.nonNull`
- `Objects.requireNonNullElse` / `requireNonNullElseGet`

### 5. ★ Bean Validation（JSR 380 / Jakarta Validation）
- 引入 Hibernate Validator
- 内置约束注解：`@NotNull` / `@NotBlank` / `@NotEmpty` / `@Size` / `@Min` / `@Max` / `@Email` / `@Pattern` / `@Past` / `@Future`
- 在 Record 上使用约束注解
- 级联校验：`@Valid`

### 6. 自定义校验注解
- 定义 `@ValidPhone` 注解
- 实现 `ConstraintValidator`
- 复用已有注解做组合约束

### 7. 嵌套结构校验
- 对象嵌套对象的递归校验
- 容器内元素的批量校验
- `@Valid` 在集合上的使用

### 8. Optional 与可空字段校验
- Optional 字段的语义校验
- null 字段的检查策略
- `@Nullable` + 业务层 null 检查

### 9. ★ Sealed 类型穷尽性校验
- 配合 switch 模式匹配的编译期穷尽检查
- 编译期保证所有分支被处理

### 10. 校验失败处理
- 异常体系：`IllegalArgumentException` / `NullPointerException` / `IllegalStateException`
- 自定义业务异常：`ValidationException`
- 错误聚合：使用 `Validator` 收集所有错误（`Set<ConstraintViolation<T>>`）
- 错误信息格式：字段路径 + 错误消息

### 11. JSON 反序列化校验
- Jackson + Bean Validation 集成
- `@JsonProperty` + `@NotNull` 联合校验
- 反序列化前的 Schema 校验

### 12. 单元测试中的断言
- JUnit 5 断言：`assertEquals` / `assertThrows` / `assertAll`
- AssertJ 流式断言
- 校验测试用例设计（边界值、null、空集合等）

### 13. 完整实战示例
- 使用 `data_types.java` 中的 `User` / `Order` / `Pet` / `Article` 模型
- 演示从原始数据 → 校验 → 业务对象转换的全流程
- 展示错误聚合报告

### 14. Java 校验机制总结
- 编译期：静态类型 + sealed 穷尽检查 + Checker Framework
- 运行期：Bean Validation + instanceof 模式匹配 + assert
- 测试期：JUnit + AssertJ

---

## 三、关键版本与特性速查

| 特性 | 版本 | 说明 |
|---|---|---|
| 泛型（Generics） | Java 5 | 类型擦除 |
| 枚举（enum） | Java 5 | 类级别类型 |
| 注解（Annotation） | Java 5 | 类型元数据 |
| 自动装箱 / 拆箱 | Java 5 | 基础 ↔ 包装 |
| `for-each` | Java 5 | 集合遍历 |
| `try-with-resources` | Java 7 | 资源自动关闭 |
| 菱形 `<>` | Java 7 | 类型推断 |
| Lambda | Java 8 | 函数式编程 |
| `Optional` | Java 8 | 空值容器 |
| Stream API | Java 8 | 流式处理 |
| `default` 方法 | Java 8 | 接口默认实现 |
| Type Annotation | Java 8 | `@NonNull String` |
| 接口 `private` 方法 | Java 9 | 私有辅助方法 |
| 不可变集合工厂 | Java 9 | `List.of` / `Map.of` |
| `var` 局部变量 | Java 10 | 类型推断 |
| Text Blocks | Java 13/15 | `"""..."""` |
| Switch 表达式 | Java 14 | 箭头语法 + `yield` |
| Record | Java 14/16 | 不可变数据载体 |
| `sealed` | Java 15/17 | 封闭类 / 接口 |
| `instanceof` 模式匹配 | Java 16 | `if (obj instanceof T t)` |
| Pattern Matching for switch | Java 21 | switch 模式匹配 |
| Record Pattern | Java 21 | `case Point(int x, int y)` |
| 虚拟线程 | Java 21 | 并发新特性（与类型无关） |

---

## 四、文件预计行数

- `data_types.java`：约 1200–1500 行
- `data_validation.java`：约 800–1100 行
- `outline.md`：本文件