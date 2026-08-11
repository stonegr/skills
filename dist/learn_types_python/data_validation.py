"""
data_validation.py — Python 数据类型运行时校验完整指南
========================================================

适用版本：Python 3.10 ~ 3.14
学习目标：
    1. 掌握「渐进式类型」在运行时的三种落地方式
    2. 学会用 Pydantic v2 做完整的运行时校验
    3. 理解静态检查 vs 运行时校验的分工

依赖：
    pip install pydantic>=2.0

运行方式：
    python data_validation.py
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import (
    Annotated,
    Any,
    Final,
    Literal,
    TypeGuard,
    TypeVar,
    cast,
    runtime_checkable,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)

# 关联上一份文件的实战模型
try:
    from data_types import (
        Address,
        Article,
        Order,
        OrderItem,
        Pet,
        PetKind,
        User,
    )
except ImportError:
    # 允许独立运行
    Address = Article = Order = OrderItem = Pet = PetKind = User = None  # type: ignore

T = TypeVar("T")


print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
# ============================================================================
# § 1. 校验全景 —— 静态 vs 运行时
# ============================================================================
"""
Python 类型的校验分三层：

┌────────────────────────────────────────────────────────────┐
│  静态层（IDE / CI 阶段）                                     │
│  工具：mypy / pyright / ruff                                │
│  时机：编码时 / pre-commit / CI                              │
│  能力：检查类型注解是否匹配                                  │
│  限制：运行时拿到的 dict / JSON 它管不了                      │
└────────────────────────────────────────────────────────────┘
                          ↓ 不够
┌────────────────────────────────────────────────────────────┐
│  原生运行时（手写）                                          │
│  工具：isinstance / assert / match-case                     │
│  优点：零依赖、灵活                                          │
│  缺点：复杂模型写起来啰嗦                                     │
└────────────────────────────────────────────────────────────┘
                          ↓ 业务复杂
┌────────────────────────────────────────────────────────────┐
│  第三方运行时校验库                                          │
│  工具：Pydantic v2（主流）/ attrs+cattrs / beartype / typeguard│
│  优点：声明式、自动嵌套校验、错误聚合                          │
│  缺点：多一层依赖                                            │
└────────────────────────────────────────────────────────────┘

推荐策略：
  - 函数签名 / 类内部：靠 mypy / pyright 做静态检查
  - 边界（API 入参、配置文件、数据库读取、消息队列）：
      必加 Pydantic / 手写校验
"""


# ============================================================================
# § 2. 原生运行时校验
# ============================================================================

# 2.1 isinstance / issubclass —— 最基础
def parse_age(raw: object) -> int:
    if not isinstance(raw, int):
        raise TypeError(f"expected int, got {type(raw).__name__}")
    if raw < 0:
        raise ValueError(f"age must be >= 0, got {raw}")
    return raw

# 2.2 assert —— 适合「内部不变量」，不适合「用户输入」
def divide(a: int, b: int) -> float:
    assert b != 0, "divisor cannot be zero"
    return a / b

# 2.3 ★ match-case 模式匹配（PEP 634，3.10+）—— 形状校验神器
def describe_shape(shape: object) -> str:
    match shape:
        case {"type": "circle", "radius": float(r)} if r > 0:
            return f"circle with radius {r}"
        case {"type": "rectangle", "width": w, "height": h}:
            return f"rectangle {w}x{h}"
        case {"type": "point", "x": x, "y": y}:
            return f"point at ({x}, {y})"
        case {"type": str(t)}:
            return f"unknown shape type: {t}"
        case _:
            return "not a recognized shape"

print("\n--- § 2. match-case 校验 ---")
print(describe_shape({"type": "circle", "radius": 5.0}))      # circle with radius 5.0
print(describe_shape({"type": "rectangle", "width": 3, "height": 4}))  # rectangle 3x4
print(describe_shape({"type": "triangle"}))                   # unknown shape type: triangle
print(describe_shape("hello"))                                # not a recognized shape

# 2.4 TypeGuard 自定义类型收窄
def is_str_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in value)

def join_or_default(items: list[object], default: str) -> str:
    if is_str_list(items):
        return ",".join(items)        # 此分支 items: list[str]
    return default


# ============================================================================
# § 3. Pydantic v2 —— 主流运行时校验
# ============================================================================
"""
★ Pydantic v2 是 Python 生态中事实标准的数据校验库：
  - 性能：Rust 写的核心（比 v1 快 5-50 倍）
  - 错误聚合：一次报所有错误
  - 自动类型转换：能从 str 解析 int / datetime / UUID
  - 嵌套校验：自动递归
  - 生态：FastAPI / SQLModel / LangChain 都用它
