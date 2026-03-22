from os import getenv
from pathlib import Path
from platform import system
from shutil import which
from subprocess import CalledProcessError, run
from threading import Event

__all__ = ["AppleLivePhotoImporter"]


class AppleLivePhotoImporter:
    def __init__(self, logger):
        self.logger = logger
        self.enabled = self._check_enabled()
        self.script = (
            Path(__file__).resolve().parents[2]
            .joinpath("tools", "apple", "import_live_photo.swift")
        )
        self.swift = which("xcrun") or which("swift")
        self.photos = None
        self.foundation = None
        if system() == "Darwin":
            try:
                import Foundation
                import Photos
            except ImportError:
                self.photos = None
                self.foundation = None
            else:
                self.photos = Photos
                self.foundation = Foundation

    @staticmethod
    def _check_enabled() -> bool:
        return getenv("DOUK_APPLE_LIVE_IMPORT", "").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    def import_pair(self, photo: Path, motion: Path) -> bool:
        if not self.enabled or system() != "Darwin":
            return False
        if self.photos and self.foundation:
            return self.import_pair_with_pyobjc(photo, motion)
        if not self.script.is_file():
            self.logger.warning("未找到 macOS 实况导入脚本，已跳过 Photos 导入")
            return False
        if not self.swift:
            self.logger.warning("未检测到 swift/xcrun，已跳过 Photos 导入")
            return False
        command = (
            [self.swift, "swift", str(self.script), str(photo), str(motion)]
            if Path(self.swift).name == "xcrun"
            else [self.swift, str(self.script), str(photo), str(motion)]
        )
        try:
            result = run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self.logger.warning(
                f"导入 Apple 实况到 Photos 失败: {message or 'unknown error'}"
            )
            return False
        message = result.stdout.strip()
        if message:
            self.logger.info(f"Apple 实况已导入 Photos: {message}", False)
        else:
            self.logger.info("Apple 实况已导入 Photos", False)
        return True

    def import_pair_with_pyobjc(self, photo: Path, motion: Path) -> bool:
        status = self.photos.PHPhotoLibrary.authorizationStatusForAccessLevel_(2)
        if status not in (3, 4):
            self.logger.warning(
                f"Photos 权限状态不允许导入 Apple 实况，当前状态码: {status}"
            )
            return False

        photo_url = self.foundation.NSURL.fileURLWithPath_(str(photo.resolve()))
        motion_url = self.foundation.NSURL.fileURLWithPath_(str(motion.resolve()))
        done = Event()
        result = {"success": False, "error": None, "id": None}

        def change_block():
            request = self.photos.PHAssetCreationRequest.creationRequestForAsset()
            photo_options = (
                self.photos.PHAssetResourceCreationOptions.alloc().init()
            )
            photo_options.setShouldMoveFile_(False)
            request.addResourceWithType_fileURL_options_(
                self.photos.PHAssetResourceTypePhoto,
                photo_url,
                photo_options,
            )
            motion_options = (
                self.photos.PHAssetResourceCreationOptions.alloc().init()
            )
            motion_options.setShouldMoveFile_(False)
            request.addResourceWithType_fileURL_options_(
                self.photos.PHAssetResourceTypePairedVideo,
                motion_url,
                motion_options,
            )
            placeholder = request.placeholderForCreatedAsset()
            if placeholder is not None:
                result["id"] = str(placeholder.localIdentifier())

        def completion(success, error):
            result["success"] = bool(success)
            result["error"] = None if error is None else str(error)
            done.set()

        self.photos.PHPhotoLibrary.sharedPhotoLibrary().performChanges_completionHandler_(
            change_block,
            completion,
        )
        if not done.wait(20):
            self.logger.warning("Apple 实况导入超时")
            return False
        if result["success"]:
            self.logger.info(
                f"Apple 实况已导入 Photos: {result['id'] or 'created'}",
                False,
            )
            return True
        self.logger.warning(
            "PhotoKit 拒绝了当前 Apple 实况资产对: "
            f"{result['error'] or 'unknown error'}"
        )
        return False
