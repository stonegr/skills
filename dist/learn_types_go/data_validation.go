// Package main 是 Go 数据类型校验教学版。
//
// 适用版本：Go 1.18 ~ 1.26
// 学习目标：
//   1. 掌握「编译期类型检查 + 运行时校验」的两层策略
//   2. 学会用 encoding/json、reflect、go-playground/validator 做运行时校验
//   3. 学会错误聚合（errors.Join 1.20+）
//
// 依赖：
//   go get github.com/go-playground/validator/v10
//
// 运行方式：
//   go run data_validation.go
package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"reflect"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/go-playground/validator/v10"
)

// ============================================================================
// § 1. 校验全景 —— 编译期 vs 运行期
// ============================================================================
//
// Go 类型的校验分两层：
//
// ┌────────────────────────────────────────────────────────────┐
// │  编译期（Go 编译器）                                         │
// │  工具：go build / go vet                                    │
// │  时机：每次编译                                              │
// │  能力：检查命名类型、接口实现、泛型约束、方法签名              │
// │  限制：拿不到 JSON / 数据库 / 配置文件里的「动态数据」         │
// └────────────────────────────────────────────────────────────┘
//                          ↓ 不够
// ┌────────────────────────────────────────────────────────────┐
// │  运行期（手写 + 第三方）                                      │
// │  方案 1：encoding/json（标准库，隐式校验字段类型）            │
// │  方案 2：reflect 手写校验（灵活但啰嗦）                       │
// │  方案 3：go-playground/validator（最主流，tag 驱动）          │
// │  方案 4：业务层 Validate() 方法                              │
// │  方案 5：json.RawMessage + 自定义 UnmarshalJSON 处理 union   │
// └────────────────────────────────────────────────────────────┘
//
// 推荐策略：
//   - 函数签名 / 业务内部：靠 go build 编译期检查
//   - 边界（API 入参、数据库读取、消息队列、配置文件）：
//     必加 json.Unmarshal + validator.Struct

// ============================================================================
// § 2. 编译期类型检查
// ============================================================================
//
// Go 编译器本身做静态类型检查，举几个常见例子：

func demoCompileTime() {
	// 2.1 命名类型严格区分
	type UserID int
	// var i int = UserID(1)     // 编译错误：cannot use UserID(1) (type UserID) as type int
	var uid UserID = 1            // OK
	_ = uid

	// 2.2 泛型约束编译期生效
	// Min("a", "b")  // cmp.Ordered 约束不允许 string 吗？其实允许（1.22+）

	// 2.3 接口隐式实现（编译期检查方法集）
	// 类型只要有对应方法就自动实现接口，不需要 implements
	var s fmt.Stringer = time.Now() // time.Time 有 String() 方法
	_ = s

	fmt.Println("  编译期检查通过（看 IDE / go build）")
}

// ============================================================================
// § 3. encoding/json 反序列化校验
// ============================================================================
//
// json.Unmarshal 会做「隐式校验」：
//   - 字段类型不匹配 → 返回 *json.UnmarshalTypeError
//   - 必填字段缺失 → 零值（不报错！需要手动检查）
//   - 数字精度损失 → 浮点字段建议用 json.Number 或 string
//   - 未知字段 → 默认忽略（不会报错）

type AddressJSON struct {
	Street     string `json:"street"`
	City       string `json:"city"`
	Country    string `json:"country"`
	PostalCode string `json:"postal_code"`
}

type UserJSON struct {
	ID    int          `json:"id"`
	Name  string       `json:"name"`
	Email string       `json:"email"`
	Age   *int         `json:"age,omitempty"` // 指针 + omitempty：可空
	Addr  AddressJSON  `json:"address"`
	Tags  []string     `json:"tags,omitempty"`
	Meta  map[string]any `json:"meta,omitempty"`
}

