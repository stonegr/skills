/**
 * data_types.ts — TypeScript 数据类型定义完整指南
 * ==================================================
 *
 * 适用版本：TypeScript 4.9 ~ 7.0（推荐 5.4+ 享受 NoInfer / 类型谓词推断）
 * 学习目标：
 *   1. 掌握 TypeScript 静态类型系统的全部能力
 *   2. 看懂高级类型编程（条件 / 映射 / infer / 模板字面量 / satisfies）
 *   3. 学会用 interface + class + 泛型描述真实业务模型
 *   4. 配合 data_validation.ts 做运行时校验（Zod）
 *
 * 运行方式：
 *   npx tsc --strict data_types.ts        # 编译期检查
 *   npx tsx data_types.ts                  # 直接执行（需安装 tsx）
 *   node --loader tsx data_types.ts        # 或用 ts-node
 */

// ============================================================================
// § 1. 类型系统全景
// ============================================================================
//
// TypeScript 类型系统三大特点（区别于 Java / Go / Rust）：
//
// 1. 静态类型 + 编译期检查
//    - 所有类型不匹配在编译期就会报错
//    - 运行时**完全不检查**类型注解（编译后类型擦除，类型仅用于 IDE / tsc）
//
// 2. 结构化类型（Structural Typing）
//    - 不需要 nominal 兼容（不像 Java 要 implements）
//    - 只要形状匹配，就是兼容类型（duck typing 静态版）
//
// 3. 类型即文档
//    - 类型注解是「活的文档」，IDE 能直接看到
//    - 类型 + 接口 + 泛型构成完整的领域建模工具
//
// 配合 4.9+ satisfies、5.0+ const 泛型、模板字面量，整个类型系统已经非常强大。

// ============================================================================
// § 2. 基础类型
// ============================================================================

// 2.1 基础类型
const isActive: boolean = true;
const age: number = 30;
const name: string = "Alice";
const big: bigint = 100n;
const sym: symbol = Symbol("id");

// 2.2 null / undefined / void / never
const nothing: null = null;
const notSet: undefined = undefined;
function noReturn(): void {
  // 没有 return 语句
}
function fail(): never {
  throw new Error("never returns");
}

// 2.3 unknown —— 安全的 any（与 any 的关键区别）
//
// any:     可以赋给任何类型，也可以从任何类型赋过来（绕过类型检查）
// unknown: 可以接受任何类型赋值，但只能赋给 unknown / any（必须先收窄）
let value: unknown = "hello";
// value.toUpperCase()           // ❌ 编译错误：unknown 不能直接调用方法
if (typeof value === "string") {
  value.toUpperCase(); // ✅ 收窄后是 string
}

// 2.4 字面量类型 —— 把类型收窄到特定值
type Direction = "north" | "south" | "east" | "west";
type DiceRoll = 1 | 2 | 3 | 4 | 5 | 6;

function move(direction: Direction): string {
  return `Moving ${direction}`;
}

// ============================================================================
// § 3. 容器类型
// ============================================================================

// 3.1 数组 —— 两种写法等价
const nums1: number[] = [1, 2, 3];
const nums2: Array<number> = [1, 2, 3];

// 3.2 元组（tuple）—— 固定长度 + 位置类型
const point3d: [number, number, number] = [1.0, 2.0, 3.0];
const record: [number, string, boolean] = [1, "alice", true];

// 标签元组（4.0+）—— 给位置起名字，可读性更好
const labeledPoint: [x: number, y: number, z: number] = [1, 2, 3];

// 可变元组（4.0+）—— ...rest
type StringNumberPair = [string, number];
const pair: StringNumberPair = ["age", 30];
const pairWithExtra: [string, number, ...string[]] = ["id", 1, "tag1", "tag2"];

// 3.3 对象 / Record
const userObj: { name: string; age: number } = { name: "Alice", age: 30 };
const config: Record<string, number> = { timeout: 30, retries: 3 };

// 3.4 Map<K, V> / Set<T> / WeakMap / WeakSet
const map = new Map<string, number>();
map.set("alice", 30);
const set = new Set<number>([1, 2, 3]);

// ============================================================================
// § 4. 联合与交叉
// ============================================================================

// 4.1 联合类型（Union）—— A | B 表示「A 或 B」
type StringOrNumber = string | number;

