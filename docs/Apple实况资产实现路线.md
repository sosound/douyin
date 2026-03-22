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
- 在 macOS 上显式设置 `DOUK_APPLE_LIVE_IMPORT=1` 时，会优先通过 PyObjC PhotoKit 把 `jpeg + mov` 作为 `photo + pairedVideo` 导入 Photos；若不可用，再回退到 Swift 辅助脚本

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
- `StillImageTime` 元数据轨道可以写出，但按当前实测结果，它不是 `pairedVideo` 被 Photos 接受的硬门槛

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

`jpeg + mov` 不是终点；真正的目标应当是“把它变成一组可被 Apple Photos 接受并同步到 iPhone 的实况资产”。这条路线的关键不是“合并文件”，而是“补齐配对关系、元数据和导入链路”。`
