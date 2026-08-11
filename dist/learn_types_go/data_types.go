// Package main 是 Go 类型系统学习入口（单文件教学版）。
//
// 适用版本：Go 1.18 ~ 1.26（推荐 1.21+ 享受 slices/maps、1.22+ cmp.Ordered、1.23+ iter）
// 学习目标：
//   1. 掌握 Go 静态类型系统的全部能力
//   2. 看懂 1.18 泛型、1.21 slices 包、1.23 iter 包
//   3. 学会用 struct + struct tag + 接口 + 嵌入 描述真实业务模型
//   4. 配合 data_validation.go 做运行时校验
//
// 运行方式：
//   go run data_types.go
package main

import (
	"cmp" // 1.21+
	"errors"
	"fmt"
	"slices" // 1.21+
	"strings"
	"time"
)

// ============================================================================
// § 1. 类型系统全景
// ============================================================================
//
// Go 类型系统三大特点（区别于 Python / TypeScript / Rust）：
//
// 1. 静态强类型 + 编译期检查
//   - 所有类型不匹配在编译期就会报错
//   - 没有「运行时类型注解」概念，类型信息在编译后被擦除（除接口外）
//
// 2. 隐式接口实现（structural typing 的轻量版）
//   - 类型不需要写 implements 关键字
//   - 只要方法集匹配，就自动满足接口
//
// 3. 命名类型严格区分
//   - type X int 定义的新类型 X 与 int 不能混用
//   - 需要显式转换
//
// 配合 1.18 泛型 + 1.21 slices/maps + 1.23 iter，整个类型系统已经相当完整。
//
// 零值机制（Go 特色）：
//   - 每个类型都有零值：int→0、bool→false、string→""、指针/slice/map→nil
//   - 不需要构造函数也能保证变量可用
//   - 复合类型（struct）的零值是其所有字段零值的组合

// ============================================================================
// § 2. 基础类型
// ============================================================================

// 2.1 布尔
var isActive bool = true
var isDeleted bool // 零值: false

// 2.2 整数族
var (
	i   int     = 42     // 平台相关（32 或 64 位）
	i8  int8    = -128   // 显式大小
	i16 int16   = 32767
	i32 int32   = 2147483647
	i64 int64   = 9223372036854775807
	u   uint    = 0      // 无符号
	u8  uint8   = 255
	u16 uint16  = 65535
	u32 uint32  = 4294967295
	u64 uint64  = 18446744073709551615
)

// 2.3 字节与字符
//   byte   = uint8 别名  （强调字节语义）
//   rune   = int32 别名  （强调 Unicode 码点语义）
var (
	b   byte = 'A'                // ASCII 字符
	r   rune = '中'               // Unicode 码点
	str       = "Hello, 世界"      // UTF-8 字符串
)

// 2.4 浮点
var (
	f32 float32 = 3.14
	f64 float64 = 3.141592653589793
)

// 2.5 复数
var c128 complex128 = 1 + 2i

// 2.6 字符串（不可变字节序列）
var greeting string = "Hello"

// 演示 rune 遍历 Unicode 字符
func demoRune() {
	for i, r := range str {
		fmt.Printf("  byte idx=%d, rune=%q (U+%04X)\n", i, r, r)
	}
}

// ============================================================================
// § 3. 复合类型
// ============================================================================

// 3.1 数组（长度是类型的一部分，固定大小）
var (
	scores  [5]int                  = [5]int{90, 85, 92, 78, 88}
	matrix  [3][3]float64            = [3][3]float64{}  // 二维数组
	zeroArr [10]byte                             // 零值数组（10 个 0）
)

// 3.2 切片（动态长度，引用底层数组）
var (
	emptySlice []int                       // nil 切片（零值）
	fullSlice  []int = []int{1, 2, 3}      // 字面量
	makeSlice  []int = make([]int, 5, 10)   // make 创建（len=5, cap=10）
)

// 切片操作：append / [low:high] / copy
func demoSlice() {
	s := []int{1, 2, 3}
	s = append(s, 4, 5)   // [1 2 3 4 5]
	sub := s[1:4]         // [2 3 4]（半开区间）
	clone := slices.Clone(s) // 1.21+ slices.Clone
	fmt.Println(clone, sub)
}

