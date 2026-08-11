# Python 类型系统学习大纲

> 覆盖版本：Python 3.10 ~ 3.14（推荐 3.12+，享受 PEP 695 新语法）
> 文件基于「静态类型提示（PEP 484+）」+ `typing` 标准库
> 风格：详细 + 可运行 + 真实业务模型（User/Order/Pet/Article）

---

## 文件 1：`data_types.py` —— 数据类型定义

### 1. 类型系统概览
- Python 是**渐进式类型**（gradual typing）：可以选择性加注解
- 运行时**不强制**检查类型，靠第三方工具（mypy / pyright / ruff）做静态检查
- `typing` 标准库 + 3.12 起的新语法（`type X = ...` / `class C[T]:`）

### 2. 基础类型
- `int` / `float` / `bool` / `str` / `bytes`
- `None` 与 `NoneType`
- 字面量类型 `Literal`（PEP 586，3.8+）

### 3. 容器类型
- `list[T]`、`tuple[T1, T2, ...]` / `tuple[T, ...]`、`set[T]`、`frozenset[T]`
- `dict[K, V]` 与 `collections.abc` 中的 `Mapping` / `Sequence` / `Iterable`
- 3.9+ 支持内建类型直接参数化 `list[int]`；之前用 `List[int]`

### 4. 联合类型与可选类型
- `Union[A, B]` 或 PEP 604 的 `A | B`（3.10+）
- `Optional[T]` = `T | None`
- 字面量联合 `Literal["draft", "published"]`
- `Never` / `NoReturn`（底部类型）

### 5. 枚举
- `Enum` / `IntEnum` / `StrEnum`（3.11+）
- `auto()` 自动赋值
- 字面量扩展：`enum.Enum` 自动产生 `Literal` 类型（type checker 友好）

### 6. 数据类与结构类型
- `@dataclass`（3.7+）与 `@dataclass(frozen=True, slots=True)`
- `dataclass(slots=True)`（3.10+）
- `dataclass(kw_only=True)`（3.10+）
- `TypedDict`（PEP 589，3.8+）与 `Required`/`NotRequired`（PEP 655，3.11+）
- `NamedTuple`
- ★ `Self` 类型（PEP 673，3.11+）—— 返回当前实例的精确类型

### 7. 协议（Protocol）—— 结构化子类型
- ★ `Protocol`（PEP 544，3.8+）—— Python 的「鸭子类型静态版」
- `@runtime_checkable` —— 让 Protocol 也可在运行时用 `isinstance` 检查
- 协议成员：方法 / 属性 / 描述符

### 8. 泛型
- 3.12 新语法：`class Box[T]:`、`def first[T](x: list[T]) -> T:`
- 3.12 之前的写法：`TypeVar` + `Generic[T]`
- 泛型约束：`TypeVar('T', bound=SupportsInt)`
- 协变 / 逆变 / 不变（`covariant=True` / `contravariant=True`）
- `ParamSpec`（PEP 612）—— 参数规格变量，装饰器利器
- `TypeVarTuple`（PEP 646，3.11+）—— 可变参数元组

### 9. 类型别名
- `type X = ...`（PEP 695，3.12+）
- 旧写法 `X: TypeAlias = ...`（PEP 613，3.10+）
- `NewType('UserId', int)`（PEP 484）—— 创建语义上的新类型（int 的子类）
- `TypeAliasType`（3.12+）

### 10. Callable 与函数签名
- `Callable[[Arg1, Arg2], ReturnType]`
- `ParamSpec` + `Concatenate`（装饰器场景）
- `@overload`（PEP 484）—— 多签名重载

### 11. 类型守卫（TypeGuard / TypeIs）
- ★ `TypeGuard[T]`（PEP 647，3.10+）—— 自定义类型判断函数
- ★ `TypeIs[T]`（PEP 742，3.12+）—— 更严格的类型收窄

### 12. 高级与装饰器
- `Final`（PEP 591，3.8+）—— 常量
- `ClassVar`（PEP 526）—— 类变量
- `Annotated[T, metadata]`（PEP 593，3.9+）—— 给类型附加元数据
- `@override`（PEP 698，3.12+）—— 强制覆写父类方法
- `@runtime_checkable`
- `@deprecated`（PEP 702，3.13+）
- `@dataclass_transform`（PEP 681，3.12+）

### 13. 类型转换
- `cast(T, x)` —— 强制类型断言（仅静态层）
- `isinstance` / `issubclass`
- `type(x)` 与 `type[Class]`
- `typing.get_type_hints()`

### 14. 类型推断
- 局部变量由赋值推导
- 函数返回值按 `return` 语句推断
- `reveal_type(x)` —— mypy/pyright 内省工具

### 15. ★ Python 独有特色汇总
- 渐进式类型 + 运行时无检查
- `Protocol` 结构化子类型
- `TypedDict` 描述 dict 形状
- `Self` 自动推断子类
- 模式匹配 `match-case`（PEP 634，3.10+）
- `dataclass` 一行定义值对象
- 3.12 的极简泛型语法（PEP 695）

