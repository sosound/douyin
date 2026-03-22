from json import dump
from pathlib import Path
from typing import Callable
from typing import TYPE_CHECKING
from typing import Union

from src.interface.template import API
from src.translation import _

if TYPE_CHECKING:
    from src.config import Parameter
    from src.testers import Params


class Detail(API):
    def __init__(
        self,
        params: Union["Parameter", "Params"],
        cookie: str = "",
        proxy: str = None,
        detail_id: str = ...,
    ):
        super().__init__(params, cookie, proxy)
        self.detail_id = detail_id
        self.api = f"{self.domain}aweme/v1/web/aweme/detail/"
        self.text = _("作品")

    def generate_params(
        self,
    ) -> dict:
        return self.params | {
            "aweme_id": self.detail_id,
            "version_code": "190500",
            "version_name": "19.5.0",
        }

    async def run(
        self,
        referer: str = None,
        single_page=True,
        data_key: str = "aweme_detail",
        error_text="",
        cursor="cursor",
        has_more="has_more",
        params: Callable = lambda: {},
        data: Callable = lambda: {},
        method="GET",
        headers: dict = None,
        *args,
        **kwargs,
    ):
        return await super().run(
            referer,
            single_page,
            data_key,
            error_text,
            cursor,
            has_more,
            params,
            data,
            method,
            headers,
            *args,
            **kwargs,
        )

    def check_response(
        self,
        data_dict: dict,
        data_key: str,
        error_text="",
        cursor="cursor",
        has_more="has_more",
        *args,
        **kwargs,
    ):
        try:
            if not (d := data_dict[data_key]):
                self.log.warning(error_text)
            else:
                self.response = d
                self.dump_detail_response(data_dict, d)
        except KeyError:
            self.log.error(
                _("数据解析失败，请告知作者处理: {data}").format(data=data_dict)
            )

    def dump_detail_response(self, data_dict: dict, detail: dict) -> None:
        if not getattr(self.runtime_params, "detail_dump", False):
            return
        aweme_id = (
            self.detail_id
            or detail.get("aweme_id")
            or detail.get("awemeId")
            or "unknown"
        )
        dump_dir = Path(self.runtime_params.cache).joinpath("detail_dump")
        dump_dir.mkdir(exist_ok=True)
        dump_path = dump_dir.joinpath(f"aweme_detail_{aweme_id}.json")
        with dump_path.open("w", encoding="utf-8") as f:
            dump(data_dict, f, indent=2, ensure_ascii=False)
        self.log.info(f"作品详情原始响应已保存: {dump_path}", False)


async def test():
    from src.testers import Params

    async with Params() as params:
        i = Detail(
            params,
            detail_id="",
        )
        print(await i.run())


if __name__ == "__main__":
    from asyncio import run

    run(test())
