# Apple 实况资产实现路线

## 文档目的

本文档用于明确当前项目如果继续沿着“让 `jpeg + mov` 更接近 iPhone 原生 `Live Photo` 体验”推进，应该采用什么工程路线。

本文档刻意不再讨论“单个独立 live 文件”目标，因为这不是当前最合理的实现方向。

## 目标定义

这里的目标不是：

- 生成一个通用单文件
- 让任何播放器都把它当成 Apple 原生 `Live Photo`

这里的目标是：

- 保留当前项目的 `jpeg + mov` 导出能力
- 在 macOS 环境中补齐 Apple 生态更关心的配对信息
- 让导入 Photos 后的资源更有机会被识别为实况资产
- 最终通过 iCloud Photos 或 Apple 设备链路同步到 iPhone

## 已有能力

当前仓库已经具备：

- 从抖音上游提取 `实况` 的静态图和动态视频
- 默认导出 `jpeg + mp4`
- `live_photo_mode = apple` 时导出 `jpeg + mov`

当前仓库尚未具备：

- 为图片和视频写入统一的 Apple 配对标识
- 为视频补齐 Apple 实况识别相关的额外元数据轨道
- 在 macOS Photos 中完成正式导入

当前分支已经落地的能力：

- `apple` 模式导出结束后会生成 `.livephoto.json` 资产清单
- 在 macOS 上检测到 `Quartz / AVFoundation` 时，会为 `jpeg` 写入 Apple `ContentIdentifier`
- 检测到 `exiftool` 时，会为 `.mov` 写入匹配的 `ContentIdentifier`
- 在 macOS 上检测到 `AVFoundation / CoreMedia` 时，会为 `.mov` 追加 `still-image-time` timed metadata track
- 在 macOS 上显式设置 `DOUK_APPLE_LIVE_IMPORT=1` 时，会优先通过 PyObjC PhotoKit 把 `jpeg + mov` 作为 `photo + pairedVideo` 导入 Photos；若不可用，再回退到 Swift 辅助脚本
- Web 端已经提供单作品导出入口，可直接调用后端导出并下载产物
- Web 端当前已经覆盖三类媒体保存到 `照片.app`：
  - `实况`：导出 `jpeg + mov + .livephoto.json`，并导入 `照片.app`
  - `静态图`：混合作品中的纯图片会作为普通照片导入 `照片.app`
  - `视频`：普通视频作品可直接下载并导入 `照片.app`

## 路线结论

最合理的路线是分成 4 步，而不是继续追“一个独立文件”：

1. 继续下载并导出 `jpeg + mov`
2. 为两份资源写入同一个资产标识
3. 让 `.mov` 具备更接近 Apple 实况所需的元数据结构
4. 通过 macOS Photos 把它作为一组配对资源导入

## 哪些信息是官方确认的

以下部分可以认为是官方层面比较稳妥的信息：

- Photos/PhotoKit 的资源模型允许把图片资源和 `pairedVideo` 资源作为同一资产导入
- `Live Photo` 在 Apple 生态里不是“普通视频文件”
- 真正的导入目标应该是 Photos 资产，而不是播放器意义上的单个媒体文件

这意味着：

`最终目标应该是“生成可被 Photos 接受的配对资产”，而不是“合成一个万能文件”。`

## 哪些信息属于工程推断

以下部分属于结合 Apple 生态行为、社区实现和现有样本做出的工程判断，不应当表述为 Apple 的公开格式规范：

- 仅有 `jpeg + mov` 文件对，通常还不足以稳定表现为原生实况
- 图片和视频之间通常需要共享同一个内容标识
- 视频一侧通常还需要额外的实况相关元数据，尤其是静态主帧时间相关信息
- 单靠当前仓库的 `ffmpeg remux` 还不够

换句话说：