func demoJSON() {
	fmt.Println("\n--- § 3. json.Unmarshal ---")

	// 3.1 正常解析
	goodJSON := `{
		"id": 1,
		"name": "Alice",
		"email": "alice@example.com",
		"age": 30,
		"address": {"street": "长安街", "city": "北京", "country": "CN"},
		"tags": ["vip", "active"]
	}`
	var u UserJSON
	if err := json.Unmarshal([]byte(goodJSON), &u); err != nil {
		fmt.Printf("  解析失败: %v\n", err)
	} else {
		age := *u.Age
		fmt.Printf("  解析成功: id=%d, name=%s, age=%d, city=%s, tags=%v\n",
			u.ID, u.Name, age, u.Addr.City, u.Tags)
	}

	// 3.2 类型不匹配 → *json.UnmarshalTypeError
	badTypeJSON := `{"id": "not-a-number", "name": "Bob", "email": "b@e.com"}`
	var u2 UserJSON
	if err := json.Unmarshal([]byte(badTypeJSON), &u2); err != nil {
		var typeErr *json.UnmarshalTypeError
		if errors.As(err, &typeErr) {
			fmt.Printf("  类型错误: field=%s, expected=%s, got=%s\n",
				typeErr.Field, typeErr.Type, typeErr.Value)
		}
	}

	// 3.3 必填字段缺失（不会报错！）
	missingJSON := `{"id": 2}` // name 和 email 缺失
	var u3 UserJSON
	if err := json.Unmarshal([]byte(missingJSON), &u3); err != nil {
		fmt.Printf("  解析失败: %v\n", err)
	} else {
		fmt.Printf("  必填字段缺失: name=%q, email=%q (零值不报错!)\n", u3.Name, u3.Email)
	}

	// 3.4 嵌套结构自动递归
	nestedJSON := `{"id": 3, "name": "C", "email": "c@e.com", "address": {"street": "x", "city": "y", "country": "z"}}`
	var u4 UserJSON
	if err := json.Unmarshal([]byte(nestedJSON), &u4); err != nil {
		fmt.Printf("  解析失败: %v\n", err)
	} else {
		fmt.Printf("  嵌套解析: city=%s\n", u4.Addr.City)
	}
}

// ============================================================================
// § 4. 类型断言与 type switch（运行时形状判断）
// ============================================================================

func demoTypeSwitch() {
	fmt.Println("\n--- § 4. type switch ---")

	values := []any{
		"hello",
		42,
		3.14,
		[]int{1, 2, 3},
		map[string]int{"a": 1},
		nil,
		true,
	}

	for _, v := range values {
		switch x := v.(type) {
		case nil:
			fmt.Printf("  nil\n")
		case string:
			fmt.Printf("  string: %q\n", x)
		case int:
			fmt.Printf("  int: %d\n", x)
		case float64:
			fmt.Printf("  float64: %.2f\n", x)
		case bool:
			fmt.Printf("  bool: %v\n", x)
		case []int:
			fmt.Printf("  []int: %v\n", x)
		case map[string]int:
			fmt.Printf("  map[string]int: %v\n", x)
		default:
			fmt.Printf("  unknown: %T = %v\n", x, x)
		}
	}
}

// ============================================================================
// § 5. reflect 手写校验
// ============================================================================
//
// 用 reflect 读 struct 字段和 tag，写一个简单的「必填字段」校验器
// 实际业务里通常用 validator 库（第 6 节），但理解 reflect 有助于自定义规则

// 5.1 简单必填校验器
type SimpleValidator struct {
	errors []string
}

func (v *SimpleValidator) Check(obj any, requiredFields ...string) {
	val := reflect.ValueOf(obj)
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}
	if val.Kind() != reflect.Struct {
		v.errors = append(v.errors, "expected struct or pointer to struct")
		return
	}

	for _, fieldName := range requiredFields {
		f := val.FieldByName(fieldName)
		if !f.IsValid() {
			v.errors = append(v.errors, fmt.Sprintf("field %s not found", fieldName))
			continue
		}
		if f.IsZero() {
			v.errors = append(v.errors, fmt.Sprintf("field %s is required", fieldName))
		}
	}
}

func (v *SimpleValidator) Errors() error {
	if len(v.errors) == 0 {
		return nil
	}
	return errors.Join(toAnySlice(v.errors)...) // 1.20+ errors.Join
}

func toAnySlice(errs []string) []error {
	out := make([]error, len(errs))
	for i, e := range errs {
		out[i] = errors.New(e)
	}
	return out
}

// 5.2 用 tag 驱动校验（演示 reflect 读 tag）
type UserWithTag struct {
	Name  string `validate:"required,min=2,max=20"`
	Email string `validate:"required,email"`
	Age   int    `validate:"min=0,max=150"`
}

