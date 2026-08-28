"""
calculator.py — 被测代码示例
=============================

提供一组可被 pytest 测试的"业务函数"，覆盖：
  - 纯函数（add/subtract/multiply/divide/factorial/is_prime）
  - 抛错路径（divide by zero）
  - 文件 IO（load_config 读 JSON）

之所以把这些功能揉在一个文件，是因为 demo 测试需要演示：
  - 普通断言（test_assertion.py）
  - 异常断言（test_exception.py）
  - fixture 的 yield 风格（test_fixture.py）
  - patch 替换模块函数（test_mock.py）
  - tmp_path 临时文件（test_tmp.py）
"""


def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b


def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("factorial undefined for negative numbers")
    if n in (0, 1):
        return 1
    return n * factorial(n - 1)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def load_config(path: str) -> dict:
    """从 JSON 文件读配置。"""
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(path: str, data: dict) -> None:
    """写配置到 JSON 文件。"""
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
