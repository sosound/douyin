from .base import APIModel


class Detail(APIModel):
    detail_id: str


class DetailTikTok(Detail):
    pass


class DetailDownload(Detail):
    live_photo_mode: str = "apple"
    folder_name: str = ""
