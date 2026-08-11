/**
 * data_validation.ts — TypeScript 数据类型运行时校验完整指南
 * ===========================================================
 *
 * 适用版本：TypeScript 4.9 ~ 7.0
 * 学习目标：
 *   1. 掌握「编译期类型检查 + 运行时校验」的两层策略
 *   2. 学会用 Zod 做 schema 校验
 *   3. 学会 z.infer 把 schema 转成类型（schema 是单一真相源）
 *
 * 依赖：
 *   npm install zod
 *
 * 运行方式：
 *   npx tsc --strict data_validation.ts
 *   npx tsx data_validation.ts
 */

import { z } from "zod";

// ============================================================================
// § 1. 校验全景 —— 编译期 vs 运行期
// ============================================================================
//
// TypeScript 类型的校验分两层：
//
// ┌────────────────────────────────────────────────────────────┐
// │  编译期（tsc / IDE）                                         │
// │  工具：tsc --strict / VS Code                                │
// │  时机：每次保存/编译                                          │
// │  能力：检查类型注解、interface 兼容性、泛型约束                │
// │  限制：拿不到 JSON / API / localStorage 里的「动态数据」        │
// └────────────────────────────────────────────────────────────┘
//                          ↓ 不够
// ┌────────────────────────────────────────────────────────────┐
// │  运行期（Zod / Yup / Joi）                                   │
// │  Zod（★ 当前主流推荐）                                        │
// │  特点：                                                       │
// │    - 声明式：链式 API 描述 schema                              │
// │    - TS 优先：z.infer 拿类型，单一真相源                       │
// │    - 错误聚合：一次报所有错误                                  │
// │    - 零依赖：纯 TS，无外部依赖                                 │
// │                                                              │
// │  其他：Yup（老牌，schema 先行）、io-ts（FP 风格）、            │
// │       Valibot（轻量）、ArkType（性能最佳）                    │
// └────────────────────────────────────────────────────────────┘
//
// 推荐策略：
//   - 函数签名 / 业务内部：靠 tsc 编译期检查
//   - 边界（API 入参、localStorage、URL query、消息队列）：
//     必加 Zod schema 校验

// ============================================================================
// § 2. 编译期类型检查
// ============================================================================
//
// 演示：故意写错代码，看 tsc 报错（运行前先 npx tsc --noEmit 试一下）
function demoCompileTime(): void {
  // 2.1 类型不匹配
  // const x: number = "hello"  // ❌ TS2322

  // 2.2 属性缺失
  interface User { name: string; age: number; }
  // const u: User = { name: "Alice" }  // ❌ TS2741

  // 2.3 可空处理
  // const y: string = null  // ❌ TS2322 (strictNullChecks)

  console.log("  编译期检查通过（看 IDE 红线 / tsc 报错）");
}

// ============================================================================
// § 3. JSON.parse 的隐式校验（最轻量）
// ============================================================================
//
// JSON.parse(text) 返回 any
// 必须先校验再使用，否则等于放弃类型安全
function demoJSONParse(): void {
  console.log("\n--- § 3. JSON.parse 隐式校验 ---");

  // 3.1 解析为 unknown
  const raw: unknown = JSON.parse('{"name": "Alice", "age": 30}');

  // 3.2 必须做形状检查（手写）
  if (
    typeof raw === "object" && raw !== null &&
    "name" in raw && "age" in raw &&
    typeof (raw as any).name === "string" &&
    typeof (raw as any).age === "number"
  ) {
    const user = raw as { name: string; age: number };
    console.log(`  手写校验通过: ${user.name}, ${user.age}`);
  }

  // 3.3 问题：手写啰嗦、易错、不能复用 —— 用 Zod
  console.log("  （手写太啰嗦，下面用 Zod 解决）");
}

// ============================================================================
// § 4. ★ Zod（主流推荐）
// ============================================================================

// 4.1 基础 schema
const AddressSchema = z.object({
  street: z.string().min(1),
  city: z.string().min(1),
  country: z.string().default("China"),
  postalCode: z.string().regex(/^\d{6}$/).optional(),
});

const PetSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1).max(30),
  kind: z.enum(["dog", "cat", "bird", "fish"]),
  ageYears: z.number().int().min(0).max(50).default(0),
  tags: z.array(z.string()).default([]),
});

const UserSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(1).max(50),
  email: z.string().email(),
  age: z.number().int().min(0).max(150).optional(),
  address: AddressSchema.optional(),
  pets: z.array(PetSchema).default([]),
  roles: z.array(z.enum(["admin", "editor", "viewer"])).default([]),
  createdAt: z.string().datetime().or(z.date()),
});

// 4.2 ★ 类型推断 —— schema 是单一真相源
//
// 不需要单独写 interface！直接 z.infer 拿类型
type User = z.infer<typeof UserSchema>;
type Pet = z.infer<typeof PetSchema>;
type Address = z.infer<typeof AddressSchema>;

function demoBasicZod(): void {
  console.log("\n--- § 4. Zod 基础用法 ---");

  // 4.3 成功
  const goodData = {
    id: 1,
    name: "Alice",
    email: "alice@example.com",
    age: 30,
    address: { street: "长安街 1 号", city: "北京", postalCode: "100000" },
    pets: [{ id: 1, name: "旺财", kind: "dog", ageYears: 3, tags: ["friendly"] }],
    roles: ["admin"],
    createdAt: new Date().toISOString(),
  };

  const result = UserSchema.safeParse(goodData);
  if (result.success) {
    const user: User = result.data;
    console.log(`  成功: ${user.name}, age=${user.age}, pets=${user.pets.length}`);
  } else {
    console.log(`  失败: ${result.error.message}`);
  }

  // 4.4 失败 —— 错误聚合
  const badData = {
    id: -1,                       // 负数错
    name: "",                     // 空字符串错
    email: "bad-email",           // 邮箱格式错
    age: 200,                     // 超界错
    address: { street: "x", city: "y", postalCode: "abc" }, // 多个错
    pets: [{ id: -1, name: "", kind: "alien" }],           // 多个错
  };
  const bad = UserSchema.safeParse(badData);
  if (!bad.success) {
    console.log(`  错误聚合（${bad.error.issues.length} 个错误）:`);
    for (const err of bad.error.issues) {
      const path = err.path.join(".");
      console.log(`    - ${path}: ${err.message}`);
    }
  }
}

// ============================================================================
// § 5. z.infer 与类型联动
// ============================================================================
//
// 关键概念：schema 是单一真相源（single source of truth）
// 不再需要「interface + Zod schema」两套维护

// 5.1 直接用 z.infer 替代手写 interface
type Article = z.infer<typeof ArticleSchema>;
type Order = z.infer<typeof OrderSchema>;
type OrderItem = z.infer<typeof OrderItemSchema>;

const ArticleSchema = z.object({
  id: z.number().int().positive(),
  title: z.string().min(1).max(200),
  authorId: z.number().int().positive(),
  content: z.string(),
  status: z.enum(["draft", "review", "published", "archived"]).default("draft"),
  publishedAt: z.string().datetime().optional(),
  tags: z.array(z.string()).default([]),
});

const OrderItemSchema = z.object({
  productId: z.string().min(1),
  quantity: z.number().int().positive(),
  unitPrice: z.number().nonnegative(),
});

const OrderSchema = z.object({
  orderId: z.string().regex(/^ORD-\d{6}$/),
  customer: UserSchema,
  items: z.array(OrderItemSchema).min(1),
  status: z.enum(["pending", "paid", "shipped", "delivered", "cancelled"]).default("pending"),
  shippingAddress: AddressSchema.optional(),
  notes: z.string().optional(),
  placedAt: z.string().datetime().or(z.date()),
});

// 5.2 派生类型
type OrderInput = z.input<typeof OrderSchema>;      // 校验前的「输入类型」（字段都可空）
type OrderOutput = z.output<typeof OrderSchema>;    // 校验后的「输出类型」（应用默认值）

// ============================================================================
// § 6. 嵌套结构校验
// ============================================================================