// 3.3 映射（无序键值对）
var (
	emptyMap  map[string]int                  // nil map（只读）
	priceMap  = map[string]float64{           // 字面量
		"apple":  5.0,
		"banana": 3.0,
	}
	makeMap   = make(map[string]int, 100)     // 预分配容量
)

// 3.4 指针
var (
	x       int  = 42
	p       *int = &x   // 取地址
	val     int  = *p   // 解引用
)

// 3.5 函数类型（一等公民）
type BinaryOp func(int, int) int

func add(a, b int) int      { return a + b }
func mul(a, b int) int      { return a * b }

var op BinaryOp = add

// 3.6 接口（详见 § 8）
// 3.7 通道（详见 § 11）

// ============================================================================
// § 4. 类型声明
// ============================================================================

// 4.1 定义新类型（与底层类型不兼容）
//
//	type UserID int  // UserID 是新类型，int 不能直接当 UserID 用
type UserID int
type Email string

// 4.2 类型别名（1.9+）—— 与原类型完全等价
//
//	type MyInt = int  // MyInt 就是 int，可以互换
type (
	MyInt   = int      // 别名
	MyError = error    // 别名（用于 error 类型重命名）
)

// 4.3 ★ 命名类型 vs 别名（重点）
//
//	type X T       // 命名类型：需要显式转换 T(x) 才能互转
//	type X = T      // 类型别名：完全等价
//
// 业务建模推荐用「命名类型」（强类型安全）：
//
//	type UserID int
//	type OrderID int
//
// 迁移 / 包装推荐用「别名」（最小改动）：
//
//	type OldName = NewName

func demoTypeDef() {
	var uid UserID = UserID(1)
	// var i int = uid        // 编译错误：cannot use uid (type UserID) as type int
	var i int = int(uid)      // 显式转换
	var my MyInt = 42
	var j int = my            // 别名可以直接用
	fmt.Println(uid, i, my, j)
}

// 4.4 命名类型的方法（详见 § 7）
// UserID 可以有自己的方法
func (u UserID) String() string {
	return fmt.Sprintf("User#%d", int(u))
}

func (e Email) IsValid() bool {
	return strings.Contains(string(e), "@")
}

// ============================================================================
// § 5. 常量与 iota
// ============================================================================

// 5.1 命名常量
const (
	AppName    = "MyApp"
	AppVersion = "1.0.0"
	MaxRetries = 3
)

// 5.2 ★ iota —— 自动递增常量生成器（Go 特色）
//
//	每个 const 块中 iota 从 0 开始，每行 +1
//	常用于枚举值
type OrderStatus int

const (
	StatusPending OrderStatus = iota // 0
	StatusPaid                        // 1
	StatusShipped                     // 2
	StatusDelivered                   // 3
	StatusCancelled                   // 4
)

// 5.3 跳号 iota
type Permission int

const (
	PermRead Permission = 1 << iota // 1
	PermWrite                       // 2
	PermExecute                     // 4
)

// 5.4 字符串枚举（用 iota 配 string() 方法）
type Priority string

const (
	PriorityLow    Priority = "low"
	PriorityMedium Priority = "medium"
	PriorityHigh   Priority = "high"
)

// 5.5 无类型常量（untyped constant）
//
//	无类型常量可隐式转换为合适类型
//	例：const x = 10，x 可以赋给 int、int64、float64 等
const (
	DefaultTimeout = 30 * time.Second   // 无类型常量 time.Duration
	MaxConnections = 1000
)

// ============================================================================
// § 6. 结构体（struct）
// ============================================================================

// 6.1 基础结构体
type Point struct {
	X, Y float64
}

// 6.2 ★ struct tag —— 字段元数据（Go 特色）
//
//	tag 是字符串字面量，格式：key:"value" 多个用空格分隔
//	用 reflect 包读取
//	常见用途：JSON 序列化、ORM 映射、参数校验
type UserProfile struct {
	ID       UserID  `json:"id" validate:"required,min=1"`
	Name     string  `json:"name" validate:"required,min=1,max=50"`
	Email    Email   `json:"email" validate:"required,email"`
	Age      int     `json:"age" validate:"gte=0,lte=150"`
	Bio      string  `json:"bio,omitempty"`           // omitempty：空字符串不序列化
	Nickname *string `json:"nickname,omitempty"`      // 指针 + omitempty：nil 不序列化
}

