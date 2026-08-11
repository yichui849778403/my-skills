# 洞鉴 V2 API 详细参考

Base: `/api/v2/` | Auth: `token` header

## 通用约定

- 所有 POST filter 接口支持分页：`{"filters": {...}, "page": 1, "page_size": 20, "ordering": ["-id"]}`
- **绝大多数 filter 接口还需额外传 `limit` 和 `offset`**（与 `page`/`page_size` 并存），只有 `/result/filter/` 例外
- `/result/filter/` 必须传 `result_type`（小写值如 `"vuln"`），不需要 `limit`/`offset`
- 列表响应格式**因接口而异**：
  - `/plan/filter/`、`/result/filter/`：`data.count` + `data.result`
  - `/vuln/filter/`、`/website/filter/` 等：`data.total` + `data.content`
- 单条响应格式：`{"err":"","msg":"操作成功","data":{...}}`
- 错误响应：`{"err":"ERROR_CODE","msg":"错误描述","data":null}`

---

## 工作区 (Project)

| Method | Path | 描述 |
|--------|------|------|
| GET | `/project/` | 获取工作区列表（需 `?limit=N`） |
| POST | `/project/` | 创建工作区 |
| POST | `/project/filter/` | 分页查询工作区 |
| GET | `/project/{id}/` | 获取工作区详情 |
| POST | `/project/{id}/` | 更新工作区 |

创建工作区示例：
```json
{"name": "项目名称", "full_name": "完整名称", "remark": "备注", "parents_id": null}
```

---

## 策略模板 (Template)

| Method | Path | 描述 |
|--------|------|------|
| GET | `/template/summary/` | 获取模板摘要列表 |
| GET | `/template/` | 获取所有模板（含策略详情） |
| GET | `/template/{id}/` | 获取指定模板详情 |

---

## 任务计划 (Plan) ⭐核心

| Method | Path | 描述 |
|--------|------|------|
| POST | `/plan/filter/` | 分页查询扫描计划 |
| GET | `/plan/{id}/` | 获取计划详情 |
| DELETE | `/plan/{id}/` | 删除计划 |
| POST | `/plan/create/` | 创建扫描计划 |
| POST | `/plan/update/` | 更新扫描计划 |
| POST | `/plan/stop/` | 停止计划 |
| POST | `/plan/execute/` | 执行计划（手动触发） |

### 创建扫描计划请求体

```json
{
  "name": "计划名称",
  "project_id": 1,
  "template_id": 1,
  "target": {
    "type": "manual",   // manual | file
    "manual": {
      "ip_list": ["192.168.1.0/24"],
      "website_list": ["https://example.com"],
      "domain_list": ["example.com"]
    }
  },
  "schedule": {
    "type": "once"  // once | daily | weekly | monthly
  },
  "engine_ids": [1],
  "remark": "备注"
}
```

`type` 枚举：`manual`（手动输入）/ `file`（文件导入）

### 执行/停止计划

```json
// 执行
{"plan_ids": [1, 2]}

// 停止
{"plan_ids": [1, 2]}
```

---

## 任务配置

### 扫描插件
| Method | Path | 描述 |
|--------|------|------|
| POST | `/plugin/filter/` | 查询内置扫描插件 |
| POST | `/custom_plugin/filter/` | 查询自定义插件 |
| GET | `/custom_plugin/{id}/` | 获取自定义插件详情 |

### 扫描字典
| Method | Path | 描述 |
|--------|------|------|
| POST | `/scannerdict/` | 创建扫描字典 |
| DELETE | `/scannerdict/` | 删除扫描字典 |
| POST | `/scannerdict/filter/` | 查询扫描字典列表 |
| GET | `/scannerdict/{id}/` | 获取字典详情 |

### 主机凭据
| Method | Path | 描述 |
|--------|------|------|
| POST | `/host_credential/` | 创建主机凭据 |
| POST | `/host_credential/verify/` | 验证凭据 |

### 其他配置
| Method | Path | 描述 |
|--------|------|------|
| POST | `/portgroup/filter/` | 端口组列表 |
| POST | `/hostlogrule/filter/` | 主机日志规则 |
| POST | `/upload_file/` | 上传文件（目标文件等） |
| POST | `/engine/filter/` | 引擎列表 |
| GET | `/reverse_platform/{uuid}/` | 反连平台详情 |
| POST | `/reverse_platform/filter/` | 反连平台列表 |

---

## 白名单 (Whitelist)

