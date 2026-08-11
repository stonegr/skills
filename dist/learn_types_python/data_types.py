"""
data_types.py — Python 数据类型定义完整指南
================================================

适用版本：Python 3.10 ~ 3.14（推荐 3.12+ 以使用 PEP 695 新泛型语法）
学习目标：
    1. 掌握 Python 渐进式类型系统的全部能力
    2. 看懂 typing 标准库的常见用法
    3. 学会用 dataclass + TypedDict + Protocol 描述真实业务模型
    4. 配合 data_validation.py 做运行时校验

运行方式：
    pip install mypy ruff  # 可选，仅静态检查时需要
    python data_types.py   # 直接运行也能看到 demo 输出
"""

from __future__ import annotations

# 标准库
import enum
import re
import sys
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
)
from dataclasses import dataclass, field, fields
from datetime import date, datetime
from typing import (
    Annotated,
    Any,
    ClassVar,
    Concatenate,
    Final,
    Literal,
    NewType,
    NoReturn,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
    TypedDict,  # PEP 589 (3.8+)
    cast,
    final,
    get_type_hints,
    overload,
    runtime_checkable,
)
from typing import Generic  # 单独导入（PEP 695 之前需要显式继承）

# TypeAliasType 是 3.12+ 加的（PEP 695），3.10 不可用
try:
    from typing import TypeAliasType  # Python 3.12+
except ImportError:
    TypeAliasType = None  # type: ignore[misc,assignment]

# Self 是 3.11+ 加的（PEP 673），3.10 用 typing_extensions
try:
    from typing import Self  # Python 3.11+
except ImportError:
    from typing_extensions import Self  # type: ignore[no-redef]

# 3.10+ 才有的 PEP 655 TypedDict 字段标记
try:
    from typing import NotRequired, Required  # Python 3.11+
except ImportError:  # 兜底：3.10 及以下用 typing_extensions
    from typing_extensions import NotRequired, Required  # type: ignore[no-redef]

# 3.13+ 才有 typing.TypeIs，3.10 ~ 3.12 用 typing_extensions
try:
    from typing import TypeIs
except ImportError:
    from typing_extensions import TypeIs  # type: ignore[no-redef]

# 3.12+ 才有 typing.override（PEP 698）
try:
    from typing import override
except ImportError:
    from typing_extensions import override  # type: ignore[no-redef]

print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
# ============================================================================
# § 1. 类型系统全景
# ============================================================================
"""
Python 的类型系统有三大特点（区别于 Java/Go/Rust 等静态语言）：

1. 渐进式类型（Gradual Typing）
   - 可以一部分代码加类型注解，另一部分保持动态
   - 运行时**完全不检查**类型注解（PEP 484 明确说明）
   - 由第三方工具（mypy / pyright / ruff / pyre）做静态检查

2. 结构化子类型（Structural Subtyping）
   - 默认「鸭子类型」语义：一个类不需要显式继承某个基类，
     只要它有相应方法就被视为该类型的子类型
   - Protocol 把这种语义静态化（PEP 544）

3. 元组异构、其它容器同构
   - tuple[int, str, float] —— 三个位置类型可以不同
   - list[T] / set[T] / dict[K, V] —— 元素类型一致

注解默认不影响运行：
    def add(a: int, b: int) -> int:
        return a + b

    add("hello", "world")  # 运行时正常返回 "helloworld"，mypy 会报错
"""


# ============================================================================
# § 2. 基础类型
# ============================================================================

# 2.1 内建基础类型
name: str = "Alice"           # 字符串
age: int = 30                 # 整数
height: float = 1.68          # 浮点
is_active: bool = True        # 布尔
data: bytes = b"\x00\x01\x02" # 字节串
nothing: None = None          # None 是 NoneType 的唯一实例

# 2.2 字面量类型（PEP 586，3.8+）
# Literal 把类型收窄到「特定值」，常用于 enum 替代品
Direction = Literal["north", "south", "east", "west"]

