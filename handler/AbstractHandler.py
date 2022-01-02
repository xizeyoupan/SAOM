from abc import ABCMeta, abstractmethod
from SAOM import SAOM


class AbstractHandler(metaclass=ABCMeta):
    """
    这个类名需要与文件名保持一致
    音乐处理所必须实现的接口
    SAOM 实例采用异步上下文管理器的方式调用Handler实例
    所以需要实现 __aenter__ 和 __aexit__

    请在根目录config.json中配置handler字段
    下面是一个最简示例
    "netease": {"handlerName": "NeteaseHandler","name": "网易云","shortcut": "ne"}
    "netease": 配置的名字
    "handlerName": 实现了 AbstractHandler 的类名
    "name": 名字
    "shortcut": 在命令中 -m 后面的指定的值，用于选择哪个handler
    """

    @abstractmethod
    def __init__(self, ctx: SAOM) -> None:
        """
        SAOM 实例会把自身作为ctx传入
        """
        self.ctx = ctx

    @abstractmethod
    async def __aenter__(self):
        return self

    @abstractmethod
    async def single_song(self, search_key: str):
        """
        单曲点歌

        最后必须要调用ctx.song_did_download(song_info)来通知SAOM 实例下载完成
        在这个生命周期中可能有用的函数,会改变游戏内的提示信息，*为必须:

        ctx.song_will_search(search_key): 建议搜索前调用

        ctx.song_did_search(song_info): 建议搜索完成后调用，song_info 必有的字段为:
        song_info = {"song_name": song_name, "artist_name": artist_name, "song_id": song_id,"handler_name": handler_name}

        ctx.no_copyright(song_info): 没有版权，song_info 字段同上

        ctx.song_do_download(song_info): 正在下载，song_info 字段在上面基础上增加
        song_info['downloading']，表示下载进度，值在为float类型，0.0-1.0之间

        *ctx.song_did_download(song_info): 下载完成，song_info 字段在上面基础上增加
        song_info["song_url"] : 歌曲下载地址
        song_info["file_name"] : 歌曲文件名
        song_info["content"] : 歌曲文件内容, BytesIO对象

        """
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass
