# -*- coding: utf-8 -*-
from requests import session as RqSession, get as RqGet
from json import loads as json_load
from traceback import format_exc as printErrer
from re import findall
from api import writeLog


class MusicScrapyNetease(object):
    """网易云api爬虫"""
    @staticmethod
    def downloadSong(song_id:int, br:str="128", url:bool=False):
        """下载128 192 320 flac"""
        api_url = "https://api.itooi.cn/netease/url?id={}&quality={}".format(song_id, br)
        if url:
            return api_url
        response = RqGet(url=api_url)
        return response.content

    @staticmethod
    def getSongInfos(song_id:int):
        """获取音乐信息"""
        api_url = "https://api.itooi.cn/netease/song?id={}".format(song_id)
        response = RqGet(url=api_url)
        reply_json = response.json()["data"]["songs"]
        length = reply_json["dt"]
        album_json = reply_json["al"]
        album_name = album_json["name"]
        pic_url = album_json["picUrl"]
        title = reply_json["name"]
        songers_list = reply_json["ar"]
        # 歌手
        songers = ""
        for songer in songers_list:
            songers += "{};".format(songer["name"])
        songers  = songers[:-1]
        return title, length, songers, album_name, pic_url

    @staticmethod
    def fromSongListGetSongs(song_list_id:int, func):
        """从歌单中获得歌曲"""
        api_url = "https://api.itooi.cn/netease/songList?id={}".format(song_list_id)
        response = RqGet(url=api_url)
        reply_json = response.json()
        songs_list = reply_json["data"]["tracks"]
        for song_json in songs_list:
            song_id = song_json["id"]
            title, length, songers, album, pic_url = MusicScrapyNetease.getSongInfos(int(song_id))
            url = MusicScrapyNetease.downloadSong(int(song_id), url=True)
            func(title, songers, length, url, album, pic_url)

    @staticmethod
    def search(content:str, page:int, func):
        """获取专辑信息"""
        api_url = "https://api.itooi.cn/netease/search?keyword={}&type=song&pageSize=20&page={}".format(content, page)
        response = RqGet(url=api_url)
        songs_json = response.json()["data"]["songs"]
        for song in songs_json:
            length = song["dt"]
            song_id = song["id"]
            url = MusicScrapyNetease.downloadSong(int(song_id), url=True)
            pic_url = song["al"]["picUrl"]
            album = song["al"]["name"]
            songers_list = song["ar"]
            songers = ""
            for songer in songers_list:
                songers += "{},".format(songer["name"])
            songers = songers[:-1]
            title = song["name"]
            func(title, songers, length, url, album, pic_url)


class MusicScrapyTongzan(object):
    """歌曲爬虫www.tongzan.com"""
    ORIGIN_QQ = "tencent"  # QQ
    ORIGIN_NETEASE = "netease"  # 网易云
    ORIGIN_KUGOU = "kugou"  # 酷狗
    ORIGIN_BAIDU = "baidu"  # 百度
    def __init__(self):
        self.host = "https://tongzan.com"
        self.callback_url = "jQuery1113025711367530255314_1593404740630"
        self.url = "https://tongzan.com/music/api.php?callback=" + self.callback_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
        }
        self.session = RqSession()
        self.max_page = 1

    def search(self, search:str, source:str, page:int, func):
        """搜索歌曲"""
        data = {
            "types": "search",
            "count": "20",
            "source": source,
            "pages": int(page),
            "name": search,
        }
        response = self.session.post(url=self.url, headers=self.headers, data=data)
        reply_text = findall(r"jQuery.+?\((.+)\)", response.text)[0]
        reply_json = json_load(reply_text)
        for song_json in reply_json:
            song_id = song_json["id"]  # 歌曲id
            title = song_json["name"]  # 标题
            # 歌手
            songers_list = song_json["artist"]
            songers = ""
            for songer in songers_list:
                songers += "{},".format(songer)
            songers = songers[:-1]
            album = song_json["album"]  # 专辑名
            source2 = song_json["source"]  # 来源
            # 图片
            pic_id = song_json["pic_id"]  # 图片id
            pic_url = self.getPic(int(pic_id), source2)
            # url
            url_id = song_json["url_id"]  # urlid
            url = self.getUrl(int(url_id), source2)
            lyric_id = song_json["lyric_id"]  # 歌词id
            func(title, songers, None, url, album, pic_url)

    def getPic(self, pic_id:int, source:str):
        """获取图片"""
        data = {
            "types": "pic",
            "id": str(pic_id),
            "source": source,
        }
        pic_url = ""
        try:
            response = self.session.post(url=self.url, headers=self.headers, data=data)
            resply_text = findall(r"jQuery.+?\((.+)\)", response.text)[0]
            resply_json = json_load(resply_text)
            pic_url = resply_json["url"]
        except Exception as e:
            out_str = "爬虫错误！:{}\n{}".format(e.args, printErrer)
            writeLog(out_str, "error")
        finally:
            return pic_url

    def getUrl(self, song_id:int, source:str):
        """获取歌曲url"""
        data = {
            "types": "url",
            "id": str(song_id),
            "source": source,
        }
        url = ""
        try:
            response = self.session.post(url=self.url, headers=self.headers, data=data)
            resply_text = findall(r"jQuery.+?\((.+)\)", response.text)[0]
            reply_json = json_load(resply_text)
            url = reply_json["url"]
            size = reply_json["size"]  # 文件大小
            br = reply_json["br"]  # eg.128/320
        except Exception as e:
            out_str = "爬虫错误！:{}\n{}".format(e.args, printErrer)
            writeLog(out_str, "error")
        finally:
            return url

    def getLyric(self, lyric_id:int, source:str):
        """获取歌词"""
        data = {
            "types": "lyric",
            "id": str(lyric_id),
            "source": source,
        }
        lyric = ""
        try:
            response = self.session.post(url=self.url, headers=self.headers, data=data)
            resply_text = findall(r"jQuery.+?\((.+)\)", response.text)[0]
            reply_json = json_load(resply_text)
            lyric = reply_json["lyric"]
        except Exception as e:
            out_str = "爬虫错误！:{}\n{}".format(e.args, printErrer)
            writeLog(out_str, "error")
        return lyric


if __name__ == '__main__':
    MusicScrapyNetease.search("父亲写的散文诗", 1)