"""

# 3.1 BaseModel 基础
class UserSchema(BaseModel):
    """User 的运行时校验层"""
    model_config = ConfigDict(
        str_strip_whitespace=True,   # 自动 strip 字符串首尾空白
        extra="forbid",              # 禁止未声明字段
        validate_assignment=True,    # 赋值时也校验
    )

    id: int = Field(ge=1, description="用户 ID，必须 >= 1")
    name: str = Field(min_length=1, max_length=50)
    email: str = Field(pattern=r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
    age: int | None = Field(default=None, ge=0, le=150)
    address: "AddressSchema | None" = None
    pets: list["PetSchema"] = Field(default_factory=list)
    roles: frozenset[Literal["admin", "editor", "viewer"]] = Field(default_factory=frozenset)
    created_at: datetime = Field(default_factory=datetime.now)

# 3.2 嵌套模型
class AddressSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    street: str
    city: str
    country: str = "China"
    postal_code: str | None = Field(default=None, pattern=r"^\d{6}$")

class PetSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=30)
    kind: Literal["dog", "cat", "bird", "fish"]
    age_years: int = Field(default=0, ge=0, le=50)
    tags: list[str] = Field(default_factory=list)

# 解决嵌套前向引用
UserSchema.model_rebuild()


# 3.3 自定义校验器 —— @field_validator
class SignupSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str
    password: str
    password_confirm: str

    @field_validator("username")
    @classmethod
    def username_must_be_alnum(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("username must be alphanumeric")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 chars")
        if not any(c.isupper() for c in v):
            raise ValueError("password must contain uppercase")
        return v

# 3.4 跨字段校验 —— @model_validator
class DateRangeSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: date
    end: date

    @model_validator(mode="after")
    def end_after_start(self) -> "DateRangeSchema":
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self


# ============================================================================
# § 4. 其他运行时校验方案
# ============================================================================

# 4.1 TypeAdapter —— 对「非 BaseModel 类型」做校验
#    例如：list[int]、dict[str, Any]、Union[A, B] 都行
IntListAdapter = TypeAdapter(list[int])
result = IntListAdapter.validate_python(["1", "2", "3"])  # 自动转成 [1, 2, 3]
print(f"\n--- § 4. TypeAdapter list[int] ---")
print(f"validated: {result} (types: {[type(x).__name__ for x in result]})")

# 4.2 校验 JSON 字符串
JsonDictAdapter = TypeAdapter(dict[str, int | str])
parsed = JsonDictAdapter.validate_json('{"name": "Alice", "age": "30"}')
print(f"parsed JSON: {parsed}")

# 4.3 dataclass 也能用 Pydantic 校验
# pydantic.dataclass 在 3.12+ 才加进 pydantic 主模块
try:
    from pydantic import dataclass as pydantic_dataclass

    @pydantic_dataclass(config=ConfigDict(extra="forbid"))
    class PointDC:
        x: float
        y: float

    # PointDC(x=1.0, y=2.0)  # OK
    # PointDC(x="bad", y=2.0)  # 报错
except ImportError:
    # 3.10 / 3.11 / pydantic<2.7 没有 pydantic.dataclass，跳过演示
    PointDC = None
    pydantic_dataclass = None


# ============================================================================
# § 5. 嵌套结构校验
# ============================================================================

class CartItemSchema(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: PositiveInt
    unit_price: Annotated[float, Field(ge=0)]

class CartSchema(BaseModel):
    user_id: int
    items: list[CartItemSchema] = Field(default_factory=list)
    coupon: str | None = None

# Pydantic 自动递归校验嵌套结构
raw_cart = {
    "user_id": 1,
    "items": [
        {"product_id": "P-100", "quantity": 2, "unit_price": 99.0},
        {"product_id": "P-200", "quantity": 1, "unit_price": 199.0},
    ],
}
cart = CartSchema.model_validate(raw_cart)
print(f"\n--- § 5. 嵌套校验 ---")
print(f"cart.items count: {len(cart.items)}, all valid")

# 嵌套校验失败时 —— 错误信息的 loc 会指明路径
bad_cart = {
    "user_id": 1,
    "items": [
        {"product_id": "P-100", "quantity": -1, "unit_price": 99.0},  # quantity<0
        {"product_id": "", "quantity": 2, "unit_price": -5},          # 两个错
    ],
}
try:
    CartSchema.model_validate(bad_cart)
except ValidationError as e:
    print(f"\n--- 嵌套校验失败（错误聚合）---")
    for err in e.errors():
        print(f"  loc={err['loc']}, msg={err['msg']}, type={err['type']}")


# ============================================================================
# § 6. 可选字段校验
# ============================================================================

class OptionalFieldsSchema(BaseModel):
    """演示 Optional 字段的三种写法"""
    # 写法 1：default=None
    nickname: str | None = None

    # 写法 2：default=具体值
    theme: str = "light"

    # 写法 3：Optional + 约束
    age: int | None = Field(default=None, ge=0, le=150)

# 缺字段 / 显式 None / 提供值 —— 都正确处理
for raw in [{}, {"nickname": "abc"}, {"age": None}, {"age": 200}]:
    try:
        OptionalFieldsSchema.model_validate(raw)
        print(f"OK: {raw}")
    except ValidationError as e:
        print(f"FAIL: {raw} → {e.errors()[0]['msg']}")


# ============================================================================
# § 7. 联合类型校验
# ============================================================================

# 7.1 普通 Union —— Pydantic 按「声明顺序」尝试
# 注意：left-to-right mode 会选第一个匹配的，可能不是「最精确」的
class CatSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["cat"]
    name: str
    indoor: bool = True

class DogSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["dog"]
    name: str
    breed: str

PetUnion = Annotated[
    CatSchema | DogSchema,
    Field(discriminator="type"),  # 7.2 判别联合（discriminated union）
]

class OwnerWithPetsSchema(BaseModel):
    owner_name: str
    pets: list[PetUnion]

# 7.3 验证判别联合
raw_pets = [
    {"type": "cat", "name": "咪咪", "indoor": True},
    {"type": "dog", "name": "旺财", "breed": "柴犬"},
]
owner_data = OwnerWithPetsSchema.model_validate({"owner_name": "Alice", "pets": raw_pets})
print(f"\n--- § 7. 判别联合 ---")
for pet in owner_data.pets:
    print(f"  {pet.type}: {pet.name}")  # type: Literal 收窄自动生效


# ============================================================================
# § 8. 校验失败处理
# ============================================================================

# 8.1 基础：捕获 ValidationError
def parse_user(raw: dict[str, Any]) -> UserSchema:
    try:
        return UserSchema.model_validate(raw)
    except ValidationError as e:
        # e.errors() 返回结构化错误列表
        print(f"Validation failed with {e.error_count()} errors:")
        for err in e.errors():
            print(f"  - {err['loc']}: {err['msg']}")
        raise

# 8.2 自定义异常包装
class DomainValidationError(ValueError):
    """业务层校验错误：把 Pydantic 错误包装成业务异常"""
    def __init__(self, errors: list[dict[str, Any]]) -> None:
        self.errors = errors
        msgs = [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in errors]
        super().__init__("; ".join(msgs))

def safe_parse_user(raw: dict[str, Any]) -> UserSchema:
    try:
        return UserSchema.model_validate(raw)
    except ValidationError as e:
        raise DomainValidationError(e.errors()) from e

# 8.3 错误聚合：Pydantic 默认一次报所有错误（不像 JavaScript validator 第一个错就停）
bad_user = {
    "id": -1,                           # id < 1
    "name": "",                         # 空字符串
    "email": "not-an-email",            # 格式错
    "age": 200,                         # 超界
}
try:
    safe_parse_user(bad_user)
except DomainValidationError as e:
    print(f"\n--- § 8. 错误聚合 ---")
    print(f"Got {len(e.errors)} errors:")
    print(e)


# ============================================================================
# § 9. 与 data_types.py 联动
# ============================================================================
"""
data_types.py 里定义的是「dataclass 实体模型」
data_validation.py 里定义的是「Pydantic 校验层」
两个并存：dataclass 用于业务层（轻量），Schema 用于边界（重校验）
"""

# 9.1 定义校验层 —— 与 data_types.py 的 Order 对应
class OrderItemSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: str = Field(min_length=1)
    quantity: PositiveInt
    unit_price: Annotated[float, Field(ge=0)]

class OrderSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(pattern=r"^ORD-\d{6}$")
    customer: UserSchema
    items: list[OrderItemSchema] = Field(min_length=1)
    status: Literal["pending", "paid", "shipped", "delivered", "cancelled"] = "pending"
    shipping_address: AddressSchema | None = None
    notes: str | None = None
    placed_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def check_items_total(self) -> "OrderSchema":
        if not self.items:
            raise ValueError("order must have at least one item")
        return self

# 9.2 解析 JSON 字符串 → Order
api_response = """
{
    "order_id": "ORD-000001",
    "customer": {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
        "address": {
            "street": "长安街 1 号",
            "city": "北京",
            "postal_code": "100000"
        }
    },
    "items": [
        {"product_id": "P-100", "quantity": 2, "unit_price": 99.0},
        {"product_id": "P-200", "quantity": 1, "unit_price": 199.0}
    ],
    "shipping_address": {
        "street": "长安街 1 号",
        "city": "北京",
        "postal_code": "100000"
    }
}
"""
order = OrderSchema.model_validate_json(api_response)
print(f"\n--- § 9. 解析 JSON 订单 ---")
print(f"order_id: {order.order_id}")
print(f"customer: {order.customer.name} ({order.customer.email})")
print(f"items count: {len(order.items)}")

# 9.3 Schema → dataclass 实例（业务层使用）
def order_to_domain(schema: OrderSchema) -> Order:
    """把 Pydantic 校验后的数据转成 dataclass 业务对象"""
    if Order is None:
        raise RuntimeError("data_types module not loaded")
    user_schema = schema.customer
    user = User(
        id=user_schema.id,
        name=user_schema.name,
        email=user_schema.email,
        age=user_schema.age,
        address=Address(
            street=user_schema.address.street,
            city=user_schema.address.city,
            postal_code=user_schema.address.postal_code,
        ) if user_schema.address else None,
    )
    return Order(
        order_id=schema.order_id,
        customer=user,
        items=[
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in schema.items
        ],
        shipping_address=Address(
            street=schema.shipping_address.street,
            city=schema.shipping_address.city,
            postal_code=schema.shipping_address.postal_code,
        ) if schema.shipping_address else None,
        status=schema.status,
    )

if Order is not None:
    domain_order = order_to_domain(order)
    print(domain_order.summary())


# 9.4 TypeAdapter 直接校验 list[Order]
OrderListAdapter = TypeAdapter(list[OrderSchema])
orders_raw = json.loads(f"[{api_response}]")  # 用上面的订单再包一层列表
orders = OrderListAdapter.validate_python(orders_raw)
print(f"\n--- § 9. TypeAdapter 校验 list[Order] ---")
print(f"validated {len(orders)} order(s)")


# ============================================================================
# § 10. ★ Python 独有校验机制汇总
# ============================================================================
"""
[1] match-case（PEP 634）—— 不引入第三方库也能做形状校验
[2] @runtime_checkable Protocol —— isinstance 检查结构化接口
[3] TypeGuard / TypeIs —— 类型守卫函数
[4] TypedDict —— 静态强、运行时弱（仅作为 IDE 提示）
[5] dataclass.astuple / asdict —— 实例与 dict/tuple 互转
[6] @dataclass_transform —— 标记自定义类有 dataclass 行为
[7] Annotated —— 给类型加元数据，让校验库读取
"""


# ============================================================================
# § 11. 实战校验示例 —— 综合演示
# ============================================================================

print("\n========== § 11. 实战校验综合演示 ==========")

# 11.1 解析真实 API 响应
sample_api_response = json.dumps({
    "order_id": "ORD-000002",
    "customer": {
        "id": 42,
        "name": "Bob",
        "email": "bob@example.com",
        "age": 25,
    },
    "items": [
        {"product_id": "P-300", "quantity": 3, "unit_price": 49.9},
    ],
    "status": "pending",
})

parsed_order = OrderSchema.model_validate_json(sample_api_response)
print(f"[A] 成功解析: {parsed_order.order_id} - {parsed_order.customer.name}")

# 11.2 故意构造非法数据，看错误聚合
bad_response = json.dumps({
    "order_id": "INVALID",          # 格式错
    "customer": {
        "id": 0,                     # id >= 1
        "name": "",                  # 空 name
        "email": "no-at-sign",       # 邮箱错
        "age": 999,                  # 超界
    },
    "items": [],                     # min_length=1 违反
})
try:
    OrderSchema.model_validate_json(bad_response)
except ValidationError as e:
    print(f"\n[B] 错误聚合（一次性发现 {e.error_count()} 个错误）:")
    for err in e.errors():
        loc = ".".join(str(p) for p in err["loc"])
        print(f"  - {loc}: {err['msg']}")

# 11.3 用 match-case 做「Union[Pet, Article]」形状校验
def parse_pet_or_article(raw: dict[str, Any]) -> str:
    match raw:
        case {"kind": str(kind), "name": str(name)}:
            return f"Pet: {name} ({kind})"
        case {"title": str(title), "status": str(status)}:
            return f"Article: '{title}' [{status}]"
        case _:
            return "Unknown shape"

print(f"\n[C] match-case 校验:")
print(f"  {parse_pet_or_article({'kind': 'dog', 'name': '旺财'})}")
print(f"  {parse_pet_or_article({'title': 'Python 入门', 'status': 'draft'})}")
print(f"  {parse_pet_or_article({'foo': 'bar'})}")

# 11.4 用 TypeAdapter 校验纯容器类型
MixedAdapter = TypeAdapter(dict[str, list[int] | str])
print(f"\n[D] TypeAdapter 校验 dict[str, list[int] | str]:")
print(f"  {MixedAdapter.validate_python({'a': [1, 2, 3], 'b': 'hello'})}")

# 11.5 自定义校验器示例
print(f"\n[E] Signup 自定义校验:")
try:
    SignupSchema.model_validate({
        "username": "Alice123",
        "password": "weak",
        "password_confirm": "weak",
    })
except ValidationError as e:
    print(f"  自定义错误: {e.errors()}")

# 11.6 完整链路：JSON → Schema → dataclass → 业务逻辑
print(f"\n[F] 完整链路:")
raw_json = json.dumps({
    "order_id": "ORD-000003",
    "customer": {
        "id": 100,
        "name": "Carol",
        "email": "carol@example.com",
    },
    "items": [
        {"product_id": "P-A", "quantity": 1, "unit_price": 100.0},
        {"product_id": "P-B", "quantity": 2, "unit_price": 50.0},
    ],
})
schema = OrderSchema.model_validate_json(raw_json)
if Order is not None:
    domain = order_to_domain(schema)
    print(domain.summary())

print("\n========== 全部演示完成 ==========")