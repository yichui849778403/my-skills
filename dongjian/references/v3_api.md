# 洞鉴 V3 API 参考（平台管理）

Base: `/api/v3/` | Auth: JWT Token 或 `token` header | Base: `/api/v3/` | Auth: JWT Token 或 `token` header

**注意**：V3 API 主要用于平台管理，渗透测试场景优先使用 V2 API（见 v2_api.md）。

## 认证

| Method | Path | 描述 |
|--------|------|------|
| POST | `/uauth/login/` | 用户登录，获取 JWT token |
| POST | `/uauth/token/verify/` | 验证 JWT token |

登录示例：
```json
POST /api/v3/uauth/login/
{"username": "admin", "password": "xxx"}
// 返回 JWT token
```

## 账户管理

| Method | Path | 描述 |
|--------|------|------|
| POST | `/account/role/list/` | 角色列表 |
| GET | `/account/role/{role_id}/` | 角色详情 |
| POST | `/account/role/{role_id}/` | 更新角色 |
| POST | `/account/role/create/` | 创建角色 |
| POST | `/account/user/list/` | 用户列表 |
| POST | `/account/user/create/` | 创建用户 |
| GET | `/account/user/detail/` | 当前用户信息 |
| POST | `/account/user/detail/` | 更新当前用户信息 |

## 组织单位（项目）

| Method | Path | 描述 |
|--------|------|------|
| POST | `/server/project/list/` | 项目列表 |
| POST | `/server/project/create/` | 创建项目 |
| GET | `/server/project/{project_id}/` | 项目详情 |
| POST | `/server/project/{project_id}/` | 更新项目 |
| POST | `/server/project/delete/` | 删除项目 |
| GET | `/server/project/user-accessible/` | 当前用户可访问的项目 |

## 引擎管理

| Method | Path | 描述 |
|--------|------|------|
| POST | `/engine/tags/list/` | 引擎标签列表 |
| POST | `/engine/tags/create/` | 创建引擎标签 |
| POST | `/engine/tags/update/{tag_id}/` | 更新引擎标签 |
| POST | `/engine/tags/delete/` | 删除引擎标签 |

## 基础功能

| Method | Path | 描述 |
|--------|------|------|
| GET | `/server/api_alive/` | 健康检查（无需认证） |
| GET | `/server/license_info/` | 许可证信息 |
| GET | `/server/license_status/` | 许可证状态 |
| POST | `/server/read_license/` | 读取许可证 |
| POST | `/server/upload_license/` | 上传许可证 |
| POST | `/server/reset_password/` | 重置admin密码 |

## 产品自定义 (OEM)

| Method | Path | 描述 |
|--------|------|------|
| GET | `/oem/get_oem/` | 获取OEM自定义信息 |
| POST | `/oem/update_oem/` | 更新OEM自定义信息 |

## 通用过滤格式

V3 API 的 filter 请求格式：
```json
{
  "filters": {
    "field_name": "value",
    "field__in": [1, 2],
    "field__contains": "search"
  },
  "page": 1,
  "page_size": 20,
  "ordering": ["-created_time"],
  "fields": ["id", "name"]
}
```

## 通用响应格式

```json
{
  "err": "",
  "msg": "操作成功",
  "data": {...}  // 或 {"count": N, "items": [...]}
}
```