// 6.3 ★ 字段嵌入（embedding）—— 「组合优于继承」
//
//	匿名字段（只有类型没有名字）的方法会被「提升」到外层结构体
//	这是 Go 模拟继承的方式
type Timestamps struct {
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type Article struct {
	Timestamps                  // 嵌入：Article 自动有 CreatedAt/UpdatedAt 字段
	Title       string          `json:"title"`
	Author      string          `json:"author"`
	Content     string          `json:"content"`
	Tags        []string        `json:"tags"`
}

// 6.4 构造函数惯例（NewXxx）
func NewArticle(title, author, content string) *Article {
	now := time.Now()
	return &Article{
		Timestamps: Timestamps{CreatedAt: now, UpdatedAt: now},
		Title:      title,
		Author:     author,
		Content:    content,
		Tags:       []string{},
	}
}

// ============================================================================
// § 7. 方法（method）
// ============================================================================

// 7.1 值接收者 vs 指针接收者
//
// 值接收者：不修改原对象
// 指针接收者：可修改原对象；大结构体传指针效率更高
//
// 经验法则：
//   1. 如果方法需要修改接收者，必须用指针
//   2. 如果结构体很大，建议用指针
//   3. 同类型的值方法和指针方法不能混用（要么全值，要么全指针）

// 指针接收者：能修改
func (p *Point) Move(dx, dy float64) {
	p.X += dx
	p.Y += dy
}

// 值接收者：不能修改
func (p Point) Distance(other Point) float64 {
	dx := p.X - other.X
	dy := p.Y - other.Y
	return (dx*dx + dy*dy) * 0.5 // 注：仅为演示，未做开方
}

// 7.2 命名类型方法
func (s OrderStatus) String() string {
	switch s {
	case StatusPending:
		return "pending"
	case StatusPaid:
		return "paid"
	case StatusShipped:
		return "shipped"
	case StatusDelivered:
		return "delivered"
	case StatusCancelled:
		return "cancelled"
	default:
		return "unknown"
	}
}

func (s OrderStatus) IsTerminal() bool {
	return s == StatusDelivered || s == StatusCancelled
}

// 7.3 ★ 方法集规则（重要）
//
//   类型 T 的方法集：只包含「值接收者」方法
//   类型 *T 的方法集：包含「值接收者 + 指针接收者」全部方法
//
// 因此：实现接口时，值类型只能调用值接收者方法，指针类型可以调用全部。

// ============================================================================
// § 8. 接口（interface）
// ============================================================================

// 8.1 ★ 接口定义方法集
//
//	任何类型只要实现了接口的所有方法，就隐式实现该接口
//	不写 implements 关键字
type Stringer interface {
	String() string
}

type Describer interface {
	Describe() string
}

// 8.2 嵌入接口（接口组合）
//
//	ReadWriter = Reader + Writer
type Reader interface {
	Read(p []byte) (n int, err error)
}

type Writer interface {
	Write(p []byte) (n int, err error)
}

type ReadWriter interface {
	Reader
	Writer
}

// 8.3 空接口 any（1.18+）
//
//	interface{} 的别名，表示「任何类型」
//	常用于 JSON 反序列化到 interface{} / 容器元素类型
type AnyMap = map[string]any

// 8.4 标准库常用接口

// error 接口
type error interface {
	Error() string
}

// errorString 是 errors.New 的实现
var ErrNotFound = errors.New("not found")
var ErrInvalid = errors.New("invalid input")

// 8.5 自定义错误类型
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("validation failed: %s: %s", e.Field, e.Message)
}

