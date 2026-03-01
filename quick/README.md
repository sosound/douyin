# iPhone 快捷指令集成（Quick）— 直连 GalaxyStream

> 目录：`quick/`  
> 目标：在 iPhone 上通过「快捷指令」直接调用 **GalaxyStream（DouK-Downloader）公网 API**，完成抖音分享链接解析与无水印下载，**无需自建 Flask 后端**。

---

## 1. 整体思路

- **API 服务**：使用公网 GalaxyStream 接口  
  - Base URL：`http://source.galaxystream.online:5555`（与 `flask_app` 的 `api_preset: galaxy` 一致；若你使用其它 DouK-Downloader 地址可替换）
  - 无需在本机或服务器部署任何后端。
- **快捷指令**：作为前端入口，完成：
  - 从「共享菜单」或「剪贴板」接收抖音分享内容（短链、完整链接或带链接的文案）；
  - 先解析短链（可选）：调用 `POST /douyin/share` 得到完整链接；
  - 从链接或文案中取得作品 ID（19 位数字），再调用 `POST /douyin/detail` 获取作品数据；
  - 从返回的 `data.downloads` 取下载地址，在手机端直接下载并保存到相册/文件。

本目录包含：可导入的快捷指令文件、解析页（供公网部署）、以及步骤说明文档。

---

## 2. 直接导入快捷指令（公网获取）

若你有可公网访问的地址（如 **source.galaxystream.online** 或 GitHub Pages），可将本目录的**解析页**与**快捷指令文件**部署上去，用户在 iPhone 上打开该地址即可下载并导入快捷指令。

### 2.1 本目录提供的文件

| 文件 | 说明 |
|------|------|
| `index.html` | 解析页：粘贴链接即可解析并获取下载地址；页内提供「下载并导入快捷指令」按钮 |
| `抖音去水印下载.shortcut` | 预制的快捷指令（运行后会打开解析页） |
| `build-shortcut.js` | 用于重新生成 `.shortcut` 的脚本（可指定解析页 URL） |

### 2.2 部署到公网（如 source.galaxystream.online）

1. 将 **index.html**、**抖音去水印下载.shortcut** 放到同一可访问路径下（例如 `https://source.galaxystream.online/quick/`），确保：
   - 访问 `https://source.galaxystream.online/quick/` 会打开 `index.html`
   - 访问 `https://source.galaxystream.online/quick/抖音去水印下载.shortcut` 会返回 `.shortcut` 文件
2. 在 **iPhone 的 Safari** 中打开解析页地址，点击「下载并导入快捷指令」。
3. 若系统允许，会提示添加到「快捷指令」；若无法直接导入（如部分 iOS 版本限制），请按页内链接或 [douyin_shortcut_galaxy.md](douyin_shortcut_galaxy.md) 手动创建。

### 2.3 自定义解析页 URL 后重新生成快捷指令

若你的解析页部署在其他地址，可重新生成 `.shortcut` 使快捷指令打开你的页面：

```bash
cd quick
npm install @joshfarrant/shortcuts-js   # 仅首次需要
node build-shortcut.js "https://你的域名/quick/"
```

生成的 `抖音去水印下载.shortcut` 内已写入该 URL，部署同一目录后即可用「下载并导入快捷指令」分发。

---

## 3. 依赖条件

1. **网络**
  - iPhone 可访问 GalaxyStream 的 Base URL（如 `http://source.galaxystream.online:5555`）。  
  - 若实际使用 HTTP 或其它域名/端口，请在快捷指令中统一替换该 Base URL。
2. **iPhone 环境**
  - iOS 16+（推荐）  
  - 已安装「快捷指令」App  
  - 如需从分享菜单运行：在「设置 > 快捷指令」中允许「允许不受信任的快捷指令」（首次需打开）。

---

## 4. GalaxyStream 接口约定（快捷指令用）