def move(direction: Direction) -> str:
    return f"Moving {direction}"

# 2.3 LiteralString（PEP 675，3.11+）
# 比 str 更严格：只接受「字面量拼接出来的字符串」
# 用途：阻止 SQL 注入 / shell 注入 等敏感场景
def run_query(sql: LiteralString) -> None:
    print(f"Executing: {sql}")

run_query("SELECT * FROM users")                      # OK
table: LiteralString = "users"
run_query(f"SELECT * FROM {table}")                   # OK（LiteralString 拼接）
# run_query(input())                                 # 静态层报错：input() 是 str


# ============================================================================
# § 3. 容器类型
# ============================================================================

# 3.1 容器字面量 —— 3.9+ 起可以直接在内建类型上加 []，不用 List/Dict
nums: list[int] = [1, 2, 3]
name_to_age: dict[str, int] = {"alice": 30, "bob": 25}
unique_tags: set[str] = {"python", "typing"}
frozen: frozenset[int] = frozenset({1, 2, 3})

# 3.2 tuple —— Python 唯一允许「异构位置类型」的容器
# tuple[T1, T2, T3] —— 固定长度、位置类型不同
point_3d: tuple[float, float, float] = (1.0, 2.0, 3.0,)
record: tuple[int, str, bool] = (1, "alice", True)

# tuple[T, ...] —— 任意长度，元素同类型
nums_tuple: tuple[int, ...] = (1, 2, 3, 4)

# tuple[()] —— 空元组
empty: tuple[()] = ()

# 3.3 collections.abc 中的「抽象容器」 —— 在函数签名里推荐用它们
#   Iterable[T]    可迭代
#   Iterator[T]    迭代器（有 __next__）
#   Sequence[T]    有序、可索引、可切片
#   Mapping[K, V]  只读映射
#   MutableMapping[K, V]  可写映射
def first_item(items: Sequence[int]) -> int:
    return items[0]

def total_length(strings: Iterable[str]) -> int:
    return sum(len(s) for s in strings)


# ============================================================================
# § 4. 联合类型与可选类型
# ============================================================================

# 4.1 Union —— PEP 604 (3.10+) 起 `X | Y` 是推荐写法
#       `int | str` 与 `Union[int, str]` 完全等价
IntOrStr: TypeAlias = int | str

def parse(value: str) -> int | float:
    """返回 int 或 float（取决于是否能解析为整数）"""
    try:
        return int(value)
    except ValueError:
        return float(value)

# 4.2 Optional —— 历史上 `Optional[T]` = `T | None`；现在推荐 `T | None`
def find_user(user_id: int) -> dict[str, Any] | None:
    """找不到用户时返回 None，而不是抛异常"""
    return {"id": user_id, "name": "Alice"} if user_id > 0 else None

# 4.3 字面量联合 —— 模拟 enum 但更轻量
Status = Literal["draft", "published", "archived"]
Priority = Literal["low", "medium", "high"]

# 4.4 Never / NoReturn（底部类型）—— 表示「永远不会发生」
# PEP 673 (3.11+) 加了 Never；之前用 NoReturn
def fail(msg: str) -> NoReturn:
    raise RuntimeError(msg)


# ============================================================================
# § 5. 枚举（Enum）
# ============================================================================

# 5.1 标准 Enum —— Pythonic 的常量集合
class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

