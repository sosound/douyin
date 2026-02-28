# DouK-Downloader Web API 接口详细文档

> 基于项目源码整理，适用于 `http://127.0.0.1:5555` 服务

---

## 通用说明

- **请求头**：如需 token 校验，在 Header 中传入 `token`
- **基础 URL**：`http://127.0.0.1:5555`
- **通用参数**（多数接口继承）：
  - `cookie`：可选，平台 Cookie
  - `proxy`：可选，代理地址
  - `source`：可选，默认 `false`；为 `true` 时返回原始响应数据

---

## 一、项目 / 配置

### 1.1 GET `/token` — 测试令牌有效性

**Headers**：`token`（如已配置）

**响应示例**：
```json
{
  "message": "验证成功！",
  "data": null,
  "params": null,
  "time": "2025-02-28 12:00:00"
}
```

---

### 1.2 GET `/settings` — 获取项目全局配置

**响应**：返回 `Settings` 完整配置对象

---

### 1.3 POST `/settings` — 更新项目全局配置

**请求体**：仅需传入要更新的字段，支持部分更新

**响应**：返回更新后的完整配置

---

## 二、抖音接口

### 2.1 POST `/douyin/share` — 解析分享链接

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | ✅ | 包含分享链接的字符串 |
| proxy | string | | 代理地址 |

**响应**：
```json
{
  "message": "请求链接成功！",
  "url": "https://v.douyin.com/xxx 解析后的完整链接",
  "params": { "text": "...", "proxy": "" },
  "time": "..."
}
```

---

### 2.2 POST `/douyin/detail` — 获取单个作品数据（含下载地址）

**请求体**：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| detail_id | string | ✅ | - | 作品 ID（从链接中提取，如 `7201234567890123456`） |
| cookie | string | | "" | 抖音 Cookie |
| proxy | string | | "" | 代理 |
| source | bool | | false | 为 true 时返回原始 API 响应 |

**响应**（`source=false` 时）：
```json
{
  "message": "获取数据成功！",
  "data": {
    "type": "视频 | 图集 | 实况",
    "id": "作品ID",
    "desc": "作品描述",
    "create_time": "发布时间戳",
    "author": "作者信息",
    "statistics": { "digg_count": 0, "comment_count": 0, ... },
    "downloads": ["https://...无水印视频/图集下载地址"],
    "static_cover": "https://...静态封面",
    "dynamic_cover": "https://...动态封面"
  },
  "params": { ... },
  "time": "..."
}
```

---

### 2.3 POST `/douyin/account` — 获取账号作品列表

**请求体**：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| sec_user_id | string | ✅ | - | 账号 sec_uid |
| tab | string | | "post" | `post`=发布 / `favorite`=喜欢 / `collection`=收藏 |
| earliest | string/int/float | | null | 作品最早发布日期 |
| latest | string/int/float | | null | 作品最晚发布日期 |
| pages | int | | null | 最大请求次数（仅喜欢页有效） |
| cursor | int | | 0 | 游标 |
| count | int | | 18 | 每页数量，需 > 0 |
| cookie | string | | "" | Cookie |
| proxy | string | | "" | 代理 |
| source | bool | | false | 是否返回原始数据 |

---

### 2.4 POST `/douyin/mix` — 获取合集作品

**请求体**：`mix_id` 与 `detail_id` 二选一

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| mix_id | string | | null | 合集 ID |
| detail_id | string | | null | 属于该合集的任一作品 ID |
| cursor | int | | 0 | 游标 |
| count | int | | 12 | 每页数量，需 > 0 |
| cookie | string | | "" | Cookie |
| proxy | string | | "" | 代理 |
| source | bool | | false | 是否返回原始数据 |

---

### 2.5 POST `/douyin/live` — 获取直播数据

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| web_rid | string | ✅ | 直播 web_rid |
| cookie | string | | Cookie |
| proxy | string | | 代理 |
| source | bool | | 是否返回原始数据 |

**响应 data 包含**：`flv_pull_url`、`hls_pull_url_map`、直播标题、主播信息等

---

### 2.6 POST `/douyin/comment` — 获取作品评论

**请求体**：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| detail_id | string | ✅ | - | 作品 ID |
| pages | int | | 1 | 最大请求页数，需 > 0 |
| cursor | int | | 0 | 游标 |
| count | int | | 20 | 每页评论数，需 > 0 |
| count_reply | int | | 3 | 每条评论的回复数，需 > 0 |
| reply | bool | | false | 是否拉取回复 |
| cookie | string | | "" | Cookie |
| proxy | string | | "" | 代理 |
| source | bool | | false | 是否返回原始数据 |

---

### 2.7 POST `/douyin/reply` — 获取评论回复

