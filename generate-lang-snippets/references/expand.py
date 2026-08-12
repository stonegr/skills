#!/usr/bin/env python3
"""
VSCode snippet 展开模拟器

验证 snippets 文件里的 body 在 JSON 解码 + snippet 引擎展开后，
产生的最终代码是否符合预期。

用法：
    python3 expand.py <lang>.code-snippets
    python3 expand.py <lang>.code-snippets "snip_name"
"""

import json
import re
import sys
from pathlib import Path


def expand(body_lines, placeholders):
    """模拟 VSCode snippet 引擎的展开逻辑。

    支持：
      - \\$ -> 字面 $
      - \\\\ -> 字面 \\
      - $N -> 占位符 N 的值（占位符不存在则为空）
      - ${N} -> 同上
      - ${N:default} -> 占位符 N 的值，否则用 default
      - ${N|a,b,c|} -> 占位符 N 的值（snippet 引擎本身会弹选择框，展开时取 N 的值）
    """
    full = "\n".join(body_lines)
    out = []
    i = 0
    while i < len(full):
        c = full[i]
        if c == "\\" and i + 1 < len(full):
            nxt = full[i + 1]
            if nxt == "$":
                out.append("$")
                i += 2
                continue
            if nxt == "\\":
                out.append("\\")
                i += 2
                continue
            out.append(c)
            i += 1
            continue
        if c == "$" and i + 1 < len(full):
            nxt = full[i + 1]
            if nxt.isdigit():
                n = int(nxt)
                val = placeholders.get(n, placeholders.get(str(n), ""))
                if val:
                    out.append(expand([val], placeholders))
                else:
                    out.append("")
                i += 2
                continue
            if nxt == "{":
                m = re.match(r"^\{(\d+)(?::([^}]*))?\}", full[i + 1 :])
                if m:
                    n = int(m.group(1))
                    default = m.group(2) or ""
                    val = placeholders.get(n, placeholders.get(str(n), default))
                    out.append(val)
                    i += 1 + len(m.group(0))
                    continue
                m2 = re.match(r"^\{(\d+)\|([^}]*)\|\}", full[i + 1 :])
                if m2:
                    n = int(m2.group(1))
                    val = placeholders.get(n, placeholders.get(str(n), ""))
                    out.append(val)
                    i += 1 + len(m2.group(0))
                    continue
                out.append(c)
                i += 1
                continue
            out.append(c)
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def sample_placeholders(name, body):
    """根据 placeholder 默认值生成示例输入。

    支持嵌套 placeholder：若占位符 N 的默认值里出现 ${M:foo} 或 $M，
    会先记录 N 的"临时"默认值，再在占位符 M 解析完后用 M 的值替换。
    """
    ph = {}
    refs = {}  # N -> template string containing $M / ${M:...}
    for line in body:
        for m in re.finditer(r"\$\{(\d+)\|([^}]*)\|\}", line):
            n = int(m.group(1))
            options = m.group(2)
            if n not in ph and options:
                ph[n] = options.split(",")[0]
        for m in re.finditer(r"\$\{(\d+)(?::([^}]*))?\}", line):
            n = int(m.group(1))
            default = m.group(2) or ""
            if default and re.search(r"\$\{?\d", default):
                refs[n] = default
            elif n not in ph and default:
                ph[n] = default
        for m in re.finditer(r"\$(\d)\b", line):
            n = int(m.group(1))
            if n not in ph:
                ph[n] = "X"
    # 解析嵌套引用：refs[N] 中的 $M / ${M:foo} 替换为 ph[M] 的值
    for n, tmpl in refs.items():
        resolved = re.sub(
            r"\$\{(\d+)(?::([^}]*))?\}",
            lambda m: ph.get(int(m.group(1)), m.group(0)),
            tmpl,
        )
        resolved = re.sub(
            r"\$(\d)\b",
            lambda m: ph.get(int(m.group(1)), m.group(0)),
            resolved,
        )
        ph[n] = resolved
    return ph


def main():
    if len(sys.argv) < 2:
        print("Usage: expand.py <file.code-snippets> [snippet_name]", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    target_name = sys.argv[2] if len(sys.argv) > 2 else None

    data = json.loads(path.read_text())

    for name, snippet in data.items():
        if target_name and name != target_name:
            continue
        body = snippet["body"]
        ph = sample_placeholders(name, body)
        result = expand(body, ph)
        sep = "=" * 60
        print(f"{sep}\n{name}  (prefix: {snippet['prefix']})\n{sep}")
        print(result)
        print()


if __name__ == "__main__":
    main()
