---
name: nuclei
description: Nuclei v3.11.0 漏洞扫描器。基于 YAML 模板的快速漏洞扫描引擎，支持
  HTTP/DNS/TCP/SSL/JavaScript/Headless 等多种协议，内置约 13,531 个社区 PoC
  模板。适用于渗透测试中的漏洞验证、批量扫描、CVE 检测、弱口令爆破、OOB 反连检测、Web
  指纹识别等场景。触发词：nuclei、nuclei扫描、漏洞验证、PoC扫描、CVE检测、nuclei模板。
agent_created: true
---

# Nuclei 漏洞扫描器 Skill

## 环境信息

所有路径均为当前环境的实际路径，直接使用即可，无需确认。

| 项目 | 路径 |
|------|------|
| **可执行文件** | `C:\HACK\1漏洞扫描工具\nuclei\nuclei.exe` |
| **模板仓库** | `C:\Users\84977\nuclei-templates` (v10.4.7, ~13,531 模板) |
| **配置文件** | `C:\Users\84977\AppData\Roaming\nuclei\config.yaml` |
| **报告配置** | `C:\Users\84977\AppData\Roaming\nuclei\reporting-config.yaml` |
| **忽略规则** | `C:\Users\84977\AppData\Roaming\nuclei\.nuclei-ignore` |

实际调用始终使用完整路径 `C:\HACK\1漏洞扫描工具\nuclei\nuclei.exe`。

## 智能扫描策略（AI 自动配置 — 最优先）

**用户给 URL → AI 自动拼最优命令，禁止裸 `-u` 全量跑。**

nuclei 扫描慢的根源：不加筛选直接跑全部 13,531 个模板。正确做法是按场景分层筛选。

### 固定基础参数（每次必加）

```
-as                    # 自动识别技术栈，只加载匹配模板（这是最快加速手段）
-s critical,high,medium  # 默认只扫中高危，跳过 info/low
-c 50 -bs 50 -rl 300   # 对授权渗透测试目标，适当提高并发
-stream                 # 实时输出，不用等全部跑完才看结果
-o <output_file>        # 保存结果到文件
```

### Web 渗透测试场景（用户最常用）

```powershell
# 标准 Web 扫描 — 自动技术栈匹配 + 中高危 + CVE
& "C:\HACK\1漏洞扫描工具\nuclei\nuclei.exe" -u <target> -as -s critical,high,medium -c 50 -bs 50 -rl 300 -stream -o scan_result.txt
```

### 场景参数动态调整规则

| 场景 | 参数调整 |
|------|----------|
| **用户赶时间/快速摸底** | `-s critical,high` 只扫高危 |
| **深度审计/写报告** | 保留 `medium`，加 `-jsonl` 输出详细数据 |
| **目标有 WAF/生产环境** | `-rl 50 -c 10` 降速防封 |
| **内网目标** | `-c 80 -bs 80 -rl 500` 内网带宽充足可加倍 |
| **用户指定了具体中间件** | 追加 `-templates\http\technologies\` 或 `-t templates\http\cves\` |
| **需要验证单个 CVE** | `-t <cve_yaml> -debug` |
| **怀疑有 SSRF/盲 RCE** | nuclei 默认已启用 interactsh OOB，无需额外参数 |
| **目标是 SPA/前后端分离** | 追加 `-pt http` 排除 headless 以外的非 HTTP 模板 |

### 扫描完后的标准动作

1. 读取 `-o` 输出文件，汇总发现的漏洞数量、严重级别分布
2. 对 critical/high 结果逐条解读，给出验证建议
3. 如果有 `-jsonl` 输出，提取 curl-command 给出复现命令

### 禁止行为

- ❌ 禁止裸 `nuclei -u target`（全量模板 12,658 个，慢且噪音大）
- ❌ 禁止不加 `-s` 筛选（等同于扫 info 级别，几千个低危告警无意义）
- ❌ 禁止不加 `-as` 或 `-t`（所有模板全灌）

## 常用命令模板

智能扫描策略已覆盖日常场景，以下仅保留特殊场景：

### JSON 输出（便于脚本处理）

```bash
C:\HACK\1漏洞扫描工具\nuclei\nuclei.exe -u <target_url> -as -s critical,high -jsonl -o result.jsonl
```

### Fuzz 模板（默认被忽略，需显式启用）

```bash
C:\HACK\1漏洞扫描工具\nuclei\nuclei.exe -u <target_url> -itags fuzz -s critical,high
```

### 调试单个模板

```bash
C:\HACK\1漏洞扫描工具\nuclei\nuclei.exe -u <target_url> -t C:\Users\84977\nuclei-templates\http\cves\CVE-XXXX-XXXX.yaml -debug
```

### 更新模板库

```bash
C:\HACK\1漏洞扫描工具\nuclei\nuclei.exe -ut
```

## 关键参数速查

### 目标 (-u / -l)

| 参数 | 说明 |
|------|------|
| `-u https://target.com` | 扫描单个目标 |
| `-l targets.txt` | 从文件读取目标列表（一行一个） |

