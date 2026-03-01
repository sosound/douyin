# DouK-Downloader 详细接口说明

> 基于 OpenAPI 3.1 规范自动生成，来源: `docs/douk-openapi.json`

## 基本信息

- **项目**: DouK-Downloader
- **版本**: 5.8.beta
- **Base URL**: `http://<host>:5555`（如 `http://82.156.100.59:5555` 或 `http://source.galaxystream.online:5555`）

---

## /

### GET /

**访问项目 GitHub 仓库**

重定向至项目 GitHub 仓库主页

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /token

### GET /token

**测试令牌有效性**

项目默认无需令牌；公开部署时，建议设置令牌以防止恶意请求！

令牌设置位置：`src/custom/function.py` - `is_valid_token()`

**Header 参数**

- `token` (可选): Token

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /settings

### POST /settings

**更新项目全局配置**

更新项目配置文件 settings.json

仅需传入需要更新的配置参数

返回更新后的全部配置参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `Settings`

- **accounts_urls** (`array`), 默认: []
- **accounts_urls_tiktok** (`array`), 默认: []
- **mix_urls** (`array`), 默认: []
- **mix_urls_tiktok** (`array`), 默认: []
- **owner_url** (`None`), 默认: {}
- **owner_url_tiktok** (`null`)
- **root** (`string`)
- **folder_name** (`string`)
- **name_format** (`string`)
- **desc_length** (`integer`)
- **name_length** (`integer`)
- **date_format** (`string`)
- **split** (`string`)
- **folder_mode** (`boolean`)
- **music** (`boolean`)
- **truncate** (`integer`)
- **storage_format** (`string`)
- **cookie** (`string`)
- **cookie_tiktok** (`string`)
- **dynamic_cover** (`boolean`)
- **static_cover** (`boolean`)
- **proxy** (`string`)
- **proxy_tiktok** (`string`)
- **twc_tiktok** (`string`)
- **download** (`boolean`)
- **max_size** (`integer`)
- **chunk** (`integer`)
- **timeout** (`integer`)
- **max_retry** (`integer`)
- **max_pages** (`integer`)
- **run_command** (`string`)
- **ffmpeg** (`string`)
- **live_qualities** (`string`)
- **douyin_platform** (`boolean`)
- **tiktok_platform** (`boolean`)
- **browser_info** (`None`)
- **browser_info_tiktok** (`None`)

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

### GET /settings

**获取项目全局配置**

返回项目全部配置参数

**Header 参数**

- `token` (可选): Token

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/share

### POST /douyin/share

**获取分享链接重定向的完整链接**

**参数**:

- **text**: 包含分享链接的字符串；必需参数
- **proxy**: 代理；可选参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `ShortUrl`

- **text** (`string`) **必填**
- **proxy** (`string`)

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/detail

### POST /douyin/detail

**获取单个作品数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **detail_id**: 抖音作品 ID；必需参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `Detail`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **detail_id** (`string`) **必填**

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/account

### POST /douyin/account

**获取账号作品数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **sec_user_id**: 抖音账号 sec_uid；必需参数
- **tab**: 账号页面类型；可选参数，默认值：`post`
- **earliest**: 作品最早发布日期；可选参数
- **latest**: 作品最晚发布日期；可选参数
- **pages**: 最大请求次数，仅对请求账号喜欢页数据有效；可选参数
- **cursor**: 可选参数
- **count**: 可选参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `Account`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **sec_user_id** (`string`) **必填**
- **tab** (`string`), 默认: post
- **earliest** (`string`)
- **latest** (`string`)
- **pages** (`integer`)
- **cursor** (`integer`), 默认: 0
- **count** (`integer`), 默认: 18

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/mix

### POST /douyin/mix

**获取合集作品数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **mix_id**: 抖音合集 ID
- **detail_id**: 属于合集的抖音作品 ID
- **cursor**: 可选参数
- **count**: 可选参数