// 8.6 类型断言
func demoTypeAssertion() {
	var s Stringer = UserID(42)
	if uid, ok := s.(UserID); ok {
		fmt.Printf("  type assertion OK: %d\n", int(uid))
	}

	// 8.7 type switch
	var i any = "hello"
	switch v := i.(type) {
	case string:
		fmt.Printf("  string: %q\n", v)
	case int:
		fmt.Printf("  int: %d\n", v)
	case bool:
		fmt.Printf("  bool: %v\n", v)
	default:
		fmt.Printf("  unknown: %T\n", v)
	}
}

// ============================================================================
// § 9. ★ 泛型（Generics，1.18+）
// ============================================================================
//
// 1.18 是 Go 自开源以来最大的变化，引入了：
//   - 类型参数（type parameters）
//   - 类型约束（type constraints）
//   - 类型推断（type inference）
//
// 泛型函数
func Map[T, U any](s []T, f func(T) U) []U {
	result := make([]U, len(s))
	for i, v := range s {
		result[i] = f(v)
	}
	return result
}

// 泛型类型
type Box[T any] struct {
	Value T
}

func (b Box[T]) Get() T {
	return b.Value
}

// 9.3 预定义约束
//
//   - any (1.18+)        等价于 interface{}
//   - comparable (1.18+) 可比较类型（支持 == 和 !=）
//   - cmp.Ordered (1.22+) 有序类型（支持 < > <= >=）

// 查找元素（用 comparable 约束）
func Index[T comparable](s []T, target T) int {
	for i, v := range s {
		if v == target {
			return i
		}
	}
	return -1
}

// 通用 Min（用 cmp.Ordered，1.22+）
func Min[T cmp.Ordered](a, b T) T {
	if a < b {
		return a
	}
	return b
}

// 9.4 ★ 自定义类型约束（接口现在是「类型集合」）
//
//	interface { int | float64 | string }   —— 联合类型
//	interface { ~int }                     —— 底层类型是 int 的所有命名类型
type Number interface {
	~int | ~int32 | ~int64 | ~float32 | ~float64
}

func Sum[T Number](nums []T) T {
	var total T
	for _, n := range nums {
		total += n
	}
	return total
}

// 9.5 泛型类型实例化
func demoGenerics() {
	// 函数泛型
	doubled := Map([]int{1, 2, 3}, func(x int) int { return x * 2 })
	_ = doubled

	// 类型泛型
	intBox := Box[int]{Value: 42}
	strBox := Box[string]{Value: "hello"}
	fmt.Println(intBox.Get(), strBox.Get())

	// 类型推断（多数情况下不需要写 [T]）
	_ = Index([]string{"a", "b", "c"}, "b") // T 自动推断为 string
	_ = Min(3, 5)                            // T 自动推断为 int
	_ = Min(3.14, 2.71)                      // T 自动推断为 float64
}

// ============================================================================
// § 10. 切片与映射的泛型（1.21+）
// ============================================================================
//
// 1.21 标准库加了 slices / maps 包，专门操作 slice 和 map
// 之前要 sort.Strings、sort.Ints、append([]int, ...) 等等

func demoSlicesMaps() {
	// 10.1 slices 包
	ints := []int{3, 1, 4, 1, 5, 9, 2, 6}
	slices.Sort(ints)                  // 排序
	fmt.Println("sorted:", ints)
	fmt.Println("contains 4:", slices.Contains(ints, 4))
	fmt.Println("index of 5:", slices.Index(ints, 5))
	fmt.Println("max:", slices.Max(ints))
	fmt.Println("min:", slices.Min(ints))

	// 切片操作
	uniq := mapValuesToSlice(map[string]int{"a": 1, "b": 2, "c": 3})
	slices.Sort(uniq)
	fmt.Println("  sorted values:", uniq)

	// 10.2 maps 包（导入路径 golang.org/x/exp/maps）
	// 标准库没有 maps 包，要用 x/exp/maps 才能用 maps.Keys / maps.Values
	// 这里演示标准库可用的方式
	scoresMap := map[string]int{"alice": 90, "bob": 85, "carol": 78}
	keys := make([]string, 0, len(scoresMap))
	for k := range scoresMap {
		keys = append(keys, k)
	}
	slices.Sort(keys)
	fmt.Println("  sorted keys:", keys)
}

