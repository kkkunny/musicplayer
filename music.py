# -*- coding: utf-8 -*-
# 音乐
from PySide2.QtCore import QUrl
from PySide2.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from requests import get as RqGet
from random import shuffle as randomList
from time import time as TimeStamp
from constant import *


class MusicSong(object):
    """音乐单曲"""
    def __init__(self, title:str, songers:str, length:int=None, album:str="", url:str=None, path:str=None, pic_url:str=None, pic_path:str=None):
        self.title = title  # 标题
        self.songers = songers  # 歌手
        self.length = length  # 时长(毫秒)
        self.album = album  # 专辑
        self.url = url  # 网络地址
        self.path = path  # 本地地址
        self.pic_url = pic_url  # 图片网络地址
        self.pic_path = pic_path  # 图片本地地址

    def getLength(self) -> str:
        """获取歌曲时长"""
        if self.length:
            minute = int(self.length / 1000 // 60)
            second = round(((self.length / 1000 / 60) - minute) * 60)
            length = "{}:{}".format(minute, second)
            return length
        return ""


class MusicPlayer(object):
    """音乐播放器"""
    MODE1 = "列表循环"
    MODE2 = "随机播放"
    MODE3 = "列表播放"
    MODE4 = "单曲循环"
    DIRECTION_NEXT = "next"
    DIRECTION_PREV = "prev"
    STUTS_STOPPING = QMediaPlayer.StoppedState  # 停止状态
    STUTS_PAUSING = QMediaPlayer.PausedState  # 暂停状态
    STUTS_PLAYING = QMediaPlayer.PlayingState  # 播放状态
    def __init__(self, mode:str):
        # 属性
        self.__player = QMediaPlayer()  # Qt播放器
        self.cur_song = None  # 当前播放的歌曲
        self.songs = []  # 播放列表[(), ...]
        self.__songs = QMediaPlaylist()  # Qt播放列表
        self.mode = mode  # 模式
        # 设置
        self.__player.setPlaylist(self.__songs)  # 设置播放列表
        self.__player.audioAvailableChanged.connect(self.audioAvailableChangedFunc)  # 音频是否可用

    def play(self):
        """播放"""
        self.__player.play()

    def playPrev(self):
        """播放上一首"""
        index = self.songs.index(self.cur_song)  # 查找当前播放歌曲在歌曲播放列表中的索引
        if index - 1 >= 0:  # 上一首在列表内
            self.playSong(self.songs[index-1])  # 播放上一首
        elif self.mode == self.MODE2:  # 随机播放
            randomList(self.songs)
            self.playSong(self.songs[len(self.songs)-1])  # 播放最后一首
        else:  # 不在列表内
            self.playSong(self.songs[len(self.songs)-1])  # 播放最后一首

    def playNext(self):
        """播放下一首"""
        index = self.songs.index(self.cur_song)  # 查找当前播放歌曲在歌曲播放列表中的索引
        if index + 1 < len(self.songs):  # 下一首在列表内
            self.playSong(self.songs[index+1])  # 播放下一首
        else:  # 不在列表内
            if self.mode == self.MODE3:  # 列表播放
                self.stop()
            elif self.mode == self.MODE2:  # 随机播放
                randomList(self.songs)
                self.playSong(self.songs[0])  # 播放第一首
            else:
                self.playSong(self.songs[0])  # 播放第一首

    def pause(self):
        """暂停"""
        self.__player.pause()

    def stop(self):
        """停止(暂停并将播放进度归零)"""
        self.__player.stop()
        self.cur_song = self.songs[0]  # 回到第一首

    def nextControl(self, directin:str):
        """下一首控制"""
        if self.mode in (self.MODE1, self.MODE2, self.MODE3):  # 列表循环
            if directin == self.DIRECTION_NEXT:  # 下一首
                self.playNext()  # 播放下一首
            elif directin == self.DIRECTION_PREV:  # 上一首
                self.playPrev()  # 播放上一首
        elif self.mode == self.MODE4:  # 单曲循环
            self.playSong(self.cur_song)  # 播放当前这首歌曲

    def playSong(self, song:MusicSong):
        """播放一首歌曲"""
        self.cur_song = song  # 改变当前播放的音乐
        self.__songs.clear()  # 清空Qt播放列表
        if song.url and not song.path:  # 只有url
            # 下载音乐
            path = CACHE_PATH + "/{}".format(int(TimeStamp()))
            response = RqGet(url=song.url)
            if response.status_code == 200:
                with open(path + ".mp3", "wb") as file:
                    file.write(response.content)
                song.path = path + ".mp3"
                # 下载图片
                response = RqGet(url=song.pic_url)
                if response.status_code == 200:
                    with open(path + ".jpg", "wb") as file:
                        file.write(response.content)
                    song.pic_path = path + ".jpg"
                self.__songs.addMedia(QMediaContent(QUrl.fromLocalFile(song.path)))
                self.play()
        elif (not song.url and song.path) or (song.url and song.path):  # 有本地地址
            self.__songs.addMedia(QMediaContent(QUrl.fromLocalFile(song.path)))
            self.play()

    def playList(self, songs:list):
        """播放一个列表的歌曲"""
        self.songs = songs
        self.playSong(self.songs[0])

    def addToList(self, song:MusicSong):
        """增加歌曲到播放列表"""
        if song not in self.songs:
            self.songs.append(song)

    def getListLength(self) -> int:
        """获取播放列表长度"""
        return len(self.songs)

    def getMusicLength(self) -> int:
        """获取当前播放歌曲的长度"""
        if self.cur_song.length:
            return self.cur_song.length
        else:
            return self.__player.duration()

    def setPlayProcess(self, value:int):
        """设置播放进度"""
        self.__player.setPosition(value)

    def getPlayProcess(self):
        """获取已经播放的时长"""
        return self.__player.position()

    def getStuts(self):
        """获取当前播放状态"""
        return self.__player.state()

    def setVolume(self, value:int):
        """设置音量"""
        self.__player.setVolume(value)

    def getVolume(self) -> int:
        """获取音量"""
        return self.__player.volume()

    def setMuted(self, stuts:bool):
        """静音"""
        self.__player.setMuted(stuts)

    def getMuted(self) -> bool:
        """获取静音状态"""
        return self.__player.isMuted()

    def setMode(self, mode:str):
        """设置播放模式"""
        self.mode = mode
        if mode == self.MODE2:  # 随机播放
            randomList(self.songs)

    def playStutsChanged(self, func):
        """播放状态改变"""
        self.__player.stateChanged.connect(func)  # 歌曲播放状态改变

    def audioAvailableChangedFunc(self):
        """播放状态改变时调用的函数"""
        # 根据播放模式播放下一首歌曲
        if self.__player.state() == self.STUTS_PAUSING:  # 暂停时
            self.nextControl(self.DIRECTION_NEXT)

    def positionChanged(self, func):
        """播放进度改变"""
        self.__player.positionChanged.connect(func)  # 播放进度改变

    def curSongChanged(self, func):
        """当前播放的歌曲变化"""
        self.__player.currentMediaChanged.connect(func)