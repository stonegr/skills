/**
 * ============================================================================
 *  Java 类型系统 —— 数据类型定义详解
 *  版本基线：Java 21 LTS（涵盖 Java 5 ~ 21 关键特性）
 *  教学目标：系统掌握 Java 各种数据类型的定义、用法与适用场景
 * ============================================================================
 *
 *  本文件覆盖：
 *    1.  基础类型（Primitive Types）
 *    2.  包装类型（Wrapper Types）与自动装箱
 *    3.  数组（Array）
 *    4.  容器类型（Collection Framework）
 *    5.  枚举（enum）
 *    6.  类与对象（class）
 *    7.  抽象类与接口
 *    8.  嵌套类与内部类
 *    9.  Record（Java 16 正式）
 *   10.  Sealed Class / Interface（Java 17 正式）
 *   11.  泛型（Generics）
 *   12. Optional 与空值处理
 *   13. 注解（Annotation）
 *   14. 类型推断（var, <>, pattern var）
 *   15. 类型转换
 *   16. Pattern Matching 模式匹配（Java 16 ~ 21）
 *   17. Switch 表达式（Java 14 正式）
 *   18. Text Blocks 文本块（Java 15 正式）
 *   19. Java 独有特色总结
 *   20. 完整实战模型（User / Order / Pet / Article）
 *
 *  注：所有示例可在 Java 21 环境下直接编译运行。
 * ============================================================================
 */