**`mix_id` 和 `detail_id` 二选一，只需传入其中之一即可**

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `Mix`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **mix_id** (`string`)
- **detail_id** (`string`)
- **cursor** (`integer`), 默认: 0
- **count** (`integer`), 默认: 12

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/live

### POST /douyin/live

**获取直播数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **web_rid**: 抖音直播 web_rid

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `Live`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **web_rid** (`string`)

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/comment

### POST /douyin/comment

**获取作品评论数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **detail_id**: 抖音作品 ID；必需参数
- **pages**: 最大请求次数；可选参数
- **cursor**: 可选参数
- **count**: 可选参数
- **count_reply**: 可选参数
- **reply**: 可选参数，默认值：False

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `Comment`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **detail_id** (`string`) **必填**
- **pages** (`integer`), 默认: 1
- **cursor** (`integer`), 默认: 0
- **count** (`integer`), 默认: 20
- **count_reply** (`integer`), 默认: 3
- **reply** (`boolean`), 默认: False

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/reply

### POST /douyin/reply

**获取评论回复数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **detail_id**: 抖音作品 ID；必需参数
- **comment_id**: 评论 ID；必需参数
- **pages**: 最大请求次数；可选参数
- **cursor**: 可选参数
- **count**: 可选参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `Reply`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **detail_id** (`string`) **必填**
- **comment_id** (`string`) **必填**
- **pages** (`integer`), 默认: 1
- **cursor** (`integer`), 默认: 0
- **count** (`integer`), 默认: 3

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/search/general

### POST /douyin/search/general

**获取综合搜索数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **keyword**: 关键词；必需参数
- **offset**: 起始页码；可选参数
- **count**: 数据数量；可选参数
- **pages**: 总页数；可选参数
- **sort_type**: 排序依据；可选参数
- **publish_time**: 发布时间；可选参数
- **duration**: 视频时长；可选参数
- **search_range**: 搜索范围；可选参数
- **content_type**: 内容形式；可选参数