| Method | Path | 描述 |
|--------|------|------|
| POST | `/whitelist/` | 创建白名单 |
| DELETE | `/whitelist/` | 删除白名单 |
| POST | `/whitelist/update/` | 更新白名单 |
| POST | `/whitelist/filter/` | 查询白名单列表 |
| GET | `/whitelist/{id}/` | 获取白名单详情 |

---

## 任务实例 (XProcess) ⭐核心

| Method | Path | 描述 |
|--------|------|------|
| POST | `/xprocess/filter/` | 分页查询任务实例 |
| GET | `/xprocess/{id}/` | 获取任务实例详情 |
| GET | `/xprocess/{id}/progress/` | 获取扫描进度 |
| GET | `/xprocess/{id}/info/` | 获取任务执行信息 |
| POST | `/xprocess/stop/` | 停止任务 |
| POST | `/xprocess/pause/` | 暂停任务 |
| POST | `/xprocess/resume/` | 恢复任务 |
| POST | `/xprocess/pause/stage/` | 暂停某个扫描阶段 |
| POST | `/xprocess/resume/stage/` | 恢复某个扫描阶段 |

### 查询过滤器常用参数

```json
{
  "filters": {
    "project_id": 1,
    "status": "running"  // pending/running/paused/stopped/finished/failed
  },
  "page": 1,
  "page_size": 10,
  "ordering": ["-created_time"]
}
```

### 任务实例响应字段

- `id`, `plan_id`, `project_id`
- `status`: pending / running / paused / stopped / finished / failed
- `progress`: 进度百分比
- `created_time`, `start_time`, `end_time`
- `template_name`: 使用的策略模板名

---

## 任务结果 (Result)

| Method | Path | 描述 |
|--------|------|------|
| POST | `/result/filter/` | 按任务实例查询扫描结果（**必须传 `result_type`**） |
| GET | `/result/{id}/` | 获取扫描结果详情 |

### result/filter 请求体

```json
{
  "filters": {
    "project_id": 1,
    "xprocess_id": 638
  },
  "result_type": "vuln",
  "page": 1,
  "page_size": 50,
  "ordering": ["-severity"]
}
```

- ⚠️ `result_type` **必填**，取值（小写）：`"vuln"`, `"host"`, `"service"`, `"website"`, `"webpage"`, `"domain"`, `"openapi"` 等
- ⚠️ result/filter **不需要** `limit`/`offset` 参数（与其它 filter 接口不同）
- 响应格式：`data.count` + `data.result`
- 这是**按扫描任务读取漏洞的首选方式**，能准确拿到某次扫描产出的所有漏洞

结果类型包括：HostResult, ServiceResult, ApplicationResult, DomainResult, WebsiteResult, WebpageResult, OpenapiResult, VulnResult 等。

---

## 基线管理

| Method | Path | 描述 |
|--------|------|------|
| POST | `/ssh_key/filter/` | SSH密钥列表 |
| POST | `/ssh_key/create/` | 创建SSH密钥 |
| POST | `/check_sets/filter/` | 检查项集列表 |
| POST | `/baseline/task/filter/` | 基线任务列表 |
| POST | `/baseline/task/create/` | 创建基线任务 |
| POST | `/baseline/task/stop/` | 停止基线任务 |
| POST | `/baseline/task/execute/` | 执行基线任务 |
| POST | `/process/item/filter/` | 基线检查项结果 |

---

## Web 资产 (Website)

| Method | Path | 描述 |
|--------|------|------|
| POST | `/website/` | 添加 Web 资产 |
| DELETE | `/website/` | 删除 Web 资产 `{"website_ids": [1]}` |
| POST | `/website/filter/` | 分页查询 Web 资产 |
| POST | `/website/filter/simple` | 简化查询 |
| GET | `/website/{id}/` | 获取 Web 资产详情 |
| POST | `/website/{id}/` | 更新 Web 资产 |
| GET | `/website/openapi/{id}/` | 获取 OpenAPI 详情 |

### 添加 Web 资产
```json
{
  "project_id": 1,
  "url": "https://example.com",
  "name": "示例站点",
  "remark": "备注"
}
```

---

## 主机资产 (IP)

| Method | Path | 描述 |
|--------|------|------|
| GET | `/ip/os/` | 获取操作系统列表 |
| POST | `/ip/` | 添加主机资产 |
| DELETE | `/ip/` | 删除主机资产 `{"ip_ids": [1]}` |
| POST | `/ip/filter/` | 分页查询主机资产 |
| GET | `/ip/{id}/` | 获取主机详情 |
| POST | `/ip/{id}/` | 更新主机资产 |