// reflectValidator 用 reflect 读 tag 跑校验规则
func reflectValidator(obj any) error {
	val := reflect.ValueOf(obj)
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}
	typ := val.Type()

	var errs []error
	for i := 0; i < typ.NumField(); i++ {
		field := typ.Field(i)
		tag, ok := field.Tag.Lookup("validate")
		if !ok {
			continue
		}

		value := val.Field(i)
		for _, rule := range strings.Split(tag, ",") {
			if err := checkRule(field.Name, value, rule); err != nil {
				errs = append(errs, err)
			}
		}
	}
	return errors.Join(errs...)
}

func checkRule(name string, val reflect.Value, rule string) error {
	// 解析 "key=value" 或纯 "key"
	var key, param string
	if idx := strings.Index(rule, "="); idx >= 0 {
		key, param = rule[:idx], rule[idx+1:]
	} else {
		key = rule
	}

	switch key {
	case "required":
		if val.IsZero() {
			return fmt.Errorf("%s: required", name)
		}
	case "min":
		switch val.Kind() {
		case reflect.String:
			n, _ := strconv.Atoi(param)
			if len(val.String()) < n {
				return fmt.Errorf("%s: min length %d", name, n)
			}
		case reflect.Int, reflect.Int32, reflect.Int64:
			n, _ := strconv.Atoi(param)
			if val.Int() < int64(n) {
				return fmt.Errorf("%s: min %d", name, n)
			}
		}
	case "max":
		switch val.Kind() {
		case reflect.String:
			n, _ := strconv.Atoi(param)
			if len(val.String()) > n {
				return fmt.Errorf("%s: max length %d", name, n)
			}
		case reflect.Int, reflect.Int32, reflect.Int64:
			n, _ := strconv.Atoi(param)
			if val.Int() > int64(n) {
				return fmt.Errorf("%s: max %d", name, n)
			}
		}
	case "email":
		emailRegex := regexp.MustCompile(`^[\w.+-]+@[\w-]+\.[\w.-]+$`)
		if val.Kind() == reflect.String && !emailRegex.MatchString(val.String()) {
			return fmt.Errorf("%s: invalid email", name)
		}
	}
	return nil
}

func demoReflect() {
	fmt.Println("\n--- § 5. reflect 手写校验 ---")

	// 5.1 必填字段
	v := &SimpleValidator{}
	v.Check(UserJSON{ID: 1}, "ID", "Name", "Email", "Age", "Addr")
	if err := v.Errors(); err != nil {
		fmt.Printf("  校验失败:\n")
		for _, e := range strings.Split(err.Error(), "\n") {
			fmt.Printf("    - %s\n", e)
		}
	}

	// 5.2 tag 驱动
	good := UserWithTag{Name: "Alice", Email: "alice@example.com", Age: 30}
	if err := reflectValidator(good); err != nil {
		fmt.Printf("  good error: %v\n", err)
	} else {
		fmt.Printf("  good 通过\n")
	}

	bad := UserWithTag{Name: "A", Email: "bad-email", Age: 200}
	if err := reflectValidator(bad); err != nil {
		fmt.Printf("  bad 失败:\n")
		for _, e := range strings.Split(err.Error(), "\n") {
			fmt.Printf("    - %s\n", e)
		}
	}
}

// ============================================================================
// § 6. ★ go-playground/validator（最主流）
// ============================================================================
//
// go-playground/validator 是 Go 生态最广泛使用的校验库：
//   - 用 struct tag 声明规则
//   - 自动递归嵌套结构
//   - 支持跨字段比较
//   - 支持自定义验证器
//   - 性能好（基于反射 + 编译期 cache）

// 6.1 基础使用
type UserValidator struct {
	ID       int        `validate:"required,gte=1"`
	Name     string     `validate:"required,min=1,max=50"`
	Email    string     `validate:"required,email"`
	Age      *int       `validate:"omitempty,gte=0,lte=150"`
	Status   string     `validate:"required,oneof=active inactive pending"`
	Roles    []string   `validate:"required,min=1,dive,oneof=admin editor viewer"`
	Address  AddressVal `validate:"required"`
	Created  time.Time  `validate:"required"`
}

