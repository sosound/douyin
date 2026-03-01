# 抖音作品下载 - Flask 应用

调用 DouK-Downloader 的 `/douyin/detail` 接口，在 Web 页面获取作品数据并下载视频/图集。

## 功能

- 输入作品链接（支持完整链接和 v.douyin.com 短链接）
- 自动解析短链接
- 获取作品详情（类型、描述、作者、点赞/评论数）
- 代理下载（绕过防盗链，支持 Cookie 和代理）

## 前置条件

1. DouK-Downloader 的 **Web API** 已可用（本地或远程，见下方配置）
2. Python 3.12+

## 配置（API 后端地址）

API 根地址 `API_BASE` 可配置，支持本地与远程：

| 方式 | 说明 |
|------|------|
| **config.json** | 在 `flask_app` 目录下复制 `config.json.example` 为 `config.json`，设置 `api_preset` 或 `api_base` |
| **环境变量** | `DOUK_API_PRESET=galaxy` 或 `DOUK_API_BASE=http://...` |

**预设：**

- `local` → `http://127.0.0.1:5555`（默认）
- `galaxy` → `http://source.galaxystream.online:5555`

**示例 config.json：**

```json
{
  "api_preset": "galaxy"
}
```

或直接写完整地址：

```json
{
  "api_base": "http://source.galaxystream.online:5555"
}
```

## 安装与运行

```bash
cd flask_app
pip install -r requirements.txt
python app.py
```

访问：http://127.0.0.1:5009

## 使用说明

1. 在「作品链接」粘贴抖音作品链接
2. 可选填写 Cookie（需登录态时）和代理（如 `http://127.0.0.1:7890`）
3. 点击「获取作品数据」，再点击「点击下载」保存文件