function demoNested(): void {
  console.log("\n--- § 6. 嵌套结构校验 ---");

  const cartSchema = z.object({
    userId: z.number().int().positive(),
    items: z.array(z.object({
      productId: z.string(),
      quantity: z.number().int().positive(),
      unitPrice: z.number().nonnegative(),
    })).min(1),
    coupon: z.string().optional(),
  });

  const goodCart = {
    userId: 1,
    items: [
      { productId: "P-100", quantity: 2, unitPrice: 99.0 },
      { productId: "P-200", quantity: 1, unitPrice: 199.0 },
    ],
  };
  const good = cartSchema.safeParse(goodCart);
  console.log(`  嵌套校验通过: items=${good.success ? (good.data as any).items.length : 0}`);

  // 嵌套失败 —— 错误信息会指明路径
  const badCart = {
    userId: 1,
    items: [
      { productId: "P-100", quantity: -1, unitPrice: 99.0 },  // quantity<0
      { productId: "", quantity: 2, unitPrice: -5 },          // 两个错
    ],
  };
  const bad = cartSchema.safeParse(badCart);
  if (!bad.success) {
    console.log(`  嵌套校验失败（${bad.error.issues.length} 个错误）:`);
    for (const err of bad.error.issues) {
      console.log(`    - ${err.path.join(".")}: ${err.message}`);
    }
  }
}

// ============================================================================
// § 7. 可选与可空字段
// ============================================================================

function demoOptional(): void {
  console.log("\n--- § 7. 可选与可空字段 ---");

  // 7.1 .optional() —— 字段可以缺失
  // 7.2 .nullable() —— 字段可以是 null
  // 7.3 .default(value) —— 字段缺失时使用默认值

  const schema = z.object({
    name: z.string().min(1),
    nickname: z.string().optional(),               // 可缺失
    description: z.string().nullable().default(""), // 可空，默认为空字符串
    age: z.number().int().min(0).optional(),       // 可缺失
  });

  for (const raw of [
    { name: "A" },
    { name: "B", nickname: "Bee" },
    { name: "C", description: null },
    { name: "D", age: 30 },
  ]) {
    const r = schema.safeParse(raw);
    console.log(`  ${JSON.stringify(raw)} → ${r.success ? "OK" : "FAIL"}`);
  }
}

// ============================================================================
// § 8. 联合类型校验
// ============================================================================

// 8.1 普通 z.union —— 按顺序尝试，可能不精确
const PetUnionSchema = z.union([
  z.object({ kind: z.literal("cat"), name: z.string(), indoor: z.boolean() }),
  z.object({ kind: z.literal("dog"), name: z.string(), breed: z.string() }),
]);

// 8.2 ★ z.discriminatedUnion —— 按 type 字段精确分发（更快更准）
const PetDiscriminatedSchema = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("cat"), name: z.string(), indoor: z.boolean() }),
  z.object({ kind: z.literal("dog"), name: z.string(), breed: z.string() }),
]);

function demoUnion(): void {
  console.log("\n--- § 8. 联合类型校验（判别联合）---");

  for (const raw of [
    { kind: "cat", name: "咪咪", indoor: true },
    { kind: "dog", name: "旺财", breed: "柴犬" },
    { kind: "bird", name: "小鸟" }, // 非法
    { kind: "cat", name: "" },     // 缺 indoor + name 为空
  ]) {
    const r = PetDiscriminatedSchema.safeParse(raw);
    if (r.success) {
      // TS 知道 r.data.kind 是 "cat" | "dog"
      if (r.data.kind === "cat") {
        console.log(`  cat 校验通过: ${r.data.name}, indoor=${r.data.indoor}`);
      } else {
        console.log(`  dog 校验通过: ${r.data.name}, breed=${r.data.breed}`);
      }
    } else {
      console.log(`  ${raw.kind} 失败: ${r.error.issues[0]?.message}`);
    }
  }
}

// ============================================================================
// § 9. 校验失败处理
// ============================================================================

