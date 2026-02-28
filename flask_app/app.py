"""
Flask 应用：调用 DouK-Downloader API 获取抖音作品并下载
"""
import re
import time
from urllib.parse import quote, urlparse

import httpx
from flask import Flask, Response, jsonify, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = "douyin-downloader-flask-secret"  # 生产环境请更换

# 配置
API_BASE = "http://127.0.0.1:5555"
DOWNLOAD_TIMEOUT = 120
CONTENT_TYPE_EXT = {
    "video/mp4": "mp4",
    "video/quicktime": "mov",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "audio/mp4": "m4a",
    "audio/mpeg": "mp3",
}

# 正则
DETAIL_ID_RE = re.compile(r"\b(\d{19})\b")
DETAIL_LINK_RE = re.compile(
    r"https?://(?:www\.)?douyin\.com/(?:video|note|slides)/(\d{19})"
)
# 允许：完整短链、以及分享文案里常见的“无协议短链”
SHORT_LINK_RE = re.compile(r"(?:https?://)?v\.douyin\.com/[0-9A-Za-z]+/?")
HTML_START = (b"<!doctype", b"<html", b"<meta", b"<script")


def extract_detail_id(text: str) -> str | None:
    """从链接或文本中提取作品 ID"""
    text = (text or "").strip()
    if not text:
        return None
    m = DETAIL_LINK_RE.search(text) or DETAIL_ID_RE.search(text)
    return m.group(1) if m else None


def resolve_short_link(text: str, proxy: str = "") -> str | None:
    """解析短链接为完整链接"""
    text = (text or "").strip()
    m = SHORT_LINK_RE.search(text)
    if not m:
        return None
    # 如果用户粘贴的是“v.douyin.com/xxxx/”无协议形式，补全协议以提高解析成功率
    short_url = m.group(0)
    if short_url.startswith("v.douyin.com/"):
        text = text.replace(short_url, f"https://{short_url}", 1)
    try:
        resp = httpx.post(
            f"{API_BASE}/douyin/share",
            json={"text": text, "proxy": proxy},
            timeout=15.0,
        )
        data = resp.json()
        return data.get("url") if "请求链接成功" in (data.get("message") or "") else None
    except Exception:
        return None


def fetch_detail(detail_id: str, cookie: str = "", proxy: str = "") -> dict:
    """调用 /douyin/detail 获取作品数据"""
    try:
        resp = httpx.post(
            f"{API_BASE}/douyin/detail",
            json={"detail_id": detail_id, "cookie": cookie, "proxy": proxy, "source": False},
            timeout=30.0,
        )
        return resp.json()
    except httpx.RequestError as e:
        return {"message": f"请求失败: {e!s}", "data": None}
    except Exception as e:
        return {"message": f"错误: {e!s}", "data": None}


def is_safe_download_url(url: str) -> bool:
    """校验下载地址（仅 https，排除本机防 SSRF）"""
    try:
        p = urlparse(url)
        if p.scheme != "https":
            return False
        host = (p.hostname or "").lower()
        return host not in ("localhost", "127.0.0.1", "0.0.0.0") and not host.endswith(".local")
    except Exception:
        return False


def download_headers(cookie: str = "") -> dict:
    """构建下载请求头"""
    h = {
        "Accept": "*/*",
        "Referer": "https://www.douyin.com/?recommend=1",
        "Origin": "https://www.douyin.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    }
    if cookie:
        h["Cookie"] = cookie
    return h


@app.route("/")
def index():
    return render_template("index.html", error=request.args.get("error"))


@app.route("/api/detail", methods=["POST"])
def api_detail():
    """获取作品数据"""
    data = request.get_json() or {}
    link = (data.get("link") or "").strip()
    cookie = (data.get("cookie") or "").strip()
    proxy = (data.get("proxy") or "").strip()

    if not link:
        return jsonify({"success": False, "message": "请输入作品链接", "data": None})

    if cookie:
        session["douyin_cookie"] = cookie
    if proxy:
        session["douyin_proxy"] = proxy

    detail_id = extract_detail_id(link)
    # 支持“分享口令/分享文案 + v.douyin.com 短链”这种输入：提取不到 ID 就尝试先解析短链
    if not detail_id:
        resolved = resolve_short_link(link, proxy)
        if resolved:
            link = resolved
            detail_id = extract_detail_id(link)

    if not detail_id:
        return jsonify({
            "success": False,
            "message": "无法提取作品 ID，请确认链接格式正确",
            "data": None,
        })

    result = fetch_detail(detail_id, cookie, proxy)
    if not result.get("data"):
        return jsonify({
            "success": False,
            "message": result.get("message", "获取数据失败"),
            "data": None,
            "detail_id": detail_id,
        })

    return jsonify({
        "success": True,
        "message": "获取数据成功！",
        "data": result["data"],
        "detail_id": detail_id,
    })


@app.route("/download")
def download_proxy():
    """代理下载，绕过防盗链"""
    url = request.args.get("url")
    if not url:
        return redirect(f"/?error={quote('缺少 url 参数')}")
    if not is_safe_download_url(url):
        return redirect(f"/?error={quote('不支持的下载地址')}")

    headers = download_headers(session.get("douyin_cookie", ""))
    proxy = session.get("douyin_proxy")

    try:
        r = httpx.get(
            url,
            headers=headers,
            timeout=DOWNLOAD_TIMEOUT,
            follow_redirects=True,
            proxy=proxy or None,
        )
        r.raise_for_status()
        content = r.content
        ct = r.headers.get("content-type", "application/octet-stream")

        if "text/html" in ct.lower():
            return redirect(f"/?error={quote('CDN 返回 HTML，可能链接已过期或需 Cookie')}")
        if content.lstrip()[:100].lower().startswith(HTML_START):
            return redirect(f"/?error={quote('CDN 返回 HTML，可能链接已过期或需 Cookie')}")

        ext = CONTENT_TYPE_EXT.get(ct.split(";")[0].strip().lower(), "mp4")
        return Response(
            content,
            content_type=ct,
            headers={"Content-Disposition": f'attachment; filename="douyin_{int(time.time())}.{ext}"'},
        )
    except httpx.HTTPStatusError as e:
        return redirect(f"/?error={quote(f'下载失败: {e.response.status_code}')}")
    except Exception as e:
        return redirect(f"/?error={quote(f'下载失败: {str(e)}')}")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5009, debug=True)