// 辅助函数：把 map 的值转成 slice（标准库没有，自己写）
func mapValuesToSlice[K comparable, V any](m map[K]V) []V {
	out := make([]V, 0, len(m))
	for _, v := range m {
		out = append(out, v)
	}
	return out
}

// 10.3 内置 min / max（1.21+）
func demoBuiltinMinMax() {
	fmt.Println("min(1, 2, 3):", min(1, 2, 3))
	fmt.Println("max(1.0, 2.0):", max(1.0, 2.0))
}

// 10.4 ★ iter 包 + range over func（1.23+）
//
// Go 1.23 允许自定义 range 遍历源
// iter.Seq[V any]            函数签名 func(yield func(V) bool)
// iter.Seq2[K, V any]        函数签名 func(yield func(K, V) bool)
//
// 这样可以用 for k, v := range myfunc { ... } 的形式遍历任意数据源

// Push 函数生成 1..n 的迭代器
func Push(n int) func(yield func(int) bool) {
	return func(yield func(int) bool) {
		for i := 1; i <= n; i++ {
			if !yield(i) {
				return
			}
		}
	}
}

// MapIter 转换迭代器
func MapIter(seq func(yield func(int) bool), f func(int) int) func(yield func(int) bool) {
	return func(yield func(int) bool) {
		seq(func(v int) bool {
			return yield(f(v))
		})
	}
}

func demoIter() {
	// range over func（1.23+）
	for v := range Push(5) {
		fmt.Printf("  %d ", v)
	}
	fmt.Println()

	// 转换
	for v := range MapIter(Push(3), func(x int) int { return x * x }) {
		fmt.Printf("  %d ", v)
	}
	fmt.Println()
}

// ============================================================================
// § 11. 通道（chan）
// ============================================================================

// 11.1 创建通道
var (
	unbuffered = make(chan int)          // 无缓冲
	buffered   = make(chan int, 10)      // 有缓冲 10
)

// 11.2 方向
func sender(out chan<- int) { // 只发送
	out <- 42
}

func receiver(in <-chan int) int { // 只接收
	return <-in
}

// 11.3 关闭与 range
func demoChan() {
	ch := make(chan int, 3)
	ch <- 1
	ch <- 2
	ch <- 3
	close(ch) // 关闭后 range 会自然结束

	for v := range ch {
		fmt.Printf("  received: %d\n", v)
	}
}

// ============================================================================
// § 12. 函数与多返回值
// ============================================================================

// 12.1 ★ 多返回值（Go 特色）
func divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, errors.New("division by zero")
	}
	return a / b, nil
}

// 12.2 命名返回值
func stats(nums []int) (min, max, sum int) {
	if len(nums) == 0 {
		return // 命名返回值会自动 zero
	}
	min, max = nums[0], nums[0]
	for _, n := range nums {
		sum += n
		if n < min {
			min = n
		}
		if n > max {
			max = n
		}
	}
	return // 等价于 return min, max, sum
}

// 12.3 变参
func sum(nums ...int) int {
	total := 0
	for _, n := range nums {
		total += n
	}
	return total
}

// 12.4 defer / panic / recover
func demoDefer() {
	defer fmt.Println("  3. defer 最后执行")
	defer fmt.Println("  2. defer 倒序执行")
	fmt.Println("  1. 函数体")
}

func safeDivide(a, b float64) (result float64, err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("recovered panic: %v", r)
		}
	}()
	if b == 0 {
		panic("division by zero")
	}
	result = a / b
	return
}

// ============================================================================
// § 13. 错误处理
// ============================================================================

// 13.1 自定义错误类型
type BusinessError struct {
	Code    int
	Message string
}

func (e *BusinessError) Error() string {
	return fmt.Sprintf("[E%d] %s", e.Code, e.Message)
}

// 13.2 errors.Is / errors.As（1.13+）
//
//	Is：判断错误链中是否有特定错误值
//	As：把错误链中的错误提取到目标类型
func demoErrorChain() {
	wrapped := fmt.Errorf("user service: %w", &BusinessError{Code: 1001, Message: "user not found"})

	// 13.3 ★ errors.Join（1.20+）—— 聚合多个错误
	err1 := errors.New("validation: name required")
	err2 := errors.New("validation: email invalid")
	joined := errors.Join(err1, err2)
	fmt.Println("joined error:", joined)

	_ = wrapped
}