function format(value: string | number): string {
  if (typeof value === "string") {
    return value.trim();
  }
  return value.toFixed(2);
}

// 4.2 交叉类型（Intersection）—— A & B 表示「A 且 B」
type Named = { name: string };
type Aged = { age: number };
type Person = Named & Aged; // { name: string; age: number }

// 4.3 ★ 判别联合（Discriminated Union）—— TS 类型编程的杀手锏
//
// 用一个共同字段（tag）让 TS 自动收窄
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rectangle"; width: number; height: number }
  | { kind: "point"; x: number; y: number };

function area(shape: Shape): number {
  // TS 自动收窄：每个 case 里的 shape 都是「对应的子类型」
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
    case "point":
      return 0;
  }
}

// ============================================================================
// § 5. 字面量类型与 as const
// ============================================================================

// 5.1 字面量联合
type Status = "draft" | "published" | "archived";
type Priority = "low" | "medium" | "high";

// 5.2 ★ as const —— 把对象/数组字面量「冻结」为 readonly 字面量
const configConst = {
  apiUrl: "https://api.example.com",
  timeout: 5000,
} as const;
// configConst.apiUrl = "other"   // ❌ 编译错误：readonly
// configConst.timeout = 3000     // ❌ 编译错误：readonly
// 推导出的类型是：
//   { readonly apiUrl: "https://api.example.com"; readonly timeout: 5000 }
// 而不是宽泛的 { apiUrl: string; timeout: number }

// 5.3 字面量扩展：union 中遇到字面量会被「扩宽」
// 实际效果：当 union 类型与字面量比较时，TS 自动只保留「该字面量的分支」

// ============================================================================
// § 6. 枚举（Enum）
// ============================================================================

// 6.1 数字枚举（默认从 0 开始）
enum DirectionEnum {
  Up, // 0
  Down, // 1
  Left, // 2
  Right, // 3
}

// 6.2 字符串枚举（推荐，更清晰）
enum HttpStatus {
  OK = "200",
  NotFound = "404",
  ServerError = "500",
}

function respond(status: HttpStatus, body: string) {
  return { status, body };
}

// 6.3 const enum（编译期擦除，无运行时对象）
const enum Color {
  Red = "#FF0000",
  Green = "#00FF00",
  Blue = "#0000FF",
}
const c: Color = Color.Red;

// 6.4 与字面量联合的对比
//
// 字面量联合（推荐）：
//   type Status = "draft" | "published"
//   优点：无运行时开销、Tree-shakable、inferred 类型更精确
//
// 枚举（必要时使用）：
//   enum Status { Draft = "draft" }
//   优点：可以在编译时反向映射（数字枚举）
//   缺点：有运行时对象、与 const enum 有兼容问题

// ============================================================================
// § 7. 接口与类型别名
// ============================================================================

// 7.1 interface —— 描述对象形状
interface UserIface {
  id: number;
  name: string;
  email: string;
  age?: number; // 可选
  readonly createdAt: Date; // 只读
}

// 7.2 type —— 更通用的类型定义
type UserType = {
  id: number;
  name: string;
  email: string;
};

// 7.3 差异对比
//
// interface：
//   ✓ 可以声明合并（同名 interface 自动合并）
//   ✓ 适合描述「对象/类」的形状
//   ✗ 不能描述联合、映射等高级类型
//
// type：
//   ✓ 可以描述任何类型（联合、交叉、条件、映射）
//   ✓ 适合描述「类型工具」
//   ✗ 不能声明合并

// 7.4 ★ 声明合并（Declaration Merging）—— interface 特有
//
// 同名的多个 interface 会自动合并
interface BoxShape {
  width: number;
}
interface BoxShape {
  height: number;
}
// 合并后：interface BoxShape { width: number; height: number }

// 7.5 接口继承
interface AdminUser extends UserIface {
  role: "admin";
  permissions: string[];
}

// ============================================================================
// § 8. 类（class）
// ============================================================================

// 8.1 基础类
class Animal {
  // 字段声明（默认 public）
  public name: string;
  private sound: string; // 私有（TS 层）
  protected age: number; // 派生类可访问

  constructor(name: string, sound: string, age: number) {
    this.name = name;
    this.sound = sound;
    this.age = age;
  }

  public speak(): string {
    return `${this.name} says ${this.sound}`;
  }
}