`mp4 -> mov` 只是把动态片段换了容器，不等于生成了 Apple 可识别的实况资产。`

## 推荐实现结构

建议新增一个独立模块，例如：

- `src/module/apple_live_photo.py`

职责拆分如下：

### 1. 资产准备阶段

输入：

- `photo_path`
- `motion_path`

输出：

- 规范化后的 `jpeg`
- 规范化后的 `mov`
- 一条唯一 `asset_id`

建议行为：

- 若动态文件仍是 `mp4`，先 remux 为 `mov`
- 为每组实况生成一个 UUID 作为 `asset_id`
- 将导出路径组织为稳定的成对命名

### 2. 元数据写入阶段

建议引入一个外部工具写元数据，优先级如下：

1. `exiftool`
2. macOS 原生 AVFoundation / PhotoKit 辅助程序

原因：

- 当前项目里的 `ffmpeg` 适合下载和 remux
- 但“Apple 实况配对元数据”不适合只靠 `ffmpeg` 硬写

这一阶段至少需要解决两个问题：

- 图片和视频要共享同一个内容标识
- 视频要有足够接近 Apple 实况的附加元数据

### 3. Photos 导入阶段

建议新增一个 macOS 专用辅助程序，例如：

- `tools/apple/import_live_photo.swift`

职责：

- 使用 PhotoKit 发起 `PHAssetCreationRequest`
- 将 `jpeg` 作为 `photo`
- 将 `mov` 作为 `pairedVideo`
- 在本机 Photos 中创建资产

这一步比“直接把文件丢进手机文件系统”更符合 Apple 生态的真实使用路径。

### 4. 验证阶段

验证标准不应该是“这个文件能不能被播放器打开”，而应该是：

- macOS Photos 中是否显示为实况
- 长按或播放时是否呈现动态
- iCloud 同步到 iPhone 后是否仍保留实况属性
- 封面是否停在预期主帧

## 对当前仓库的具体改造建议

### 第一阶段：最小可落地版本

目标：

- 不改动现有下载主流程
- 在 `apple` 模式导出结束后追加“Apple 实况后处理”

建议改动点：

- 在 [src/downloader/download.py](/Users/star/code/douyin/src/downloader/download.py) 的 `finalize_live_photo_exports()` 后追加后处理钩子
- 在 [src/module/ffmpeg.py](/Users/star/code/douyin/src/module/ffmpeg.py) 继续保留 `remux_to_mov()`，只负责容器转换
- 新增 `src/module/apple_live_photo.py`，专门负责：
  - 生成 `asset_id`
  - 调用元数据工具
  - 校验结果

这一阶段已经落地为：

- `jpeg + mov`
- 资产清单导出
- 在可用环境下为 `.mov` 写入 `ContentIdentifier`
- 结果校验日志

### 第二阶段：macOS 导入集成

目标：

- 在 macOS 上把后处理后的成对资源导入 Photos

建议改动点：

- 新增 Swift 辅助程序
- Python 主程序在检测到 `Darwin` 环境且用户显式开启时调用它

当前分支的触发方式：

- 仅在 macOS 上生效
- 需要设置环境变量 `DOUK_APPLE_LIVE_IMPORT=1`
- 优先使用 Python 环境中的 `PyObjC Photos` 桥
- 图片侧 Apple 标识依赖 `PyObjC Quartz`
- 若没有 PyObjC，再尝试系统可用的 `swift` 或 `xcrun`
- 首次导入时需要用户授予 Photos 写入权限

当前实测结论：

- 通过 PhotoKit 导入 `photo + video` 可以成功
- 仅有 `jpeg + mov + MOV ContentIdentifier` 时，`photo + pairedVideo` 会被 Photos 以 `PHPhotosErrorDomain Code=3302` 拒绝
- 当 JPEG 侧补齐 Apple `ContentIdentifier`，且 MOV 侧也具备匹配的 `ContentIdentifier` 后，PhotoKit `photo + pairedVideo` 导入已实测成功
- `still-image-time` 元数据轨道已经可以稳定写出，并能在 `ffprobe` 中看到第 3 条 `mebx` metadata stream
- `StillImageTime` 元数据轨道不是 `pairedVideo` 被 Photos 接受的硬门槛
- 动态视频中的音频流可以完整保留到最终 `.mov`
- 但按当前实测结果，即使 `.mov` 中保留了 AAC 音轨，且已经补齐 `ContentIdentifier + still-image-time`，导入 `照片.app` 后仍不能像 iPhone 原生拍摄的 Live Photo 那样播放声音
- 对多张实况样本，`jpeg + mov + ContentIdentifier` 的批量导出是稳定的
- 但 `still-image-time` 在批量样本上的写入当前仍不稳定，应视为 best-effort，而不是稳定能力

建议新增配置项：

- `live_photo_mode`: 保持 `pair` / `apple`
- `apple_live_import`: 是否导入 Photos
- `apple_live_tool`: 元数据工具路径

### 第三阶段：主帧质量与体验优化

目标：

- 让导入后的实况更接近“停在好看的那一帧”

这一步需要额外处理：

- 主图与视频时序的对齐
- 视频中静态主帧时刻的表达
- 主图 EXIF 时间与视频时间字段同步

这一步可以排在后面，因为它属于“体验优化”，不是第一阶段的落地门槛。

### 第四阶段：原生 Live Photo 对照分析

目标：

- 确认为什么当前导入型实况已经“可识别、可长按动、可保留音轨”，但 `照片.app` 仍不播放声音

当前阶段性判断：

- 问题不在抖音上游是否携带音频
- 问题也不在当前导出链路是否把音频保留下来
- 更可能的差异在于 Apple 原生拍摄实况资产中仍存在额外的 QuickTime atoms / metadata / 导入语义

后续建议：

1. 找一组 iPhone 原生拍摄的 Live Photo 资产对做本地对照
2. 并排比较原生 `.MOV` 与当前导出 `.mov` 的 container atoms / metadata tracks / tag 结构
3. 仅在发现明确差异后，再评估是否值得继续模拟

在没有完成原生资产对照前，项目不应再将“实况有声播放”表述为当前能力。

## 当前 Web 交付形态

本轮已把一部分能力接入到本地 Web 测试页，便于非命令行方式验证。

### 入口

- Web 页面：`http://127.0.0.1:5009`
- API 文档：`http://127.0.0.1:5555/docs`

