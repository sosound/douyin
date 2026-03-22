from os import getenv
from pathlib import Path
from platform import system
from shutil import which
from subprocess import CalledProcessError, run
from threading import Event
from time import sleep

__all__ = ["AppleLivePhotoImporter"]


class AppleLivePhotoImporter:
    APPLESCRIPT_IMPORT_SETTLE_SECONDS = 6

    def __init__(self, logger):
        self.logger = logger
        self.enabled = self._check_enabled()
        self.script = (
            Path(__file__).resolve().parents[2]
            .joinpath("tools", "apple", "import_live_photo.swift")
        )
        self.swift = which("xcrun") or which("swift")
        self.osascript = which("osascript")
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

    def _authorized_access_levels(self) -> tuple[int, ...]:
        if not self.photos:
            return ()
        levels = []
        add_only = getattr(self.photos, "PHAccessLevelAddOnly", None)
        read_write = getattr(self.photos, "PHAccessLevelReadWrite", None)
        if add_only is not None:
            levels.append(add_only)
        if read_write is not None and read_write not in levels:
            levels.append(read_write)
        return tuple(levels) or (1, 2)

    def _photos_access_allowed(self) -> bool:
        if not self.photos:
            return False
        for level in self._authorized_access_levels():
            status = self.photos.PHPhotoLibrary.authorizationStatusForAccessLevel_(
                level
            )
            if status in (3, 4):
                return True
        return False

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
            if self.import_pair_with_pyobjc(photo, motion):
                return True
            if self.osascript:
                self.logger.warning(
                    "Apple 实况的 PhotoKit 导入失败，已回退到 Photos AppleScript 导入"
                )
                return self.import_pair_with_osascript(photo, motion)
            return False
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

    def import_pair_with_osascript(self, photo: Path, motion: Path) -> bool:
        if not self.osascript:
            self.logger.warning("未检测到 osascript，已跳过 Apple 实况导入")
            return False
        photo_path = str(photo.resolve()).replace("\\", "\\\\").replace('"', '\\"')
        motion_path = str(motion.resolve()).replace("\\", "\\\\").replace('"', '\\"')
        command = [
            self.osascript,
            "-e",
            (
                'tell application "Photos" to import '
                f'{{POSIX file "{photo_path}", POSIX file "{motion_path}"}} '
                "with skip check duplicates"
            ),
        ]
        try:
            run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self.logger.warning(
                f"AppleScript 导入 Apple 实况到 Photos 失败: {message or 'unknown error'}"
            )
            return False
        # Photos 在 AppleScript import 返回后仍会异步整理资源。
        # 多组实况连续导入过快时，前一组可能还没稳定配对就被后一组打断。
        sleep(self.APPLESCRIPT_IMPORT_SETTLE_SECONDS)
        self.logger.info(
            f"Apple 实况已通过 AppleScript 导入 Photos: {photo.name}",
            False,
        )
        return True

    def import_photo(self, photo: Path) -> bool:
        if not self.enabled or system() != "Darwin":
            return False
        if self.photos and self.foundation:
            if self.import_photo_with_pyobjc(photo):
                return True
            if self.osascript:
                self.logger.warning(
                    "静态图片的 PhotoKit 导入失败，已回退到 Photos AppleScript 导入"
                )
                return self.import_photo_with_osascript(photo)
            return False
        if self.osascript:
            return self.import_photo_with_osascript(photo)
        self.logger.warning("当前环境缺少可用的 Photos 导入桥，已跳过静态图片导入")
        return False

    def import_video(self, video: Path) -> bool:
        if not self.enabled or system() != "Darwin":
            return False
        if self.photos and self.foundation:
            if self.import_video_with_pyobjc(video):
                return True
            if self.osascript:
                self.logger.warning(
                    "视频的 PhotoKit 导入失败，已回退到 Photos AppleScript 导入"
                )
                return self.import_video_with_osascript(video)
            return False
        if self.osascript:
            return self.import_video_with_osascript(video)
        self.logger.warning("当前环境缺少可用的 Photos 导入桥，已跳过视频导入")
        return False

    def import_pair_with_pyobjc(self, photo: Path, motion: Path) -> bool:
        if not self._photos_access_allowed():
            self.logger.warning(
                "Photos 权限状态不允许导入 Apple 实况，"
                f"当前状态码: {[self.photos.PHPhotoLibrary.authorizationStatusForAccessLevel_(level) for level in self._authorized_access_levels()]}"
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

    def import_photo_with_pyobjc(self, photo: Path) -> bool:
        if not self._photos_access_allowed():
            self.logger.warning(
                "Photos 权限状态不允许导入静态图片，"
                f"当前状态码: {[self.photos.PHPhotoLibrary.authorizationStatusForAccessLevel_(level) for level in self._authorized_access_levels()]}"
            )
            return False

        photo_url = self.foundation.NSURL.fileURLWithPath_(str(photo.resolve()))
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
            self.logger.warning("静态图片导入超时")
            return False
        if result["success"]:
            self.logger.info(
                f"静态图片已导入 Photos: {result['id'] or 'created'}",
                False,
            )
            return True
        self.logger.warning(
            "PhotoKit 拒绝了当前静态图片: "
            f"{result['error'] or 'unknown error'}"
        )
        return False

    def import_photo_with_osascript(self, photo: Path) -> bool:
        if not self.osascript:
            self.logger.warning("未检测到 osascript，已跳过静态图片导入")
            return False
        path = str(photo.resolve()).replace("\\", "\\\\").replace('"', '\\"')
        command = [
            self.osascript,
            "-e",
            f'tell application "Photos" to import {{POSIX file "{path}"}} with skip check duplicates',
        ]
        try:
            run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self.logger.warning(
                f"AppleScript 导入静态图片到 Photos 失败: {message or 'unknown error'}"
            )
            return False
        self.logger.info(f"静态图片已导入 Photos: {photo.name}", False)
        return True

    def import_video_with_pyobjc(self, video: Path) -> bool:
        if not self._photos_access_allowed():
            self.logger.warning(
                "Photos 权限状态不允许导入视频，"
                f"当前状态码: {[self.photos.PHPhotoLibrary.authorizationStatusForAccessLevel_(level) for level in self._authorized_access_levels()]}"
            )
            return False

        video_url = self.foundation.NSURL.fileURLWithPath_(str(video.resolve()))
        done = Event()
        result = {"success": False, "error": None, "id": None}

        def change_block():
            request = self.photos.PHAssetCreationRequest.creationRequestForAsset()
            video_options = (
                self.photos.PHAssetResourceCreationOptions.alloc().init()
            )
            video_options.setShouldMoveFile_(False)
            request.addResourceWithType_fileURL_options_(
                self.photos.PHAssetResourceTypeVideo,
                video_url,
                video_options,
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
            self.logger.warning("视频导入超时")
            return False
        if result["success"]:
            self.logger.info(
                f"视频已导入 Photos: {result['id'] or video.name}",
                False,
            )
            return True
        self.logger.warning(
            "PhotoKit 拒绝了当前视频: "
            f"{result['error'] or 'unknown error'}"
        )
        return False

    def import_video_with_osascript(self, video: Path) -> bool:
        if not self.osascript:
            self.logger.warning("未检测到 osascript，已跳过视频导入")
            return False
        path = str(video.resolve()).replace("\\", "\\\\").replace('"', '\\"')
        command = [
            self.osascript,
            "-e",
            f'tell application "Photos" to import POSIX file "{path}"',
        ]
        try:
            run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            self.logger.warning(
                f"AppleScript 导入视频到 Photos 失败: {message or 'unknown error'}"
            )
            return False
        self.logger.info(f"视频已导入 Photos: {video.name}", False)
        return True