# 5.2 IntEnum / StrEnum —— 自动混入 int / str 的子类
class PriorityEnum(enum.IntEnum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10

# ★ 5.3 StrEnum（3.11+）—— 与 str 行为完全一致，适合做 Literal 替代品
# 3.10 兼容写法：继承 (str, enum.Enum)
class HttpStatus(str, enum.Enum):
    OK = "200"
    NOT_FOUND = "404"
    SERVER_ERROR = "500"

# Python 3.11+ 推荐写法（注释展示）：
#     class HttpStatus(enum.StrEnum):
#         OK = "200"
#         ...

def respond(status: HttpStatus, body: str) -> dict[str, str]:
    return {"status": status, "body": body}

# 5.4 字面量扩展（PEP 586 + enum 协同）
# 当你使用 Enum 时，类型检查器自动把所有成员当作 Literal 看待
# 例如：c: Color 实际等价于 c: Literal[Color.RED, Color.GREEN, Color.BLUE]


# ============================================================================
# § 6. 数据类与结构类型
# ============================================================================

# 6.1 @dataclass 基础（PEP 557，3.7+）
@dataclass
class Point:
    x: float
    y: float

# 6.2 frozen + slots —— 不可变 + 节省内存（3.10+ slots 参数）
@dataclass(frozen=True, slots=True)
class FrozenPoint:
    x: float
    y: float

    def distance_to(self, other: FrozenPoint) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

# 6.3 默认值与 field() —— 容器默认值必须用 field(default_factory=...)
@dataclass
class Cart:
    user_id: int
    items: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

# 6.4 kw_only=True（3.10+）—— 强制所有字段只能通过关键字传参
@dataclass(kw_only=True)
class UserPreferences:
    theme: str = "light"
    language: str = "zh-CN"

# 6.5 ★ TypedDict（PEP 589，3.8+）—— 描述「dict 的形状」
class UserDict(TypedDict):  # type: ignore[misc]  # 故意演示
    """一个 User 的 dict 形状（不是类！是类型）"""
    id: int
    name: str
    email: str

# 用法
user_dict: UserDict = {"id": 1, "name": "Alice", "email": "a@b.com"}

# 6.6 TypedDict + Required/NotRequired（PEP 655，3.11+）
class PartialUserDict(TypedDict, total=False):
    """total=False —— 所有字段默认非必填"""
    id: int             # NotRequired[int]
    name: str           # NotRequired[str]
    email: Required[str]  # 但 email 强制必填

# 用法
partial: PartialUserDict = {"email": "a@b.com"}  # OK

# 6.7 NamedTuple —— 同时拥有「tuple 不可变性」+「字段访问」
from typing import NamedTuple

class Point3D(NamedTuple):
    x: float
    y: float
    z: float

    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5


# ============================================================================
# § 7. 协议（Protocol）—— 结构化子类型（PEP 544）
# ============================================================================

"""
★ Python 独有特色：Protocol

Protocol 让类型检查器按「形状」判断子类型关系，
而不是按「继承关系」（后者叫 nominal subtyping）。

类不需要显式继承 Protocol，就能满足它的形状要求 —— 这就是「鸭子类型」
的静态版。
"""

@runtime_checkable  # 允许运行时用 isinstance(x, SupportsClose) 检查
class SupportsClose(Protocol):
    def close(self) -> None: ...

class File:
    """没有继承 SupportsClose，但形状一致 → 类型检查器视为 SupportsClose 子类"""
    def close(self) -> None:
        print("File closed")

def close_resource(r: SupportsClose) -> None:
    r.close()

close_resource(File())  # OK：File 有 close 方法

# 7.2 Protocol 含属性
class HasName(Protocol):
    name: str

class Person:
    def __init__(self, name: str) -> None:
        self.name = name

# Person 自动满足 HasName（无需继承）


# ============================================================================
# § 8. 泛型
# ============================================================================

# 8.1 通用写法（兼容 3.10+）—— TypeVar + Generic[T]
T = TypeVar("T")
U = TypeVar("U")

class Box(Generic[T]):
    """泛型容器：与类型参数 T 绑定"""
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

# 泛型函数
def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None

class LegacyStack(Generic[T]):
    """演示：3.12 之前必须显式继承 Generic[T]"""
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# 8.1.bis 3.12+ 新语法（PEP 695）—— 仅作语法展示注释，运行时由版本决定
"""
Python 3.12+ 推荐写法（PEP 695 —— 本文件运行在 3.10，所以用注释展示）：

    class Box[T]:                       # 不再需要继承 Generic
        def __init__(self, value: T) -> None: ...
        def get(self) -> T: ...

    def first[T](items: Sequence[T]) -> T | None: ...
    type JsonDict[T] = dict[str, T]     # 泛型 type alias 也支持
"""

# 8.3 泛型约束 —— TypeVar('T', bound=Number)
from decimal import Decimal

Number = TypeVar("Number", int, float, Decimal)
def double(n: Number) -> Number:
    return n * 2

# 8.4 协变 / 逆变 / 不变
#   covariant=True    只读容器（如 Sequence）
#   contravariant=True 只写容器（如 Consumer）
#   默认 invariant     可读写容器（如 list）
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)