function demoErrorHandling(): void {
  console.log("\n--- § 9. 校验失败处理 ---");

  const schema = z.object({
    email: z.string().email("请输入有效的邮箱"),
    age: z.number().int().min(0, "年龄不能为负").max(150, "年龄不能超过 150"),
  });

  // 9.1 safeParse 风格（不抛异常）
  const result = schema.safeParse({ email: "bad", age: 200 });
  if (!result.success) {
    console.log("  safeParse 错误（不抛异常）:");
    for (const err of result.error.issues) {
      console.log(`    - ${err.path.join(".")}: ${err.message} (code: ${err.code})`);
    }
  }

  // 9.2 .format() —— 嵌套错误对象
  const formatted = result.success ? null : result.error.format();
  console.log("  格式化错误:", JSON.stringify(formatted, null, 2).split("\n")[0]);

  // 9.3 .flatten() —— 扁平错误对象
  const flat = result.success ? null : result.error.flatten();
  console.log("  扁平错误:", JSON.stringify(flat));
}

// ============================================================================
// § 10. 与 data_types.ts 联动
// ============================================================================
//
// 假设 data_types.ts 定义了：
//   class User { id; name; email; age; address; pets; ... }
//   class Order { orderId; customer; items; ... }
//
// 这里演示：用 Zod 校验 → 转换为业务对象

function parseAndValidate(rawJSON: string): { success: true; order: Order } | { success: false; errors: string[] } {
  // 第一步：JSON parse
  let raw: unknown;
  try {
    raw = JSON.parse(rawJSON);
  } catch (e) {
    return { success: false, errors: [`JSON 解析失败: ${(e as Error).message}`] };
  }

  // 第二步：Zod 校验
  const result = OrderSchema.safeParse(raw);
  if (!result.success) {
    const errors = result.error.issues.map(
      (e) => `${e.path.join(".") || "(root)"}: ${e.message}`
    );
    return { success: false, errors };
  }

  return { success: true, order: result.data };
}

function demoIntegration(): void {
  console.log("\n--- § 10. 完整链路（JSON → Zod → 类型安全）---");

  // 10.1 正常 JSON
  const goodJSON = JSON.stringify({
    orderId: "ORD-000001",
    customer: {
      id: 1,
      name: "Alice",
      email: "alice@example.com",
      age: 30,
      address: { street: "长安街 1 号", city: "北京", postalCode: "100000" },
      createdAt: new Date().toISOString(),
    },
    items: [
      { productId: "P-100", quantity: 2, unitPrice: 99.0 },
      { productId: "P-200", quantity: 1, unitPrice: 199.0 },
    ],
    shippingAddress: { street: "长安街 1 号", city: "北京", postalCode: "100000" },
    placedAt: new Date().toISOString(),
  });

  const good = parseAndValidate(goodJSON);
  if (good.success) {
    const o = good.order;
    console.log(`  解析成功: ${o.orderId} for ${o.customer.name}`);
    const total = o.items.reduce((s, i) => s + i.quantity * i.unitPrice, 0);
    console.log(`  订单总额: ${total.toFixed(2)}`);
  }

  // 10.2 故意构造非法数据
  const badJSON = JSON.stringify({
    orderId: "INVALID",          // 格式错
    customer: {
      id: 0,                     // id 必填正整数
      name: "",                  // 空 name
      email: "not-an-email",     // 邮箱错
      age: 999,                  // 超界
    },
    items: [],                   // 至少 1 个
  });
  const bad = parseAndValidate(badJSON);
  if (!bad.success) {
    console.log(`  错误聚合（${bad.errors.length} 个错误）:`);
    for (const e of bad.errors) {
      console.log(`    - ${e}`);
    }
  }
}

// ============================================================================
// § 11. ★ TypeScript 独有校验机制
// ============================================================================
//
// [1] z.infer —— schema 即类型（单一真相源）
// [2] discriminatedUnion —— 比 union 更精确、更快
// [3] safeParse —— 不抛异常，符合 FP 风格
// [4] z.input / z.output —— 校验前/后类型不同（处理默认值）
// [5] .brand() —— 品牌类型（编译期防混淆 ID）
// [6] 判别联合 + type guard 收窄（编译期 + 运行时联动）

// 11.5 ★ z.brand() —— 编译期防混淆
//
// 把 string 标记为 UserId / OrderId，编译期防止「id 串错类型」
const UserIdSchema = z.string().uuid().brand<"UserId">();
const OrderIdSchema = z.string().regex(/^ORD-\d{6}$/).brand<"OrderId">();

type UserId = z.infer<typeof UserIdSchema>;   // string & { __brand: "UserId" }
type OrderId = z.infer<typeof OrderIdSchema>;

