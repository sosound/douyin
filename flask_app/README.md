# 抖音作品下载 - Flask 应用

调用 DouK-Downloader 的 `/douyin/detail` 接口，在 Web 页面获取作品数据并下载视频/图集。

## 功能

- 输入作品链接（支持完整链接和 v.douyin.com 短链接）
- 自动解析短链接
- 获取作品详情（类型、描述、作者、点赞/评论数）
- 代理下载（绕过防盗链，支持 Cookie 和代理）

## 前置条件

1. 已启动 DouK-Downloader 的 **Web API 模式**（`http://127.0.0.1:5555`）
2. Python 3.12+

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