---

## 服务资产 (Service)

| Method | Path | 描述 |
|--------|------|------|
| GET | `/service/application_protocol/` | 获取应用协议列表 |
| POST | `/service/` | 添加服务资产 |
| DELETE | `/service/` | 删除服务资产 |
| POST | `/service/filter/` | 分页查询服务资产 |
| GET | `/service/{id}/` | 获取服务详情 |
| POST | `/service/{id}/` | 更新服务资产 |

---

## 域名资产 (Domain)

| Method | Path | 描述 |
|--------|------|------|
| POST | `/domain/` | 添加域名资产 |
| DELETE | `/domain/` | 删除域名资产 |
| POST | `/domain/filter/` | 分页查询域名资产 |
| POST | `/domain/filter/simple` | 简化查询 |
| GET | `/domain/{id}/` | 获取域名详情 |
| POST | `/domain/{id}/` | 更新域名资产 |

---

## 漏洞资产 (Vuln) ⭐核心

| Method | Path | 描述 |
|--------|------|------|
| GET | `/vuln/{id}/` | 获取漏洞详情 |
| POST | `/vuln/{id}/` | 更新漏洞状态 |
| POST | `/vuln/batch_update/` | 批量更新漏洞 |
| DELETE | `/vuln/` | 删除漏洞 `{"vuln_ids": [1]}` |
| POST | `/vuln/filter/` | 分页查询漏洞 |
| POST | `/vuln/retest/` | 单个漏洞复测 |
| POST | `/vuln/retest/batch/` | 批量漏洞复测 |
| POST | `/vuln/retest/batch/result/` | 批量复测结果查询 |
| GET | `/vuln/retest/{task_id}/` | 查询复测任务状态 |
| POST | `/vulnerability/average-fix-time` | 平均修复时间统计 |

### 漏洞过滤器常用参数

```json
{
  "filters": {
    "project_id": 1,
    "severity": "high",       // info/low/medium/high/critical
    "status": "unfixed",      // unfixed/fixed/ignored/retesting
    "definiteness": "confirmed", // confirmed/suspected/false_positive
    "vuln_name__contains": "SQL",
    "website_id": 1,
    "ip_id": 1
  },
  "page": 1,
  "page_size": 20,
  "ordering": ["-severity", "-updated_time"]
}
```

### 漏洞严重级别

- `info` - 信息
- `low` - 低危
- `medium` - 中危
- `high` - 高危
- `critical` - 严重

### 漏洞状态

- `unfixed` - 未修复
- `fixed` - 已修复
- `ignored` - 已忽略
- `retesting` - 复测中

### 更新漏洞状态

```json
{
  "status": "fixed",
  "remark": "已修复"
}
```

### 批量更新漏洞

```json
{
  "vuln_ids": [1, 2, 3],
  "update": {
    "status": "ignored",
    "remark": "误报"
  }
}
```

### 复测漏洞

```json
// 单个复测
{"vuln_id": 1}

// 批量复测
{"vuln_ids": [1, 2, 3]}
```

---

## 审计日志

| Method | Path | 描述 |
|--------|------|------|
| POST | `/auditlog/filter/` | 查询审计日志 |
| GET | `/auditlog/action/` | 获取操作类型列表 |

---

## 报表 (Report) ⭐

| Method | Path | 描述 |
|--------|------|------|
| POST | `/report/download/` | 下载报表（返回文件） |
| POST | `/report/` | 创建报表 |
| POST | `/report/template/filter/` | 查询报表模板 |
| POST | `/report/filter/` | 分页查询报表记录 |
| GET | `/report/{id}/` | 获取报表详情 |
| DELETE | `/report/{id}/` | 删除报表 `{"report_ids": [1]}` |

### 创建扫描任务报表

```json
{
  "xprocess_id": 1,
  "template_id": 2,
  "report_name": "测试报告",
  "report_format": "pdf"
}
```

### 报表模板（template_id）

| ID | 模板名 | template_type | 说明 |
|----|--------|--------------|------|
| 2 | 扫描任务报表模板 | XPROCESS | 标准扫描报告 |
| 18 | 扫描任务报表模板(全量) | XPROCESS | 全量报告（含全部细节） |
| 3 | 漏洞报表模板 | VULN | 仅漏洞列表 |
| 1 | 基线检查报表模板 | BASELINE_PROCESS | 基线检查 |
| 8 | 扫描任务对比报表模板 | TASK_COMPARE | 任务对比 |