**请求体**：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| detail_id | string | ✅ | - | 作品 ID |
| comment_id | string | ✅ | - | 评论 ID |
| pages | int | | 1 | 最大请求页数 |
| cursor | int | | 0 | 游标 |
| count | int | | 3 | 每页数量 |
| cookie | string | | "" | Cookie |
| proxy | string | | "" | 代理 |
| source | bool | | false | 是否返回原始数据 |

---

### 2.8 POST `/douyin/search/general` — 综合搜索

**请求体**：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| keyword | string | ✅ | - | 搜索关键词 |
| pages | int | | 1 | 总页数，需 > 0 |
| offset | int | | 0 | 起始页码，≥ 0 |
| count | int | | 10 | 每页数量，5–20 |
| sort_type | int | | 0 | 0=综合 1=最多点赞 2=最新发布 |
| publish_time | int | | 0 | 0=不限 1=一天 7=一周 180=半年 |
| duration | int | | 0 | 0=不限 1=1分钟 2=5分钟 3=15分钟 |
| search_range | int | | 0 | 搜索范围 |
| content_type | int | | 0 | 内容形式 |
| cookie | string | | "" | Cookie |
| proxy | string | | "" | 代理 |
| source | bool | | false | 是否返回原始数据 |

---

### 2.9 POST `/douyin/search/video` — 视频搜索

**请求体**：与综合搜索类似，无 `content_type`，其余参数含义相同

---

### 2.10 POST `/douyin/search/user` — 用户搜索

**请求体**：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| keyword | string | ✅ | - | 搜索关键词 |
| pages | int | | 1 | 总页数 |
| offset | int | | 0 | 起始页码 |
| count | int | | 10 | 每页数量 |
| douyin_user_fans | int | | 0 | 粉丝数量筛选 |
| douyin_user_type | int | | 0 | 用户类型 |
| cookie | string | | "" | Cookie |
| proxy | string | | "" | 代理 |
| source | bool | | false | 是否返回原始数据 |

---

### 2.11 POST `/douyin/search/live` — 直播搜索

**请求体**：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| keyword | string | ✅ | - | 搜索关键词 |
| pages | int | | 1 | 总页数 |
| offset | int | | 0 | 起始页码 |
| count | int | | 10 | 每页数量 |
| cookie | string | | "" | Cookie |
| proxy | string | | "" | 代理 |
| source | bool | | false | 是否返回原始数据 |

---

## 三、TikTok 接口

### 3.1 POST `/tiktok/share` — 解析分享链接

**请求体**：同 `/douyin/share`（`text`、`proxy`）

---

### 3.2 POST `/tiktok/detail` — 获取单个作品数据

**请求体**：同 `/douyin/detail`（`detail_id`、`cookie`、`proxy`、`source`）

---

### 3.3 POST `/tiktok/account` — 获取账号作品

**请求体**：同 `/douyin/account`（`sec_user_id` 为 TikTok 的 secUid，其余参数一致）

---

### 3.4 POST `/tiktok/mix` — 获取合辑作品

**请求体**：

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| mix_id | string | ✅ | - | TikTok 合辑 ID |
| cursor | int | | 0 | 游标 |
| count | int | | 30 | 每页数量，需 > 0 |
| cookie | string | | "" | TikTok Cookie |
| proxy | string | | "" | 代理 |
| source | bool | | false | 是否返回原始数据 |

---

### 3.5 POST `/tiktok/live` — 获取直播数据

**请求体**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| room_id | string | ✅ | TikTok 直播 room_id |
| cookie | string | | Cookie |
| proxy | string | | 代理 |
| source | bool | | 是否返回原始数据 |

---

## 四、响应格式

### 成功响应（DataResponse）

```json
{
  "message": "获取数据成功！",
  "data": { ... },
  "params": { "请求参数回显" },
  "time": "2025-02-28 12:00:00"
}
```

### 失败响应

```json
{
  "message": "获取数据失败！",
  "data": null,
  "params": { ... },
  "time": "..."
}
```

### 链接类响应（UrlResponse）

```json
{
  "message": "请求链接成功！",
  "url": "https://...",
  "params": { ... },
  "time": "..."
}
```

---

## 五、快速示例

### 下载单个抖音作品

```python
import httpx

resp = httpx.post(
    "http://127.0.0.1:5555/douyin/detail",
    json={"detail_id": "7201234567890123456"},
)
data = resp.json()
if data["data"]:
    for url in data["data"]["downloads"]:
        # 用 httpx/requests 下载 url 到本地
        print(url)
```

### 获取作品评论

```python
resp = httpx.post(
    "http://127.0.0.1:5555/douyin/comment",
    json={"detail_id": "7201234567890123456", "pages": 2},
)
```

### 搜索视频

```python
resp = httpx.post(
    "http://127.0.0.1:5555/douyin/search/video",
    json={"keyword": "美食", "pages": 1, "sort_type": 1},
)
```