以下为快捷指令需要使用的两个接口，均以 **JSON 请求体、JSON 响应**。

### 4.1 解析分享链接（短链 → 完整链接）

- **URL**：`POST <BaseURL>/douyin/share`  
例如：`POST http://source.galaxystream.online:5555/douyin/share`
- **请求体（JSON）**：
  - `text`（必填）：包含分享链接的字符串（剪贴板或分享输入）
  - `proxy`（可选）：留空即可
- **响应**：
  - 成功时：`message` 含「请求链接成功」、`url` 为解析后的完整链接（如 `https://www.douyin.com/video/7201234567890123456`）
  - 从 `url` 中可提取 19 位数字作为作品 ID（`detail_id`）

### 4.2 获取作品数据（含下载地址）

- **URL**：`POST <BaseURL>/douyin/detail`  
例如：`POST http://source.galaxystream.online:5555/douyin/detail`
- **请求体（JSON）**：
  - `detail_id`（必填）：抖音作品 ID（19 位数字）
  - `cookie`、`proxy`（可选）：留空即可
  - `source`（可选）：不传或 `false`
- **响应**：
  - 成功时：`data` 对象中含 `downloads` 数组（无水印视频/图集下载地址）
  - 快捷指令取 **第一个下载地址**：`data.downloads[0]`，用于「下载」或「获取 URL 内容」保存到相册/文件

---

## 5. 快捷指令步骤示意（伪流程）

1. **获取输入文本**
  - 从「共享的输入」获取文本；若为空，则从「剪贴板」获取。
2. **得到作品 ID（detail_id）**
  - **方式 A**：对当前文本用正则匹配 **19 位连续数字**（如 `\d{19}`），若匹配到则视为 `detail_id`，跳步骤 4。  
  - **方式 B**：若未匹配到，则先调用 **解析分享链接**：  
    - 请求：`POST <BaseURL>/douyin/share`，Body 类型 JSON，内容 `{"text": "<上一步的文本>"}`；  
    - 从响应中取 `url`；  
    - 再对 `url` 用同一正则匹配 19 位数字，得到 `detail_id`。
3. **若仍无 detail_id**
  - 提示「无法解析链接，请确认是抖音分享链接或复制了链接」。
4. **获取作品数据**
  - 请求：`POST <BaseURL>/douyin/detail`，Body 类型 JSON，内容 `{"detail_id": "<上一步的 detail_id>"}`。
5. **解析 JSON 响应**
  - 检查是否有 `data` 且 `data.downloads` 非空；  
  - 取 `data.downloads` 的**第一项**作为「下载链接」。
6. **下载并保存**
  - 用「下载」或「获取 URL 的内容」（以文件形式），URL 为「下载链接」；  
  - 完成后可「存储到相册」或「存储文件」。

更细的逐步说明见：**[抖音去水印下载（Galaxy 直连）— 步骤说明](douyin_shortcut_galaxy.md)**。

---

## 6. 与 Flask 版的区别


| 项目   | 原 Flask 版                                                  | 当前 Galaxy 直连版                                                           |
| ---- | ---------------------------------------------------------- | ----------------------------------------------------------------------- |
| 后端   | 需在本机/服务器跑 Flask（如 5009）                                    | 无需自建，直连 GalaxyStream 公网 API                                             |
| 获取作品 | `POST http://<电脑IP>:5009/api/detail`，body `{"link":"..."}` | 先（按需）`/douyin/share`，再 `POST /douyin/detail`，body `{"detail_id":"..."}` |
| 下载链接 | 响应 `data.downloads[0]`                                     | 同上，`data.downloads[0]`                                                  |


---

## 7. 后续可做（TODO）

- 在 `quick/` 下可补充：导出/导入快捷指令的 JSON 模板（若平台支持）。  
- 若 GalaxyStream 提供「一键从分享文本返回下载链接」的聚合接口，可再简化快捷指令为单次请求。