### Web 当前支持的动作

1. 输入抖音作品链接并获取详情
2. 如果作品类型是 `实况`
   - 显示“导出 Apple 实况资产”
   - 导出目录下生成：
     - `.jpeg`
     - `.mov`
     - `.livephoto.json`
   - 若开启 `DOUK_APPLE_LIVE_IMPORT=1`，会自动尝试导入 `照片.app`
3. 如果作品类型是 `视频`
   - 显示“下载并导入照片.app”
   - 导出目录下生成：
     - `.mp4`
   - 若开启 `DOUK_APPLE_LIVE_IMPORT=1`，会自动尝试导入 `照片.app`

### 混合作品当前行为

对“静态图 + 动态图混合”的实况作品，当前行为已经明确：

- 带 `video` 的项：
  - 走 Apple 实况资产导出与导入链路
- `video = ''` 的项：
  - 保留为普通 `jpeg`
  - 同步作为普通照片导入 `照片.app`

### 导出目录

Web 导出的默认目录是项目根目录下的：

- `.web_exports/`

每次单作品导出会创建一个子目录，例如：

- `WEB_<detail_id>_<timestamp>`

## 当前验证进展（2026-03-22）

本轮已经完成以下闭环验证：

1. 真实抖音 `note` 型实况作品可提取为 `image + video`
2. 一类落地页为 `/video/...`、但产品侧表现为动图的作品，也已能识别为 `实况`
3. `apple` 模式可以导出：
   - `jpeg`
   - `mov`
   - `.livephoto.json`
