# -*- coding: utf-8 -*-
# 常量设置
# 文件夹路径
UI_PATH = "./ui"  # ui文件夹
IMG_PATH = UI_PATH + "/img"  # 图片文件夹
INFOS_PATH = "./infos"  # 信息文件夹
CACHE_PATH = "./cache"  # 缓存目录
LOG_PATH = "./log"  # log目录
# 文件目录
INI_LOCAL_MUSIC_PATH = INFOS_PATH + "/local_music.ini"  # 本地音乐配置
INI_PATH = INFOS_PATH + "/setting.ini"  # 基本配置
LOG_FILE_PATH  = LOG_PATH + "/log.txt"  # log文件

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
}
# 其他
ALLOWED_FORMAT = ("mp3")  # 允许的文件格式