class ImmutableList(Generic[T_co]):  # type: ignore[misc]
    def __init__(self, items: Sequence[T_co]) -> None:
        self._items: tuple[T_co, ...] = tuple(items)

    def __iter__(self) -> Iterator[T_co]:
        return iter(self._items)

# 8.5 ★ ParamSpec（PEP 612，3.10+）—— 装饰器利器
#   用于保留被装饰函数的参数签名
P = ParamSpec("P")
R = TypeVar("R")

def with_logging(f: Callable[P, R]) -> Callable[P, R]:
    """装饰器：保留被装饰函数的所有参数类型"""
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {f.__name__}")
        result = f(*args, **kwargs)
        print(f"Done")
        return result
    return wrapper

@with_logging
def greet(name: str, age: int, *, verbose: bool = False) -> str:
    return f"Hello {name}, age {age}"

# greet("Alice", 30, verbose=True)  # mypy 知道 verbose 必须是关键字参数

# 3.12+ PEP 695 等价写法（注释展示，本文件运行在 3.10）：
#     def with_logging[**P, R](f: Callable[P, R]) -> Callable[P, R]: ...

# 8.6 ★ TypeVarTuple（PEP 646，3.11+）—— 可变元组（注释展示，3.10 不支持）
"""
Python 3.11+ 写法：

    from typing import TypeVarTuple, Unpack
    Ts = TypeVarTuple('Ts')

    def concat_strings(*args: Unpack[Ts]) -> tuple[Unpack[Ts], int]:
        return (*args, len(args))
"""


# ============================================================================
# § 9. 类型别名
# ============================================================================

# 9.1 通用写法 —— TypeAlias
UserIdAlias: TypeAlias = int
EmailAlias: TypeAlias = str
JsonDict: TypeAlias = dict[str, Any]

# 9.2 3.12+ 推荐写法（PEP 695）—— 注释展示
"""
Python 3.12+ 推荐写法（PEP 695）：

    type UserId = int           # 不再需要 TypeAlias 标注
    type Email = str
    type JsonDict = dict[str, Any]

    # 泛型别名也支持
    type ApiResponse[T] = dict[str, T]
"""

# 9.3 NewType —— 创建「语义上独立」的新类型
#   比 type alias 更严格：UserId 和 int 不能混用（静态层）
UserIdNew = NewType("UserIdNew", int)
EmailNew = NewType("EmailNew", str)

def send_email(to: EmailNew, subject: str, body: str) -> None:
    print(f"Send to {to}: {subject}")

uid = UserIdNew(12345)
# send_email(uid, "Hi", "Hello")  # 静态层报错：int 不是 EmailNew
send_email(EmailNew("a@b.com"), "Hi", "Hello")  # OK


# ============================================================================
# § 10. Callable 与函数签名
# ============================================================================

# 10.1 Callable[[Arg1, Arg2], ReturnType]
Handler: TypeAlias = Callable[[str, int], bool]

def register(handler: Handler) -> None:
    ...