// 8.2 ★ private fields（#）—— 编译期硬私有
class BankAccount {
  #balance: number; // # 前缀 = 真正的硬私有（JS 引擎层）

  constructor(initial: number) {
    this.#balance = initial;
  }

  deposit(amount: number) {
    this.#balance += amount;
  }

  get balance(): number {
    return this.#balance;
  }
}

// 8.3 readonly 字段
class DocumentEntity {
  readonly id: number;
  name: string;
  email: string;

  constructor(id: number, name: string, email: string) {
    this.id = id;
    this.name = name;
    this.email = email;
  }
}

// 8.4 ★ 抽象类
abstract class ShapeAbs {
  abstract area(): number;
  abstract perimeter(): number;

  describe(): string {
    return `Area: ${this.area()}, Perimeter: ${this.perimeter()}`;
  }
}

class Circle extends ShapeAbs {
  constructor(public radius: number) {
    super();
  }
  area(): number {
    return Math.PI * this.radius ** 2;
  }
  perimeter(): number {
    return 2 * Math.PI * this.radius;
  }
}

// 8.5 ★ implements 接口
interface Printable {
  print(): void;
}
class Document implements Printable {
  constructor(public content: string) {}
  print(): void {
    console.log(this.content);
  }
}

// 8.6 静态字段 + 静态方法
class AppConfig {
  static readonly VERSION = "1.0.0";
  static instances = 0;

  constructor() {
    AppConfig.instances++;
  }
}

// ============================================================================
// § 9. 函数类型
// ============================================================================

// 9.1 函数声明 + 类型
function add(a: number, b: number): number {
  return a + b;
}

// 9.2 函数表达式
const multiply = (a: number, b: number): number => a * b;

// 9.3 可选参数 + 默认参数
function greet(name: string, greeting: string = "Hello"): string {
  return `${greeting}, ${name}`;
}
function createUser(name: string, age?: number): object {
  return { name, age: age ?? null };
}

// 9.4 剩余参数
function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}

// 9.5 函数类型
type Handler = (event: string) => void;
const clickHandler: Handler = (e) => console.log(`clicked: ${e}`);

// 9.6 函数重载（overload）
function processValue(input: string): string;
function processValue(input: number): number;
function processValue(input: string | number): string | number {
  if (typeof input === "string") {
    return input.trim();
  }
  return input * 2;
}
// processValue(true)  // ❌ 编译错误

// ============================================================================
// § 10. 泛型（Generics）
// ============================================================================

// 10.1 泛型函数
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}

// 10.2 泛型接口
interface Box<T> {
  value: T;
  getValue(): T;
}

const stringBox: Box<string> = { value: "hi", getValue() { return this.value; } };

// 10.3 泛型类
class Container<T> {
  constructor(public value: T) {}
  getValue(): T {
    return this.value;
  }
}

// 10.4 ★ 泛型约束（extends）
function getLength<T extends { length: number }>(item: T): number {
  return item.length;
}
// getLength(42)        // ❌ 数字没有 length
// getLength("hello")   // ✅ 字符串有 length
// getLength([1, 2, 3]) // ✅ 数组有 length

// 10.5 多泛型 + keyof 约束
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
const u = { name: "Alice", age: 30 };
const userName = getProperty(u, "name"); // string
// getProperty(u, "foo")  // ❌ foo 不在 u 的 key 中

// 10.6 泛型默认值（2.3+）
interface ApiResponse<T = unknown, E = Error> {
  data: T;
  error: E | null;
}
const resp: ApiResponse = { data: { foo: 1 }, error: null };
const resp2: ApiResponse<string, TypeError> = { data: "ok", error: null };

// 10.7 ★ const 泛型（5.0+）—— 字面量类型保留
//
// 普通泛型：参数类型会被「放宽」为 T
// const 泛型：参数类型保留为字面量
function regularFetch<T>(url: T): T { return url; }
const r1 = regularFetch("/api/users"); // r1: string（不是字面量）

function constFetch<const T>(url: T): T { return url; }
const r2 = constFetch("/api/users"); // r2: "/api/users"（字面量保留）

// ============================================================================
// § 11. 可选与空值
// ============================================================================

// 11.1 T | undefined / T | null
let maybeString: string | undefined = "hello";
maybeString = undefined; // OK

// 11.2 strictNullChecks 开启时，null/undefined 必须显式声明

