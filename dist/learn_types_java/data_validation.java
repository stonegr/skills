/**
 * ============================================================================
 *  Java 类型系统 —— 数据类型校验详解
 *  版本基线：Java 21 LTS
 *  教学目标：掌握 Java 各层级的类型/数据校验机制
 * ============================================================================
 *
 *  本文件覆盖：
 *    1.  静态类型检查（javac / IDE / Checker Framework）
 *    2.  Objects 工具类 + assert 断言
 *    3.  instanceof 模式匹配校验
 *    4.  ★ 自实现轻量 Validation 框架（模拟 Bean Validation）
 *    5.  内置约束：@NotNull / @NotBlank / @NotEmpty / @Size / @Min / @Max
 *                / @Email / @Pattern / @Range / @Past / @Future
 *    6.  ★ 自定义校验注解 + ConstraintValidator
 *    7.  嵌套结构校验（@Valid 级联）
 *    8.  Optional 字段校验
 *    9.  ★ Sealed + switch 模式匹配穷尽性校验
 *   10.  校验失败处理：异常体系 + 错误聚合 + 自定义异常
 *   11.  JSON 反序列化校验思路（Jackson + Bean Validation）
 *   12.  单元测试中的断言（JUnit 5 / AssertJ 代码片段）
 *   13.  完整实战示例：校验 User / Order / Pet / Article
 *   14.  Java 校验机制总结
 *
 *  注：本文件**不依赖** Hibernate Validator 等外部 jar，自实现的轻量框架可独立运行。
 *      工业项目推荐使用 jakarta.validation + hibernate-validator，思路一致。
 * ============================================================================
 */

import java.lang.annotation.*;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.regex.Pattern;

public class data_validation {

    // =========================================================================
    // 1. 静态类型检查
    // =========================================================================

    /*
     * ---------- 编译期类型检查 ----------
     *   javac 是 Java 的静态类型检查器，类型错误直接编译失败。
     *
     *   IDE（IntelliJ IDEA、Eclipse）会做增量检查 + 实时提示。
     *
     *   注解处理器（Annotation Processor）在编译期运行，可做代码生成与检查。
     *   例：Lombok、MapStruct、Checker Framework。
     *
     * ---------- Checker Framework（可选强类型检查）----------
     *   引入 org.checkerframework:checker:
     *     @NonNull String s = null;   // 编译错误
     *     @Nullable String s = null;  // OK
     *   适合大型项目做空安全审计。
     *
     * ---------- Maven/Gradle 配置示例 ----------
     *   <!-- jakarta.validation -->
     *   <dependency>
     *     <groupId>jakarta.validation</groupId>
     *     <artifactId>jakarta.validation-api</artifactId>
     *     <version>3.0.2</version>
     *   </dependency>
     *   <!-- hibernate-validator -->
     *   <dependency>
     *     <groupId>org.hibernate.validator</groupId>
     *     <artifactId>hibernate-validator</artifactId>
     *     <version>8.0.1.Final</version>
     *   </dependency>
     *
     *   import jakarta.validation.constraints.*;
     *   import jakarta.validation.Valid;
     *   import jakarta.validation.ConstraintViolation;
     *   import jakarta.validation.Validation;
     *   import jakarta.validation.Validator;
     *   import jakarta.validation.ValidatorFactory;
     */

    public static void staticTypeCheckingDemo() {
        // ---------- 编译期拦截 ----------
        // int x = "hello";           // 编译错误：不兼容的类型
        // List<String> list = new ArrayList<Integer>();   // 编译错误
        // String s = null; int n = s.length();           // 可能空指针（普通 javac 不查）

        // ---------- 启用 -Xlint:unchecked 检查泛型 ----------
        List rawList = new ArrayList();           // 原始类型（raw type），不推荐
        rawList.add("string");
        rawList.add(42);
        // 编译警告：[unchecked] 对原始类型 ArrayList 的成员调用...

        // ---------- 显式类型 vs var 的取舍 ----------
        var inferred = List.of(1, 2, 3);          // List<Integer>
        List<Integer> explicit = List.of(1, 2, 3);
        // 两者类型相同；var 仅减少样板代码，不影响类型检查

        System.out.println("静态检查演示完成。rawList = " + rawList + ", inferred = " + inferred);
    }