// ============================================================================
// § 14. 类型断言与类型转换
// ============================================================================

// 类型转换：T(x) —— 显式
func demoConversion() {
	var i int = 42
	var f float64 = float64(i)
	var s string = fmt.Sprintf("%d", i)
	_ = f
	_ = s
}

// 类型断言：x.(T) —— 运行时检查
func demoAssertion() {
	var i any = "hello"

	// 安全的类型断言
	if s, ok := i.(string); ok {
		fmt.Printf("  string: %q\n", s)
	}

	// 不安全的类型断言（失败会 panic）
	// s := i.(int)  // panic
}

// type switch
func describe(v any) string {
	switch x := v.(type) {
	case int:
		return fmt.Sprintf("int=%d", x)
	case string:
		return fmt.Sprintf("string=%q", x)
	case bool:
		return fmt.Sprintf("bool=%v", x)
	case Stringer:
		return fmt.Sprintf("Stringer=%s", x.String())
	case error:
		return fmt.Sprintf("error=%v", x.Error())
	case nil:
		return "nil"
	default:
		return fmt.Sprintf("unknown type %T", x)
	}
}

// ============================================================================
// § 15. 反射（reflect）
// ============================================================================
//
// reflect 包提供运行时类型信息和值操作
// 主要场景：通用序列化、ORM 映射、tag 驱动的校验
// 性能开销：比直接调用慢 10-100 倍
//
// 注：完整 reflect 用法放 data_validation.go 里演示
// 这里只展示「读 struct tag」占位

// ============================================================================
// § 16. ★ Go 独有特色汇总
// ============================================================================
// § 16. ★ Go 独有特色汇总
// ============================================================================
//
// [1] 隐式接口实现（structural typing）—— 不写 implements
// [2] 类型嵌入（embedding）—— 用组合模拟继承
// [3] 多返回值 + 显式 error（替代 try-catch）
// [4] struct tag（编译期元数据，运行期 reflect 读取）
// [5] defer / panic / recover（错误恢复）
// [6] 1.18 泛型（类型参数 + 类型约束 + 类型推断）
// [7] 1.21 slices / maps 标准库（替代 sort.Ints 等老 API）
// [8] 1.22 cmp.Ordered（替代 constraints.Ordered）
// [9] 1.23 iter 包 + range over func（自定义迭代器）
// [10] 命名类型严格区分（type X int 与 int 不兼容）

// ============================================================================
// § 17. 完整实战模型
// ============================================================================
//
// 真实业务场景下的「Go 类型系统综合应用」：
//   - struct 描述实体
//   - 命名类型做 ID（强类型安全）
//   - struct tag 做 JSON / 校验
//   - 接口定义业务接口
//   - 嵌入组合公共字段
//   - 泛型做容器
//   - 自定义错误做业务错误

// 17.1 地址（命名类型演示）
type Address struct {
	Street     string `json:"street" validate:"required"`
	City       string `json:"city" validate:"required"`
	Country    string `json:"country" validate:"required"`
	PostalCode string `json:"postal_code" validate:"omitempty,len=6"`
}

// 17.2 命名类型 ID（强类型安全）
type (
	ArticleID string
	OrderID   string
	PetID     int64
)