4. `jpeg` 与 `mov` 可以写入匹配的 `ContentIdentifier`
5. `mov` 可追加 `still-image-time` timed metadata track
6. PhotoKit 已可把它们作为 `photo + pairedVideo` 导入 `照片.app`
7. 多张实况样本已验证可以批量导出成 4 组 `jpeg + mov`

本轮同时完成了一个重要边界确认：

- 抖音实况动态视频中的音频流可以保留到最终 `.mov`
- 但当前导入型 Live Photo 仍未达到“像 iPhone 原生实况那样带声音播放”的效果

此外，还完成了一个收口性验证：

- 多张实况样本中的 4 个 `.mov` 均保留了 `aac / 44100 Hz / 双声道` 音轨
- 但批量写入 `still-image-time` timed metadata track 当前仍然不稳定
- 因此该能力现阶段不应纳入对外能力描述

因此，当前最准确的能力描述应当是：

- 已实现“Apple 可接受的实况资产导入”
- 已实现“动态视频音轨保留”
- 已实现“多张实况的批量导出”
- 尚未实现“原生 Live Photo 级别的声音播放体验”
- 尚未实现“批量稳定写入 still-image-time 元数据轨”

## 当前收口结论

截至 `2026-03-22`，本轮探索建议先收口到以下结论：

1. 抖音实况的公开上游模型可以稳定视为：
   - `静态图 + 动态视频`
2. 当前项目已经能够把这组资源稳定转换为：
   - `jpeg + mov`
   - 匹配的 `ContentIdentifier`
   - 可导入 `照片.app` 的 `photo + pairedVideo`
3. 动态视频中的音频可以稳定保留到最终 `.mov`
4. 但导入 `照片.app` 后，仍不能复现 iPhone 原生实况的有声播放体验
5. `still-image-time` 在单条短样本上可写出，但在批量多张实况样本上仍不稳定

因此，当前最稳妥的项目表述应当是：

- 已支持 Apple 实况资产导入
- 已支持音轨保留
- 不承诺 `照片.app / iPhone` 中的有声播放
- 不承诺批量样本上的 `still-image-time` 稳定写入

## 暂停前建议

如果后续重新开启这一方向，建议优先顺序调整为：

1. 先获取一组 iPhone 原生拍摄的 Live Photo 资产做对照
2. 再决定是否继续追 `still-image-time` 与更深层 QuickTime metadata
3. 在此之前，不建议继续在当前 PyObjC `AVAssetReader/Writer` 路线中反复打磨

原因：

- 当前收益已经明显递减
- Swift 原生小工具路线又受限于本机 SDK / toolchain 版本不匹配
- 继续局部试错，很可能重复投入而不产生新的确定性结论

## 为什么不建议把目标继续定义成“单文件”

原因很直接：

- 当前项目拿到的上游资源本来就是拆分的
- Apple 生态最终消费的是资产关系，而不是通用媒体单文件
- 就算做出一个单文件，也更可能被当普通视频，而不是原生实况

因此本项目后续应该避免继续出现这样的目标表述：

- “合成一个 live 文件”
- “输出一个文件直接等于 iPhone 实况”

更准确的表述应当是：

- “生成可导入 Apple Photos 的实况资产对”

## 近期执行顺序

推荐按下面顺序推进：

1. 先把 `apple` 模式定义为“Apple 实况资产预处理模式”，而不是“仅导出 mov”
2. 新增 `src/module/apple_live_photo.py`
3. 在后处理阶段为 `jpeg + mov` 写入配对标识
4. 增加一个 macOS 辅助导入程序
5. 用真实 iPhone / macOS Photos 做闭环验证

## 一句话结论

`jpeg + mov` 不是终点；真正的目标应当是“把它变成一组可被 Apple Photos 接受并同步到 iPhone 的实况资产”。当前已经完成导入链路、批量导出与音轨保留验证，但“原生 Live Photo 级别的有声播放”和“批量稳定 still-image-time”仍未攻克。`