### 过滤 (-s / -tags / -id)

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `-s` | 按严重程度筛选 | `info, low, medium, high, critical` |
| `-tags` | 按标签筛选 | `cve, xss, sqli, rce, lfi, ssrf, exposure` 等 |
| `-etags` | 排除指定标签 | 同上 |
| `-id` | 按模板 ID 执行 | 模板文件名/ID |
| `-eid` | 排除模板 ID | 同上 |

### 协议类型 (-pt)

| 值 | 说明 |
|------|------|
| `http` | HTTP 请求探测（最常用） |
| `dns` | DNS 探测 |
| `tcp` / `network` | TCP/网络协议探测 |
| `ssl` | SSL/TLS 证书探测 |
| `file` | 本地文件检测 |
| `headless` | 无头浏览器检测 |
| `javascript` | JS 协议探测 |
| `workflow` | 工作流 |

### 输出 (-o / -j / -jsonl / -me)

| 参数 | 说明 |
|------|------|
| `-o result.txt` | 文本输出 |
| `-jsonl` | JSON Lines 格式（实时） |
| `-je result.json` | JSON 格式导出 |
| `-me report.md` | Markdown 报告导出 |
| `-se report.sarif` | SARIF 格式导出 |
| `-silent` | 静默模式（仅输出结果） |
| `-nc` | 禁用彩色输出 |

### 并发与限速 (-c / -bs / -rl)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-rl 300` | 150 | 每秒最大请求数 |
| `-c 50` | 25 | 并行模板数 |
| `-bs 50` | 25 | 每个模板最大并行检测数 |

**渗透测试建议**：测试环境可适当调高并发 (例如 `-c 50 -bs 50 -rl 300`)，内网环境可加倍。生产环境使用默认值避免触发 WAF。

### 代理 (-p)

```bash
C:\HACK\1漏洞扫描工具\nuclei\nuclei.exe -u <target> -p http://127.0.0.1:8080
```

### 调试 (-debug / -v)

| 参数 | 说明 |
|------|------|
| `-debug` | 显示所有请求和响应 |
| `-v` | 详细模式 |
| `-vv` | 额外详细模式 |
| `-stats` | 显示扫描统计 |

## 默认忽略的标签

从 `.nuclei-ignore` 可知，以下标签默认跳过（可能导致误报或侵入性操作）：

| 标签 | 原因 |
|------|------|
| `dos` | 拒绝服务，破坏性 |
| `local` | 本地检测，远程无效 |
| `fuzz` | 模糊测试，高噪音 |
| `bruteforce` | 暴力破解，风险高 |
| `txt-service` | 文本服务探针 |

需要使用这些标签时，显式添加 `-itags <tag>` 参数。

## 模板目录结构

```
C:\Users\84977\nuclei-templates\
├── http/
│   ├── cves/                    # CVE PoC (~5000+)
│   ├── vulnerabilities/         # SQLi, XSS, SSRF, LFI, RCE...
│   ├── misconfiguration/        # .git, .env, debug endpoint...
│   ├── exposures/               # 备份文件, 配置文件泄露
│   ├── technologies/            # WordPress, Tomcat, Jenkins...
│   ├── default-logins/          # 默认口令
│   └── fuzzing/                 # 模糊测试
├── headless/                    # 无头浏览器检测
└── javascript/                  # JS 协议探测
```

## 注意事项

1. **结果确认**：nuclei 的结果需人工验证，每个 finding 包含 `request`/`response`，`-debug` 可查看交互细节
2. **代理联动**：`-p http://127.0.0.1:8080` 配合 Burp Suite 观察流量
3. **严禁未授权扫描**：扫描流量与所选模板数量直接相关
4. nuclei.exe 单文件约 121MB，无需额外依赖
5. `-ut` 更新模板需 GitHub 网络可达，`.nuclei-ignore` 由 nuclei 自动管理不要手动编辑

## 输出结果解读

终端格式：`[severity] [url] [template-id] detail`

JSONL 关键字段：`template-id`, `info.severity`, `host`, `matched-at`, `request`, `response`, `curl-command`