type AddressVal struct {
	Street     string `validate:"required"`
	City       string `validate:"required"`
	Country    string `validate:"required,len=2"` // ISO 国家代码
	PostalCode string `validate:"omitempty,numeric,len=6"`
}

// 6.2 跨字段校验
type PasswordChange struct {
	OldPassword string `validate:"required,min=8"`
	NewPassword string `validate:"required,min=8,nefield=OldPassword"`
	Confirm     string `validate:"required,eqfield=NewPassword"`
}

func demoValidator() {
	fmt.Println("\n--- § 6. go-playground/validator ---")

	// 创建单例（带缓存，性能好）
	validate := validator.New()

	// 6.1 校验成功
	age := 30
	good := UserValidator{
		ID: 1, Name: "Alice", Email: "alice@example.com",
		Age: &age, Status: "active", Roles: []string{"admin"},
		Address: AddressVal{Street: "长安街", City: "北京", Country: "CN", PostalCode: "100000"},
		Created: time.Now(),
	}
	if err := validate.Struct(good); err != nil {
		fmt.Printf("  good 校验失败: %v\n", err)
	} else {
		fmt.Printf("  good 校验通过\n")
	}

	// 6.2 校验失败（多错误聚合）
	bad := UserValidator{
		ID: 0, Name: "", Email: "bad-email",
		Status: "wrong", Roles: []string{"admin", "god"},
		Address: AddressVal{Street: "", City: "北京", Country: "USA", PostalCode: "abc"},
	}
	if err := validate.Struct(bad); err != nil {
		fmt.Println("  bad 校验失败（多错误聚合）:")
		for _, e := range err.(validator.ValidationErrors) {
			fmt.Printf("    - field=%s, tag=%s, param=%s, msg=%s\n",
				e.Field(), e.Tag(), e.Param(), e.Error())
		}
	}

	// 6.3 跨字段校验
	pwd := PasswordChange{
		OldPassword: "12345678",
		NewPassword: "12345678", // 与旧密码相同
		Confirm:     "different",  // 与新密码不同
	}
	if err := validate.Struct(pwd); err != nil {
		fmt.Println("  pwd 校验失败:")
		for _, e := range err.(validator.ValidationErrors) {
			fmt.Printf("    - field=%s, tag=%s, msg=%s\n",
				e.Field(), e.Tag(), e.Error())
		}
	}
}

// 6.4 自定义验证器
//
// 注册一个 "is-strong-password" 验证器
func registerStrongPassword(v *validator.Validate) {
	v.RegisterValidation("is-strong-password", func(fl validator.FieldLevel) bool {
		pwd := fl.Field().String()
		if len(pwd) < 8 {
			return false
		}
		var hasUpper, hasLower, hasDigit bool
		for _, c := range pwd {
			switch {
			case 'A' <= c && c <= 'Z':
				hasUpper = true
			case 'a' <= c && c <= 'z':
				hasLower = true
			case '0' <= c && c <= '9':
				hasDigit = true
			}
		}
		return hasUpper && hasLower && hasDigit
	})
}

type SignupWithCustom struct {
	Username string `validate:"required,alphanum,min=3,max=20"`
	Password string `validate:"required,is-strong-password"`
}

func demoCustomValidator() {
	fmt.Println("\n--- § 6.4 自定义验证器 ---")

	validate := validator.New()
	registerStrongPassword(validate)

	// 弱密码
	weak := SignupWithCustom{Username: "alice", Password: "weak"}
	if err := validate.Struct(weak); err != nil {
		fmt.Printf("  弱密码失败: %v\n", err)
	}

	// 强密码
	strong := SignupWithCustom{Username: "alice", Password: "Strong123"}
	if err := validate.Struct(strong); err != nil {
		fmt.Printf("  强密码失败（不应该发生）: %v\n", err)
	} else {
		fmt.Printf("  强密码通过\n")
	}
}

// ============================================================================
// § 7. 自定义 Validate() 方法（业务层入口）
// ============================================================================
//
// 业务层通常实现 Validate() error 方法作为统一的校验入口
// 内部可以组合 validator.Struct + 业务规则

type BusinessValidatable interface {
	Validate() error
}