# 10.2 Callable[..., ReturnType] —— 任意参数
AnyCallable: TypeAlias = Callable[..., Any]

# 10.3 @overload（PEP 484）—— 同一函数多种签名
@overload
def json_loads(s: str) -> Any: ...
@overload
def json_loads(s: bytes) -> Any: ...
def json_loads(s: str | bytes) -> Any:
    """运行时不区分，统一处理"""
    import json
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    return json.loads(s)

# 10.4 Protocol + __call__ 表达复杂签名
class Combiner(Protocol):
    def __call__(self, *vals: bytes, maxlen: int | None = None) -> list[bytes]: ...


# ============================================================================
# § 11. 类型守卫（TypeGuard / TypeIs）
# ============================================================================

"""
★ Python 独有特色：TypeGuard / TypeIs

类型守卫让自定义函数能「告诉类型检查器」返回 bool 后，
参数被收窄到某个类型。
"""

def is_str_list(value: list[object]) -> TypeGuard[list[str]]:
    """如果返回 True，value 被收窄为 list[str]"""
    return all(isinstance(x, str) for x in value)

def process(value: list[object]) -> None:
    if is_str_list(value):
        # 此分支 value: list[str]
        print(",".join(value))
    else:
        print("not all strings")

# 11.2 ★ TypeIs（PEP 742，3.12 提案 / 3.13 落地）—— 比 TypeGuard 更严格
# 区别：TypeIs 表示「返回 True 时是 T，返回 False 时不是 T」
#      TypeGuard 只保证「返回 True 时是 T」，返回 False 时类型不变
def is_int(x: int | str) -> TypeIs[int]:
    return isinstance(x, int)

def handle(x: int | str) -> None:
    if is_int(x):
        x += 1   # OK：x 是 int
    else:
        x.upper()  # OK：x 是 str（TypeIs 比 TypeGuard 更精确）


# ============================================================================
# § 12. 高级与装饰器
# ============================================================================

# 12.1 Final（PEP 591，3.8+）—— 标记常量/不可重写
MAX_RETRIES: Final = 3
API_VERSION: Final[str] = "v2.3"

# 12.2 @final（PEP 591）—— 标记类不可继承 / 方法不可重写
@final
class ImmutableConfig:
    pass

# 12.3 ClassVar（PEP 526）—— 类变量
@dataclass
class AppState:
    instance_count: ClassVar[int] = 0   # 所有实例共享
    name: str                          # 每个实例独立

    def __post_init__(self) -> None:
        AppState.instance_count += 1

# 12.4 Annotated（PEP 593，3.9+）—— 给类型附加元数据
#   运行时通过 typing.get_type_hints(obj, include_extras=True) 获取
PositiveInt = Annotated[int, "must be > 0"]
EmailAnnotated = Annotated[str, "must match email regex"]

# 12.5 ★ @override（PEP 698，3.12+）—— 强制方法覆写父类
class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    @override
    def speak(self) -> str:  # mypy 确认是覆写父类
        return "Woof"

# 12.6 @dataclass_transform（PEP 681，3.12+）
#   让自定义装饰器（如 SQLAlchemy 的 Mapped）也能享受 dataclass 特性
try:
    from typing import dataclass_transform  # Python 3.12+
except ImportError:
    from typing_extensions import dataclass_transform  # type: ignore[no-redef]

@dataclass_transform()
def my_model(cls: type) -> type:
    cls.__annotations__ = getattr(cls, "__annotations__", {})
    return cls


# ============================================================================
# § 13. 类型转换
# ============================================================================

# 13.1 cast() —— 强制类型断言（仅静态层，不影响运行）
value: Any = "hello"
length: int = cast(int, len(value))  # mypy 相信 length 是 int

# 13.2 isinstance / issubclass
def describe(x: object) -> str:
    if isinstance(x, int):
        return f"int: {x}"
    if isinstance(x, str):
        return f"str: {x!r}"
    return f"other: {type(x).__name__}"

