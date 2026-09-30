#!/usr/bin/env python3
"""校验两个目录是否逐文件一致（MD5 全量比对）。

用在 skill 分发/复制之后，确认副本与源头完全一致。
比"文件数相同"严格：同名文件内容被改过、大小一样也能查出来。

用法:
    python verify_copy.py <源目录> <目标目录>

示例:
    python verify_copy.py "C:/Users/84977/.workbuddy/skills/foo" "C:/Users/84977/.codex/skills/foo"

退出码:
    0 = 完全一致
    1 = 有差异，或目录不存在
"""

from __future__ import annotations

import hashlib
import os
import re
import sys


def normalize(path: str) -> str:
    """把 Git Bash 风格的 /c/Users/... 转成 Windows 的 C:\\Users\\..."""
    path = path.strip().strip('"').strip("'")
    m = re.match(r"^/([A-Za-z])/(.*)$", path)
    if m:
        return "{}:\\{}".format(m.group(1).upper(), m.group(2).replace("/", "\\"))
    if re.match(r"^/[A-Za-z]$", path):
        return "{}:\\".format(path[1].upper())
    return path


def snapshot(root: str) -> dict[str, str]:
    """返回 {相对路径: 文件 MD5}。"""
    out: dict[str, str] = {}
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            full = os.path.join(dirpath, name)
            digest = hashlib.md5()
            with open(full, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    digest.update(chunk)
            out[os.path.relpath(full, root)] = digest.hexdigest()
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 1

    src, dst = normalize(argv[1]), normalize(argv[2])
    for label, path in (("源", src), ("目标", dst)):
        if not os.path.isdir(path):
            print("{}目录不存在: {}".format(label, path))
            return 1

    a, b = snapshot(src), snapshot(dst)
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])

    print("源   {}  {} 文件".format(src, len(a)))
    print("目标 {}  {} 文件".format(dst, len(b)))
    print(
        "仅源有 {} | 仅目标有 {} | 内容不同 {}".format(
            len(only_a), len(only_b), len(changed)
        )
    )
    for label, items in (("仅源", only_a), ("仅目标", only_b), ("不同", changed)):
        for item in items[:10]:
            print("  {}: {}".format(label, item))
        if len(items) > 10:
            print("  {}: ...另有 {} 项".format(label, len(items) - 10))

    ok = not (only_a or only_b or changed)
    print("结论:", "完全一致" if ok else "不一致")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
