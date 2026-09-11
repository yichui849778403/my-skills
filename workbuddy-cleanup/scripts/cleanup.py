#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WorkBuddy 用户数据目录 (~/.workbuddy) 清理工具。

用法:
    python cleanup.py                 # 只扫描并列出可清理项 (dry-run)
    python cleanup.py --apply         # 执行 safe 级清理
    python cleanup.py --apply --aggressive   # safe + review 级 (会触发重新下载)
    python cleanup.py --sessions      # 额外清理 GUI 中已删除的会话 jsonl (默认已包含在 safe)
    python cleanup.py --keep-logs 3   # 保留最近 N 天的日志目录 (默认 2)

注意:
    - 建议完全退出 WorkBuddy 后运行, 效果最干净。
    - 程序仍在运行时也能跑: 被占用的文件删不掉, 脚本会自动把它们截断为 0 字节
      先把磁盘空间回收掉, 只留空壳, 下次重启后重跑即彻底清除。
    - 绝不会碰: binaries/、*.db*、memory/、skills/、settings.json、mcp.json、connectors/、
      storage/、local_storage/
"""
import os
import sys
import shutil
import sqlite3
import argparse
import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.join(os.path.expanduser("~"), ".workbuddy")

# --- safe 级: 纯缓存/日志, 删了自动重建, 无功能损失 ---
SAFE_FILES = [
    "cache/acc-product-config-v3.json",
]
SAFE_DIRS = [           # 清空内容但保留目录本身
    "app/session/Cache",
    "app/session/GPUCache",
    "app/session/Code Cache",
    "app/session/DawnWebGPUCache",
    "app/session/DawnGraphiteCache",
    "app/session/DIPS",
    "app/session/Network",
    "app/session/WebStorage",
    "app/session/Shared Dictionary",
    "app/session/SharedStorage",
    "app/session/Partitions",
    "traces",
    "shell-snapshots",
    "logs/sandbox",
    "logs/migration",
    "logs/Crash-Log",
    "logs/startup",
    "logs/update",
    "logs/Diagnostics",
    "logs/editor_sdk",
]
SAFE_LOGS = [           # logs 根目录下的单文件日志
    "logs/AppStartup.log",
    "logs/automation.log",
    "logs/installer.log",
    "logs/vendor-extract.log",
    "logs/renderer.log",
    "logs/main.log",
    "logs/daemon.log",
    "logs/mcp-apps-diag.log",
    "logs/file-service.log",
    "logs/win-share-target-registrar.log",
    "logs/daemon.old.log",      # 轮转日志, 删后自动重建
    "logs/main.old.log",
    "logs/renderer.old.log",
]
SAFE_GLOBS = [          # (目录, 后缀) 按模式匹配删除
    ("pending-telemetry", ".reported"),
    ("audit-log", ".jsonl"),
]

# --- review 级: 能省大空间, 但删后会重新下载或丢功能, 需 --aggressive ---
REVIEW_DIRS = [
    "connectors-marketplace",
    "security/threat-database",
    "plugins/marketplaces/codebuddy-plugins-official/external_plugins",
    "plugins/cache/workbuddy-builtin/weixinpay",
]


def human(n):
    for unit in ("B", "K", "M", "G"):
        if n < 1024 or unit == "G":
            return "%.1f%s" % (n, unit) if unit != "B" else "%dB" % n
        n /= 1024.0


def dirsize(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def fsize(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def shorten(p):
    """绝对路径转成相对 ~/.workbuddy 的短路径, 便于阅读。"""
    try:
        rp = os.path.relpath(os.path.abspath(p), ROOT)
        return rp if not rp.startswith("..") else os.path.abspath(p)
    except Exception:
        return p


def deleted_session_ids():
    """读取 workbuddy.db 中 GUI 已软删除(deleted_at 非空)的会话 id。"""
    db = os.path.join(ROOT, "workbuddy.db")
    if not os.path.exists(db):
        return [], "db 不存在"
    try:
        con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
        cur = con.cursor()
        cur.execute("SELECT id FROM sessions WHERE deleted_at IS NOT NULL")
        ids = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT COUNT(*) FROM sessions WHERE deleted_at IS NULL")
        alive = cur.fetchone()[0]
        con.close()
        return ids, "存活会话 %d 个" % alive
    except Exception as e:
        return [], "读取失败: %s" % e


def stale_session_jsonls():
    """projects/ 下对应已删除会话的 .jsonl 文件列表 (含大小)。"""
    ids, note = deleted_session_ids()
    if not ids:
        return [], note
    idset = set(ids)
    found = []
    pdir = os.path.join(ROOT, "projects")
    for root, _, files in os.walk(pdir):
        for f in files:
            if f.endswith(".jsonl"):
                sid = f[:-6]
                if sid in idset:
                    p = os.path.join(root, f)
                    found.append((p, fsize(p)))
    return found, note


def collect(keep_logs, aggressive, do_sessions=True):
    items = []  # (级别, 显示名, 绝对路径, 类型file/dir/purge, 大小)

    for rel in SAFE_FILES:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            items.append(("safe", rel, p, "file", fsize(p)))

    for rel in SAFE_DIRS:
        p = os.path.join(ROOT, rel)
        if os.path.isdir(p):
            items.append(("safe", rel, p, "purge", dirsize(p)))

    for rel in SAFE_LOGS:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            items.append(("safe", rel, p, "file", fsize(p)))

    for rel, suffix in SAFE_GLOBS:
        p = os.path.join(ROOT, rel)
        if os.path.isdir(p):
            for f in os.listdir(p):
                if f.endswith(suffix):
                    fp = os.path.join(p, f)
                    if os.path.isfile(fp):
                        items.append(("safe", "%s/%s" % (rel, f), fp, "file", fsize(fp)))

    # 按日期的日志目录, 保留最近 keep_logs 天
    logs_dir = os.path.join(ROOT, "logs")
    if os.path.isdir(logs_dir):
        dated = []
        for d in os.listdir(logs_dir):
            p = os.path.join(logs_dir, d)
            if os.path.isdir(p) and len(d) == 10 and d[4] == "-" and d[7] == "-":
                dated.append(d)
        dated.sort(reverse=True)
        for d in dated[keep_logs:]:
            p = os.path.join(logs_dir, d)
            items.append(("safe", "logs/%s" % d, p, "dir", dirsize(p)))

    if do_sessions:
        for p, sz in stale_session_jsonls()[0]:
            items.append(("safe", "projects/.../" + os.path.basename(p)[:8] + ".jsonl", p, "file", sz))

    if aggressive:
        for rel in REVIEW_DIRS:
            p = os.path.join(ROOT, rel)
            if os.path.isdir(p):
                items.append(("review", rel, p, "dir", dirsize(p)))

    return items


def force_truncate(path):
    """删除失败时的兜底: 把文件截断为 0 字节, 立刻回收磁盘空间。

    Windows 上被独占打开的文件删不掉也改不了名, 但通常仍可读写;
    截断后内容清空、空间释放, 只剩一个 0 字节空壳, 重启程序后即可删除。
    """
    try:
        with open(path, "r+b") as f:
            f.truncate(0)
        return True
    except Exception:
        return False


def _has_content(path):
    """目录里是否还剩下非 0 字节的文件。"""
    try:
        for root, _, files in os.walk(path):
            for fn in files:
                if fsize(os.path.join(root, fn)) > 0:
                    return True
    except Exception:
        pass
    return False


def rm_any(path, stats):
    """删除文件/目录树。单个文件失败不中断整体清理。

    - 文件: 先删; 失败则清只读位重试; 再失败则截断为 0 字节回收空间。
    - 目录: rmtree 带 onerror, 遇到被占用文件跳过并截断, 其余文件继续删。
    """
    try:
        if os.path.isfile(path) or os.path.islink(path):
            try:
                os.remove(path)
                return
            except Exception:
                pass
            try:                       # 只读位有时会导致 WinError 5
                os.chmod(path, 0o666)
                os.remove(path)
                return
            except Exception:
                pass
            if force_truncate(path):
                stats["truncated"].append(path)
            else:
                stats["failed"].append((path, "被占用且无法截断"))
            return

        if not os.path.isdir(path):
            return

        def _onerror(func, p, exc_info):
            """rmtree 遇到错误时的处理: 重试 -> 截断 -> 记录后继续。"""
            try:
                os.chmod(p, 0o666)
            except Exception:
                pass
            try:
                func(p)                 # 重试一次
                return
            except Exception:
                pass
            if os.path.isfile(p):
                if force_truncate(p):
                    stats["truncated"].append(p)
                else:
                    stats["failed"].append((p, "被占用且无法截断"))
            else:
                # 目录删不掉: 若里面只剩被截断的 0 字节空壳, 属预期结果, 不重复报错
                if _has_content(p):
                    stats["failed"].append((p, str(exc_info[1])))

        shutil.rmtree(path, onerror=_onerror)

        # rmtree 后若目录仍在(多半剩被截断的空壳文件), 尽量收掉空目录
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for d in dirs:
                    try:
                        os.rmdir(os.path.join(root, d))
                    except Exception:
                        pass
            try:
                os.rmdir(path)
            except Exception:
                pass
    except Exception as e:
        stats["failed"].append((path, str(e)))


def do_remove(items, aggressive):
    freed = 0
    stats = {"truncated": [], "failed": []}
    for lvl, name, path, kind, size in items:
        if lvl == "review" and not aggressive:
            continue
        if kind == "purge":                     # 清空内容, 保留目录本身
            try:
                entries = [os.path.join(path, f) for f in os.listdir(path)]
            except Exception as e:
                stats["failed"].append((path, str(e)))
                continue
            for fp in entries:
                rm_any(fp, stats)
        else:
            rm_any(path, stats)

        # 按"实际减少的占用"统计, 截断掉的部分也算释放
        if os.path.isdir(path):
            remain = dirsize(path)
        elif os.path.exists(path):
            remain = fsize(path)
        else:
            remain = 0
        freed += max(0, size - remain)
    return freed, stats["failed"], stats["truncated"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真正执行删除, 默认只扫描")
    ap.add_argument("--aggressive", action="store_true", help="含 review 级 (会触发重新下载)")
    ap.add_argument("--no-sessions", action="store_true", help="跳过会话 jsonl 清理")
    ap.add_argument("--keep-logs", type=int, default=2, help="保留最近 N 天日志, 默认 2")
    args = ap.parse_args()

    if not os.path.isdir(ROOT):
        print("目录不存在:", ROOT)
        return 1

    items = collect(args.keep_logs, args.aggressive, not args.no_sessions)
    total_before = dirsize(ROOT)
    safe = [i for i in items if i[0] == "safe"]
    rev = [i for i in items if i[0] == "review"]

    print("=" * 62)
    print("WorkBuddy 数据目录: %s" % ROOT)
    print("当前总占用: %s" % human(total_before))
    print("=" * 62)

    def dump(title, group):
        if not group:
            return 0
        print("\n[%s]" % title)
        sub = 0
        for lvl, name, path, kind, size in sorted(group, key=lambda x: -x[4]):
            print("  %-52s %8s" % (name[:52], human(size)))
            sub += size
        print("  小计: %s" % human(sub))
        return sub

    s = dump("safe 级  纯缓存/日志, 删后自动重建", safe)
    r = dump("review 级  删后会重新下载或丢功能 (需 --aggressive)", rev)
    print("\n可释放合计: %s" % human(s + r))

    ids, note = deleted_session_ids()
    print("\n会话状态: %s, GUI 已删除但仍占磁盘 %d 个" % (note, len(ids)))

    if not args.apply:
        print("\n(dry-run, 未删除任何文件。加 --apply 执行; 加 --apply --aggressive 连 review 级一起清)")
        return 0

    freed, failed, truncated = do_remove(items, args.aggressive)
    total_after = dirsize(ROOT)
    print("\n已释放: %s" % human(freed))
    print("清理后总占用: %s" % human(total_after))
    if truncated:
        print("\n以下 %d 个文件被占用删不掉, 已截断为 0 字节 "
              "(空间已回收, 重启程序后重跑即可彻底清除):" % len(truncated))
        for p in truncated[:15]:
            print("  ~ %s" % shorten(p))
        if len(truncated) > 15:
            print("  ... 其余 %d 个" % (len(truncated) - 15))
    if failed:
        print("\n以下 %d 项清理失败 (退出 WorkBuddy 后重跑):" % len(failed))
        for p, e in failed[:15]:
            print("  - %s : %s" % (shorten(p), e))
        if len(failed) > 15:
            print("  ... 其余 %d 项" % (len(failed) - 15))
    return 0


if __name__ == "__main__":
    sys.exit(main())