# 13.3 type[Class] —— 类对象本身（而不是实例）
def create(cls: type[Point]) -> Point:
    return cls(0.0, 0.0)

create(Point)  # OK

# 13.4 get_type_hints —— 运行时获取带完整注解的对象
def demo() -> int: ...
print(get_type_hints(demo))  # {'return': <class 'int'>}


# ============================================================================
# § 14. 类型推断
# ============================================================================

"""
Python 类型推断的几个事实：

1. 局部变量：按第一次赋值推导
   x = 10          # x: int
   x = "hello"     # x: str（重新推导）

2. 函数返回值：按所有 return 语句的类型联合推导
   def f(b):       # return: bool
       if b:
           return True
       return False

3. 容器元素：靠「上下文」推断（赋值给 list[int] 时 [] 内必须是 int）

4. reveal_type(x) —— mypy 内省工具，告诉你推断出的类型
"""

x = [1, 2, 3]
# reveal_type(x)   # mypy: Revealed type is "list[int]"


# ============================================================================
# § 15. ★ Python 独有特色汇总
# ============================================================================
"""
[1] 渐进式类型 —— 静态注解不影响运行时，可选性
[2] Protocol 结构化子类型 —— 鸭子类型的静态化
[3] TypedDict —— 描述 JSON/dict 形状的专用工具
[4] Self —— 子类方法返回 self 时保留子类类型
[5] dataclass 一行值对象 —— 不写 __init__/__repr__/__eq__
[6] match-case（PEP 634，3.10+）—— 模式匹配，详见 data_validation.py
[7] @runtime_checkable —— 让 Protocol 也能用于 isinstance
[8] TypeGuard / TypeIs —— 自定义类型收窄
[9] PEP 695（3.12）极简泛型语法：class C[T]: / type X = ...
[10] ParamSpec / Concatenate —— 装饰器类型签名保留
"""


# ============================================================================
# § 16. 完整实战模型（User / Address / Pet / Article / Order）
# ============================================================================
"""
真实业务场景下的「类型系统综合应用」：
- dataclass 描述实体
- Optional 描述可空字段
- Literal 描述状态枚举
- TypedDict 描述 API 响应
- Protocol 描述业务接口
- Self 描述工厂方法
- Annotated 给字段加约束提示
"""

# ----- 16.1 Address：嵌套 dataclass -----
@dataclass(frozen=True, slots=True, kw_only=True)
class Address:
    street: str
    city: str
    country: str = "China"
    postal_code: str | None = None

    @override  # 类型层声明：重写 object.__str__
    def __str__(self) -> str:
        return f"{self.city}, {self.country}"