function demoBrand(): void {
  console.log("\n--- § 11.5 z.brand 品牌类型 ---");

  const uidResult = UserIdSchema.safeParse("550e8400-e29b-41d4-a716-446655440000");
  if (uidResult.success) {
    const uid: UserId = uidResult.data;
    // console.log(uid.length) // OK：仍是 string
    console.log(`  UserId 品牌校验通过: ${uid}`);

    // 编译期：uid 和普通 string 不能混用
    // const otherId: UserId = "any-string"  // ❌ 编译错误
  }
}

// ============================================================================
// § 12. 实战校验示例
// ============================================================================

// 12.1 API 响应包装
const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.discriminatedUnion("status", [
    z.object({ status: z.literal("success"), data: dataSchema }),
    z.object({
      status: z.literal("error"),
      error: z.object({ code: z.number().int(), message: z.string() }),
    }),
  ]);

const UserApiResponseSchema = ApiResponseSchema(UserSchema);

function demoApiResponse(): void {
  console.log("\n--- § 12. API 响应校验 ---");

  // 成功响应
  const successResp = {
    status: "success" as const,
    data: { id: 1, name: "Alice", email: "alice@example.com", createdAt: new Date().toISOString() },
  };
  const s = UserApiResponseSchema.safeParse(successResp);
  if (s.success) {
    // 编译期：s.data.status 是 "success" | "error"
    if (s.data.status === "success") {
      console.log(`  success: ${s.data.data.name}`);
    }
  }

  // 错误响应
  const errorResp = {
    status: "error" as const,
    error: { code: 1001, message: "User not found" },
  };
  const e = UserApiResponseSchema.safeParse(errorResp);
  if (e.success && e.data.status === "error") {
    console.log(`  error: [${e.data.error.code}] ${e.data.error.message}`);
  }
}

// 12.2 localStorage 读取
const StorageUserSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string().email(),
});

function loadUserFromStorage(key: string): User | null {
  // 模拟 localStorage（值为 JSON 字符串）
  const raw = (globalThis as any)[key] ?? null;
  if (!raw) return null;

  // localStorage 拿到的总是字符串，需要 JSON.parse
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return null;
  }

  const result = StorageUserSchema.safeParse(parsed);
  return result.success ? (result.data as User) : null;
}

function demoStorage(): void {
  console.log("\n--- § 12.2 localStorage 边界校验 ---");

  // 设置模拟数据
  (globalThis as any).userA = JSON.stringify({ id: 1, name: "Alice", email: "alice@example.com" });
  (globalThis as any).userB = JSON.stringify({ id: 2, name: "Bob", email: "bad-email" });

  const a = loadUserFromStorage("userA");
  const b = loadUserFromStorage("userB");
  console.log(`  userA: ${a ? a.name : "null"}`);
  console.log(`  userB: ${b ? b.name : "null (校验失败)"}`);
}

// 12.3 URL query 参数校验
const SearchQuerySchema = z.object({
  q: z.string().min(1).optional(),
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  sort: z.enum(["asc", "desc"]).default("desc"),
});

function demoQuery(): void {
  console.log("\n--- § 12.3 URL query 边界校验 ---");

  const query = "?page=2&limit=10&sort=asc";
  const params = Object.fromEntries(new URLSearchParams(query));
  const r = SearchQuerySchema.safeParse(params);
  if (r.success) {
    console.log(`  q=${r.data.q}, page=${r.data.page}, limit=${r.data.limit}, sort=${r.data.sort}`);
  } else {
    console.log("  query 校验失败");
  }
}

// ============================================================================
// 演示入口
// ============================================================================

export function demo(): void {
  console.log("=== TypeScript 数据校验演示 ===\n");

  demoCompileTime();
  demoJSONParse();
  demoBasicZod();
  demoNested();
  demoOptional();
  demoUnion();
  demoErrorHandling();
  demoIntegration();
  demoBrand();
  demoApiResponse();
  demoStorage();
  demoQuery();

  console.log("\n=== 演示完成 ===");
}

// 如果直接执行此文件
declare const require: { main?: unknown };
declare const module: { exports: unknown };
if (typeof require !== "undefined" && require.main === module) {
  demo();
}