type OrderValidatable struct {
	validate *validator.Validate
	ID       string  `validate:"required,uuid"`
	Customer int     `validate:"required,gte=1"`
	Total    float64 `validate:"gte=0"`
	Status   string  `validate:"required,oneof=pending paid shipped"`
	Items    []Item  `validate:"required,min=1,dive"`
}

type Item struct {
	ProductID string  `validate:"required"`
	Quantity  int     `validate:"required,gte=1,lte=1000"`
	UnitPrice float64 `validate:"gte=0"`
}

func (o *OrderValidatable) Validate() error {
	if err := o.validate.Struct(o); err != nil {
		return fmt.Errorf("order validation: %w", err)
	}
	// 业务规则
	if o.Status == "shipped" && o.Total == 0 {
		return errors.New("shipped order must have total > 0")
	}
	return nil
}

func demoBusinessValidate() {
	fmt.Println("\n--- § 7. 自定义 Validate() ---")

	validate := validator.New()
	order := &OrderValidatable{
		validate: validate,
		ID:       "550e8400-e29b-41d4-a716-446655440000",
		Customer: 1, Total: 0,
		Status: "shipped",
		Items:  []Item{{ProductID: "P-1", Quantity: 2, UnitPrice: 99}},
	}
	if err := order.Validate(); err != nil {
		fmt.Printf("  业务校验失败: %v\n", err)
	} else {
		fmt.Printf("  业务校验通过\n")
	}
}

// ============================================================================
// § 8. 嵌套结构校验
// ============================================================================
//
// validator 库自动递归校验嵌套结构
// 嵌套指针需要 deref
// 切片/数组用 dive 进入元素

type Company struct {
	Name    string  `validate:"required"`
	CEO     *Person `validate:"required"` // 指针必填
	Workers []Person `validate:"required,min=1,dive"`
}

type Person struct {
	Name  string `validate:"required"`
	Email string `validate:"required,email"`
	Age   int    `validate:"gte=0,lte=150"`
}

func demoNested() {
	fmt.Println("\n--- § 8. 嵌套结构校验 ---")

	validate := validator.New()

	// 8.1 正常
	good := Company{
		Name: "Acme",
		CEO:  &Person{Name: "Alice", Email: "alice@acme.com", Age: 45},
		Workers: []Person{
			{Name: "Bob", Email: "bob@acme.com", Age: 30},
		},
	}
	if err := validate.Struct(good); err != nil {
		fmt.Printf("  good 失败: %v\n", err)
	} else {
		fmt.Printf("  good 通过\n")
	}

	// 8.2 嵌套失败
	bad := Company{
		Name: "Acme",
		CEO:  nil, // 必填为 nil
		Workers: []Person{
			{Name: "Bob", Email: "bad-email", Age: 200}, // 多处错
		},
	}
	if err := validate.Struct(bad); err != nil {
		fmt.Println("  bad 嵌套校验失败:")
		for _, e := range err.(validator.ValidationErrors) {
			fmt.Printf("    - field=%s, tag=%s, msg=%s\n",
				e.Field(), e.Tag(), e.Error())
		}
	}
}

// ============================================================================
// § 9. 可选与零值字段
// ============================================================================
//
// Go 没有 nullable 类型，用指针 *T 表示可空
//   - 指针 + omitempty：nil 不序列化
//   - 指针 + 校验：validate:"omitempty,gte=0" 允许 nil
//   - 必填：直接 T 不用指针

// 9.1 sql.NullXxx 模式（标准库）
//   sql.NullString / sql.NullInt64 / sql.NullTime —— 显式「可空」包装
//   字段有两个：Valid bool + 实际值
//   推荐在需要「区分零值 vs 显式 null」时用

func demoOptional() {
	fmt.Println("\n--- § 9. 可选字段 ---")

	// 9.1 Age 为 nil 不报错
	validate := validator.New()
	u := UserValidator{
		ID: 1, Name: "A", Email: "a@b.com",
		Age: nil, // 指针为 nil + omitempty
		Status: "active", Roles: []string{"admin"},
		Address: AddressVal{Street: "s", City: "c", Country: "CN"},
		Created: time.Now(), // 必填，避免无关错误
	}
	if err := validate.Struct(u); err != nil {
		fmt.Printf("  optional 失败: %v\n", err)
	} else {
		fmt.Printf("  optional nil 通过（指针为 nil 不报错）\n")
	}
}