# ----- 16.2 PetKind：StrEnum（3.11+）做 Literal 替代 -----
# 3.10 兼容：继承 (str, enum.Enum)
class PetKind(str, enum.Enum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    FISH = "fish"

# Python 3.11+ 写法（注释展示）：
#     class PetKind(enum.StrEnum):
#         DOG = "dog"
#         ...

# ----- 16.3 Pet：含枚举 + Optional + 自定义校验 -----
@dataclass(slots=True)
class Pet:
    name: str
    kind: PetKind
    age_years: int = 0
    tags: list[str] = field(default_factory=list)
    owner: "User | None" = None  # 前向引用（用字符串）

    def __post_init__(self) -> None:
        if self.age_years < 0:
            raise ValueError(f"Pet age cannot be negative: {self.age_years}")
        if not self.name.strip():
            raise ValueError("Pet name cannot be empty")

# ----- 16.4 User：Self 工厂方法 + 派生属性 -----
@dataclass
class User:
    id: UserIdNew         # NewType：让 id 不能误传给 email
    name: str
    email: EmailNew
    age: int | None = None
    address: Address | None = None
    pets: list[Pet] = field(default_factory=list)
    roles: frozenset[Literal["admin", "editor", "viewer"]] = field(
        default_factory=frozenset
    )
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_adult(self) -> bool:
        return self.age is not None and self.age >= 18

    @classmethod
    def guest(cls) -> Self:
        """工厂方法：用 Self 让子类调用时返回子类实例"""
        return cls(id=UserIdNew(0), name="Guest", email=EmailNew("guest@local"))

    def add_pet(self, pet: Pet) -> Self:
        pet.owner = self
        self.pets.append(pet)
        return self

# ----- 16.5 Article：状态枚举 + 可选字段 -----
ArticleStatus = Literal["draft", "review", "published", "archived"]

@dataclass
class Article:
    title: str
    author: User
    status: ArticleStatus = "draft"
    content: str = ""
    published_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def publish(self) -> None:
        if self.status == "published":
            raise ValueError("Already published")
        self.status = "published"
        self.published_at = datetime.now()

# ----- 16.6 Order：泛型 + 复杂嵌套 -----
@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price

OrderStatus = Literal["pending", "paid", "shipped", "delivered", "cancelled"]

@dataclass
class Order:
    order_id: str
    customer: User
    items: list[OrderItem]
    status: OrderStatus = "pending"
    shipping_address: Address | None = None
    notes: str | None = None
    placed_at: datetime = field(default_factory=datetime.now)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    def summary(self) -> str:
        lines = [f"Order {self.order_id} ({self.status})"]
        for item in self.items:
            lines.append(f"  - {item.product_id} x {item.quantity} = {item.subtotal:.2f}")
        lines.append(f"Total: {self.total:.2f}")
        return "\n".join(lines)


# ----- 16.7 Protocol 定义业务接口 -----
class DiscountPolicy(Protocol):
    """折扣策略接口 —— 任何实现 apply_discount 的类都满足"""
    def apply_discount(self, total: float) -> float: ...

class PercentageDiscount:
    def __init__(self, percent: float) -> None:
        self.percent = percent

    def apply_discount(self, total: float) -> float:
        return total * (1 - self.percent / 100)

class FlatDiscount:
    def __init__(self, amount: float) -> None:
        self.amount = amount

    def apply_discount(self, total: float) -> float:
        return max(0.0, total - self.amount)

def checkout(order: Order, policy: DiscountPolicy) -> float:
    """policy 形参：任何有 apply_discount 方法的对象都行"""
    return policy.apply_discount(order.total)


# ----- 16.8 TypedDict：API 响应结构 -----
class CreateUserRequest(TypedDict):
    """POST /users 的请求体形状"""
    name: str
    email: str
    age: NotRequired[int]  # 可选字段

class ApiResponse(TypedDict):
    """通用 API 响应"""
    code: int
    message: str
    data: NotRequired[Any]


# ----- 16.9 演示运行 -----
if __name__ == "__main__":
    addr = Address(street="长安街 1 号", city="北京", postal_code="100000")
    user = User(
        id=UserIdNew(1),
        name="Alice",
        email=EmailNew("alice@example.com"),
        age=30,
        address=addr,
    )

    dog = Pet(name="旺财", kind=PetKind.DOG, age_years=3)
    user.add_pet(dog)

    article = Article(title="Python 类型系统入门", author=user, status="draft")
    article.publish()

    order = Order(
        order_id="ORD-001",
        customer=user,
        items=[
            OrderItem(product_id="P-100", quantity=2, unit_price=99.0),
            OrderItem(product_id="P-200", quantity=1, unit_price=199.0),
        ],
        shipping_address=addr,
    )

    discount = PercentageDiscount(percent=10)
    final_total = checkout(order, discount)

    print(f"User: {user.name} ({user.email}), Adult: {user.is_adult}")
    print(f"Pet: {dog.name} ({dog.kind})")
    print(f"Article: '{article.title}' status={article.status}")
    print(f"Order total: {order.total:.2f}, after discount: {final_total:.2f}")