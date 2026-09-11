---
name: workbuddy-cleanup
description: 清理 WorkBuddy 用户数据目录 ~/.workbuddy（Windows: C:\Users\<用户名>\.workbuddy）以释放磁盘空间。按安全等级分级扫描/删除缓存、日志、已删会话与市场插件包。触发词：清理 workbuddy、workbuddy 太占空间、.workbuddy 目录瘦身、清理缓存、清理日志、清理会话记录。
agent_created: true
---

# WorkBuddy 数据目录清理

## 触发条件

用户提到 `.workbuddy` 目录占空间、想清理缓存/日志/会话记录，或说"workbuddy 太大了"时使用。

## 核心认知（2026-08-29 实测，总占用约 695 MB）

`.workbuddy` 的空间分布极不均匀，**大头是运行时和市场缓存，会话数据只占零头**：

| 目录 | 体积 | 性质 |
|---|---|---|
| `binaries/` | 452 MB | 自带 Node 268M + PortableGit 132M + Python 53M。**系统已装 Node/Git/Python 时属重复占用，但删后 WorkBuddy 可能自动重下 → 默认不动** |
| `plugins/` | 153 MB | 其中 `cache/workbuddy-builtin/weixinpay` 40M（微信支付插件，几乎用不到）、`marketplaces/.../external_plugins` 25M（市场里未安装的插件预览包） |
| `connectors-marketplace/` | 31 MB | 市场全量 connector 的本地副本，**不等于你已安装的**（已装的在 `connectors/`） |
| `security/threat-database/` | 21 MB | 威胁特征库，删后安全检查功能会重下或失效 |
| `app/session/` | 17 MB | Electron 磁盘缓存，纯缓存 |
| `logs/` | 13 MB | **每天 4~6 MB，是最强累积源**，一个月不清约 150 MB |
| `traces/`、`shell-snapshots/` | 约 1.5 MB | 按进程 PID / 按命令累积，只增不减 |
| `projects/` | 约 0.3 MB | 会话 jsonl。**GUI 里删掉的会话，jsonl 仍在磁盘上** |

## 清理分级

### safe 级（随时可删，删后自动重建，无功能损失）
- `logs/` 下按日期目录（保留最近 2 天）、根日志（含 `daemon.old.log`/`main.old.log`/`renderer.old.log` 轮转日志，单个就 5~10 MB）、`sandbox`/`migration`/`Crash-Log`/`startup`/`update`/`Diagnostics`/`editor_sdk`
- `app/session/` 下 Cache、GPUCache、Code Cache、DawnWebGPUCache、DawnGraphiteCache、DIPS、Network、WebStorage、Shared Dictionary、SharedStorage、Partitions
- `traces/`、`shell-snapshots/`
- `cache/acc-product-config-v3.json`
- `pending-telemetry/*.reported`、`audit-log/*.jsonl`
- `projects/` 下 **GUI 已删除会话** 的 `.jsonl`（依据 `workbuddy.db` 里 `sessions.deleted_at` 非空判定）

### review 级（能省大空间，但删后会重新下载或丢功能，需 `--aggressive`）
- `plugins/cache/workbuddy-builtin/weixinpay`（40 MB）
- `connectors-marketplace/`（31 MB）
- `plugins/marketplaces/codebuddy-plugins-official/external_plugins`（25 MB）
- `security/threat-database/`（21 MB）

### 绝对不能碰
- `binaries/`（删了可能触发重新下载，反而更慢）
- `workbuddy.db`、`workbuddy.db-wal/-shm`、`edge-sync-mapping-v*.db*`（SQLite 数据与预写日志，运行中删会损坏）
- `memory/`、`skills/`、`settings.json`、`mcp.json`、`connectors/`、`storage/`、`local_storage/`、`plans/`、`workspace/`
- `MEMORY.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`

## 执行方式

脚本：`~/.workbuddy/skills/workbuddy-cleanup/scripts/cleanup.py`

```bash
# 1) 先扫描，不删任何文件
python cleanup.py

# 2) 确认无误后执行 safe 级
python cleanup.py --apply

# 3) 想连 review 级一起清（接受重新下载）
python cleanup.py --apply --aggressive

# 只保留最近 5 天日志
python cleanup.py --apply --keep-logs 5
```

## 重要注意事项

1. **先退出 WorkBuddy 再删**：程序正在写的日志文件在 Windows 上删不掉，脚本会跳过并列出失败项，退出后重跑即可。
   - 脚本已内置兜底：删不掉的文件会自动**截断为 0 字节**先把空间回收，只剩空壳，重启后重跑即彻底清除。所以运行时清理同样有效，只是会留下空文件。
   - `shutil.rmtree` **必须传 `onerror`**，否则碰到第一个被占用的文件就整体中止，同目录下其他本来能删的文件会全部残留（2026-09-02 修掉这个 bug，4 个日志目录因此各剩一堆文件）。
2. **先 dry-run 再 apply**：任何一次清理都先跑不带 `--apply` 的版本，把清单给用户看，尤其是会话 jsonl——**GUI 删错的会话在这里还有最后一次找回机会**。
3. **会话清理用 db 判定，不要手工猜**：`sessions` 表 `deleted_at` 为空 = 存活，非空 = 用户已在 GUI 删除。只删后者对应的 `<session-id>.jsonl`。
4. 用户的产出文件在项目目录（如 `C:\AI工作项目目录`），**不在 `.workbuddy` 里**，清理不影响产出。

5. **Windows 上删文件报 `WinError 5 拒绝访问` 的定位流程**（2026-09-02 实测）：
   - 先排除只读属性：`os.stat(p).st_mode & stat.S_IWRITE`。文件是 `0666` 却仍报错 → 是被进程**独占打开**（句柄未带 `FILE_SHARE_DELETE`），不是权限问题。
   - 再 `os.rename(p, p + ".tmp")` 试改名：改名也失败 ⇒ 确认句柄占用；改名成功 ⇒ 只是删除被拦。
   - **截断兜底**：这类文件通常仍可 `open(p, "r+b").truncate(0)`，截断成功即等于回收了空间（日志类文件的最优解）。
   - 想查占用者用 `psutil.process_iter()` + `proc.open_files()`，但**无管理员权限时约 2/3 进程会 AccessDenied**（本机 287 个进程里 181 个扫不到），SYSTEM 级进程（Defender 等）根本定位不到。**别在这上面耗时间**，按占用处理即可，重启程序后自然可删。
   - 旁证线索：日志目录下的 `sdk/conversations.zip.lock`（空目录）+ `conversations.zip.tmp-<pid>-<时间戳>` 是每天 00:00 的日志归档任务产物；若其中的 PID 已退出，说明是僵尸锁，随日志一并清掉即可。

## 清理频率建议

每月一次 `python cleanup.py --apply` 即可；`--aggressive` 半年一次或空间告急时用。

## 目录外的更大目标（可选提醒）

- `C:\Users\<用户名>\AppData\Local\Programs\WorkBuddy` 约 1.2 GB（应用本体，`ffmpeg.dll.bak` 3 MB 是更新残留可删，其余别动）
- `C:\Users\<用户名>\AppData\Local\WorkBuddy\logs` 约 11 MB（安装/更新日志，可删）