// ============================================================================
// § 10. 联合类型校验（Union by type tag）
// ============================================================================
//
// Go 1.18+ 的「类型联合约束」是编译期概念
// 运行时遇到 interface{} / any 字段时，常用「判别联合」（discriminated union）
//   - JSON 里加 "type" 字段
//   - 自定义 UnmarshalJSON 根据 type 分发

type PetUnion struct {
	Type string `json:"type"`
	Data any    `json:"data"`
}

// Cat 和 Dog 是不同结构，但都属于 Pet
type Cat struct {
	Type      string `json:"type" validate:"required,eq=cat"`
	Name      string `json:"name" validate:"required"`
	Indoor    bool   `json:"indoor"`
}

type Dog struct {
	Type  string `json:"type" validate:"required,eq=dog"`
	Name  string `json:"name" validate:"required"`
	Breed string `json:"breed" validate:"required"`
}

// 自定义 PetUnion 的 UnmarshalJSON 实现判别联合
func (p *PetUnion) UnmarshalJSON(data []byte) error {
	// 先解析出 type 字段
	var tag struct {
		Type string `json:"type"`
	}
	if err := json.Unmarshal(data, &tag); err != nil {
		return fmt.Errorf("pet: missing type field: %w", err)
	}

	// 根据 type 分发
	switch tag.Type {
	case "cat":
		var c Cat
		if err := json.Unmarshal(data, &c); err != nil {
			return err
		}
		p.Type = "cat"
		p.Data = c
	case "dog":
		var d Dog
		if err := json.Unmarshal(data, &d); err != nil {
			return err
		}
		p.Type = "dog"
		p.Data = d
	default:
		return fmt.Errorf("pet: unknown type %q", tag.Type)
	}
	return nil
}

func demoUnion() {
	fmt.Println("\n--- § 10. 判别联合 ---")

	validate := validator.New()

	for _, raw := range []string{
		`{"type": "cat", "name": "咪咪", "indoor": true}`,
		`{"type": "dog", "name": "旺财", "breed": "柴犬"}`,
		`{"type": "bird", "name": "小鸟"}`, // 不支持的类型
		`{"type": "cat", "name": ""}`,      // name 为空
	} {
		var p PetUnion
		if err := json.Unmarshal([]byte(raw), &p); err != nil {
			fmt.Printf("  parse 失败: %v\n", err)
			continue
		}
		if err := validate.Struct(p.Data); err != nil {
			fmt.Printf("  %s 校验失败: %v\n", p.Type, err)
		} else {
			fmt.Printf("  %s 校验通过: %+v\n", p.Type, p.Data)
		}
	}
}

// ============================================================================
// § 11. 校验失败处理 —— errors.Join (1.20+)
// ============================================================================

// 11.1 ★ errors.Join 把多个错误聚合成一个
func demoErrorJoin() {
	fmt.Println("\n--- § 11. errors.Join ---")

	err1 := errors.New("field A: required")
	err2 := errors.New("field B: must be positive")
	err3 := fmt.Errorf("field C: invalid format %w", err1) // 包装

	// 1.20+ 多错误聚合
	joined := errors.Join(err1, err2, err3)
	fmt.Printf("  joined: %v\n", joined)

	// 解构：errors.Is / errors.As 仍能识别
	fmt.Printf("  errors.Is(err1): %v\n", errors.Is(joined, err1))
}

// ============================================================================
// § 12. 与 data_types.go 联动
// ============================================================================
//
// 假设 data_types.go 定义了：
//   type User struct { ... } with ID UserID, Name, Email ...
//   type Order struct { ... } with Items, Status ...
//
// 这里演示：用 json + validator 做完整校验流程

// 12.1 跨包引用（data_types.go）—— 用相同的结构演示
//     实际使用时是  import "learn_types_go" 然后用 data_types.User{...}

// 这里复制一份简化结构用于演示
type UserDTO struct {
	ID    int     `json:"id" validate:"required,gte=1"`
	Name  string  `json:"name" validate:"required,min=1,max=50"`
	Email string  `json:"email" validate:"required,email"`
	Age   *int    `json:"age,omitempty" validate:"omitempty,gte=0,lte=150"`
}

