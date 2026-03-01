"""
Flask 应用配置：API 后端地址等可配置项
"""
import json
import os
from pathlib import Path

# 预置 API 后端地址
API_BASE_PRESETS = {
    "local": "http://127.0.0.1:5555",
    "galaxy": "http://source.galaxystream.online:5555",
}

# 配置文件路径（与 config.py 同目录）
CONFIG_DIR = Path(__file__).resolve().parent
CONFIG_FILE = CONFIG_DIR / "config.json"


def _load_config() -> dict:
    """从 config.json 读取配置（若存在）"""
    if not CONFIG_FILE.is_file():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_api_base() -> str:
    """
    获取 DouK-Downloader API 根地址，优先级：
    1. 环境变量 DOUK_API_BASE（完整 URL）
    2. 环境变量 DOUK_API_PRESET（local / galaxy）
    3. config.json 中的 api_base
    4. config.json 中的 api_preset
    5. 默认 galaxy（http://source.galaxystream.online:5555）
    """
    # 环境变量优先
    env_base = os.environ.get("DOUK_API_BASE", "").strip()
    if env_base:
        return env_base.rstrip("/")
    preset_name = os.environ.get("DOUK_API_PRESET", "").strip().lower()
    if preset_name and preset_name in API_BASE_PRESETS:
        return API_BASE_PRESETS[preset_name]

    cfg = _load_config()
    # config.json 中的完整 URL
    cfg_base = (cfg.get("api_base") or "").strip()
    if cfg_base:
        return cfg_base.rstrip("/")
    # config.json 中的预设名
    cfg_preset = (cfg.get("api_preset") or "").strip().lower()
    if cfg_preset in API_BASE_PRESETS:
        return API_BASE_PRESETS[cfg_preset]

    return API_BASE_PRESETS["galaxy"]


# 对外暴露：应用启动时解析
API_BASE = get_api_base()

# 其他可配置项（也可从 config.json 读取，此处保留默认）
DOWNLOAD_TIMEOUT = 120