**部分参数传入规则请查阅文档**: [参数含义](https://github.com/JoeanAmier/TikTokDownloader/wiki/Documentation#%E9%87%87%E9%9B%86%E6%90%9C%E7%B4%A2%E7%BB%93%E6%9E%9C%E6%95%B0%E6%8D%AE%E6%8A%96%E9%9F%B3)

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `GeneralSearch`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **keyword** (`string`) **必填**
- **pages** (`integer`), 默认: 1
- **offset** (`integer`), 默认: 0
- **count** (`integer`), 默认: 10
- **channel** (`integer`), 默认: 0
- **sort_type** (`integer`), 默认: 0
- **publish_time** (`integer`), 默认: 0
- **duration** (`integer`), 默认: 0
- **search_range** (`integer`), 默认: 0
- **content_type** (`integer`), 默认: 0

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/search/video

### POST /douyin/search/video

**获取视频搜索数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **keyword**: 关键词；必需参数
- **offset**: 起始页码；可选参数
- **count**: 数据数量；可选参数
- **pages**: 总页数；可选参数
- **sort_type**: 排序依据；可选参数
- **publish_time**: 发布时间；可选参数
- **duration**: 视频时长；可选参数
- **search_range**: 搜索范围；可选参数

**部分参数传入规则请查阅文档**: [参数含义](https://github.com/JoeanAmier/TikTokDownloader/wiki/Documentation#%E9%87%87%E9%9B%86%E6%90%9C%E7%B4%A2%E7%BB%93%E6%9E%9C%E6%95%B0%E6%8D%AE%E6%8A%96%E9%9F%B3)

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `VideoSearch`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **keyword** (`string`) **必填**
- **pages** (`integer`), 默认: 1
- **offset** (`integer`), 默认: 0
- **count** (`integer`), 默认: 10
- **channel** (`integer`), 默认: 1
- **sort_type** (`integer`), 默认: 0
- **publish_time** (`integer`), 默认: 0
- **duration** (`integer`), 默认: 0
- **search_range** (`integer`), 默认: 0

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/search/user

### POST /douyin/search/user

**获取用户搜索数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **keyword**: 关键词；必需参数
- **offset**: 起始页码；可选参数
- **count**: 数据数量；可选参数
- **pages**: 总页数；可选参数
- **douyin_user_fans**: 粉丝数量；可选参数
- **douyin_user_type**: 用户类型；可选参数

**部分参数传入规则请查阅文档**: [参数含义](https://github.com/JoeanAmier/TikTokDownloader/wiki/Documentation#%E9%87%87%E9%9B%86%E6%90%9C%E7%B4%A2%E7%BB%93%E6%9E%9C%E6%95%B0%E6%8D%AE%E6%8A%96%E9%9F%B3)

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `UserSearch`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **keyword** (`string`) **必填**
- **pages** (`integer`), 默认: 1
- **offset** (`integer`), 默认: 0
- **count** (`integer`), 默认: 10
- **channel** (`integer`), 默认: 2
- **douyin_user_fans** (`integer`), 默认: 0
- **douyin_user_type** (`integer`), 默认: 0

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /douyin/search/live

### POST /douyin/search/live

**获取直播搜索数据**

**参数**:

- **cookie**: 抖音 Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **keyword**: 关键词；必需参数
- **offset**: 起始页码；可选参数
- **count**: 数据数量；可选参数
- **pages**: 总页数；可选参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `LiveSearch`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **keyword** (`string`) **必填**
- **pages** (`integer`), 默认: 1
- **offset** (`integer`), 默认: 0
- **count** (`integer`), 默认: 10
- **channel** (`integer`), 默认: 3

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /tiktok/share

### POST /tiktok/share

**获取分享链接重定向的完整链接**

**参数**:

- **text**: 包含分享链接的字符串；必需参数
- **proxy**: 代理；可选参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `ShortUrl`

- **text** (`string`) **必填**
- **proxy** (`string`)

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /tiktok/detail

### POST /tiktok/detail

**获取单个作品数据**

**参数**:

- **cookie**: TikTok Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **detail_id**: TikTok 作品 ID；必需参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `DetailTikTok`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **detail_id** (`string`) **必填**

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /tiktok/account

### POST /tiktok/account

**获取账号作品数据**

**参数**:

- **cookie**: TikTok Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **sec_user_id**: TikTok 账号 secUid；必需参数
- **tab**: 账号页面类型；可选参数，默认值：`post`
- **earliest**: 作品最早发布日期；可选参数
- **latest**: 作品最晚发布日期；可选参数
- **pages**: 最大请求次数，仅对请求账号喜欢页数据有效；可选参数
- **cursor**: 可选参数
- **count**: 可选参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `AccountTiktok`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **sec_user_id** (`string`) **必填**
- **tab** (`string`), 默认: post
- **earliest** (`string`)
- **latest** (`string`)
- **pages** (`integer`)
- **cursor** (`integer`), 默认: 0
- **count** (`integer`), 默认: 18

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /tiktok/mix

### POST /tiktok/mix

**获取合辑作品数据**

**参数**:

- **cookie**: TikTok Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **mix_id**: TikTok 合集 ID；必需参数
- **cursor**: 可选参数
- **count**: 可选参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `MixTikTok`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **mix_id** (`string`)
- **cursor** (`integer`), 默认: 0
- **count** (`integer`), 默认: 30

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---

## /tiktok/live

### POST /tiktok/live

**获取直播数据**

**参数**:

- **cookie**: TikTok Cookie；可选参数
- **proxy**: 代理；可选参数
- **source**: 是否返回原始响应数据；可选参数，默认值：False
- **room_id**: TikTok 直播 room_id；必需参数

**Header 参数**

- `token` (可选): Token

**Request Body (JSON)**

Schema: `Live`

- **cookie** (`string`)
- **proxy** (`string`)
- **source** (`boolean`), 默认: False
- **web_rid** (`string`)

**响应**

- 200: 成功（见下方 Schema）
- 422: 参数校验错误

---
