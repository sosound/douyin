from .base import APIModel


class ShortcutImport(APIModel):
    text: str
    live_photo_mode: str = "apple"
    folder_name: str = ""
    keep_files: bool = False
    background: bool = True