// 11.3 ★ 可选链 ?.
const userData: { address?: { city?: string } } = {};
const city = userData.address?.city; // string | undefined

// 11.4 ★ 空值合并 ??
declare const process: { env: { PORT?: string } };
const port = process.env.PORT ?? "3000";

// 11.5 非空断言 x! —— 告诉 TS「相信我，这不会是 null」
function getFirst(arr: number[] | null): number {
  return arr![0]; // 强制非空（如果实际是 null 会运行时报错）
}

// ============================================================================
// § 12. 类型别名（type）
// ============================================================================

// 12.1 简单别名
type UserID = number;
type Email = string;

// 12.2 ★ 模板字面量类型（4.1+）—— 编译期字符串拼接
type EventName = `on${Capitalize<string>}`;
// type EventName = "onClick" | "onChange" | "onFocus" | ...

// 实际应用：API 路由
type ApiRoute = `/api/${string}`;
const route1: ApiRoute = "/api/users"; // ✅
// const route2: ApiRoute = "/users";    // ❌ 不匹配

// 12.3 ★ 工具类型
interface Todo {
  title: string;
  description: string;
  completed: boolean;
  createdAt: Date;
}

type TodoPartial = Partial<Todo>; // 所有字段可选
type TodoRequired = Required<Partial<Todo>>; // 所有字段必填
type TodoPreview = Pick<Todo, "title" | "completed">; // 选取字段
type TodoWithoutDesc = Omit<Todo, "description">; // 排除字段
type TodoRecord = Record<string, Todo>; // 索引签名
type ReadonlyTodo = Readonly<Todo>; // 所有字段 readonly

// 函数工具类型
type AddFn = (a: number, b: number) => number;
type AddReturn = ReturnType<AddFn>; // number
type AddParams = Parameters<AddFn>; // [a: number, b: number]

// 异步工具类型
type PromiseResolved = Awaited<Promise<string>>; // string

// 12.4 联合工具类型
type StatusEnum = "draft" | "published" | "archived";
type ActiveStatus = Exclude<StatusEnum, "draft" | "archived">; // "published"
type DraftOrPublished = Extract<StatusEnum, "draft" | "published">;

// 12.5 ★ 字符串工具类型（4.1+）
type Upper = Uppercase<"hello">; // "HELLO"
type Lower = Lowercase<"HELLO">; // "hello"
type Cap = Capitalize<"hello">; // "Hello"
type Uncap = Uncapitalize<"Hello">; // "hello"

// ============================================================================
// § 13. 类型断言与类型守卫
// ============================================================================

// 13.1 类型断言 as T
let someValue: unknown = "hello";
const strLength = (someValue as string).length;

// 13.2 ★ 自定义类型守卫（type predicate）
function isString(value: unknown): value is string {
  return typeof value === "string";
}

function processWithGuard(value: unknown): void {
  if (isString(value)) {
    console.log(value.toUpperCase()); // 收窄为 string
  }
}

// 13.3 ★ 断言函数（3.7+）—— 抛错而不是返回 boolean
function assertString(value: unknown): asserts value is string {
  if (typeof value !== "string") {
    throw new Error("Not a string");
  }
}

function useAssert(value: unknown): void {
  assertString(value);
  console.log(value.toUpperCase()); // 收窄为 string
}

// 13.4 in 操作符收窄（4.9+ 改进）
interface Cat { meow(): void; }
interface Dog { bark(): void; }
function petAction(pet: Cat | Dog) {
  if ("meow" in pet) {
    pet.meow();
  } else {
    pet.bark();
  }
}

// ============================================================================
// § 14. ★ 高级类型编程
// ============================================================================

// 14.1 ★ 条件类型 —— T extends U ? X : Y
//
// 类似于类型层的三元表达式
type IsString<T> = T extends string ? true : false;
type A = IsString<"hello">; // true
type B = IsString<42>; // false

// 14.2 ★ infer 关键字 —— 条件类型中「推导」类型
type ArrayElement<T> = T extends Array<infer U> ? U : never;
type Elem = ArrayElement<number[]>; // number
type Str = ArrayElement<"hello">; // never

// 函数返回类型
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type R = MyReturnType<() => number>; // number

// 14.3 ★ 映射类型 —— 把一个类型的字段「变换」为另一个类型
type ReadonlyAll<T> = {
  readonly [K in keyof T]: T[K];
};

