---
name: spray
description: >
  Web 目录/路径爆破工具 (ChainReactors spray)。基于 Go 编写的高性能路径扫描器，
  支持内置字典、规则引擎、递归扫描、指纹识别、敏感信息提取。 当用户要求目录爆破、路径扫描、web fuzzing、网站路径发现、dirsearch 替代、
  隐藏文件/目录发现 时触发此 skill。
agent_created: true
---

# spray — Web 路径爆破与目录扫描

## 工具位置

```
C:\HACK\1漏洞扫描工具\spray\spray_windows_amd64.exe
```

wiki: https://chainreactors.github.io/wiki/spray

## 核心使用原则

### 用户偏好 (必须遵守)

1. **默认字典**: 用户要求目录爆破时,**始终使用 `-d default`**(内置 9646 条综合字典),除非用户明确指定其他字典。
2. **忽略 WAF 封禁**: **始终追加 `--force`**,不因错误/WAF 拦截而中断扫描。
3. **输出文件**: 默认追加 `-f <target_name>.csv`(CSV 格式便于查看)。如用户未指定,用 `--auto-file` 自动生成。
4. **--finger --recon** 影响性能,除非用户明确要求指纹/信息提取,否则不开启。
5. **--crawl** 爬虫效果不佳,不建议主动使用。

### 默认命令模板

```bash
spray_windows_amd64.exe -u <URL> --force -d default -f <output_name>
```

## 常用场景

### 场景 1: 单 URL 目录爆破 (最常用)

```powershell
& "C:\HACK\1漏洞扫描工具\spray\spray_windows_amd64.exe" -u <URL> --force -d default -f result.csv
```

指定多个字典:
```powershell
spray_windows_amd64.exe -u <URL> --force -d default -d dir -f result.csv
```

### 场景 2: 批量 URL 扫描

```powershell
spray_windows_amd64.exe -l urls.txt --force -d default -f result.csv
```

### 场景 3: CIDR 网段 + 端口扫描

```powershell
spray_windows_amd64.exe -i 192.168.1.0/24 -p 80,443,8080 -d default --force
```

### 场景 4: 添加/排除扩展名

```powershell
# 追加扩展名
spray_windows_amd64.exe -u <URL> -d default --force -e jsp,jspx,php,asp
# 排除扩展名
spray_windows_amd64.exe -u <URL> -d default --force --exclude-extension jsp
```

### 场景 5: 带 Cookie/Headers 的认证扫描

```powershell
spray_windows_amd64.exe -u <URL> --force -d default -H "Cookie: session=xxx" -H "Authorization: Bearer xxx"
```

### 场景 6: 开启指纹识别 + 敏感信息提取 (慢但全面)

```powershell
spray_windows_amd64.exe -u <URL> --force -d default --finger --recon -f result.csv
```

### 场景 7: 自定义输出格式

```powershell
# CSV 输出
spray_windows_amd64.exe -u <URL> --force -d default -O csv -f result.csv
# JSON 输出
spray_windows_amd64.exe -u <URL> --force -d default -O json -f result.json
# 树形预览 (默认，stdout)
spray_windows_amd64.exe -u <URL> --force -d default -o tree
```

### 场景 8: 从断点恢复

```powershell
spray_windows_amd64.exe --resume stat.json
```

### 场景 9: 限速扫描 (低调模式)

```powershell
spray_windows_amd64.exe -u <URL> --force -d default --rate-limit 10 -T 10
```

## 内置字典速查

| 字典 | 条数 | 适用场景 |
|------|------|----------|
| `default` | 9646 | **通用综合 (默认)** |
| `dir` | 5152 | 目录专项 |
| `admin` | 1002 | 后台管理 |
| `java` | 1665 | Java Web 应用 |
| `springboot` | 306 | Spring Boot Actuator |
| `weblogic` | 312 | WebLogic |
| `common` | 115 | 通用常见文件 |
| `cgi` | 639 | CGI 脚本 |
| `js` | 153 | JS 文件/Map |
| `log` | 208 | 日志文件 |
| `swagger` | 54 | API 文档 |

使用 `-D` 等效于 `-d default`:
```powershell
spray_windows_amd64.exe -u <URL> --force -D
```

## 关键参数速记

| 参数 | 作用 | 常用值 |
|------|------|--------|
| `-u` | 目标 URL | `http://example.com` |
| `-l` | URL 列表文件 | `urls.txt` |
| `-i` | CIDR 网段 | `192.168.1.0/24` |
| `-p` | 端口范围 | `80,443,8080-8090` |
| `-d` | 字典 (可多次) | `default`, `dir`, `admin` |
| `-D` | 使用 default 字典 | — |
| `-e` | 追加扩展名 | `jsp,php,asp` |
| `-X` | HTTP 方法 | `GET`, `POST` |
| `-H` | 请求头 | `Cookie: ...` |
| `--proxy` | 代理 | `socks5://127.0.0.1:1080` |
| `--force` | 忽略错误/WAF | — |
| `--finger` | 指纹识别 | — |
| `--recon` | 敏感信息提取 | — |
| `--rate-limit` | 限速 | `10` (10次/秒) |
| `-T` | 超时(秒) | `5` (默认) |
| `-t` | 线程数/池 | `30` |
| `-f` | 输出文件名 | — |
| `-O` | 输出格式 | `csv`, `json` |
| `--resume` | 断点续扫 | `stat.json` |

## 执行与输出

运行命令后:
1. 实时展示进度条和发现的路径
2. 输出文件 (CSV/JSON) 写入当前目录
3. 自动生成 `stat.json` 用于断点恢复
4. 结果包含: URL、状态码、Content-Length、标题 (如有 fingerprint)

## 完整帮助与内置资源

内置字典、规则、提取器、指纹引擎的完整列表见: `references/full_help.md`

查看运行时版本:
```powershell
spray_windows_amd64.exe --print    # 列出所有内置资源
spray_windows_amd64.exe --version  # 版本号
spray_windows_amd64.exe --help     # 完整帮助
```
