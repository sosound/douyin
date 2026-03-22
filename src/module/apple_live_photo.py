from json import dump
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError, run
from uuid import uuid4

from .apple_live_photo_importer import AppleLivePhotoImporter

__all__ = ["AppleLivePhotoProcessor"]


class AppleLivePhotoProcessor:
    def __init__(self, logger):
        self.logger = logger
        self.exiftool = which("exiftool")
        self.importer = AppleLivePhotoImporter(logger)
        self.foundation = None
        self.quartz = None
        try:
            import Foundation
            import Quartz
        except ImportError:
            return
        self.foundation = Foundation
        self.quartz = Quartz

    def process(self, photo: Path, motion: Path) -> bool:
        if not photo.is_file() or not motion.is_file():
            return False
        asset_id = str(uuid4()).upper()
        photo_embedded = self.write_photo_metadata(photo, asset_id)
        motion_embedded = self.write_motion_metadata(motion, asset_id)
        self.write_manifest(photo, motion, asset_id, photo_embedded, motion_embedded)
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
        if not motion_embedded:
            self.logger.warning(
                f"未能为动态文件写入 ContentIdentifier: {motion.resolve()}",
            )
            return False
        self.importer.import_pair(photo, motion)
        return photo_embedded and motion_embedded

    def write_manifest(
        self,
        photo: Path,
        motion: Path,
        asset_id: str,
        photo_embedded: bool,
        motion_embedded: bool,
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
