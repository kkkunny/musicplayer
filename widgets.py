# -*- coding: utf-8 -*-
# 控件
from PySide2.QtWidgets import QFrame, QLabel, QPushButton
from PySide2.QtGui import QPalette, QColor, QPixmap
from PySide2.QtCore import QSize, Qt
from music import *


class MusicRow(QFrame):
    """歌曲行"""
    search_all = []  # 所有歌曲
    local_all = []
    player = None  # 播放器
    TYPE_LOCAL = "local"  # 本地音乐
    TYPE_SEARCH = "search"  # 搜索音乐
    def __init__(self, parent, count:int, song:MusicSong, frame_type):
        super().__init__(parent)
        # 属性
        self.song = song  # 歌曲单曲
        self.count = count
        self.frame_type = frame_type  # 类型
        # 设置
        if self.frame_type == self.TYPE_LOCAL:  # 本地音乐
            self.local_all.append(self)
        elif self.frame_type == self.TYPE_SEARCH:  # 搜索音乐
            self.search_all.append(self)
        self.setGeometry(1, (self.count-1)*30, 998, 30)
        # 颜色
        self.is_color_change = False  # 颜色是否改变
        self.setAutoFillBackground(True)
        self.set_bg_color()
        # 计数
        count_lb = QLabel(self)
        count_lb.setGeometry(0, 0, 40, 30)
        count_lb.setText(str(self.count))
        # 音乐标题
        title_lb = QLabel(self)
        title_lb.setGeometry(110, 0, 390, 30)
        title_lb.setText(self.song.title)
        # 歌手
        songers_lb = QLabel(self)
        songers_lb.setGeometry(500, 0, 200, 30)
        songers_lb.setText(self.song.songers)
        # 专辑
        album_lb = QLabel(self)
        album_lb.setGeometry(700, 0, 200, 30)
        album_lb.setText(self.song.album)
        # 时长
        length_lb = QLabel(self)
        length_lb.setGeometry(900, 0, 100, 30)
        length_lb.setText(self.song.getLength())
        # 显示
        self.show()

    def set_bg_color(self):
        """背景颜色"""
        if self.count % 2 != 0:
            bg_color = QColor(250, 250, 250)
        else:
            bg_color = QColor(245, 245, 247)
        self.setPalette(QPalette(bg_color))

    def mousePressEvent(self, event):
        """鼠标按下"""
        self.is_color_change = True  # 颜色改变
        bg_color = QColor(227, 227, 229)
        self.setPalette(QPalette(bg_color))
        li = []
        if self.frame_type == self.TYPE_LOCAL:  # 本地音乐
            li = self.local_all
        elif self.frame_type == self.TYPE_SEARCH:  # 搜索音乐
            li = self.search_all
        for row in li:
            if row.is_color_change and row != self:
                row.set_bg_color()

    def mouseDoubleClickEvent(self, event):
        """鼠标双击"""
        row_list = []
        if self.frame_type == self.TYPE_LOCAL:  # 本地音乐
            row_list = self.local_all
        elif self.frame_type == self.TYPE_SEARCH:  # 搜索音乐
            row_list = self.search_all
        song_list = []
        for row in row_list:
            song_list.append(row.song)
        if self.player.mode == MusicPlayer.MODE2:  # 如果模式为随机播放
            randomList(song_list)
        self.player.playList(song_list)


class LeftButton(QPushButton):
    """左侧按钮"""
    all = []
    def __init__(self, parent, name:str, pos:tuple):
        super().__init__(parent=parent)
        # 属性
        self.name = name  # 名字
        self.pixmap1 = QPixmap(IMG_PATH + "/left_button_{}1.jpg".format(self.name))  # 背景图片
        self.pixmap2 = QPixmap(IMG_PATH + "/left_button_{}2.jpg".format(self.name))  # 选中时的背景图片
        self.bg_size = QSize(198, 30)
        # 设置
        self.setIcon(self.pixmap1)  # 设置图片
        self.setIconSize(self.bg_size)  # 背景大小
        self.setGeometry(pos[0], pos[1], 198, 30)  # 按钮位置和大小

    def mousePressEvent(self, event):
        """鼠标按下"""
        stuts = self.isCheckable()
        if not stuts:  # 如果是松开状态
            self.setCheckable(True)
            self.setIcon(self.pixmap2)  # 设置图片
            self.setIconSize(self.bg_size)  # 背景大小
        else:  # 如果是按下状态
            pass
        super().mousePressEvent(event)


