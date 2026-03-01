# DouK-Downloader API 说明（从 Swagger UI 存档提取）

> 来源：`DouK-Downloader - Swagger UI.webarchive`（与 http://82.156.100.59:5555/docs 或 http://source.galaxystream.online:5555/docs 内容一致）  
> Swagger UI 从 `url: '/openapi.json'` 加载规范；本列表从渲染后的 HTML 提取。

**更详细的接口说明（含请求体字段、类型、必填项）请查看：**

- **[DouK-Downloader-API-详细接口说明.md](./DouK-Downloader-API-详细接口说明.md)**（由 `openapi.json` 自动生成）
- 原始规范：**[douk-openapi.json](./douk-openapi.json)**（OpenAPI 3.1 完整 JSON）

## 基础信息

- **Base URL 示例**：`http://82.156.100.59:5555` 或 `http://source.galaxystream.online:5555`
- **OpenAPI 规范**：`{base}/openapi.json`
- **文档页**：`{base}/docs`

---

## 接口列表

| 路径 | 说明 |
|------|------|
| `GET /` | 访问项目 GitHub 仓库 |
| `GET/POST /token` | 测试令牌有效性 |
| `GET /settings` | 获取项目全局配置 |
| `POST /settings` | 更新项目全局配置 |

### 抖音 (Douyin)

| 路径 | 方法 | 说明 |
|------|------|------|
| `/douyin/share` | POST | 获取分享链接重定向的完整链接 |
| `/douyin/detail` | POST | 获取单个作品数据 |
| `/douyin/account` | POST | 获取账号作品数据 |
| `/douyin/mix` | POST | 获取合集作品数据 |
| `/douyin/live` | POST | 获取直播数据 |
| `/douyin/comment` | POST | 获取作品评论数据 |
| `/douyin/reply` | POST | 获取评论回复数据 |
| `/douyin/search/general` | POST | 获取综合搜索数据 |
| `/douyin/search/video` | POST | 获取视频搜索数据 |
| `/douyin/search/user` | POST | 获取用户搜索数据 |
| `/douyin/search/live` | POST | 获取直播搜索数据 |

### TikTok（国际版）

| 路径 | 方法 | 说明 |
|------|------|------|
| `/tiktok/share` | POST | 获取分享链接重定向的完整链接 |
| `/tiktok/detail` | POST | 获取单个作品数据 |
| `/tiktok/account` | POST | 获取账号作品数据 |
| `/tiktok/mix` | POST | 获取合辑作品数据 |
| `/tiktok/live` | POST | 获取直播数据 |

（若文档页还有 `/tiktok/comment`、`/tiktok/reply`、`/tiktok/search/*` 等，可对照 `/douyin` 的用法。）

---

## 调用说明

- 多数业务接口为 **POST**，请求体通常为 JSON。
- 常见字段（以实际 `openapi.json` 为准）：`url`、`share_url`、`keyword`、`token`、`cursor`、`count`、`aweme_id`、`sec_uid`、`mix_id`、`room_id` 等。
- 若需完整参数与响应结构，请直接访问 **{base}/openapi.json** 保存为 JSON 文件，或浏览器打开 `/docs` 查看并复制。

---

## 在项目中的使用

在 TikTokDownloader 中调用 DouK-Downloader 时，将 `base` 设为上述任一口径（或环境变量），按上表路径和 POST 请求体调用即可。需要精确字段时，请以 `openapi.json` 为准。