    // =========================================================================
    // 2. Objects 工具类 + assert 断言
    // =========================================================================

    public static void objectsAndAssert() {
        // ---------- Objects.requireNonNull ----------
        String name = "Java";
        String safe = Objects.requireNonNull(name, "name 不能为空");
        System.out.println("safe = " + safe);

        // ---------- Objects.requireNonNullElse / requireNonNullElseGet ----------
        String maybeNull = null;
        String fallback = Objects.requireNonNullElse(maybeNull, "DEFAULT");
        System.out.println("fallback = " + fallback);

        // ---------- Objects.isNull / nonNull ----------
        System.out.println("isNull(null) = " + Objects.isNull(null));
        System.out.println("nonNull(null) = " + Objects.nonNull(null));

        // ---------- Objects.equals（null 安全）----------
        System.out.println("equals = " + Objects.equals(null, null));   // true

        // ---------- Objects.hash ----------
        int hash = Objects.hash("a", 1, true);
        System.out.println("hash = " + hash);

        // ---------- assert 断言（需 -ea 启用，否则被忽略）----------
        // java -ea data_validation
        assert name != null : "name 必须非空";
        assert 1 + 1 == 2 : "数学崩了";

        System.out.println("Objects + assert 演示完成");
    }


    // =========================================================================
    // 3. instanceof 模式匹配校验
    // =========================================================================

    public static String describeObject(Object obj) {
        // ★ Java 16+：instanceof 自动绑定变量，简化类型守卫
        if (obj instanceof String s) {
            return "字符串长度: " + s.length();
        }
        if (obj instanceof Integer i && i > 0) {
            return "正整数: " + i;
        }
        if (obj instanceof List<?> list) {
            return "集合大小: " + list.size();
        }
        if (obj == null) {
            return "null";
        }
        return "未知类型: " + obj.getClass().getSimpleName();
    }

    public static void instanceofDemo() {
        System.out.println(describeObject("hello"));
        System.out.println(describeObject(42));
        System.out.println(describeObject(List.of(1, 2, 3)));
        System.out.println(describeObject(null));
    }


    // =========================================================================
    // 4. ★ 自实现轻量 Validation 框架（模拟 Bean Validation）
    // =========================================================================