- `report_format`: `"pdf"` / `"word"` / `"html"`
- 创建成功后返回 `data.id`（report_id），可用于后续下载

---

## 系统信息

| Method | Path | 描述 |
|--------|------|------|
| POST | `/engine/filter/` | 引擎列表 |
| DELETE | `/engine/{id}/` | 删除引擎 |
| GET | `/system/hosts/engine/{id}/` | 引擎 hosts 配置 |
| POST | `/system/hosts/engine/{id}/` | 更新引擎 hosts |
| GET | `/system/dns/engine/{id}/` | 引擎 DNS 配置 |
| POST | `/system/dns/engine/{id}/` | 更新引擎 DNS |
| GET | `/system/info/engine/{id}/` | 引擎系统信息 |
| GET | `/system/info/mgmt/` | 管理平台信息 |
| GET | `/system/info/services/` | 服务状态 |
| GET | `/vuln_library/info/` | 漏洞库信息 |

---

## 自定义POC

| Method | Path | 描述 |
|--------|------|------|
| POST | `/customtag/` | 创建自定义标签 |
| POST | `/upload/custompoc/` | 上传自定义POC文件 |
| POST | `/custompoc/` | 创建自定义POC |
| DELETE | `/custompoc/` | 删除自定义POC |
| POST | `/custompoc/filter/` | 查询自定义POC列表 |
| POST | `/custompoc/update/` | 更新自定义POC |
| GET | `/vuln_category/` | 获取漏洞分类 |

---

## 资产管理属性

| Method | Path | 描述 |
|--------|------|------|
| POST | `/business_system/` | 创建业务系统 |
| POST | `/business_system/filter/` | 查询业务系统列表 |
| GET | `/business_system/{id}/` | 业务系统详情 |
| POST | `/asset_tag/filter/` | 资产标签列表 |
| GET | `/asset_tag/{id}/` | 资产标签详情 |
| GET | `/asset_groups/{project_id}/` | 资产组列表 |
| POST | `/network_region/` | 创建网络区域 |
| POST | `/network_region/filter/` | 网络区域列表 |
| GET | `/network_region/{id}/` | 网络区域详情 |
| POST | `/location/filter/` | 物理位置列表 |
| GET | `/location/{id}/` | 物理位置详情 |

---

## 用户和角色

| Method | Path | 描述 |
|--------|------|------|
| POST | `/user/token/refresh/` | 刷新 API Token |
| POST | `/user/` | 创建用户 |
| POST | `/user/{id}/` | 更新用户 |
| DELETE | `/user/{id}/` | 删除用户 |
| POST | `/user/filter/` | 用户列表 |
| POST | `/account/reset_user_passwd/` | 重置用户密码 |
| POST | `/account/change_self_passwd/` | 修改自己的密码 |
| POST | `/role/` | 创建角色 |
| POST | `/role/filter/` | 角色列表 |

---

## 数据洞察 (Insight) ⭐统计

| Method | Path | 描述 |
|--------|------|------|
| POST | `/insight/asset/ip/total-count/` | 资产总数 |
| POST | `/insight/asset/ip/alive-count/` | 存活资产数 |
| POST | `/insight/asset/ip/deleted-count/` | 已删除资产数 |
| POST | `/insight/asset/ip/newly-added-count/` | 新增资产数 |
| POST | `/insight/asset/ip/continuing-count/` | 持续存在资产数 |
| POST | `/insight/asset/ip/scanned-count/` | 已扫描资产数 |
| POST | `/insight/asset/ip/risk-count/` | 风险资产数 |
| POST | `/insight/asset/ip/list/` | 资产列表(统计用) |
| POST | `/insight/vuln/total-count/` | 漏洞总数 |
| POST | `/insight/vuln/continuing-count/` | 持续存在漏洞数 |
| POST | `/insight/vuln/newly-discovered-count/` | 新发现漏洞数 |
| POST | `/insight/vuln/remediated-count/` | 已修复漏洞数 |
| POST | `/insight/vuln/list/` | 漏洞列表(统计用) |
| POST | `/insight/vuln/avg-fix-period/` | 平均修复周期 |
| POST | `/insight/xprocess/count/` | 扫描任务数统计 |
| POST | `/insight/xprocess/scanned-asset-count/` | 已扫描资产数统计 |

统计接口请求体示例：
```json
{"project_id": 1, "end_date": "2026-08-04"}
```

---

## 任务实例精简版

| Method | Path | 描述 |
|--------|------|------|
| POST | `/xprocess_lite/filter/` | 精简版任务列表（更快） |