### 16. 完整实战模型
- 定义 `User`、`Address`、`Pet`、`Article`、`Order` 五个 dataclass
- 覆盖：基础字段、容器（list/dict/tuple）、Optional、Literal、嵌套 dataclass、`Self`、`Protocol`、泛型容器、`TypedDict`、`Annotated`
- 提供 `__post_init__` 校验、`@property` 派生字段、`__repr__`

---

## 文件 2：`data_validation.py` —— 数据类型校验

### 1. 校验全景
- 静态层：mypy / pyright / ruff（写在 `data_types.py` 后看 IDE 提示）
- 运行时层：手写 `isinstance` / `pydantic` v2 / `attrs` + `cattrs` / `beartype` / `typeguard`
- 选择策略：边界校验（API 入参 / 数据库读取 / 配置文件）

### 2. 原生运行时校验
- `isinstance` / `issubclass`
- `assert` 与 `AssertionError`
- `@runtime_checkable` Protocol 的 `isinstance` 检查
- `match-case` 模式匹配校验（PEP 634）

### 3. Pydantic v2（主流推荐）
- ★ `BaseModel` 基础用法
- `Field(...)` 约束（min_length / ge / le / pattern / max_length）
- `Optional[T]` 与默认 `None`
- `Literal` 字段校验（自动枚举）
- `Annotated[T, Field(...)]`（PEP 593 推荐写法）
- 嵌套模型 / `list[Item]` / `dict[str, Item]`
- 自定义校验器：`@field_validator`、`@model_validator(mode='after'/'before')`
- 配置：`model_config = ConfigDict(...)`
- 错误处理：`ValidationError`、`.errors()`、`.error_count()`
- `TypeAdapter`（对非模型类型做校验）
- `discriminated unions`（`Field(discriminator=...)`）

### 4. 其他运行时校验库
- `dataclasses` + `dataclasses-json`（JSON 互转）
- `attrs` + `cattrs`（结构体校验）
- `typeguard`（运行时装饰器检查函数参数）
- `beartype`（PEP 593 元数据驱动）
- `TypedDict` 的运行时检查限制

### 5. 嵌套结构校验
- Pydantic 嵌套模型自动递归
- `list[Pet]` 列表元素校验
- `dict[str, list[int]]` 复杂容器
- 自定义嵌套校验器

### 6. 可选字段校验
- `Optional[T]` = `T | None`
- Pydantic 中默认 `None` 与 `Field(default=None)`
- `Required` / `NotRequired`（TypedDict）

### 7. 联合类型校验
- `Union[A, B]` 在 Pydantic 中按声明顺序尝试（left-to-right mode）
- `discriminated unions`（`tag` 字段判别）
- `TypeAdapter(int | str).validate_python(...)`

### 8. 校验失败处理
- `try / except ValidationError` 结构
- 错误信息格式：`loc` / `msg` / `type` / `input`
- 自定义错误消息
- 错误聚合：Pydantic 默认一次性报所有错误
- 自定义异常类

### 9. 与 `data_types.py` 联动
- 把 `data_types.py` 里的 `User` / `Address` / `Pet` / `Article` / `Order` 都引入
- 用 Pydantic 写对应的 `*Schema` 校验层
- 演示：
  - 解析 JSON dict → User 实例
  - 校验失败时打印详细错误
  - `TypeAdapter` 直接校验 `list[Order]`
  - 把 dataclass 实例「转」到 schema（兼容性）

### 10. ★ Python 独有校验机制
- `match-case` 模式匹配做形状校验
- `@runtime_checkable` Protocol 的 `isinstance` 鸭子校验
- `TypeGuard` 自定义收窄函数
- `dataclasses.astuple` / `asdict` 做转换
- `TypedDict` 静态强、运行时弱（仅作为提示）

### 11. 实战校验示例
- 演示解析一段 JSON 字符串（模拟 API 响应）→ 校验 → 拿到 `User`
- 故意构造一段非法数据 → 演示错误聚合输出
- 用 `TypeAdapter` 直接校验 `list[Order]`
- 用 `match-case` 校验一个 `Union[Pet, Article]`

---

## 关键 PEP / 版本对照表

| PEP | 内容 | 版本 |
|-----|------|------|
| 484 | 类型提示基础 | 3.5 |
| 526 | 变量注解 | 3.6 |
| 544 | Protocol | 3.8 |
| 586 | Literal | 3.8 |
| 589 | TypedDict | 3.8 |
| 591 | Final | 3.8 |
| 604 | `X \| Y` 联合语法 | 3.10 |
| 612 | ParamSpec | 3.10 |
| 613 | TypeAlias | 3.10 |
| 634 | match-case | 3.10 |
| 646 | TypeVarTuple / Unpack | 3.11 |
| 655 | Required / NotRequired | 3.11 |
| 673 | Self | 3.11 |
| 675 | LiteralString | 3.11 |
| 681 | dataclass_transform | 3.12 |
| 695 | 新泛型语法 | 3.12 |
| 698 | @override | 3.12 |
| 702 | @deprecated | 3.13 |
| 742 | TypeIs | 3.13（落地） |

---

## 学习顺序建议

1. 先看 `data_types.py`：建立「Python 类型系统能表达什么」的认知
2. 再看 `data_validation.py`：学习「怎么在运行时落地校验」
3. 重点章节：泛型（§8）、Protocol（§7）、Pydantic v2（校验 §3）、match-case（校验 §2）