    // ------------------- 4.1 约束注解 -------------------

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD, ElementType.PARAMETER})
    public @interface NotNull {
        String message() default "不能为 null";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface NotBlank {
        String message() default "不能为空字符串";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface NotEmpty {
        String message() default "不能为空";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface Size {
        int min() default 0;
        int max() default Integer.MAX_VALUE;
        String message() default "长度不符合要求";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface Min {
        long value();
        String message() default "不能小于指定值";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface Max {
        long value();
        String message() default "不能大于指定值";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface Range {
        long min();
        long max();
        String message() default "不在范围内";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface Email {
        String message() default "邮箱格式不合法";
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface Regex {
        String pattern();
        String message() default "正则不匹配";
    }

    /** 级联校验标记：触发嵌套对象的校验 */
    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface Valid {}

    // ------------------- 4.2 自定义校验注解示例 -------------------

    /** 自定义：合法手机号（中国大陆） */
    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface Phone {
        String message() default "手机号格式不合法";
    }

    /** 自定义：日期不能在过去 */
    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface Future {
        String message() default "必须是未来日期";
    }


    // ------------------- 4.3 校验器体系 -------------------

    /** 单条违规记录 */
    public static record ConstraintViolation(
        String objectName,
        String fieldPath,
        String message
    ) {
        @Override
        public String toString() {
            return objectName + "." + fieldPath + ": " + message;
        }
    }

    /** 校验异常：携带所有违规记录 */
    public static class ValidationException extends RuntimeException {
        private final List<ConstraintViolation> violations;

        public ValidationException(List<ConstraintViolation> violations) {
            super(formatMessage(violations));
            this.violations = violations;
        }

        public List<ConstraintViolation> violations() { return violations; }

        private static String formatMessage(List<ConstraintViolation> v) {
            StringBuilder sb = new StringBuilder("校验失败，共 " + v.size() + " 条错误：\n");
            for (ConstraintViolation cv : v) sb.append(" - ").append(cv).append("\n");
            return sb.toString();
        }
    }

    /** 约束校验器接口 */
    @FunctionalInterface
    public interface ConstraintValidator<A extends Annotation, T> {
        boolean isValid(T value, A annotation);
    }


    // ------------------- 4.4 校验引擎 -------------------

    public static class ValidationEngine {
        /** 内置校验器注册表 */
        private static final Map<Class<? extends Annotation>, ConstraintValidator<?, ?>> validators = new HashMap<>();

        static {
            register(NotNull.class,    (ConstraintValidator<NotNull, Object>)
                (v, a) -> v != null);
            register(NotBlank.class,   (ConstraintValidator<NotBlank, String>)
                (v, a) -> v != null && !v.trim().isEmpty());
            register(NotEmpty.class,   (ConstraintValidator<NotEmpty, Object>)
                (v, a) -> {
                    if (v == null) return false;
                    if (v instanceof CharSequence cs) return cs.length() > 0;
                    if (v instanceof Collection<?> c)  return !c.isEmpty();
                    if (v instanceof Map<?, ?> m)      return !m.isEmpty();
                    if (v.getClass().isArray())        return ((Object[]) v).length > 0;
                    return true;
                });
            register(Size.class,       (ConstraintValidator<Size, Object>)
                (v, a) -> {
                    if (v == null) return true;
                    int len = 0;
                    if (v instanceof CharSequence cs) len = cs.length();
                    else if (v instanceof Collection<?> c) len = c.size();
                    else if (v instanceof Map<?, ?> m) len = m.size();
                    else if (v.getClass().isArray()) len = ((Object[]) v).length;
                    else return true;
                    return len >= a.min() && len <= a.max();
                });
            register(Min.class,        (ConstraintValidator<Min, Number>)
                (v, a) -> v == null || v.longValue() >= a.value());
            register(Max.class,        (ConstraintValidator<Max, Number>)
                (v, a) -> v == null || v.longValue() <= a.value());
            register(Range.class,      (ConstraintValidator<Range, Number>)
                (v, a) -> v == null || (v.longValue() >= a.min() && v.longValue() <= a.max()));
            register(Email.class,      (ConstraintValidator<Email, String>)
                (v, a) -> v == null || Pattern.matches("^[\\w.+-]+@[\\w-]+\\.[\\w.-]+$", v));
            register(Regex.class,      (ConstraintValidator<Regex, String>)
                (v, a) -> v == null || Pattern.matches(a.pattern(), v));
            register(Phone.class,      (ConstraintValidator<Phone, String>)
                (v, a) -> v == null || Pattern.matches("^1[3-9]\\d{9}$", v));
            register(Future.class,     (ConstraintValidator<Future, LocalDate>)
                (v, a) -> v == null || !v.isBefore(LocalDate.now()));
        }

        public static <A extends Annotation, T> void register(
                Class<A> annoClass, ConstraintValidator<A, T> validator) {
            validators.put(annoClass, validator);
        }

        /**
         * 校验对象，返回违规列表（不会抛异常）。
         */
        public static <T> List<ConstraintViolation> validate(T obj) {
            return validate(obj, obj == null ? "null" : obj.getClass().getSimpleName());
        }

        public static <T> List<ConstraintViolation> validate(T obj, String objectName) {
            List<ConstraintViolation> violations = new ArrayList<>();
            if (obj == null) {
                violations.add(new ConstraintViolation(objectName, "", "对象不能为 null"));
                return violations;
            }

            Class<?> clazz = obj.getClass();
            for (Field field : getAllFields(clazz)) {
                field.setAccessible(true);
                Object value;
                try {
                    value = field.get(obj);
                } catch (IllegalAccessException e) {
                    continue;
                }

                // ---------- 收集该字段的所有约束违规 ----------
                for (Annotation anno : field.getAnnotations()) {
                    ConstraintValidator validator = validators.get(anno.annotationType());
                    if (validator == null) continue;
                    boolean valid = validator.isValid(value, anno);
                    if (!valid) {
                        String msg = invokeMessage(anno, field);
                        violations.add(new ConstraintViolation(objectName, field.getName(), msg));
                    }
                }

                // ---------- @Valid 级联校验 ----------
                if (field.isAnnotationPresent(Valid.class)) {
                    if (value instanceof Collection<?> coll) {
                        int idx = 0;
                        for (Object item : coll) {
                            violations.addAll(validate(item,
                                objectName + "." + field.getName() + "[" + (idx++) + "]"));
                        }
                    } else if (value instanceof Map<?, ?> map) {
                        int idx = 0;
                        for (Map.Entry<?, ?> entry : map.entrySet()) {
                            violations.addAll(validate(entry.getValue(),
                                objectName + "." + field.getName() + "(" + entry.getKey() + ")"));
                        }
                    } else {
                        violations.addAll(validate(value,
                            objectName + "." + field.getName()));
                    }
                }
            }
            return violations;
        }

        /** 校验并抛异常 */
        public static <T> void validateAndThrow(T obj) {
            List<ConstraintViolation> violations = validate(obj);
            if (!violations.isEmpty()) {
                throw new ValidationException(violations);
            }
        }

        private static List<Field> getAllFields(Class<?> clazz) {
            List<Field> fields = new ArrayList<>();
            while (clazz != null && clazz != Object.class) {
                Collections.addAll(fields, clazz.getDeclaredFields());
                clazz = clazz.getSuperclass();
            }
            return fields;
        }

        /** 调用 message() 方法拿到错误消息 */
        private static String invokeMessage(Annotation anno, Field field) {
            try {
                return (String) anno.annotationType().getMethod("message").invoke(anno);
            } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
                return "校验失败";
            }
        }
    }


    // =========================================================================
    // 5. ★ 自定义校验注解 + ConstraintValidator（进阶）
    // =========================================================================

    /** 自定义：字符串必须是大写 */
    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD})
    public @interface UpperCase {
        String message() default "必须全部大写";
    }

    static {
        ValidationEngine.register(UpperCase.class,
            (ConstraintValidator<UpperCase, String>)
                (v, a) -> v == null || v.equals(v.toUpperCase()));
    }


    // =========================================================================
    // 6. 实战模型 —— 用于演示校验
    // =========================================================================

    public enum Role { ADMIN, EDITOR, VIEWER }

    public sealed interface PaymentMethod permits CardPayment, AlipayPayment, BankTransferPayment {}
    public record CardPayment(String last4, String brand) implements PaymentMethod {}
    public record AlipayPayment(String account) implements PaymentMethod {}
    public record BankTransferPayment(String bank, String account) implements PaymentMethod {}

    /** 带约束注解的地址 */
    public static class Address {
        @NotBlank(message = "国家不能为空")
        private String country;

        @NotBlank(message = "城市不能为空")
        private String city;

        @Size(min = 6, max = 6, message = "邮编必须 6 位")
        private String zip;

        public Address(String country, String city, String zip) {
            this.country = country;
            this.city = city;
            this.zip = zip;
        }

        public String getCountry() { return country; }
        public String getCity() { return city; }
        public String getZip() { return zip; }
    }

    /** 带约束注解的用户模型 */
    public static class User {
        @NotNull(message = "id 必填")
        @Min(value = 1, message = "id 必须为正数")
        private Long id;

        @NotBlank(message = "用户名不能为空")
        @Size(min = 3, max = 20, message = "用户名长度必须在 3~20 之间")
        @UpperCase(message = "用户名必须大写")
        private String username;

        @NotBlank(message = "邮箱必填")
        @Email(message = "邮箱格式不合法")
        private String email;

        @Phone(message = "手机号格式不合法")
        private String phone;                  // 可选字段（无 @NotNull）

        @NotEmpty(message = "角色不能为空")
        private List<Role> roles = new ArrayList<>();

        @Valid                                  // 级联校验
        private Address address;                // 可空（无 @NotNull）

        public User(Long id, String username, String email, String phone,
                    List<Role> roles, Address address) {
            this.id = id;
            this.username = username;
            this.email = email;
            this.phone = phone;
            this.roles = roles;
            this.address = address;
        }

        public Long getId() { return id; }
        public String getUsername() { return username; }
        public String getEmail() { return email; }
        public String getPhone() { return phone; }
        public List<Role> getRoles() { return roles; }
        public Address getAddress() { return address; }
    }

    /** 订单模型 */
    public static class Order {
        @NotBlank(message = "订单号必填")
        private String orderId;

        @NotNull @Min(1)
        private Long userId;

        @NotEmpty(message = "订单项不能为空")
        @Valid                                  // 校验 List 内每个 OrderItem
        private List<OrderItem> items;

        @Range(min = 0, max = 1_000_000, message = "总金额超限")
        private Double totalAmount;

        public Order(String orderId, Long userId, List<OrderItem> items, Double totalAmount) {
            this.orderId = orderId;
            this.userId = userId;
            this.items = items;
            this.totalAmount = totalAmount;
        }

        public String getOrderId() { return orderId; }
        public Long getUserId() { return userId; }
        public List<OrderItem> getItems() { return items; }
        public Double getTotalAmount() { return totalAmount; }
    }

    public static class OrderItem {
        @NotBlank
        private String productId;

        @Min(value = 1, message = "数量必须 >= 1")
        private Integer quantity;

        @Range(min = 0, max = 999_999)
        private Double unitPrice;

        public OrderItem(String productId, Integer quantity, Double unitPrice) {
            this.productId = productId;
            this.quantity = quantity;
            this.unitPrice = unitPrice;
        }

        public String getProductId() { return productId; }
        public Integer getQuantity() { return quantity; }
        public Double getUnitPrice() { return unitPrice; }
    }

    /** 文章模型 */
    public static class Article {
        @NotBlank
        @Size(max = 100)
        private String title;

        @NotBlank
        @Email
        private String authorEmail;

        @Future(message = "发布日期必须是未来")
        private LocalDate publishDate;

        @NotEmpty
        private List<String> tags;

        public Article(String title, String authorEmail, LocalDate publishDate, List<String> tags) {
            this.title = title;
            this.authorEmail = authorEmail;
            this.publishDate = publishDate;
            this.tags = tags;
        }

        public String getTitle() { return title; }
        public String getAuthorEmail() { return authorEmail; }
        public LocalDate getPublishDate() { return publishDate; }
        public List<String> getTags() { return tags; }
    }


    // =========================================================================
    // 7. 校验失败处理：异常体系 + 错误聚合
    // =========================================================================

    /**
     * 推荐模式：
     *   1) 校验方法返回 List<ConstraintViolation>，由调用方决定如何处理。
     *   2) 或封装 validateAndThrow() 工具方法统一抛 ValidationException。
     */
    public static void validationFailureHandling() {
        // ---------- 场景 1：合法数据 ----------
        Address addr = new Address("中国", "深圳", "518000");
        User good = new User(1L, "ALICE", "alice@example.com", "13800138000",
            List.of(Role.ADMIN), addr);
        List<ConstraintViolation> violations = ValidationEngine.validate(good);
        System.out.println("合法数据校验结果: violations = " + violations.size());

        // ---------- 场景 2：多个字段都错（错误聚合）----------
        Address badAddr = new Address("", "深圳", "abc");    // country 空, zip 长度错
        User bad = new User(-1L, "alice", "not-an-email", "1234",
            new ArrayList<>(), badAddr);                      // 多个违规
        List<ConstraintViolation> badViolations = ValidationEngine.validate(bad);
        System.out.println("\n错误聚合演示（" + badViolations.size() + " 条错误）：");
        badViolations.forEach(v -> System.out.println("  - " + v));

        // ---------- 场景 3：抛 ValidationException ----------
        try {
            ValidationEngine.validateAndThrow(bad);
        } catch (ValidationException e) {
            System.out.println("\n抛 ValidationException:");
            System.out.println(e.getMessage());
            System.out.println("违规数 = " + e.violations().size());
        }
    }


    // =========================================================================
    // 8. Optional 字段校验
    // =========================================================================

    public static class Profile {
        @NotBlank
        private String username;

        // 可选字段：用 Optional 显式表达可空语义
        // 校验时只需 Optional.isPresent() 后校验内部值
        private Optional<String> bio = Optional.empty();

        public Profile(String username, Optional<String> bio) {
            this.username = username;
            this.bio = bio;
        }

        public String getUsername() { return username; }
        public Optional<String> getBio() { return bio; }
    }

    public static void optionalValidation() {
        // ---------- 校验 Optional 内的值 ----------
        Profile p1 = new Profile("alice", Optional.of("I love Java"));
        Profile p2 = new Profile("bob", Optional.empty());

        // 自定义校验：Optional 不为空时校验内容长度
        for (Profile p : List.of(p1, p2)) {
            List<ConstraintViolation> violations = ValidationEngine.validate(p);
            // 业务级 Optional 校验
            if (p.getBio().isPresent() && p.getBio().get().length() > 50) {
                violations.add(new ConstraintViolation("Profile", "bio", "简介过长"));
            }
            System.out.println(p.getUsername() + " 校验结果: " + violations.size() + " 条错误");
        }
    }


    // =========================================================================
    // 9. ★ Sealed + switch 模式匹配穷尽性校验
    // =========================================================================

    /**
     * 配合 sealed PaymentMethod，编译器保证所有分支被处理（穷尽性检查）。
     * 新增 PaymentMethod 子类后，未更新的 switch 会编译失败 —— 这是「编译期校验」。
     */
    public static String validatePayment(PaymentMethod pm) {
        // 编译器验证：所有 sealed 子类都被处理
        return switch (pm) {
            case CardPayment c -> {
                if (c.last4() == null || c.last4().length() != 4)
                    yield "信用卡号末四位不合法";
                yield "信用卡校验通过";
            }
            case AlipayPayment a -> {
                if (a.account() == null || a.account().isBlank())
                    yield "支付宝账号不能为空";
                yield "支付宝校验通过";
            }
            case BankTransferPayment b -> {
                if (b.bank() == null || b.account() == null)
                    yield "银行转账信息不完整";
                yield "银行转账校验通过";
            }
        };
    }

    public static void sealedExhaustiveCheck() {
        System.out.println("\nSealed 穷尽校验：");
        System.out.println(validatePayment(new CardPayment("1234", "VISA")));
        System.out.println(validatePayment(new AlipayPayment("user@example.com")));
        System.out.println(validatePayment(new BankTransferPayment("ICBC", "123456")));
    }


    // =========================================================================
    // 10. JSON 反序列化校验思路（Jackson + Bean Validation）
    // =========================================================================

    /*
     * ---------- 方案 1：Jackson Bean Validation 集成 ----------
     *
     *   @JsonProperty("email")
     *   @NotBlank @Email
     *   private String email;
     *
     *   // 触发校验：构造 ObjectMapper + Validator
     *   ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
     *   Validator validator = factory.getValidator();
     *   ObjectMapper mapper = new ObjectMapper()
     *       .registerModule(new JakartaValidationModule(validator));
     *
     *   UserDto dto = mapper.readValue(json, UserDto.class);
     *   // 反序列化失败 → JsonMappingException
     *   // 校验失败 → ConstraintViolationException
     *
     *
     * ---------- 方案 2：手动反序列化 + 校验 ----------
     *
     *   JsonNode root = mapper.readTree(json);
     *   if (!root.hasNonNull("email")) throw new ValidationException(...);
     *   String email = root.get("email").asText();
     *   if (!email.matches("^.+@.+$")) throw new ValidationException(...);
     *   ...
     *
     *
     * ---------- 方案 3：JSON Schema 校验 ----------
     *
     *   使用 networknt/json-schema-validator：
     *     JsonSchemaFactory factory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V202012);
     *     JsonSchema schema = factory.getSchema(schemaJson);
     *     Set<ValidationMessage> errors = schema.validate(jsonNode);
     */

    public static void jsonValidationConcept() {
        System.out.println("\nJSON 反序列化校验：见源码注释 + Jackson/Bean Validation");
    }


    // =========================================================================
    // 11. 单元测试中的断言（JUnit 5 / AssertJ 代码片段）
    // =========================================================================

    /*
     * ---------- JUnit 5 ----------
     *
     * import org.junit.jupiter.api.Test;
     * import static org.junit.jupiter.api.Assertions.*;
     *
     * class UserValidationTest {
     *
     *     @Test
     *     void shouldPassForValidUser() {
     *         User user = new User(1L, "ALICE", "alice@example.com", "13800138000",
     *                              List.of(Role.ADMIN), new Address("中国", "深圳", "518000"));
     *         List<ConstraintViolation> violations = ValidationEngine.validate(user);
     *         assertEquals(0, violations.size());
     *     }
     *
     *     @Test
     *     void shouldFailForBlankUsername() {
     *         User user = new User(1L, "", "alice@example.com", null,
     *                              List.of(Role.ADMIN), null);
     *         List<ConstraintViolation> violations = ValidationEngine.validate(user);
     *         assertFalse(violations.isEmpty());
     *         assertTrue(violations.stream()
     *             .anyMatch(v -> v.fieldPath().equals("username")));
     *     }
     *
     *     @Test
     *     void shouldThrowValidationException() {
     *         User user = new User(-1L, "abc", "bad", null, new ArrayList<>(), null);
     *         ValidationException ex = assertThrows(ValidationException.class,
     *             () -> ValidationEngine.validateAndThrow(user));
     *         assertTrue(ex.violations().size() >= 3);
     *     }
     *
     *     @Test
     *     void shouldAggregateAllErrors() {
     *         User user = new User(0L, "", "bad", "1234", new ArrayList<>(),
     *             new Address("", "深圳", "123"));
     *         List<ConstraintViolation> violations = ValidationEngine.validate(user);
     *         assertAll(
     *             () -> assertEquals(8, violations.size()),  // 一次性断言
     *             () -> assertTrue(violations.stream()
     *                 .anyMatch(v -> v.fieldPath().equals("username"))),
     *             () -> assertTrue(violations.stream()
     *                 .anyMatch(v -> v.fieldPath().equals("address.country")))
     *         );
     *     }
     * }
     *
     *
     * ---------- AssertJ 流式断言 ----------
     *
     * import static org.assertj.core.api.Assertions.*;
     *
     * assertThat(violations)
     *     .hasSize(3)
     *     .extracting(ConstraintViolation::fieldPath)
     *     .containsExactlyInAnyOrder("username", "email", "phone");
     *
     * assertThatThrownBy(() -> ValidationEngine.validateAndThrow(badUser))
     *     .isInstanceOf(ValidationException.class)
     *     .hasMessageContaining("用户名");
     */

    public static void testAssertionConcept() {
        System.out.println("\n单元测试断言：见源码注释（JUnit 5 / AssertJ）");
    }


    // =========================================================================
    // 12. 完整实战示例：从原始数据 → 校验 → 转换
    // =========================================================================

    public static void realWorldValidation() {
        System.out.println("\n========== 完整实战校验演示 ==========");

        // ---------- 场景 1：合法 User ----------
        Address addr = new Address("中国", "深圳", "518000");
        User goodUser = new User(
            1L, "ALICE", "alice@example.com", "13800138000",
            List.of(Role.ADMIN, Role.EDITOR), addr
        );
        runValidation("合法 User", goodUser);

        // ---------- 场景 2：多字段错误的 User ----------
        Address badAddr = new Address("", "深圳", "abc");
        User badUser = new User(
            -1L, "alice", "not-an-email", "1234",
            new ArrayList<>(),                  // 空角色列表
            badAddr                             // country 空、zip 错
        );
        runValidation("多字段错误 User", badUser);

        // ---------- 场景 3：合法 Order ----------
        Order goodOrder = new Order(
            "ORD-001", 1L,
            List.of(new OrderItem("P001", 2, 99.0), new OrderItem("P002", 1, 199.0)),
            397.0
        );
        runValidation("合法 Order", goodOrder);

        // ---------- 场景 4：非法 Order ----------
        Order badOrder = new Order(
            "", 0L,                             // 订单号空 + userId 非正
            new ArrayList<>(),                  // 空订单项
            -10.0                               // 负金额
        );
        runValidation("非法 Order", badOrder);

        // ---------- 场景 5：合法 Article ----------
        Article goodArticle = new Article(
            "Java 21 新特性", "author@example.com",
            LocalDate.now().plusDays(7),
            List.of("java", "lts")
        );
        runValidation("合法 Article", goodArticle);

        // ---------- 场景 6：发布日期已过 ----------
        Article badArticle = new Article(
            "Java", "author@example.com",
            LocalDate.now().minusDays(1),       // 过期日期
            List.of("java")
        );
        runValidation("过期 Article", badArticle);
    }

    /** 统一处理：校验 + 报告 */
    private static void runValidation(String label, Object obj) {
        List<ConstraintViolation> violations = ValidationEngine.validate(obj);
        System.out.println("\n[" + label + "] 校验结果: " + violations.size() + " 条错误");
        if (violations.isEmpty()) {
            System.out.println("  ✓ 通过");
        } else {
            violations.forEach(v -> System.out.println("  ✗ " + v));
        }
    }


    // =========================================================================
    // 13. Java 校验机制总结
    // =========================================================================

    /*
     *  ★ 编译期校验
     *    - javac：基础类型检查
     *    - IDE：实时增量检查
     *    - Checker Framework：可空性 / 不变性等深度检查
     *    - 注解处理器：编译期生成代码 + 检查
     *
     *  ★ 运行期校验
     *    - Objects.requireNonNull 等工具类
     *    - assert 断言（需 -ea）
     *    - instanceof / switch 模式匹配（穷尽性 + 类型守卫）
     *    - Bean Validation（JSR 380 / Jakarta Validation）工业级方案
     *    - 自实现 ValidationEngine（本文件演示的轻量框架）
     *    - JSON Schema 校验（networknt/json-schema-validator）
     *
     *  ★ 测试期校验
     *    - JUnit 5：assertEquals / assertThrows / assertAll
     *    - AssertJ：流式断言，可读性强
     *    - Mockito：模拟依赖，验证交互
     *
     *  ★ 错误处理建议
     *    - 业务校验失败抛 ValidationException，携带所有违规记录
     *    - Controller 层捕获后转为 400 Bad Request + 结构化错误响应
     *    - 不要只抛 IllegalArgumentException，会丢失多条错误信息
     */


    // =========================================================================
    // 主入口
    // =========================================================================

    public static void main(String[] args) {
        System.out.println("========== Java 类型校验演示 ==========\n");

        System.out.println("--- 1) 静态类型检查（编译期） ---");
        staticTypeCheckingDemo();

        System.out.println("\n--- 2) Objects + assert ---");
        objectsAndAssert();

        System.out.println("\n--- 3) instanceof 模式匹配校验 ---");
        instanceofDemo();

        System.out.println("\n--- 4) 校验失败处理 ---");
        validationFailureHandling();

        System.out.println("\n--- 5) Optional 字段校验 ---");
        optionalValidation();

        System.out.println("\n--- 6) Sealed 穷尽校验 ---");
        sealedExhaustiveCheck();

        System.out.println("\n--- 7) JSON 校验思路 ---");
        jsonValidationConcept();

        System.out.println("\n--- 8) 测试断言思路 ---");
        testAssertionConcept();

        System.out.println("\n--- 9) 完整实战校验 ---");
        realWorldValidation();

        System.out.println("\n========== 演示结束 ==========");
    }
}