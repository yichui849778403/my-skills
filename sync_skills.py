# -*- coding: utf-8 -*-
"""One-click sync: local custom skills -> this GitHub repo.

Scans %USERPROFILE%\\.workbuddy\\skills for skills marked `agent_created: true`
(i.e. skills authored locally, not third-party marketplace ones) and mirrors
them into this repo, then commits and pushes.

Preserves the `disable-model-invocation` frontmatter that newer WorkBuddy
builds strip out during their automatic field migration, so the setting is
not lost when restoring this backup on a fresh machine.
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.expanduser("~"), ".workbuddy", "skills")

# Skills kept out of the repo even if locally present (third-party / marketplace).
EXCLUDE_SKILLS = {"grill-me", "ppt-master"}
EXCLUDE_DIRS = {"__pycache__", ".git", ".idea", ".vscode"}

# Fallback committer identity, used only when the repo has no configured one
# (e.g. a fresh clone on a new machine).
AUTHOR = [
    "-c", "user.name=huzhichao",
    "-c", "user.email=huzhichao@users.noreply.github.com",
]

# Original `disable-model-invocation` values, re-injected on sync.
PRESERVE = {
    "app-pentest": "true",
    "data-classification-risk-assessment": "true",
    "dongjian": "true",
    "pentest-report": "true",
    "ppt-notes-polish": "false",
    "retest-report": "true",
}


def read_norm(path):
    with open(path, "rb") as f:
        raw = f.read()
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def write_norm(path, data):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def is_local_skill(path):
    """A locally-authored skill: SKILL.md exists and frontmatter has agent_created: true."""
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.isfile(skill_md):
        return False
    try:
        head = read_norm(skill_md)[:800].decode("utf-8", "ignore")
    except Exception:
        return False
    return "agent_created: true" in head


def discover():
    found = []
    for name in sorted(os.listdir(SRC)):
        p = os.path.join(SRC, name)
        if not os.path.isdir(p) or name in EXCLUDE_SKILLS:
            continue
        if is_local_skill(p):
            found.append(name)
    return found


def inject_field(text, field, value):
    s = text.decode("utf-8")
    if field in s:
        return text
    lines = s.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            break
        if lines[i].startswith("agent_created:"):
            lines.insert(i + 1, "%s: %s" % (field, value))
            return "\n".join(lines).encode("utf-8")
    return text


def copy_skill(skill):
    src = os.path.join(SRC, skill)
    dst = os.path.join(REPO, skill)
    n = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            sp = os.path.join(root, fn)
            rel = os.path.relpath(sp, src)
            write_norm(os.path.join(dst, rel), read_norm(sp))
            n += 1
    skill_md = os.path.join(dst, "SKILL.md")
    if skill in PRESERVE and os.path.isfile(skill_md):
        data = read_norm(skill_md)
        new = inject_field(data, "disable-model-invocation", PRESERVE[skill])
        if new != data:
            write_norm(skill_md, new)
    return n


def git(*args):
    return subprocess.run(
        ["git"] + list(args), cwd=REPO,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def main():
    if not os.path.isdir(SRC):
        print("[error] local skills dir not found: %s" % SRC)
        return 1
    if not os.path.isdir(os.path.join(REPO, ".git")):
        print("[error] not a git repo: %s" % REPO)
        return 1

    skills = discover()
    if not skills:
        print("[error] no locally-authored skills found under %s" % SRC)
        return 1
    print("[info] skills to sync: %s" % ", ".join(skills))

    r = git("pull", "--ff-only")
    if r.returncode != 0:
        print("[warn] git pull failed or not needed, continue")

    for s in skills:
        print("[ok] %s (%d files)" % (s, copy_skill(s)))

    git("add", "-A")
    if git("diff", "--cached", "--quiet").returncode == 0:
        print("[info] nothing changed, skip commit/push")
        return 0

    msg = "sync skills: update to local latest"
    if len(sys.argv) > 1 and sys.argv[1].strip():
        msg = sys.argv[1].strip()
    r = git(*AUTHOR, "commit", "-m", msg)
    if r.returncode != 0:
        print("[error] commit failed")
        print(r.stdout or "", r.stderr or "")
        return 1

    for attempt in range(1, 6):
        r = git("push", "origin", "main")
        if r.returncode == 0:
            print("[done] pushed (attempt %d)" % attempt)
            return 0
        print("[warn] push attempt %d failed, retrying..." % attempt)
    print("[error] push failed after 5 attempts, check network / VPN then re-run")
    return 1


if __name__ == "__main__":
    sys.exit(main())
