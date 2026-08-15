---
name: dongjian
description: 读取长亭洞鉴扫描结果。用户在 Web UI 手动扫描，完成后触发此 skill 拉取漏洞列表，辅助渗透测试。
agent_created: true
disable-model-invocation: true
---

# 洞鉴 — 读取扫描结果

用户在洞鉴 Web UI 手动创建和执行扫描，完成后告诉我，我拉取漏洞结果呈现。

## 连接

- Base URL: `https://[fe80::1]`
- Auth: `token: mNvf6eCRe2XBC1zjsiLABtXIZEmBYOlvwU9McjcW`
- Project ID: `1`
- curl 必须加 `-k`（自签名证书）

## 工作流

### 1. 查最近任务

```bash
curl -k -s -X POST "https://[fe80::1]/api/v2/xprocess_lite/filter/" \
  -H "token: mNvf6eCRe2XBC1zjsiLABtXIZEmBYOlvwU9McjcW" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"project_id":1},"page":1,"page_size":10,"ordering":["-id"]}'
```

取 `data.result[]`，关注：`id`(xprocess_id)、`status`、`basic_setting.taskName`、`vuln_result_sum`。

多个已完成任务 → 列出让用户选；只有一个 → 直接读。

### 2. 读漏洞

```bash
curl -k -s -X POST "https://[fe80::1]/api/v2/result/filter/" \
  -H "token: mNvf6eCRe2XBC1zjsiLABtXIZEmBYOlvwU9McjcW" \
  -H "Content-Type: application/json" \
  -d '{"filters":{"project_id":1,"xprocess_id":<ID>},"result_type":"vuln","page":1,"page_size":100,"ordering":["-severity"]}'
```

⚠️ 核心坑：
- 必须用 `/result/filter/`（不是 `/vuln/filter/`）才能按任务过滤
- `result_type` 必填，小写：`"vuln"` / `"host"` / `"service"` / `"website"`
- 响应字段：`data.count` + `data.result`（不是 `total`/`content`）
- 不需要 `limit`/`offset`

### 3. 呈现

先等级汇总，再逐条列出：

```
| 等级 | 数量 |
| CRITICAL | N |
| HIGH | N |
| MEDIUM | N |
| LOW | N |
```

按严重度从高到低，每条：名称、目标、简述。需要深入某个漏洞时再拉详情。

### 4. 可选：生成报表

```bash
curl -k -s -X POST "https://[fe80::1]/api/v2/report/" \
  -H "token: mNvf6eCRe2XBC1zjsiLABtXIZEmBYOlvwU9McjcW" \
  -H "Content-Type: application/json" \
  -d '{"xprocess_id":<ID>,"template_id":2,"report_name":"扫描报告","report_format":"pdf"}'
```

模板：`2`=标准 / `18`=全量。格式：`pdf` / `word` / `html`。