type UserRO = ReadonlyAll<{ name: string; age: number }>;
// { readonly name: string; readonly age: number }

// key remapping（4.1+）：as 重命名
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
type UserGetters = Getters<{ name: string; age: number }>;
// { getName: () => string; getAge: () => number }

// 14.4 ★ 分布式条件类型（naked type parameter in union）
//
// 当 T 是裸类型参数且是 union 时，条件类型会「分布」应用
type ToArray<T> = T extends any ? T[] : never;
type StrOrNumArr = ToArray<string | number>;
// string[] | number[]（不是 (string | number)[]）

// 14.5 ★ satisfies 操作符（4.9+）—— 校验形状但保留具体类型
//
// 问题：我们想校验对象形状，又想保留每个字段的具体字面量类型
type Colors = "red" | "green" | "blue";
type RGB = [number, number, number];

// 用 satisfies：既校验又保留
// 下面「故意」用 "bleu"（拼错）来展示 satisfies 的检测能力
// 但这样会编译失败，所以分两种演示：

// 1) 正确写法（编译通过）
const palette = {
  red: [255, 0, 0] as RGB,
  green: "#00ff00",
  blue: "#0000ff",
} satisfies Record<Colors, string | RGB>;

// 2) 错误写法的注释（如果取消注释会编译失败）
// const paletteBad = {
//   red: [255, 0, 0],
//   green: "#00ff00",
//   bleu: [0, 0, 255],  // ❌ 编译错误：bleu 不是 Colors
// } satisfies Record<Colors, string | RGB>;

// 还能保留具体类型
const redComponent = palette.red[0]; // number（不变成 string | number）
const greenStr = palette.green.toUpperCase(); // string

// 对比：如果用类型注解
// const palette2: Record<Colors, string | RGB> = { ... }  // 错误检测到了，但 palette.green 变成 string | RGB，丢失具体类型

// 14.6 ★ keyof / typeof
const point = { x: 1, y: 2 };
type Point = typeof point; // { x: number; y: number }
type PointKey = keyof Point; // "x" | "y"

// 14.7 索引访问类型
type User1 = { name: string; age: number; address: { city: string } };
type City = User1["address"]["city"]; // string
type UserValue = User1[keyof User1]; // string | number | { city: string }

// ============================================================================
// § 15. 类型推断
// ============================================================================

// 15.1 最佳通用类型推断
const arr = [1, 2, 3]; // number[]
const mixed = [1, "two", true]; // (string | number | boolean)[]

// 15.2 上下文类型推断（call-site 推断）—— 浏览器环境演示
// 仅在浏览器中执行；Node 环境跳过
declare const window: { addEventListener(event: "click", handler: (e: { clientX: number }) => void): void };
if (typeof window !== "undefined") {
  window.addEventListener("click", (event) => {
    // event: { clientX: number }（由 addEventListener 的签名推断）
    console.log(event.clientX);
  });
}

// 15.3 ★ NoInfer 工具类型（5.4+）—— 阻止泛型推断
//
// 当函数有多个类型参数时，TS 默认从所有位置推断
// NoInfer 告诉 TS「不要从这里推断」
function createFS<Path extends string, Content extends string>(
  path: Path,
  content: Content
): { path: Path; content: Content } {
  return { path, content };
}

// 不加 NoInfer：两个参数都参与推断，可能推断错误
// 加 NoInfer<Path>：只从第一个参数推断 Path

// ============================================================================
// § 16. 模块与命名空间
// ============================================================================

// 16.1 ES Modules
// import { User } from "./user";
// import type { UserType } from "./types";  // 类型导入
// export default class ...
// export { ... }

// 16.2 命名空间（旧风格，新项目不推荐）
// namespace MyApp {
//   export interface Config { ... }
//   export const version = "1.0";
// }

// ============================================================================
// § 17. 声明文件
// ============================================================================

// 17.1 .d.ts 文件：给 JS 库写类型
// declare module "my-lib" {
//   export function hello(name: string): string;
// }

// 17.2 declare global
// declare global {
//   interface Window {
//     myGlobal: string;
//   }
// }

