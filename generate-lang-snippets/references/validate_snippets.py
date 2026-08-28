#!/usr/bin/env python3
"""
VSCode snippets 文件校验脚本（支持 JSONC 注释）

功能：
  1. 剥离 `//` 单行注释后用 json.loads 解析
  2. 校验每个 snippet 必备字段（prefix / body / description）
  3. 统计 snippet 总数
  4. 检测重复 prefix（同一文件内）
  5. 统计测试 snippets 数量（以 "// 下面为测试snippets" 分隔符为界）

用法：
  python3 scripts/validate_snippets.py <file.code-snippets> [file2.code-snippets ...]
  python3 scripts/validate_snippets.py .vscode/*.code-snippets
"""
import json
import re
import sys
from pathlib import Path


def strip_jsonc(text: str) -> str:
    """剥离 // 单行注释（VSCode JSONC 格式）。

    注意：只剥离整行注释，不剥离行内注释（避免破坏字符串里的 //）。
    """
    lines = []
    for raw in text.splitlines():
        stripped = raw.lstrip()
        if stripped.startswith('//'):
            continue
        lines.append(raw)
    return '\n'.join(lines)


def has_separator(text: str) -> bool:
    """检查文件是否包含测试 snippets 分隔注释（// 下面为测试snippets）。"""
    for line in text.splitlines():
        if '下面为测试snippets' in line:
            return True
    return False


def validate_file(path: Path) -> dict:
    """校验单个 snippets 文件，返回报告字典。"""
    raw = path.read_text(encoding='utf-8')
    cleaned = strip_jsonc(raw)

    # 找分隔符在原始文本中的字符位置（用于统计测试 snippets）
    sep_idx = None
    for i, line in enumerate(raw.splitlines()):
        if '下面为测试snippets' in line:
            # 估算字符偏移：i 行之前的所有字符
            sep_idx = sum(len(l) + 1 for l in raw.splitlines()[:i])
            break

    # JSON 解析
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {
            'file': str(path),
            'ok': False,
            'error': f'JSON 解析失败: {e}',
        }

    # 检查必备字段 + 重复 prefix
    seen_prefix = {}
    dup_prefix = []
    bad_entry = []
    total = 0
    test_count = 0
    # 用 enumerate + 重新搜索位置：每次发现 key 时记一下字符偏移
    cursor = 0
    for name, snippet in data.items():
        total += 1
        # 找到这个 key 在 cleaned 里的位置（粗略，足够判定在分隔符前后）
        key_pos = cleaned.find(f'"{name}"', cursor)
        if key_pos >= 0:
            cursor = key_pos + len(name)
        if not isinstance(snippet, dict):
            bad_entry.append((total, name, 'snippet 不是 dict'))
            continue
        for field in ('prefix', 'body', 'description'):
            if field not in snippet:
                bad_entry.append((total, name, f'缺字段 {field}'))
        p = snippet.get('prefix')
        if p:
            if p in seen_prefix:
                dup_prefix.append((p, seen_prefix[p], name))
            else:
                seen_prefix[p] = name
        if sep_idx is not None and key_pos > sep_idx:
            test_count += 1

    return {
        'file': str(path),
        'ok': not bad_entry and not dup_prefix,
        'total': total,
        'test_count': test_count,
        'has_separator': sep_idx is not None,
        'dup_prefix': dup_prefix,
        'bad_entry': bad_entry,
    }


def main():
    if len(sys.argv) < 2:
        print('Usage: validate_snippets.py <file.code-snippets> [...]', file=sys.stderr)
        sys.exit(1)

    paths = [Path(p) for p in sys.argv[1:]]
    all_ok = True
    print(f'{"FILE":<40} {"TOTAL":>7} {"TEST":>7} {"SEP":>5}  STATUS')
    print('-' * 75)
    for path in paths:
        rep = validate_file(path)
        if not path.exists():
            print(f'{path:<40} {"-":>7} {"-":>7} {"-":>5}  ✗ 文件不存在')
            all_ok = False
            continue
        if not rep['ok']:
            all_ok = False
            status = '✗ ' + (rep.get('error') or
                             f"dup_prefix={rep['dup_prefix']} bad={rep['bad_entry']}")
        else:
            status = '✓'
        print(f'{rep["file"]:<40} {rep.get("total", "-"):>7} '
              f'{rep.get("test_count", "-"):>7} '
              f'{"✓" if rep.get("has_separator") else "-":>5}  {status}')

    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
