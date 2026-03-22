from json import dump
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError, run
from time import monotonic, sleep
from threading import Event
from uuid import uuid4

from .apple_live_photo_importer import AppleLivePhotoImporter

__all__ = ["AppleLivePhotoProcessor"]


class AppleLivePhotoProcessor:
    STILL_IMAGE_TIME_IDENTIFIER = "mdta/com.apple.quicktime.still-image-time"

    def __init__(self, logger):
        self.logger = logger
        self.exiftool = which("exiftool")
        self.importer = AppleLivePhotoImporter(logger)
        self.foundation = None
        self.quartz = None
        self.avfoundation = None
        self.core_media = None
        try:
            import AVFoundation
            import CoreMedia
            import Foundation
            import Quartz
        except ImportError:
            return
        self.avfoundation = AVFoundation
        self.core_media = CoreMedia
        self.foundation = Foundation
        self.quartz = Quartz

    def process(self, photo: Path, motion: Path) -> bool:
        if not photo.is_file() or not motion.is_file():
            return False
        asset_id = str(uuid4()).upper()
        photo_embedded = self.write_photo_metadata(photo, asset_id)
        still_image_time_embedded = self.write_still_image_time_metadata(motion)
        motion_embedded = self.write_motion_metadata(motion, asset_id)
        self.write_manifest(
            photo,
            motion,
            asset_id,
            photo_embedded,
            motion_embedded,
            still_image_time_embedded,
        )
        if still_image_time_embedded:
            self.logger.info(
                f"已为 Apple 风格动态文件写入 still-image-time 元数据轨: {motion.resolve()}",
                False,
            )
        if motion_embedded:
            self.logger.info(
                f"已为 Apple 风格动态文件写入 ContentIdentifier: {motion.resolve()}",
                False,
            )
        if not self.exiftool:
            if not motion_embedded:
                self.logger.warning(
                    "未检测到 exiftool，当前环境无法为动态文件写入 ContentIdentifier",
                )
        if not photo_embedded:
            self.logger.warning(
                f"未能为图片写入 Apple ContentIdentifier: {photo.resolve()}",
            )
        if not still_image_time_embedded:
            self.logger.warning(
                f"未能为动态文件写入 still-image-time 元数据轨: {motion.resolve()}",
            )
        if not motion_embedded:
            self.logger.warning(
                f"未能为动态文件写入 ContentIdentifier: {motion.resolve()}",
            )
            return False
        self.importer.import_pair(photo, motion)
        return photo_embedded and motion_embedded

    def import_static_photo(self, photo: Path) -> bool:
        if not photo.is_file():
            return False
        return self.importer.import_photo(photo)

    def import_video(self, video: Path) -> bool:
        if not video.is_file():
            return False
        return self.importer.import_video(video)

    def write_manifest(
        self,
        photo: Path,
        motion: Path,
        asset_id: str,
        photo_embedded: bool,
        motion_embedded: bool,
        still_image_time_embedded: bool,
    ) -> Path:
        manifest = photo.with_name(f"{photo.stem}.livephoto.json")
        with manifest.open("w", encoding="utf-8") as file:
            dump(
                {
                    "asset_id": asset_id,
                    "photo": photo.name,
                    "motion": motion.name,
                    "status": {
                        "photo_content_identifier_embedded": photo_embedded,
                        "motion_content_identifier_embedded": motion_embedded,
                        "motion_still_image_time_track_embedded": (
                            still_image_time_embedded
                        ),
                    },
                    "next_step": (
                        "Import the pair with a macOS Photos/PhotoKit pipeline "
                        "to finish Apple Live Photo pairing."
                    ),
                },
                file,
                indent=4,
                ensure_ascii=False,
            )
        self.logger.info(f"已生成 Apple 实况资产清单: {manifest.resolve()}", False)
        return manifest

    def write_photo_metadata(self, photo: Path, asset_id: str) -> bool:
        if not self.quartz or not self.foundation:
            return False
        source_url = self.foundation.NSURL.fileURLWithPath_(str(photo.resolve()))
        source = self.quartz.CGImageSourceCreateWithURL(source_url, None)
        if source is None:
            return False
        image = self.quartz.CGImageSourceCreateImageAtIndex(source, 0, None)
        if image is None:
            return False
        properties = dict(
            self.quartz.CGImageSourceCopyPropertiesAtIndex(source, 0, None) or {}
        )
        properties["{MakerApple}"] = {"17": asset_id}
        target = photo.with_name(f"{photo.stem}.appletmp{photo.suffix}")
        target.unlink(missing_ok=True)
        destination = self.quartz.CGImageDestinationCreateWithURL(
            self.foundation.NSURL.fileURLWithPath_(str(target.resolve())),
            "public.jpeg",
            1,
            None,
        )
        if destination is None:
            return False
        self.quartz.CGImageDestinationAddImage(destination, image, properties)
        if not self.quartz.CGImageDestinationFinalize(destination) or not target.is_file():
            target.unlink(missing_ok=True)
            return False
        target.replace(photo)
        self.logger.info(
            f"已为 Apple 风格静态图片写入 ContentIdentifier: {photo.resolve()}",
            False,
        )
        return True

    def write_still_image_time_metadata(self, motion: Path) -> bool:
        if not self.avfoundation or not self.core_media:
            return False
        target = motion.with_name(f"{motion.stem}.livephototmp{motion.suffix}")
        target.unlink(missing_ok=True)
        source_url = self.foundation.NSURL.fileURLWithPath_(str(motion.resolve()))
        target_url = self.foundation.NSURL.fileURLWithPath_(str(target.resolve()))
        asset = self.avfoundation.AVAsset.assetWithURL_(source_url)
        reader, error = self.avfoundation.AVAssetReader.assetReaderWithAsset_error_(
            asset,
            None,
        )
        if reader is None:
            self.logger.warning(f"创建 AVAssetReader 失败: {error}")
            return False
        writer, error = (
            self.avfoundation.AVAssetWriter.assetWriterWithURL_fileType_error_(
                target_url,
                self.avfoundation.AVFileTypeQuickTimeMovie,
                None,
            )
        )
        if writer is None:
            self.logger.warning(f"创建 AVAssetWriter 失败: {error}")
            return False
        track_pairs = self.create_track_pairs(asset, reader, writer)
        if not track_pairs:
            target.unlink(missing_ok=True)
            return False
        metadata_input, adaptor = self.create_still_image_time_input(writer)
        if metadata_input is None or adaptor is None:
            target.unlink(missing_ok=True)
            return False
        if not writer.startWriting():
            self.logger.warning(f"启动 AVAssetWriter 失败: {writer.error()}")
            target.unlink(missing_ok=True)
            return False
        if not reader.startReading():
            self.logger.warning(f"启动 AVAssetReader 失败: {reader.error()}")
            target.unlink(missing_ok=True)
            return False
        writer.startSessionAtSourceTime_(self.core_media.kCMTimeZero)
        if not self.copy_track_samples(track_pairs):
            self.cancel_av_session(reader, writer, target)
            return False
        if not self.append_still_image_time_group(adaptor):
            self.cancel_av_session(reader, writer, target)
            return False
        metadata_input.markAsFinished()
        finished = Event()
        writer.finishWritingWithCompletionHandler_(lambda: finished.set())
        finished.wait(20)
        if (
            writer.status() != self.avfoundation.AVAssetWriterStatusCompleted
            or reader.status() != self.avfoundation.AVAssetReaderStatusCompleted
            or not target.is_file()
        ):
            self.logger.warning(
                "生成 still-image-time 元数据轨失败: "
                f"writer={writer.status()} reader={reader.status()} "
                f"writer_error={writer.error()} reader_error={reader.error()}"
            )
            target.unlink(missing_ok=True)
            return False
        target.replace(motion)
        return True

    def create_track_pairs(self, asset, reader, writer) -> list[tuple]:
        track_pairs = []
        for media_type in (
            self.avfoundation.AVMediaTypeVideo,
            self.avfoundation.AVMediaTypeAudio,
        ):
            for track in asset.tracksWithMediaType_(media_type):
                output = (
                    self.avfoundation.AVAssetReaderTrackOutput.alloc()
                    .initWithTrack_outputSettings_(track, None)
                )
                input_ = (
                    self.avfoundation.AVAssetWriterInput.alloc()
                    .initWithMediaType_outputSettings_(media_type, None)
                )
                input_.setExpectsMediaDataInRealTime_(False)
                if not reader.canAddOutput_(output) or not writer.canAddInput_(input_):
                    self.logger.warning(f"添加 {media_type} 轨道失败")
                    return []
                reader.addOutput_(output)
                writer.addInput_(input_)
                track_pairs.append((output, input_))
        return track_pairs

    def create_still_image_time_input(self, writer):
        specification = [
            {
                (
                    self.core_media.kCMMetadataFormatDescriptionMetadataSpecificationKey_Identifier
                ): self.STILL_IMAGE_TIME_IDENTIFIER,
                (
                    self.core_media.kCMMetadataFormatDescriptionMetadataSpecificationKey_DataType
                ): self.core_media.kCMMetadataBaseDataType_SInt8,
            }
        ]
        status, format_hint = (
            self.core_media.CMMetadataFormatDescriptionCreateWithMetadataSpecifications(
                None,
                self.core_media.kCMMetadataFormatType_Boxed,
                specification,
                None,
            )
        )
        if status != 0:
            self.logger.warning(f"创建 still-image-time 格式描述失败: {status}")
            return None, None
        input_ = (
            self.avfoundation.AVAssetWriterInput.alloc()
            .initWithMediaType_outputSettings_sourceFormatHint_(
                self.avfoundation.AVMediaTypeMetadata,
                None,
                format_hint,
            )
        )
        input_.setExpectsMediaDataInRealTime_(False)
        if not writer.canAddInput_(input_):
            self.logger.warning("添加 still-image-time 元数据轨失败")
            return None, None
        writer.addInput_(input_)
        adaptor = (
            self.avfoundation.AVAssetWriterInputMetadataAdaptor.assetWriterInputMetadataAdaptorWithAssetWriterInput_(
                input_
            )
        )
        return input_, adaptor

    def copy_track_samples(self, track_pairs: list[tuple]) -> bool:
        pending = [
            {
                "output": output,
                "input": input_,
                "sample_buffer": output.copyNextSampleBuffer(),
            }
            for output, input_ in track_pairs
        ]
        idle_since = monotonic()
        while True:
            available = [item for item in pending if item["sample_buffer"] is not None]
            if not available:
                break
            ready_items = [
                item for item in available if item["input"].isReadyForMoreMediaData()
            ]
            if not ready_items:
                if monotonic() - idle_since >= 10:
                    media_types = ", ".join(
                        item["input"].mediaType() for item in available
                    )
                    self.logger.warning(f"等待写入轨道超时: {media_types}")
                    return False
                sleep(0.01)
                continue
            idle_since = monotonic()
            current = min(
                ready_items,
                key=lambda item: self.sample_buffer_sort_key(item["sample_buffer"]),
            )
            if not current["input"].appendSampleBuffer_(current["sample_buffer"]):
                self.logger.warning(
                    f"写入媒体采样失败: {current['input'].mediaType()}"
                )
                return False
            current["sample_buffer"] = current["output"].copyNextSampleBuffer()
        for item in pending:
            item["input"].markAsFinished()
        return True

    def sample_buffer_sort_key(self, sample_buffer) -> tuple[int, int, int]:
        pts = self.core_media.CMSampleBufferGetPresentationTimeStamp(sample_buffer)
        return (
            pts.epoch,
            pts.value,
            pts.timescale,
        )

    def append_still_image_time_group(self, adaptor) -> bool:
        item = self.avfoundation.AVMutableMetadataItem.alloc().init()
        item.setIdentifier_(self.STILL_IMAGE_TIME_IDENTIFIER)
        item.setKeySpace_(self.avfoundation.AVMetadataKeySpaceQuickTimeMetadata)
        item.setKey_("com.apple.quicktime.still-image-time")
        item.setDataType_(self.core_media.kCMMetadataBaseDataType_SInt8)
        item.setValue_(0)
        time_range = self.core_media.CMTimeRangeMake(
            self.core_media.kCMTimeZero,
            self.core_media.CMTimeMake(1, 1000),
        )
        group = self.avfoundation.AVTimedMetadataGroup.alloc().initWithItems_timeRange_(
            [item],
            time_range,
        )
        return bool(adaptor.appendTimedMetadataGroup_(group))

    @staticmethod
    def cancel_av_session(reader, writer, target: Path) -> None:
        reader.cancelReading()
        writer.cancelWriting()
        target.unlink(missing_ok=True)

    def write_motion_metadata(self, motion: Path, asset_id: str) -> bool:
        if not self.exiftool:
            return False
        try:
            run(
                [
                    self.exiftool,
                    "-overwrite_original",
                    f"-Keys:ContentIdentifier={asset_id}",
                    str(motion),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except CalledProcessError:
            return False
        return True