// ============================================================================
// § 18. ★ TypeScript 独有特色汇总
// ============================================================================
//
// [1] 结构化类型（structural typing）—— duck typing 静态版
// [2] 联合类型 + 判别联合（discriminated unions）
// [3] 条件类型 T extends U ? X : Y
// [4] infer 关键字
// [5] 映射类型 + key remapping
// [6] 模板字面量类型（template literal types）
// [7] satisfies 操作符（4.9+）
// [8] const 泛型（5.0+）
// [9] 自定义类型守卫 + 断言函数
// [10] 工具类型体系（Partial/Pick/Omit/Record/ReturnType/...）

// ============================================================================
// § 19. 完整实战模型
// ============================================================================
//
// 真实业务场景下的「TypeScript 类型系统综合应用」：
//   - interface 描述对象形状
//   - type 描述工具类型
//   - enum / 字面量联合做状态
//   - 判别联合做多态
//   - 泛型做容器
//   - class 实现业务逻辑

// 19.1 地址
interface Address {
  street: string;
  city: string;
  country: string;
  postalCode?: string;
}

// 19.2 Pet（用字面量联合 + class）
type PetKind = "dog" | "cat" | "bird" | "fish";

class Pet {
  constructor(
    public readonly id: number,
    public name: string,
    public kind: PetKind,
    public ageYears: number = 0,
    public tags: string[] = [],
    public owner?: User
  ) {
    if (ageYears < 0) {
      throw new Error("Pet age cannot be negative");
    }
  }

  get description(): string {
    return `${this.name} is a ${this.ageYears}-year-old ${this.kind}`;
  }
}

// 19.3 User（继承字段 + implements 接口）
interface IUser {
  id: number;
  name: string;
  email: string;
  age?: number;
  address?: Address;
  pets: Pet[];
  roles: ReadonlyArray<"admin" | "editor" | "viewer">;
}

class User implements IUser {
  static instanceCount = 0;
  readonly createdAt: Date = new Date();

  constructor(
    public readonly id: number,
    public name: string,
    public email: string,
    public age?: number,
    public address?: Address,
    public pets: Pet[] = [],
    public roles: ReadonlyArray<"admin" | "editor" | "viewer"> = []
  ) {
    User.instanceCount++;
  }

  get isAdult(): boolean {
    return this.age !== undefined && this.age >= 18;
  }

  addPet(pet: Pet): this {
    pet.owner = this;
    this.pets.push(pet);
    return this;
  }
}

// 19.4 Article（字面量联合做状态）
type ArticleStatus = "draft" | "review" | "published" | "archived";

class Article {
  private publishedAt: Date | null = null;

  constructor(
    public readonly id: number,
    public title: string,
    public author: User,
    public status: ArticleStatus = "draft",
    public content: string = "",
    public tags: string[] = []
  ) {}

  publish(): void {
    if (this.status === "published") {
      throw new Error("Already published");
    }
    this.status = "published";
    this.publishedAt = new Date();
  }

  get isPublished(): boolean {
    return this.publishedAt !== null;
  }
}

// 19.5 Order（泛型 + 判别联合做状态）
type OrderStatus = "pending" | "paid" | "shipped" | "delivered" | "cancelled";

interface OrderItem {
  productId: string;
  quantity: number;
  unitPrice: number;
}

class Order {
  constructor(
    public readonly orderId: string,
    public customer: User,
    public items: OrderItem[],
    public status: OrderStatus = "pending",
    public shippingAddress?: Address,
    public notes?: string,
    public placedAt: Date = new Date()
  ) {
    if (items.length === 0) {
      throw new Error("Order must have at least one item");
    }
  }

  get total(): number {
    return this.items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
  }

  summary(): string {
    const lines = [`Order ${this.orderId} (${this.status})`];
    for (const item of this.items) {
      lines.push(
        `  - ${item.productId} x ${item.quantity} = ${(item.quantity * item.unitPrice).toFixed(2)}`
      );
    }
    lines.push(`Total: ${this.total.toFixed(2)}`);
    return lines.join("\n");
  }
}

// 19.6 业务接口：折扣策略
interface DiscountPolicy {
  apply(total: number): number;
  description: string;
}

class PercentageDiscount implements DiscountPolicy {
  constructor(public percent: number) {}
  apply(total: number): number {
    return total * (1 - this.percent / 100);
  }
  get description(): string {
    return `${this.percent}% off`;
  }
}