// 17.3 嵌入的公共时间戳
type Audit struct {
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// 17.4 User
type User struct {
	Audit                                   // 嵌入：自动有 CreatedAt/UpdatedAt
	ID       UserID  `json:"id" validate:"required,min=1"`
	Name     string  `json:"name" validate:"required,min=1,max=50"`
	Email    Email   `json:"email" validate:"required,email"`
	Age      *int    `json:"age,omitempty" validate:"omitempty,gte=0,lte=150"`
	Address  Address `json:"address"`
	Roles    []string `json:"roles"`
}

// 实现 Stringer 接口（任意 User 都能用 fmt.Println 直接打印）
func (u User) String() string {
	return fmt.Sprintf("User<%d %s %s>", int(u.ID), u.Name, u.Email)
}

// 17.5 Pet
type Pet struct {
	Audit
	ID     PetID    `json:"id"`
	Name   string   `json:"name" validate:"required"`
	Kind   string   `json:"kind" validate:"required,oneof=dog cat bird fish"`
	Age    int      `json:"age" validate:"gte=0"`
	Tags   []string `json:"tags,omitempty"`
	Owner  *User    `json:"owner,omitempty"`
}

func (p Pet) String() string {
	return fmt.Sprintf("Pet<%s the %s>", p.Name, p.Kind)
}

// 17.6 Article（嵌入 Audit + 实现 Stringer）
type ArticleModel struct {
	Audit
	ID       ArticleID  `json:"id"`
	Title    string     `json:"title" validate:"required,max=200"`
	AuthorID UserID     `json:"author_id" validate:"required"`
	Content  string     `json:"content"`
	Tags     []string   `json:"tags"`
	Status   Priority   `json:"status" validate:"oneof=low medium high"`
}

func (a ArticleModel) String() string {
	return fmt.Sprintf("Article<%s '%s'>", a.ID, a.Title)
}

// 17.7 OrderItem + Order
type OrderItem struct {
	ProductID string  `json:"product_id" validate:"required"`
	Quantity  int     `json:"quantity" validate:"required,gte=1"`
	UnitPrice float64 `json:"unit_price" validate:"gte=0"`
}

func (item OrderItem) Subtotal() float64 {
	return float64(item.Quantity) * item.UnitPrice
}

type Order struct {
	Audit
	ID         OrderID      `json:"id"`
	CustomerID UserID       `json:"customer_id" validate:"required"`
	Items      []OrderItem  `json:"items" validate:"required,min=1,dive"`
	Status     OrderStatus  `json:"status"`
	Total      float64      `json:"total"`
	Address    *Address     `json:"address,omitempty"`
	Notes      string       `json:"notes,omitempty"`
}

// 17.8 业务接口：折扣策略
type DiscountPolicy interface {
	Apply(total float64) float64
	Description() string
}

type PercentageDiscount struct {
	Percent float64
}

func (p PercentageDiscount) Apply(total float64) float64 {
	return total * (1 - p.Percent/100)
}

func (p PercentageDiscount) Description() string {
	return fmt.Sprintf("%.1f%% off", p.Percent)
}

type FlatDiscount struct {
	Amount float64
}

func (f FlatDiscount) Apply(total float64) float64 {
	return max(0, total-f.Amount)
}

func (f FlatDiscount) Description() string {
	return fmt.Sprintf("flat %.2f off", f.Amount)
}

// 17.9 泛型仓储（演示泛型实战）
type Repository[T any] struct {
	items map[string]T
}

func NewRepository[T any]() *Repository[T] {
	return &Repository[T]{items: make(map[string]T)}
}

func (r *Repository[T]) Save(id string, item T) {
	r.items[id] = item
}

func (r *Repository[T]) Find(id string) (T, bool) {
	item, ok := r.items[id]
	return item, ok
}

func (r *Repository[T]) All() []T {
	out := make([]T, 0, len(r.items))
	for _, v := range r.items {
		out = append(out, v)
	}
	return out
}

// 17.10 业务函数：用接口 + 多返回值
func checkout(order Order, policy DiscountPolicy) (finalTotal float64, err error) {
	if len(order.Items) == 0 {
		return 0, &ValidationError{Field: "items", Message: "order must have at least one item"}
	}

	var total float64
	for _, item := range order.Items {
		total += item.Subtotal()
	}

	return policy.Apply(total), nil
}

// ============================================================================
// 演示入口
// ============================================================================

func main() {
	fmt.Println("=== Go 类型系统演示 ===")
	fmt.Printf("Go version: %s\n\n", "1.21+")

	// 基础类型
	fmt.Println("[§ 2] 基础类型:")
	demoRune()

	// 切片
	fmt.Println("\n[§ 3] 切片:")
	demoSlice()

	// 类型声明
	fmt.Println("\n[§ 4] 类型声明:")
	demoTypeDef()
	uid := UserID(42)
	fmt.Printf("  uid.String() = %s, Email.IsValid() = %v\n", uid.String(), Email("a@b.com").IsValid())

	// 切片与映射
	fmt.Println("\n[§ 10] slices/maps 包:")
	demoSlicesMaps()
	demoBuiltinMinMax()

	// iter
	fmt.Println("\n[§ 10.4] iter 包 + range over func:")
	demoIter()

	// 通道
	fmt.Println("\n[§ 11] 通道:")
	demoChan()

	// defer
	fmt.Println("\n[§ 12] defer:")
	demoDefer()

	// 类型断言 + type switch
	fmt.Println("\n[§ 14] 类型断言与 type switch:")
	demoTypeAssertion()
	fmt.Printf("  describe(42) = %s\n", describe(42))
	fmt.Printf("  describe(\"hi\") = %s\n", describe("hi"))
	fmt.Printf("  describe(UserID(7)) = %s\n", describe(UserID(7)))

	// 泛型
	fmt.Println("\n[§ 9] 泛型:")
	demoGenerics()
	fmt.Printf("  Sum([]int{1,2,3}) = %d\n", Sum([]int{1, 2, 3}))
	fmt.Printf("  Sum([]float64{1.5, 2.5}) = %.2f\n", Sum([]float64{1.5, 2.5}))

	// 错误处理
	fmt.Println("\n[§ 13] 错误处理:")
	demoErrorChain()

	// 实战模型
	fmt.Println("\n[§ 17] 实战模型:")

	// User
	age := 30
	user := User{
		Audit:   Audit{CreatedAt: time.Now(), UpdatedAt: time.Now()},
		ID:      UserID(1),
		Name:    "Alice",
		Email:   Email("alice@example.com"),
		Age:     &age,
		Address: Address{Street: "长安街 1 号", City: "北京", Country: "China", PostalCode: "100000"},
		Roles:   []string{"admin", "editor"},
	}
	fmt.Printf("  %s\n", user)

	// Pet
	pet := Pet{
		Audit: Audit{CreatedAt: time.Now(), UpdatedAt: time.Now()},
		ID:    PetID(1),
		Name:  "旺财",
		Kind:  "dog",
		Age:   3,
		Tags:  []string{"friendly", "trained"},
		Owner: &user,
	}
	fmt.Printf("  %s\n", pet)

	// Article
	article := ArticleModel{
		Audit:    Audit{CreatedAt: time.Now(), UpdatedAt: time.Now()},
		ID:       ArticleID("art-001"),
		Title:    "Go 泛型入门",
		AuthorID: UserID(1),
		Content:  "...",
		Tags:     []string{"go", "generics"},
		Status:   PriorityMedium,
	}
	fmt.Printf("  %s\n", article)

	// Order + Discount
	order := Order{
		Audit:      Audit{CreatedAt: time.Now(), UpdatedAt: time.Now()},
		ID:         OrderID("ord-001"),
		CustomerID: UserID(1),
		Items: []OrderItem{
			{ProductID: "P-100", Quantity: 2, UnitPrice: 99.0},
			{ProductID: "P-200", Quantity: 1, UnitPrice: 199.0},
		},
		Status: StatusPending,
		Address: &Address{
			Street: "长安街 1 号", City: "北京", Country: "China", PostalCode: "100000",
		},
	}
	discount := PercentageDiscount{Percent: 10}
	// 先计算 order.Total（业务层在创建 Order 时通常会算好）
	var orderTotal float64
	for _, item := range order.Items {
		orderTotal += item.Subtotal()
	}
	order.Total = orderTotal

	finalTotal, err := checkout(order, discount)
	if err != nil {
		fmt.Printf("  checkout error: %v\n", err)
	} else {
		fmt.Printf("  Order %s: total=%.2f, after %s = %.2f\n",
			order.ID, order.Total, discount.Description(), finalTotal)
	}

	// 泛型仓储
	repo := NewRepository[Pet]()
	repo.Save("p1", pet)
	if found, ok := repo.Find("p1"); ok {
		fmt.Printf("  Repository found: %s\n", found)
	}

	fmt.Println("\n=== 演示完成 ===")
}