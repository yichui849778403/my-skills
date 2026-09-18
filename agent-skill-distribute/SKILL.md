---
name: agent-skill-distribute
description: 把已装好的 skill 分发/同步到本机其他 AI agent（WorkBuddy、QwenWork、Codex 等），或给某个 agent 新装一个技能。触发词：给别的 agent 装技能、给 codex 拷一份、给 qwenwork 也装、分发 skill、同步技能到其他 agent。
agent_created: true
---

# 多 Agent 技能分发

把同一个 skill 分发给本机多个 AI agent。本质是"目录 + SKILL.md"的复制，难点只在**各家的技能目录不同**。

## 本机 agent 技能目录

| Agent | 技能目录 | 备注 |
|---|---|---|
| WorkBuddy | `C:\Users\84977\.workbuddy\skills` | 当前主力 |
| QwenWork（千问办公） | `C:\Users\84977\.qwenworkcn\skills` | 认目录名 `folderName`，可用 frontmatter 的 `disabled: true` 停用 |
| Codex | `C:\Users\84977\.codex\skills` | `.system` 是内置技能目录，用户技能直接放根目录 |
| 通用共享位 | `C:\Users\84977\.agents\skills` | 未使用；也是 dashi-ppt 安装器优先探测的位置 |

各 agent 只扫自己的目录，互不可见——装在一处，另一处看不到。

## 分发流程

1. **确认源头存在、目标不存在**
   ```bash
   SRC="/c/Users/84977/.workbuddy/skills/<skill-name>"
   DST="/c/Users/<目标agent>/.<目标目录>/skills/<skill-name>"
   [ -e "$DST" ] && echo "已存在，别覆盖"
   ```
2. **整目录复制（含子目录）**
   ```bash
   cp -r "$SRC" "$DST"
   ```
3. **校验一致性**（不要只看目录存不存在）
   ```bash
   python -c "
   import os,hashlib
   for p in [r'<源>', r'<目标>']:
       n=0;sz=0;files=[]
       for root,dirs,fs in os.walk(p):
           for f in fs:
               fp=os.path.join(root,f); n+=1; sz+=os.path.getsize(fp)
               files.append(os.path.relpath(fp,p))
       files.sort()
       print(p, n, f'{sz/1024/1024:.1f}MB', hashlib.sha256('\n'.join(files).encode()).hexdigest()[:12])
   "
   ```
   两边的文件数、总大小、清单指纹应当完全一致。

## 用官方安装器装（带 npm 分发的 skill）

比手工复制更规范（原子替换、处理旧版迁移、自动写 `.npmrc`）：

```bash
npx -y --registry=https://registry.npmmirror.com <包名>@latest --dir "<目标技能根目录>"
```

**必须显式 `--dir`**：多数安装器只探测 `~/.agents`、`~/.claude`、`~/.codex`、`~/.config/agents`，**不含 WorkBuddy 和 QwenWork 的目录**，不加参数会装错地方。

## 注意事项

- **副本互相独立**：更新要每个位置各跑一遍；源改了不会自动同步到副本。
- **依赖各装一份**：带 `node_modules` 的 skill（如 dashi-ppt）依赖不随包下发，哪边先用哪边自己 install，磁盘会成倍增长。
- **重启才对当前会话生效**：agent 的技能列表一般启动时加载。
- **判断目标 agent 认什么格式**：看它目录里已有的技能——有 SKILL.md 就能用；只有 SKILL.md、无附加元数据文件，说明纯目录即可被识别。
- **目录联接（junction）慎用**：`mklink /J` 能省空间，但带自动更新逻辑的安装器对 junction 做 rename/rmSync 替换时行为不稳定，优先用独立复制。
- **别放同一处给多个 agent 直读**：同一份代码被两个 agent 同时跑预览/构建类服务，端口会撞。