class FlatDiscount implements DiscountPolicy {
  constructor(public amount: number) {}
  apply(total: number): number {
    return Math.max(0, total - this.amount);
  }
  get description(): string {
    return `flat ${this.amount} off`;
  }
}

// 19.7 泛型仓储
class Repository<T extends { id: number }> {
  private items = new Map<number, T>();

  save(item: T): void {
    this.items.set(item.id, item);
  }
  find(id: number): T | undefined {
    return this.items.get(id);
  }
  all(): T[] {
    return Array.from(this.items.values());
  }
}

// 19.8 ★ 实战类型编程示例
// 用判别联合 + 模板字面量类型描述 API 响应
type ApiResult<T> =
  | { status: "success"; data: T }
  | { status: "error"; error: { code: number; message: string } };

function handleResponse<T>(resp: ApiResult<T>): T {
  if (resp.status === "success") {
    return resp.data;
  }
  throw new Error(`[${resp.error.code}] ${resp.error.message}`);
}

// ============================================================================
// 演示入口
// ============================================================================

export function demo(): void {
  console.log("=== TypeScript 类型系统演示 ===\n");

  // 基础
  console.log("[§ 2] 基础类型:");
  console.log(`  move("north") = ${move("north")}`);

  // 容器
  console.log("\n[§ 3] 容器:");
  console.log(`  first([1, 2, 3]) = ${first([1, 2, 3])}`);
  console.log(`  point3d = ${JSON.stringify(point3d)}`);

  // 联合
  console.log("\n[§ 4] 联合:");
  console.log(`  format("  hi  ") = "${format("  hi  ")}"`);
  console.log(`  format(3.14) = "${format(3.14)}"`);
  console.log(`  area({ kind: "circle", radius: 5 }) = ${area({ kind: "circle", radius: 5 }).toFixed(2)}`);

  // 字面量
  console.log("\n[§ 5] as const:");
  console.log(`  configConst.apiUrl = ${configConst.apiUrl}`);

  // 枚举
  console.log("\n[§ 6] 枚举:");
  console.log(`  HttpStatus.OK = ${HttpStatus.OK}`);

  // 类
  console.log("\n[§ 8] 类:");
  const acc = new BankAccount(1000);
  acc.deposit(500);
  console.log(`  BankAccount.balance = ${acc.balance}`);

  // 泛型
  console.log("\n[§ 10] 泛型:");
  console.log(`  first([1,2,3]) = ${first([1, 2, 3])}`);
  console.log(`  getProperty(u, "name") = ${getProperty(u, "name")}`);

  // satisfies
  console.log("\n[§ 14.5] satisfies:");
  console.log(`  palette.red[0] = ${palette.red[0]}`);
  console.log(`  palette.green.toUpperCase() = ${palette.green.toUpperCase()}`);

  // 实战模型
  console.log("\n[§ 19] 实战模型:");
  const addr: Address = { street: "长安街 1 号", city: "北京", country: "China" };
  const alice = new User(1, "Alice", "alice@example.com", 30, addr);
  const dog = new Pet(1, "旺财", "dog", 3);
  alice.addPet(dog);

  const article = new Article(1, "TypeScript 入门", alice, "draft");
  article.publish();

  const order = new Order(
    "ORD-001",
    alice,
    [
      { productId: "P-100", quantity: 2, unitPrice: 99.0 },
      { productId: "P-200", quantity: 1, unitPrice: 199.0 },
    ],
    "pending",
    addr
  );

  const discount = new PercentageDiscount(10);
  const finalTotal = discount.apply(order.total);
  console.log(`  User: ${alice.name} (${alice.email}), Adult: ${alice.isAdult}`);
  console.log(`  Pet: ${dog.description}`);
  console.log(`  Article: '${article.title}' status=${article.status}, published=${article.isPublished}`);
  console.log(`  Order: ${order.orderId}, total=${order.total.toFixed(2)}, after ${discount.description} = ${finalTotal.toFixed(2)}`);

  // 泛型仓储
  const petRepo = new Repository<Pet>();
  petRepo.save(dog);
  const found = petRepo.find(1);
  console.log(`  Repository found: ${found?.description}`);

  console.log("\n=== 演示完成 ===");
}

// 如果直接执行此文件（编译时忽略这部分）
declare const require: { main?: unknown };
declare const module: { exports: unknown };
if (typeof require !== "undefined" && require.main === module) {
  demo();
}
