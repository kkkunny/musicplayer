# -*- coding: utf-8 -*-
# API
from mutagen import File as MFile
from mutagen.id3 import TIT2, TPE1, TALB
from time import gmtime, strftime
from constant import LOG_FILE_PATH, INI_PATH
from re import sub as reReplace
from music import MusicSong


def get_local_music(path:str) -> MusicSong:
    """获取本地音乐信息"""
    file = MFile(path)
    title = str(file["TIT2"])  # 标题
    songers = str(file["TPE1"])  # 歌手
    album = str(file["TALB"])  # 专辑名
    length = file.info.length  # 时长(秒)
    song = MusicSong(title=title, songers=songers, length=int(length * 1000), album=album, path=path)
    return song


def write_music_infos(path:str, title:str, songers:str):
    """写入歌曲信息"""
    songFile = MFile(path)
    songFile['TIT2'] = TIT2(encoding=3, text=title)  # 插入歌名
    songFile['TPE1'] = TPE1(encoding=3, text=songers)  # 歌手
    # songFile['TALB'] = TALB(encoding=3, text=album)  # 专辑
    songFile.save()


def writeLog(content:str, log_type:str):
    """写入log"""
    # 获取当前时间
    t = gmtime()
    time = strftime("%Y-%m-%d %H:%M:%S", t)
    # 写入
    if log_type == "error":  # 错误
        out_str = "[{}][error]:\n{}\n".format(time, content)
    elif log_type == "msg":  # 信息
        out_str = "[{}][msg]:\n{}\n".format(time, content)
    else:
        out_str = "[{}][{}]:\n{}\n".format(time, log_type, content)
    print(out_str)
    with open(LOG_FILE_PATH, "a") as file:
        file.write(out_str)


def writeIni(name:str, content:str):
    """写入基本配置文件"""
    text = ""
    with open(INI_PATH, "r") as file:
        text = file.read()
    with open(INI_PATH, "w") as file:
        if "{}:".format(name) in text:  # 如果有这项
            out_str = reReplace(r"{}:.+;".format(name), "{}: {};".format(name, content), text)
        else:  # 如果没有
            out_str = text + "{}: {};\n".format(name, content)
        file.write(out_str)


if __name__ == '__main__':
    MusicScrapyTongzan().search("父亲写的散文诗", MusicScrapyTongzan.ORIGIN_NETEASE, 1, "")