type AddressDTO struct {
	Street     string `json:"street" validate:"required"`
	City       string `json:"city" validate:"required"`
	PostalCode string `json:"postal_code" validate:"omitempty,numeric,len=6"`
}

type OrderDTO struct {
	OrderID  string       `json:"order_id" validate:"required,uuid"`
	Customer UserDTO      `json:"customer" validate:"required"`
	Items    []OrderItem  `json:"items" validate:"required,min=1,dive"`
	Address  *AddressDTO  `json:"address,omitempty" validate:"omitempty"`
	Notes    string       `json:"notes,omitempty"`
}

type OrderItem struct {
	ProductID string  `json:"product_id" validate:"required"`
	Quantity  int     `json:"quantity" validate:"gte=1,lte=1000"`
	UnitPrice float64 `json:"unit_price" validate:"gte=0"`
}

func parseAndValidateOrder(rawJSON []byte) (*OrderDTO, error) {
	// 第一步：json 反序列化（隐式校验类型）
	var order OrderDTO
	if err := json.Unmarshal(rawJSON, &order); err != nil {
		return nil, fmt.Errorf("json parse: %w", err)
	}

	// 第二步：validator 校验（tag 驱动）
	validate := validator.New()
	if err := validate.Struct(order); err != nil {
		// 格式化错误：让前端好读
		var errs []string
		for _, e := range err.(validator.ValidationErrors) {
			errs = append(errs, fmt.Sprintf("field '%s' failed '%s' rule: %s",
				e.Field(), e.Tag(), e.Error()))
		}
		return nil, errors.Join(toAnySlice(errs)...)
	}

	return &order, nil
}

func demoIntegration() {
	fmt.Println("\n--- § 12. 完整链路 ---")

	// 12.1 正常 JSON
	goodJSON := []byte(`{
		"order_id": "550e8400-e29b-41d4-a716-446655440000",
		"customer": {
			"id": 1,
			"name": "Alice",
			"email": "alice@example.com",
			"age": 30
		},
		"items": [
			{"product_id": "P-100", "quantity": 2, "unit_price": 99.0}
		],
		"address": {
			"street": "长安街 1 号",
			"city": "北京",
			"postal_code": "100000"
		}
	}`)
	order, err := parseAndValidateOrder(goodJSON)
	if err != nil {
		fmt.Printf("  good 失败: %v\n", err)
	} else {
		fmt.Printf("  good 通过: %s for %s\n", order.OrderID, order.Customer.Name)
	}

	// 12.2 故意构造非法数据
	badJSON := []byte(`{
		"order_id": "not-a-uuid",
		"customer": {
			"id": 0,
			"name": "",
			"email": "bad-email",
			"age": 200
		},
		"items": [
			{"product_id": "", "quantity": 0, "unit_price": -1}
		]
	}`)
	_, err = parseAndValidateOrder(badJSON)
	if err != nil {
		fmt.Println("  bad 错误聚合:")
		for _, line := range strings.Split(err.Error(), "\n") {
			if strings.TrimSpace(line) != "" {
				fmt.Printf("    - %s\n", line)
			}
		}
	}
}

// ============================================================================
// § 13. ★ Go 独有校验机制汇总
// ============================================================================
//
// [1] json.Unmarshal 的隐式类型校验（最轻量，标准库）
// [2] validator 库的 tag 驱动校验（最主流，10k+ stars）
// [3] reflect 手写校验（最灵活，自己写规则）
// [4] 自定义 UnmarshalJSON 处理 union type（按 type 字段分发）
// [5] errors.Join（1.20+）错误聚合
// [6] 编译期强类型 + 命名类型严格区分（不需要运行时校验）

// ============================================================================
// 演示入口
// ============================================================================

func main() {
	fmt.Println("=== Go 数据校验演示 ===")

	// 编译期
	demoCompileTime()

	// json
	demoJSON()

	// type switch
	demoTypeSwitch()

	// reflect
	demoReflect()

	// validator
	demoValidator()
	demoCustomValidator()
	demoBusinessValidate()
	demoNested()
	demoOptional()
	demoUnion()
	demoErrorJoin()
	demoIntegration()

	fmt.Println("\n=== 演示完成 ===")
}