class PlayModeFrame(QFrame):
    """音乐播放模式"""
    def __init__(self, parent, pos:tuple):
        super().__init__(parent=parent)
        # 属性
        self.cur_mode = None  # 当前模式
        # 设置
        self.setGeometry(pos[0], pos[1], 30, 30)  # 位置/大小
        # 列表循环
        self.mode1 = QLabel(self)
        self.mode1.setFixedSize(self.size())
        self.mode1.setPixmap(QPixmap(IMG_PATH + "/mode1.png"))
        self.mode1.setScaledContents(True)  # 大小自适应
        # 随机播放
        self.mode2 = QLabel(self)
        self.mode2.setFixedSize(self.size())
        self.mode2.setPixmap(QPixmap(IMG_PATH + "/mode2.png"))
        self.mode2.setScaledContents(True)  # 大小自适应
        # 列表播放（只播放一遍）
        self.mode3 = QLabel(self)
        self.mode3.setFixedSize(self.size())
        self.mode3.setPixmap(QPixmap(IMG_PATH + "/mode3.png"))
        self.mode3.setScaledContents(True)  # 大小自适应
        # 单曲循环
        self.mode4 = QLabel(self)
        self.mode4.setFixedSize(self.size())
        self.mode4.setPixmap(QPixmap(IMG_PATH + "/mode4.png"))
        self.mode4.setScaledContents(True)  # 大小自适应
        # 初始模式
        self.setMode(MusicPlayer.MODE1)  # 初始模式为列表循环

    def setMode(self, mode:str):
        """设置模式"""
        self.closeAllMode()
        if mode == MusicPlayer.MODE1:  # 列表循环
            self.cur_mode = MusicPlayer.MODE1
            self.mode1.setVisible(True)
        elif mode == MusicPlayer.MODE2:  # 随机播放
            self.cur_mode = MusicPlayer.MODE2
            self.mode2.setVisible(True)
        elif mode == MusicPlayer.MODE3:  # 列表播放
            self.cur_mode = MusicPlayer.MODE3
            self.mode3.setVisible(True)
        elif mode == MusicPlayer.MODE4:  # 单曲循环
            self.cur_mode = MusicPlayer.MODE4
            self.mode4.setVisible(True)
        MusicRow.player.setMode(mode)

    def closeAllMode(self):
        """隐藏所有模式"""
        self.mode1.setVisible(False)
        self.mode2.setVisible(False)
        self.mode3.setVisible(False)
        self.mode4.setVisible(False)

    def mouseReleaseEvent(self, event):
        """鼠标松开"""
        if event.button() == Qt.LeftButton:  # 左键
            if self.cur_mode == MusicPlayer.MODE1:  # 列表循环
                self.setMode(MusicPlayer.MODE2)
            elif self.cur_mode == MusicPlayer.MODE2:  # 随机播放
                self.setMode(MusicPlayer.MODE3)
            elif self.cur_mode == MusicPlayer.MODE3:  # 列表播放
                self.setMode(MusicPlayer.MODE4)
            elif self.cur_mode == MusicPlayer.MODE4:  # 单曲循环
                self.setMode(MusicPlayer.MODE1)
        elif event.button() == Qt.RightButton:  # 右键
            if self.cur_mode == MusicPlayer.MODE1:  # 列表循环
                self.setMode(MusicPlayer.MODE4)
            elif self.cur_mode == MusicPlayer.MODE2:  # 随机播放
                self.setMode(MusicPlayer.MODE1)
            elif self.cur_mode == MusicPlayer.MODE3:  # 列表播放
                self.setMode(MusicPlayer.MODE2)
            elif self.cur_mode == MusicPlayer.MODE4:  # 单曲循环
                self.setMode(MusicPlayer.MODE3)