import java.lang.annotation.ElementType;
import java.lang.annotation.Repeatable;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class data_types {

    // =========================================================================
    // 1. 基础类型（Primitive Types）—— Java 1.0
    // =========================================================================

    /**
     * Java 有 8 种基础类型，全部小写。它们不是对象，直接存值，效率高于包装类型。
     *
     *   整数类型：byte(1)  short(2)  int(4)  long(8)
     *   浮点类型：float(4)  double(8)
     *   字符类型：char(2)   —— 存储 UTF-16 码元
     *   布尔类型：boolean(1) —— 大小由 JVM 决定
     */
    public static void primitiveTypes() {
        // ---------- 字面量 ----------
        byte b = 127;                        // -128 ~ 127
        short s = 32_767;                    // -32768 ~ 32767；下划线增强可读性（Java 7+）
        int i = 2_147_483_647;               // 默认整数类型
        long l = 9_223_372_036_854_775_807L; // 必须加 L 后缀
        float f = 3.14F;                     // 必须加 F 后缀，否则按 double 处理
        double d = 3.141592653589793;        // 默认浮点类型
        boolean flag = true;
        char c = 'A';                        // 单引号；也支持 Unicode：'\u4e2d'

        System.out.println("byte: " + b);
        System.out.println("long: " + l);
        System.out.println("double: " + d);

        // ---------- 默认值（成员变量）----------
        // 局部变量必须显式初始化，成员变量有默认值
        // 数值类型 → 0；boolean → false；char → '\u0000'；引用类型 → null
    }

    /**
     * 类型提升规则：
     *   byte / short / char → int → long → float → double
     *   表达式中若有 double，结果必为 double；若无 double，有 float 则为 float。
     */
    public static void typePromotion() {
        byte a = 10;
        byte b = 20;
        // byte c = a + b;          // 编译错误：a + b 自动提升为 int
        int c = a + b;              // 正确
        System.out.println("a + b = " + c);
    }


    // =========================================================================
    // 2. 包装类型（Wrapper Types）—— Java 5 自动装箱 / 拆箱
    // =========================================================================

    /**
     * 每个基础类型都有对应包装类，使基础类型也能参与面向对象操作（如放入集合）。
     *
     *   int → Integer, long → Long, double → Double, ...
     *   char → Character, boolean → Boolean（这两个类名不完全对应）
     *
     *  ★ Java 特色：自动装箱（Auto-boxing）/ 拆箱（Unboxing）
     *    编译器自动完成 Integer.valueOf(int) / intValue() 的转换。
     *    陷阱：包装类型可 null，拆箱时易抛 NullPointerException。
     */
    public static void wrapperTypes() {
        // ---------- 自动装箱 ----------
        Integer boxed = 42;                 // Integer.valueOf(42)
        int unboxed = boxed;                // boxed.intValue()
        System.out.println("boxed = " + boxed + ", unboxed = " + unboxed);

        // ---------- 缓存陷阱（-128 ~ 127 的 Integer 缓存）----------
        Integer a = 127;
        Integer b = 127;
        System.out.println("127 == 127? " + (a == b));      // true（同一对象）

        Integer c = 128;
        Integer d = 128;
        System.out.println("128 == 128? " + (c == d));      // false（新对象）
        System.out.println("128.equals(128)? " + c.equals(d)); // true（值比较）

        // ---------- 比较的正确姿势 ----------
        Integer x = 1000;
        Integer y = 1000;
        System.out.println("x.equals(y) = " + x.equals(y)); // 永远用 equals 比较值

        // ---------- 空指针陷阱 ----------
        Integer maybeNull = null;
        try {
            int bad = maybeNull;                            // 自动拆箱 null → NPE
        } catch (NullPointerException e) {
            System.out.println("拆箱 null 抛 NPE");
        }
    }


    // =========================================================================
    // 3. 数组（Array）
    // =========================================================================

    /**
     * 数组是固定长度的同类型容器；长度不可变，越界抛 ArrayIndexOutOfBoundsException。
     * ★ Java 数组是协变的（Covariant）：Object[] objArr = new String[10] 合法，
     *   但运行期会抛 ArrayStoreException。
     */
    public static void arrays() {
        // ---------- 声明方式 ----------
        int[] arr1 = new int[5];                  // 默认填充 0
        int[] arr2 = {1, 2, 3, 4, 5};
        int[] arr3 = new int[]{1, 2, 3, 4, 5};

        // ---------- 多维数组（数组的数组，可不规则）----------
        int[][] matrix = {
            {1, 2, 3},
            {4, 5},
            {6, 7, 8, 9}
        };
        System.out.println("matrix[1][1] = " + matrix[1][1]);  // 5

        // ---------- 数组协变陷阱 ----------
        Object[] objArr = new String[3];
        objArr[0] = "hello";                              // OK
        try {
            objArr[1] = 42;                               // 运行期抛 ArrayStoreException
        } catch (ArrayStoreException e) {
            System.out.println("数组协变运行期检查");
        }

        // ---------- Arrays 工具类 ----------
        System.out.println("arr2 = " + Arrays.toString(arr2));
        Arrays.sort(arr2);                                // 就地排序
        int idx = Arrays.binarySearch(arr2, 3);
        System.out.println("3 的索引 = " + idx);
    }


    // =========================================================================
    // 4. 容器类型（Collection Framework）
    // =========================================================================

    /**
     * 体系总览：
     *
     *   Iterable
     *   └── Collection
     *       ├── List（有序可重复）：ArrayList, LinkedList, Vector, Stack
     *       ├── Set（无序不可重复）：HashSet, LinkedHashSet, TreeSet
     *       └── Queue（队列）：LinkedList, PriorityQueue, ArrayDeque
     *
     *   Map（独立体系）：HashMap, LinkedHashMap, TreeMap, Hashtable, ConcurrentHashMap
     *
     *  ★ Java 9+ 引入不可变集合工厂：List.of / Set.of / Map.of（更省内存、线程安全）。
     */
    public static void collections() {
        // ---------- List ----------
        List<String> arrayList = new ArrayList<>(List.of("a", "b", "c"));
        arrayList.add("d");
        arrayList.remove(0);
        System.out.println("ArrayList: " + arrayList);

        // ---------- Set ----------
        Set<Integer> hashSet = new HashSet<>(List.of(1, 2, 2, 3, 3, 3));
        System.out.println("HashSet: " + hashSet);                  // [1, 2, 3]

        Set<String> linkedHashSet = new LinkedHashSet<>(List.of("c", "a", "b"));
        System.out.println("LinkedHashSet: " + linkedHashSet);      // [c, a, b] 保持插入序

        Set<Integer> treeSet = new TreeSet<>(List.of(3, 1, 2));
        System.out.println("TreeSet: " + treeSet);                  // [1, 2, 3] 自动排序

        // ---------- Map ----------
        Map<String, Integer> hashMap = new HashMap<>();
        hashMap.put("apple", 3);
        hashMap.put("banana", 5);
        System.out.println("HashMap: " + hashMap);

        Map<String, Integer> treeMap = new TreeMap<>();             // 按 key 排序
        treeMap.putAll(hashMap);
        System.out.println("TreeMap: " + treeMap);

        // ---------- Queue ----------
        Queue<Integer> queue = new ArrayDeque<>(List.of(1, 2, 3));
        queue.offer(4);                                            // 入队
        System.out.println("peek = " + queue.peek());               // 查看队首

        Deque<Integer> deque = new ArrayDeque<>();                  // 双端队列
        deque.push(1); deque.push(2); deque.push(3);
        System.out.println("pop = " + deque.pop());                // 3

        // ---------- 不可变集合（Java 9+）----------
        List<Integer> immutable = List.of(1, 2, 3);
        Set<String> immSet = Set.of("a", "b");
        Map<String, Integer> immMap = Map.of("k1", 1, "k2", 2);
        // immutable.add(4);  // 抛 UnsupportedOperationException

        // ---------- Stream 流式操作（Java 8+）----------
        List<String> filtered = arrayList.stream()
            .filter(s -> s.length() > 0)
            .map(String::toUpperCase)
            .collect(Collectors.toList());
        System.out.println("filtered: " + filtered);

        int sum = IntStream.rangeClosed(1, 100).sum();
        System.out.println("1~100 sum = " + sum);
    }


    // =========================================================================
    // 5. 枚举（enum）—— Java 5
    // =========================================================================

    /**
     * enum 本质是继承 java.lang.Enum 的 final class，不能再继承其他类，但可实现接口。
     * 构造器默认为 private。
     */
    public enum OrderStatus {
        PENDING("待支付"),
        PAID("已支付"),
        SHIPPED("已发货"),
        DELIVERED("已送达"),
        CANCELLED("已取消");

        private final String label;

        OrderStatus(String label) {
            this.label = label;
        }

        public String getLabel() {
            return label;
        }

        /** 枚举可定义方法，实现业务行为 */
        public boolean isTerminal() {
            return this == DELIVERED || this == CANCELLED;
        }
    }

    public static void enums() {
        OrderStatus status = OrderStatus.PAID;
        System.out.println("status = " + status + ", label = " + status.getLabel());
        System.out.println("isTerminal = " + status.isTerminal());

        // ---------- EnumSet / EnumMap（位向量级别高效）----------
        Set<OrderStatus> active = EnumSet.of(OrderStatus.PENDING, OrderStatus.PAID);
        System.out.println("active = " + active);

        Map<OrderStatus, String> labels = new EnumMap<>(OrderStatus.class);
        labels.put(OrderStatus.PENDING, "待支付");
        System.out.println("EnumMap: " + labels);

        // ---------- 遍历所有枚举值 ----------
        for (OrderStatus s : OrderStatus.values()) {
            System.out.println(" - " + s.name() + " (ordinal=" + s.ordinal() + ")");
        }
    }


    // =========================================================================
    // 6. 类与对象（class）
    // =========================================================================

    /**
     * 完整类示例：包含字段、构造器、方法、静态成员。
     */
    public static class Account {
        // ---------- 字段 ----------
        private static int counter = 0;          // 静态字段（属于类）
        private final long id;                   // final 字段只能赋值一次
        private String owner;                    // 实例字段
        protected double balance;
        public String currency = "CNY";

        // ---------- 构造器 ----------
        public Account(String owner, double balance) {
            this.id = ++counter;
            this.owner = Objects.requireNonNull(owner, "owner 不能为空");
            if (balance < 0) throw new IllegalArgumentException("balance 不能为负");
            this.balance = balance;
        }

        // ---------- 方法 ----------
        public void deposit(double amount) {
            if (amount <= 0) throw new IllegalArgumentException("amount 必须为正");
            this.balance += amount;
        }

        public double getBalance() {
            return balance;
        }

        @Override
        public String toString() {
            return "Account{id=" + id + ", owner='" + owner + "', balance=" + balance + " " + currency + "}";
        }

        // ---------- 静态工厂方法（Effective Java 推荐）----------
        public static Account empty(String owner) {
            return new Account(owner, 0);
        }
    }

    public static void classes() {
        Account acc = new Account("张三", 1000.0);
        acc.deposit(500.0);
        System.out.println(acc);

        Account empty = Account.empty("李四");
        System.out.println(empty);
    }


    // =========================================================================
    // 7. 抽象类与接口
    // =========================================================================

    /**
     * 抽象类：可包含抽象方法（无实现）和具体方法。
     * 适用场景：共享代码 + 强制子类实现特定行为；单继承。
     */
    public static abstract class Animal {
        protected String name;
        protected int age;

        public Animal(String name, int age) {
            this.name = name;
            this.age = age;
        }

        public abstract String speak();           // 抽象方法，子类必须实现

        public void sleep() {                     // 具体方法
            System.out.println(name + " is sleeping.");
        }
    }

    /**
     * 接口（Java 8+）：可包含抽象方法、默认方法、静态方法、私有方法（Java 9）。
     * 多实现，弥补单继承的不足。
     */
    public interface Swimmable {
        void swim();

        default void dive() {                    // 默认方法：给接口添加新方法而不破坏已有实现
            System.out.println("Diving!");
        }

        static boolean isWaterSafe() {           // 接口静态方法
            return true;
        }
    }

    public static class Dog extends Animal implements Swimmable {
        public Dog(String name, int age) {
            super(name, age);
        }

        @Override
        public String speak() {
            return "Woof!";
        }

        @Override
        public void swim() {
            System.out.println(name + " is paddling.");
        }
    }

    /**
     * ★ 函数式接口（@FunctionalInterface）：仅一个抽象方法的接口，可用于 Lambda。
     */
    @FunctionalInterface
    public interface Transformer<T, R> {
        R transform(T input);

        default <V> Transformer<T, V> andThen(Transformer<R, V> after) {
            return t -> after.transform(this.transform(t));
        }
    }

    public static void abstractAndInterface() {
        Dog dog = new Dog("旺财", 3);
        System.out.println(dog.speak());
        dog.sleep();
        dog.swim();
        dog.dive();

        // ---------- 函数式接口 + Lambda ----------
        Transformer<String, Integer> strLen = String::length;
        System.out.println("length = " + strLen.transform("hello"));
    }


    // =========================================================================
    // 8. 嵌套类与内部类
    // =========================================================================

    public static class Outer {
        private static int staticField = 1;
        private int instanceField = 2;

        // ---------- 静态嵌套类 ----------
        public static class StaticNested {
            public void show() {
                System.out.println("只能访问外部类的静态成员: " + staticField);
            }
        }

        // ---------- 成员内部类 ----------
        public class MemberInner {
            public void show() {
                System.out.println("可访问外部类所有成员: static=" + staticField
                    + ", instance=" + instanceField);
            }
        }

        public void useInner() {
            // ---------- 局部内部类 ----------
            class Local {
                void hi() { System.out.println("Local class"); }
            }
            new Local().hi();

            // ---------- 匿名内部类（Lambda 优先替代）----------
            Runnable r = () -> System.out.println("Lambda 替代匿名内部类");
            r.run();
        }
    }

    public static void nestedClasses() {
        Outer.StaticNested nested = new Outer.StaticNested();
        nested.show();

        Outer outer = new Outer();
        Outer.MemberInner inner = outer.new MemberInner();
        inner.show();

        outer.useInner();
    }


    // =========================================================================
    // 9. ★ Record（Java 14 预览 / 16 正式）
    // =========================================================================

    /**
     * ★ Record 是不可变数据载体的简洁写法。
     * 编译器自动生成：
     *   - final 字段
     *   - 规范的构造器（canonical constructor）
     *   - 访问器方法（注意：叫 name() 不是 getName()）
     *   - equals() / hashCode() / toString()
     *
     * 适用：DTO、值对象、事件消息、Map.Entry 的替代品等。
     */
    public record Point(int x, int y) {
        // ---------- 紧凑构造器（Compact Constructor）做数据校验 ----------
        public Point {
            if (x < 0 || y < 0) {
                throw new IllegalArgumentException("坐标不能为负");
            }
        }

        // ---------- 可添加额外方法 ----------
        public double distanceTo(Point other) {
            int dx = x - other.x;
            int dy = y - other.y;
            return Math.sqrt(dx * dx + dy * dy);
        }

        // ---------- 可添加静态字段和工厂方法 ----------
        public static Point origin() {
            return new Point(0, 0);
        }
    }

    /**
     * Record 可实现接口，但不能继承类（隐式继承 java.lang.Record）。
     */
    public record ColoredPoint(int x, int y, String color) implements Swimmable {
        @Override
        public void swim() {
            System.out.println("ColoredPoint 在水中漂浮");
        }
    }

    public static void records() {
        Point p1 = new Point(3, 4);
        Point p2 = Point.origin();
        System.out.println("p1 = " + p1);                           // 自动 toString
        System.out.println("p1.x() = " + p1.x());                   // 自动访问器
        System.out.println("distance = " + p1.distanceTo(p2));     // 5.0
        System.out.println("equals: " + p1.equals(new Point(3, 4))); // true
    }


    // =========================================================================
    // 10. ★ Sealed Class / Interface（Java 17 正式）
    // =========================================================================

    /**
     * ★ 封闭类型：用 permits 列出允许的子类，子类必须与父类同模块或同包。
     * 子类必须是 final / sealed / non-sealed 之一。
     * 配合 switch 模式匹配，编译器可做穷尽性检查。
     */
    public sealed interface Shape permits Circle, Rectangle, Triangle {
        double area();
    }

    public static final class Circle implements Shape {
        private final double radius;
        public Circle(double radius) { this.radius = radius; }
        @Override public double area() { return Math.PI * radius * radius; }
    }

    public static final class Rectangle implements Shape {
        private final double width, height;
        public Rectangle(double w, double h) { this.width = w; this.height = h; }
        @Override public double area() { return width * height; }
    }

    public static non-sealed class Triangle implements Shape {
        protected double base, height;
        public Triangle(double b, double h) { this.base = b; this.height = h; }
        @Override public double area() { return 0.5 * base * height; }
    }

    /**
     * ★ Record 与 sealed 配合可实现代数数据类型（ADT）：
     *   - Sum Type：sealed 父类型 + 多个 record 子类表示「或」
     *   - Product Type：record 的字段组合表示「且」
     */
    public sealed interface PaymentMethod permits CreditCard, Alipay, WechatPay {}

    public record CreditCard(String number, String cvv) implements PaymentMethod {}
    public record Alipay(String account) implements PaymentMethod {}
    public record WechatPay(String openId) implements PaymentMethod {}

    public static void sealedTypes() {
        Shape s = new Circle(2.0);
        System.out.println("area = " + s.area());

        PaymentMethod pm = new CreditCard("****1234", "123");
        describePayment(pm);
    }

    /** 演示 switch 模式匹配对 sealed 类型的穷尽检查（Java 21） */
    static void describePayment(PaymentMethod pm) {
        String desc = switch (pm) {
            case CreditCard cc -> "信用卡：" + cc.number();
            case Alipay a      -> "支付宝：" + a.account();
            case WechatPay w   -> "微信支付：" + w.openId();
        };
        System.out.println(desc);
    }


    // =========================================================================
    // 11. 泛型（Generics）—— Java 5
    // =========================================================================

    /**
     * 泛型类：定义参数化类型，编译期类型检查 + 运行期类型擦除。
     */
    public static class Box<T> {
        private T content;

        public void set(T content) { this.content = content; }
        public T get() { return content; }

        public <U> U transform(java.util.function.Function<T, U> mapper) {
            return mapper.apply(content);
        }
    }

    /**
     * 有界类型参数（Bounded Type Parameter）
     */
    public static <T extends Comparable<T>> T max(T a, T b) {
        return a.compareTo(b) >= 0 ? a : b;
    }

    /**
     * 多重界限：& 后只能接接口
     */
    public static <T extends Number & Comparable<T>> T min(T a, T b) {
        return a.compareTo(b) <= 0 ? a : b;
    }

    /**
     * 通配符（Wildcards）
     *   ?           —— 任意类型
     *   ? extends T —— 上界，Producer（读）
     *   ? super T   —— 下界，Consumer（写）
     *
     * ★ PECS 原则（Producer Extends Consumer Super）
     */
    public static double sumOfNumbers(List<? extends Number> numbers) {
        return numbers.stream().mapToDouble(Number::doubleValue).sum();
    }

    public static void addIntegers(List<? super Integer> sink) {
        sink.add(1); sink.add(2); sink.add(3);
    }

    public static void generics() {
        Box<String> box = new Box<>();
        box.set("hello");
        String upper = box.transform(String::toUpperCase);
        System.out.println("upper = " + upper);

        System.out.println("max(3,5) = " + max(3, 5));
        System.out.println("max(\"ab\",\"cd\") = " + max("ab", "cd"));

        // ---------- 上界 / 下界 ----------
        List<Integer> ints = List.of(1, 2, 3);
        List<Double>  dbls = List.of(1.5, 2.5);
        System.out.println("sumOfNumbers(ints) = " + sumOfNumbers(ints));
        System.out.println("sumOfNumbers(dbls) = " + sumOfNumbers(dbls));

        List<Number> numbers = new ArrayList<>();
        addIntegers(numbers);                       // Integer 可写入 List<Number>
        System.out.println("numbers = " + numbers);

        // ---------- 类型擦除 ----------
        // 编译期 List<String> 与 List<Integer> 不同，运行期擦除为相同 List<Object>
        List<String> list = new ArrayList<>();
        // list.add(42);    // 编译错误
        Object raw = list;                          // 允许，但失去类型安全
        System.out.println("raw class = " + raw.getClass().getName());
    }


    // =========================================================================
    // 12. Optional 与空值处理 —— Java 8
    // =========================================================================

    /**
     * Optional<T>：可能为 null 的容器。目的：让空值显式化、强制处理。
     *  ★ 反模式：
     *     - 不要把 Optional 作为类的字段（不利于序列化）
     *     - 不要作为方法参数（用 null 判断或重载代替）
     *     - Optional.isPresent() + get() 等价于 null 判断，建议用 map/filter 链
     */
    public static Optional<String> findNickname(long userId) {
        if (userId == 1L) return Optional.of("张三");
        if (userId == 2L) return Optional.of("李四");
        return Optional.empty();
    }

    public static void optionals() {
        // ---------- 创建 ----------
        Optional<String> opt1 = Optional.of("hi");             // 不允许 null
        Optional<String> opt2 = Optional.ofNullable(null);     // 允许 null
        Optional<String> opt3 = Optional.empty();

        // ---------- 链式操作 ----------
        String result = findNickname(1L)
            .filter(s -> s.length() > 1)
            .map(String::toUpperCase)
            .orElse("DEFAULT");
        System.out.println("result = " + result);              // "张三" → "张三" 长度 2 通过

        String fallback = findNickname(999L)
            .map(s -> "found:" + s)
            .orElseGet(() -> "默认昵称");                      // 惰性求值
        System.out.println("fallback = " + fallback);

        // ---------- 抛异常 ----------
        try {
            findNickname(999L).orElseThrow(() ->
                new IllegalStateException("找不到用户"));
        } catch (IllegalStateException e) {
            System.out.println("orElseThrow 抛出: " + e.getMessage());
        }

        // ---------- flatMap 解嵌套 Optional ----------
        Optional<Optional<String>> nested = Optional.of(Optional.of("x"));
        Optional<String> flat = nested.flatMap(o -> o);
        System.out.println("flat = " + flat);
    }

    /**
     * ★ 类型注解（Type Annotation）：在类型上使用的注解。
     *   需引入 Checker Framework 或 JSpecify 做静态空值检查。
     */
    public static String greet(@NonNull String name) {
        return "Hello, " + name;
    }

    public static void annotations_demo() {
        System.out.println(greet("World"));

        // ---------- @Nullable / @NonNull（JSpecify 风格演示）----------
        // 真实使用需引入 org.jspecify:jspecify 依赖
        // @NonNull String s = null;  // 编译期警告（启用检查器时为错误）
    }


    // =========================================================================
    // 13. 注解（Annotation）
    // =========================================================================

    /**
     * 自定义注解 + 元注解
     */
    @Retention(RetentionPolicy.RUNTIME)          // 保留到运行期
    @Target({ElementType.METHOD, ElementType.FIELD})
    public @interface MyAnnotation {
        String value() default "";
        int priority() default 0;
    }

    /** 可重复注解（Java 8+） */
    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.TYPE)
    @Repeatable(Schedules.class)
    public @interface Schedule {
        String cron();
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.TYPE)
    public @interface Schedules {
        Schedule[] value();
    }

    @Schedule(cron = "0 0 * * * ?")
    @Schedule(cron = "0 12 * * * ?")
    public static class ScheduledJob {}

    /**
     * 类型注解示例（Java 8+）：可在泛型参数、数组类型、new 表达式等任何类型上注解
     */
    public static class TypeAnnotationDemo<@NonNull T> {
        public List<@NonNull String> names;

        public TypeAnnotationDemo() {
            this.names = new ArrayList<>();
        }

        public void add(@NonNull String name) {
            names.add(name);
        }
    }


    // =========================================================================
    // 14. ★ 类型推断
    // =========================================================================

    public static void typeInference() {
        // ---------- 菱形操作符 <>（Java 7+）----------
        Map<String, List<Integer>> map1 = new HashMap<>();   // 右侧自动推断
        map1.put("evens", List.of(2, 4));
        map1.put("odds",  List.of(1, 3));

        // ---------- var 局部变量（Java 10+）----------
        var list = List.of(1, 2, 3);                // 推断为 List<Integer>
        var stream = list.stream();                  // Stream<Integer>
        var sum = stream.mapToInt(Integer::intValue).sum();

        // ★ var 只能用于局部变量（方法内、for 循环、try 内）
        // ★ var 不能用于方法形参、返回类型、字段

        // ---------- Lambda 形参类型推断 ----------
        java.util.function.BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
        System.out.println("add = " + add.apply(3, 5));

        // ---------- Pattern Matching 中的 var（Java 21）----------
        // case Box<T> b -> b.content()           // 直接用类型名
        // case Box<T> b when ... -> ...          // 用 var 进一步细化（略）

        System.out.println("sum = " + sum + ", map = " + map1);
    }


    // =========================================================================
    // 15. 类型转换
    // =========================================================================

    public static void typeConversion() {
        // ---------- 隐式转换（自动类型提升）----------
        int i = 100;
        long l = i;              // int → long
        double d = l;            // long → double
        System.out.println("d = " + d);

        // ---------- 强制类型转换（窄化）----------
        double pi = 3.14159;
        int truncated = (int) pi;             // 3（截断小数）
        System.out.println("truncated = " + truncated);

        long big = 130L;
        byte small = (byte) big;              // 130 → -126（溢出环绕）
        System.out.println("small = " + small);

        // ---------- 数值溢出陷阱 ----------
        int max = Integer.MAX_VALUE;
        int overflow = max + 1;                // -2147483648（环绕）
        System.out.println("overflow = " + overflow);

        // Math.addExact 在溢出时抛 ArithmeticException（Java 8+）
        try {
            int safe = Math.addExact(max, 1);
        } catch (ArithmeticException e) {
            System.out.println("Math.addExact 捕获溢出");
        }

        // ---------- 装箱 / 拆箱 隐式转换 ----------
        Integer boxedInt = 42;                 // 自动装箱
        int unboxed = boxedInt;                // 自动拆箱
        System.out.println("unboxed = " + unboxed);

        // ---------- String 转换 ----------
        String s1 = String.valueOf(42);
        String s2 = Integer.toString(42);
        int parsed = Integer.parseInt("123");
        System.out.println("parsed = " + parsed);

        // ---------- 基本类型与数字类型互转 ----------
        String binary = Integer.toBinaryString(42);     // "101010"
        int fromBin = Integer.parseInt(binary, 2);
        System.out.println("from binary " + binary + " = " + fromBin);
    }


    // =========================================================================
    // 16. ★ Pattern Matching 模式匹配（Java 16 ~ 21）
    // =========================================================================

    /**
     * ★ Java 21：Pattern Matching 全面支持
     *   1) instanceof 模式匹配（Java 16）：自动绑定 + 自动转型
     *   2) switch 模式匹配（Java 21 正式）
     *   3) record pattern（Java 21）：`case Point(int x, int y)`
     *   4) 嵌套模式匹配
     */
    public static void patternMatching() {
        Object obj = "Java 21";

        // ---------- instanceof 模式匹配 ----------
        if (obj instanceof String s) {
            System.out.println("length = " + s.length());   // s 已绑定且转型完成
        }

        // ---------- 旧写法（不推荐）----------
        if (obj instanceof String) {
            String s = (String) obj;                        // 显式转型
            System.out.println("旧写法 length = " + s.length());
        }

        // ---------- switch 模式匹配（Java 21）----------
        Object value = 42;
        String desc = switch (value) {
            case Integer i when i > 0 -> "正整数: " + i;
            case Integer i            -> "非正整数: " + i;
            case String s             -> "字符串: " + s;
            case null                 -> "null 值";
            default                   -> "其他: " + value;
        };
        System.out.println("desc = " + desc);

        // ---------- record pattern（Java 21）----------
        Object shape = new Point(3, 4);
        String shapeDesc = switch (shape) {
            case Point(int x, int y) -> "点(" + x + ", " + y + ")";
            case Circle c            -> "圆，面积=" + c.area();
            case Rectangle r         -> "矩形，面积=" + r.area();
            default                  -> "其他";
        };
        System.out.println("shapeDesc = " + shapeDesc);

        // ---------- 嵌套 record pattern ----------
        record Box<T>(T content) {}
        Box<Point> boxed = new Box<>(new Point(1, 2));
        if (boxed instanceof Box(Point(int x, int y))) {
            System.out.println("嵌套解构: x=" + x + ", y=" + y);
        }
    }


    // =========================================================================
    // 17. Switch 表达式（Java 14 正式）
    // =========================================================================

    public static void switchExpression() {
        int day = 3;
        String dayName = switch (day) {
            case 1, 2, 3, 4, 5 -> "工作日";
            case 6, 7          -> "周末";
            default            -> "未知";
        };
        System.out.println("dayName = " + dayName);

        // ---------- yield 返回值 ----------
        int n = 2;
        String result = switch (n) {
            case 1 -> "one";
            case 2 -> {
                System.out.println("复杂分支逻辑");
                yield "two";                       // yield 返回值
            }
            default -> "other";
        };
        System.out.println("result = " + result);

        // ---------- 枚举 switch ----------
        OrderStatus status = OrderStatus.SHIPPED;
        String action = switch (status) {
            case PENDING   -> "等待支付";
            case PAID      -> "准备发货";
            case SHIPPED   -> "跟踪物流";
            case DELIVERED -> "确认收货";
            case CANCELLED -> "退款处理";
        };
        System.out.println("action = " + action);
    }


    // =========================================================================
    // 18. Text Blocks 文本块（Java 13 预览 / 15 正式）
    // =========================================================================

    public static void textBlocks() {
        // ---------- 三引号字符串 ----------
        String json = """
            {
              "name": "Alice",
              "age": 30,
              "roles": ["admin", "user"]
            }
            """;
        System.out.println(json);

        // ---------- 文本块方法（Java 15+）----------
        String aligned = """
                line1
                line2
                """.stripIndent();                        // 统一去缩进
        System.out.println("aligned = [" + aligned + "]");

        String escaped = """
            <html>
                <body>Hello\n\tWorld</body>
            </html>
            """.translateEscapes();                       // 处理 \n \t 等转义
        System.out.println(escaped);

        // ---------- 模板表达式（Java 21 预览）----------
        // String name = "Alice";
        // String greeting = STR."Hello, \{name}!";       // 需启用预览功能
        // System.out.println(greeting);
    }


    // =========================================================================
    // 19. Java 独有特色总结
    // =========================================================================

    /*
     *  ★ 1) 强类型 + 静态类型 + 名义类型（Nominal Typing）
     *      类型由声明决定，不被结构相似性左右（与 TypeScript 的结构类型不同）。
     *
     *  ★ 2) 类型擦除（Type Erasure）
     *      泛型只在编译期存在，运行期 List<String> 与 List<Integer> 都是 List<Object>。
     *      不能创建泛型数组（new T[] 不合法），可通过反射绕过（@SuppressWarnings）。
     *
     *  ★ 3) 单继承 + 多实现接口
     *      类只能 extends 一个父类，但可 implements 多个接口。
     *
     *  ★ 4) 注解即类型元数据
     *      注解可被反射读取，用于框架（Spring/JUnit/Hibernate）、代码生成、运行时校验。
     *
     *  ★ 5) Sealed + Record + Pattern Matching 组合
     *      实现代数数据类型（ADT）+ 模式匹配的穷尽性检查，堪比 Scala/Kotlin。
     *
     *  ★ 6) 没有原生类型别名（Type Alias）
     *      只能用继承或包装类模拟。这是 Java 长期被诟病的点。
     *      （JEP 草案：type alias，已提出但未落地）
     */


    // =========================================================================
    // 20. 完整实战模型：User / Order / Pet / Article
    // =========================================================================

    /** ---------- 公共类型定义 ---------- */

    /** 角色枚举 */
    public enum Role { ADMIN, EDITOR, VIEWER }

    /** 支付方式（sealed ADT） */
    public sealed interface Payment permits CreditCard, Alipay, WechatPay, GiftCard {}
    public record CreditCard(String number, String cvv) implements Payment {}
    public record Alipay(String account) implements Payment {}
    public record WechatPay(String openId) implements Payment {}
    public record GiftCard(String code, double balance) implements Payment {}

    /** 收货地址（record） */
    public record Address(String country, String province, String city, String street, String zip) {
        public Address {
            Objects.requireNonNull(country, "country 必填");
            Objects.requireNonNull(city, "city 必填");
            if (zip == null || zip.length() != 6) {
                throw new IllegalArgumentException("邮编必须 6 位");
            }
        }

        public String fullAddress() {
            return country + " " + province + " " + city + " " + street + " (" + zip + ")";
        }
    }

    /** ---------- User 模型 ---------- */
    public static class User {
        private final long id;
        private final String username;
        private String email;
        private Optional<String> nickname;            // 可选昵称
        private List<Role> roles;                     // 角色列表
        private Address address;                      // 可空地址
        private Map<String, String> preferences;      // 用户偏好

        public User(long id, String username, String email) {
            this.id = id;
            this.username = Objects.requireNonNull(username);
            this.email = email;
            this.roles = new ArrayList<>();
            this.preferences = new HashMap<>();
        }

        // 标准 getter / setter / toString 省略，演示用关键方法
        public long id() { return id; }
        public String username() { return username; }
        public Optional<String> nickname() { return nickname; }
        public void setNickname(String nick) { this.nickname = Optional.ofNullable(nick); }
        public List<Role> roles() { return Collections.unmodifiableList(roles); }
        public void addRole(Role r) { if (!roles.contains(r)) roles.add(r); }
        public Optional<Address> address() { return Optional.ofNullable(address); }
        public void setAddress(Address a) { this.address = a; }
        public Map<String, String> preferences() { return Collections.unmodifiableMap(preferences); }
        public void setPref(String k, String v) { preferences.put(k, v); }

        @Override
        public String toString() {
            return "User{id=" + id + ", username='" + username + "', email='" + email + "'}";
        }
    }

    /** ---------- Order 模型 ---------- */
    public record OrderItem(String productId, String name, int quantity, double unitPrice) {
        public OrderItem {
            if (quantity <= 0) throw new IllegalArgumentException("数量必须为正");
            if (unitPrice < 0) throw new IllegalArgumentException("价格不能为负");
        }

        public double subtotal() { return quantity * unitPrice; }
    }

    public static class Order {
        private final String orderId;
        private final long userId;
        private final List<OrderItem> items;
        private OrderStatus status;
        private PaymentMethod2 paymentMethod;
        private final LocalDateTime createdAt;

        public Order(String orderId, long userId) {
            this.orderId = orderId;
            this.userId = userId;
            this.items = new ArrayList<>();
            this.status = OrderStatus.PENDING;
            this.createdAt = LocalDateTime.now();
        }

        public void addItem(OrderItem item) { items.add(item); }

        public double total() {
            return items.stream().mapToDouble(OrderItem::subtotal).sum();
        }

        public String orderId() { return orderId; }
        public long userId() { return userId; }
        public List<OrderItem> items() { return Collections.unmodifiableList(items); }
        public OrderStatus status() { return status; }
        public void setStatus(OrderStatus s) { this.status = s; }
        public PaymentMethod2 paymentMethod() { return paymentMethod; }
        public void setPaymentMethod(PaymentMethod2 pm) { this.paymentMethod = pm; }
        public LocalDateTime createdAt() { return createdAt; }

        @Override
        public String toString() {
            return "Order{id='" + orderId + "', total=" + total() + ", status=" + status + "}";
        }
    }

    /** 支付方式枚举版（与 sealed 版对比演示） */
    public sealed interface PaymentMethod2 permits CardPayment, WalletPayment, BankTransfer {}

    public record CardPayment(String last4, String brand) implements PaymentMethod2 {}
    public record WalletPayment(String provider, String account) implements PaymentMethod2 {}
    public record BankTransfer(String bankName, String accountNo) implements PaymentMethod2 {}

    /** ---------- Pet 模型：抽象类 + Record 子类 ---------- */
    public static abstract class Pet {
        protected final String name;
        protected final LocalDate birthday;

        public Pet(String name, LocalDate birthday) {
            this.name = name;
            this.birthday = birthday;
        }

        public abstract String sound();

        public int ageYears() {
            return LocalDate.now().getYear() - birthday.getYear();
        }

        public String name() { return name; }
    }

    public record Dog(String name, LocalDate birthday, String breed) extends Pet {
        public Dog {
            super(name, birthday);
        }
        @Override public String sound() { return "Woof"; }
    }

    public record Cat(String name, LocalDate birthday, boolean indoor) extends Pet {
        public Cat {
            super(name, birthday);
        }
        @Override public String sound() { return "Meow"; }
    }

    public record Bird(String name, LocalDate birthday, boolean canFly) extends Pet {
        public Bird {
            super(name, birthday);
        }
        @Override public String sound() { return "Tweet"; }
    }

    /** ---------- Article 模型：Text Blocks + Map + 嵌套 ---------- */
    public static class Article {
        private final long id;
        private final String title;
        private final String author;
        private final String content;
        private final List<String> tags;
        private final Map<String, Object> metadata;
        private Optional<LocalDate> publishedAt;

        public Article(long id, String title, String author, String content) {
            this.id = id;
            this.title = title;
            this.author = author;
            this.content = content;
            this.tags = new ArrayList<>();
            this.metadata = new HashMap<>();
            this.publishedAt = Optional.empty();
        }

        public Article withTag(String tag) { tags.add(tag); return this; }
        public Article withMeta(String key, Object value) { metadata.put(key, value); return this; }
        public Article publishedOn(LocalDate d) { this.publishedAt = Optional.of(d); return this; }

        public long id() { return id; }
        public String title() { return title; }
        public String author() { return author; }
        public String content() { return content; }
        public List<String> tags() { return Collections.unmodifiableList(tags); }
        public Map<String, Object> metadata() { return Collections.unmodifiableMap(metadata); }
        public Optional<LocalDate> publishedAt() { return publishedAt; }

        @Override
        public String toString() {
            return "Article{id=" + id + ", title='" + title + "', author='" + author
                + "', tags=" + tags + ", published=" + publishedAt.orElse(null) + "}";
        }
    }

    /** ---------- 演示：组合所有模型 ---------- */
    public static void realWorldDemo() {
        System.out.println("\n========== 实战模型演示 ==========");

        // 1) 创建地址（record，紧凑构造器自动校验邮编）
        Address addr = new Address("中国", "广东", "深圳", "科技园路 1 号", "518000");
        System.out.println("Address: " + addr.fullAddress());

        // 2) 创建用户
        User alice = new User(1L, "alice", "alice@example.com");
        alice.setNickname("小爱");
        alice.addRole(Role.ADMIN);
        alice.addRole(Role.EDITOR);
        alice.setAddress(addr);
        alice.setPref("theme", "dark");
        System.out.println("User: " + alice);
        System.out.println("昵称: " + alice.nickname().orElse("匿名"));

        // 3) 创建订单（sealed 支付方式）
        Order order = new Order("ORD-2024-001", alice.id());
        order.addItem(new OrderItem("P001", "机械键盘", 1, 899.0));
        order.addItem(new OrderItem("P002", "鼠标",     2, 199.0));
        order.setPaymentMethod(new CardPayment("1234", "VISA"));
        order.setStatus(OrderStatus.PAID);
        System.out.println("Order: " + order + ", total = " + order.total());

        // 4) 创建宠物（抽象类 + record 子类）
        Pet dog = new Dog("旺财", LocalDate.of(2020, 5, 1), "柴犬");
        Pet cat = new Cat("小花", LocalDate.of(2021, 3, 15), true);
        List<Pet> pets = List.of(dog, cat);
        for (Pet p : pets) {
            System.out.println(p.name() + " 说 " + p.sound() + "，" + p.ageYears() + " 岁");
        }

        // 5) 创建文章（Text Blocks）
        Article article = new Article(
            1L,
            "Java 21 新特性详解",
            "alice",
            """
            Java 21 是最新的 LTS 版本，带来了虚拟线程、Record Patterns、
            Pattern Matching for switch 等重要特性。本文将逐一介绍。
            """
        );
        article.withTag("java").withTag("lts").withTag("java21");
        article.withMeta("views", 1024).withMeta("category", "tech");
        article.publishedOn(LocalDate.of(2024, 9, 1));
        System.out.println("Article: " + article);
    }


    // =========================================================================
    // 辅助：注解定义
    // =========================================================================

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.TYPE_USE})
    public @interface NonNull {}

    @Retention(RetentionPolicy.RUNTIME)
    @Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.TYPE_USE})
    public @interface Nullable {}


    // =========================================================================
    // 主入口
    // =========================================================================

    public static void main(String[] args) {
        System.out.println("========== Java 类型系统演示 ==========\n");

        System.out.println("--- 1) 基础类型 ---");
        primitiveTypes();
        typePromotion();

        System.out.println("\n--- 2) 包装类型 ---");
        wrapperTypes();

        System.out.println("\n--- 3) 数组 ---");
        arrays();

        System.out.println("\n--- 4) 容器类型 ---");
        collections();

        System.out.println("\n--- 5) 枚举 ---");
        enums();

        System.out.println("\n--- 6) 类与对象 ---");
        classes();

        System.out.println("\n--- 7) 抽象类与接口 ---");
        abstractAndInterface();

        System.out.println("\n--- 8) 嵌套类 ---");
        nestedClasses();

        System.out.println("\n--- 9) Record ---");
        records();

        System.out.println("\n--- 10) Sealed ---");
        sealedTypes();

        System.out.println("\n--- 11) 泛型 ---");
        generics();

        System.out.println("\n--- 12) Optional ---");
        optionals();

        System.out.println("\n--- 13) 注解 ---");
        annotations_demo();

        System.out.println("\n--- 14) 类型推断 ---");
        typeInference();

        System.out.println("\n--- 15) 类型转换 ---");
        typeConversion();

        System.out.println("\n--- 16) Pattern Matching ---");
        patternMatching();

        System.out.println("\n--- 17) Switch 表达式 ---");
        switchExpression();

        System.out.println("\n--- 18) Text Blocks ---");
        textBlocks();

        System.out.println("\n--- 19) 实战模型 ---");
        realWorldDemo();

        System.out.println("\n========== 演示结束 ==========");
    }
}