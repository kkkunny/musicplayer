# -*- coding: utf-8 -*-
# 音乐播放器
from PySide2.QtWidgets import *
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from os import listdir
import sys
from widgets import *
from api import *
from scrapy import *


class Main(object):
    """音乐播放器主程序"""
    def __init__(self):
        self.app = QApplication(sys.argv)  # 底层
        # 读取主窗口ui
        ui_file = QFile(UI_PATH + "/main.ui")
        ui_file.open(QFile.ReadOnly)
        ui_file.close()
        self.window = QUiLoader().load(ui_file)
        # 主窗口设置
        self.mainWindow()
        # 加载配置文件
        self.startValue()  # 初始化参数
        self.getInfos()  # 获取配置文件
        # 各个部件
        self.topFrame()  # 顶部栏
        self.leftFrame()  # 左边栏
        self.buttonFrame()  # 底部栏
        self.localMusicFrame()  # 本地音乐
        # 显示
        self.window.show()  # 显示主窗口
        sys.exit(self.app.exec_())  # 主循环

    def mainWindow(self):
        """主窗口设置"""
        self.window.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏边框
        self.window.setWindowIcon(QIcon(IMG_PATH + "/icon.png"))  # 图标
        self.app.lastWindowClosed.connect(self.closed)  # 程序退出时调用函数

    def startValue(self):
        """初始化参数"""
        # 播放器
        self.player = MusicPlayer(MusicPlayer.MODE1)  # 播放器
        self.player.positionChanged(self.showProgressSlider)  # 播放进度变化
        self.player.curSongChanged(self.showPlayInfos)  # 获取当前歌曲的信息
        self.player.playStutsChanged(self.showPlayerControl)  # 显示播放/暂停按钮
        MusicRow.player = self.player  # 加载音乐播放器
        # 歌曲爬虫
        self.search_music_count = 0
        self.music_scrapy = MusicScrapyTongzan()

    def getInfos(self):
        """初始化配置文件"""
        # 获取本地音乐
        with open(INI_LOCAL_MUSIC_PATH, "r") as file:
            count = 0
            row = file.readline()
            while(row):
                count += 1
                title, songers, album, length, path = findall(r"(.+);(.+);(.+);(.+);(.+);", row)[0]
                song = MusicSong(title=title, songers=songers, length=int(length), album=album, path=path)
                MusicRow(self.window.local_list_frmae, count, song, MusicRow.TYPE_LOCAL)
                row = file.readline()
        self.local_music_count = count
        # 获取基本设置
        with open(INI_PATH, "r") as file:
            text = file.read()
            # 播放模式
            mode = findall(r"mode:(.+);", text)
            if mode:
                mode = mode[0].strip()
                self.player.mode = mode
            # 音量
            volume = findall(r"volume:(.+);", text)
            if volume:
                volume = int(volume[0].strip())
                self.player.setVolume(volume)

    def topFrame(self):
        """顶部栏"""
        # logo
        self.window.logo.setPixmap(QPixmap(IMG_PATH + "/logo.jpg"))  # logo
        self.window.logo.setScaledContents(True)  # logo大小自适应
        # 功能栏
        self.window.top_close.clicked.connect(self.window.close)  # 关闭
        self.window.top_close.setIcon(QPixmap(IMG_PATH + "/close.jpg"))
        self.window.top_close.setIconSize(QSize(self.window.top_close.size()))
        self.window.top_minimum.clicked.connect(self.window.showMinimized)  # 最小化
        self.window.top_minimum.setIcon(QPixmap(IMG_PATH + "/minimum.jpg"))
        self.window.top_minimum.setIconSize(QSize(self.window.top_minimum.size()))
        # 前进/后退
        self.window.go_back.setStyleSheet(("border:0px;"))  # 后退
        self.window.go_back.setIcon(QPixmap(IMG_PATH + "/back.png"))
        self.window.go_back.setIconSize(QSize(self.window.go_back.size()))
        self.window.go_font.setStyleSheet(("border:0px;"))  # 前进
        self.window.go_font.setIcon(QPixmap(IMG_PATH + "/go.png"))
        self.window.go_font.setIconSize(QSize(self.window.go_font.size()))
        # 搜索
        self.window.search_button.clicked.connect(self.searchMusic)  # 按钮
        self.window.search_button.setStyleSheet(("border:0px;"))
        self.window.search_button.setIcon(QPixmap(IMG_PATH + "/search_bt.png"))
        self.window.search_button.setIconSize(QSize(self.window.search_button.size()))
        self.window.search_text.returnPressed.connect(self.searchMusic)  # 搜索栏
        self.window.search_text.setStyleSheet("QLineEdit{background-color: rgb(168, 40, 40);border: 0px;border-radius: 10px;color:white;}")

    def leftFrame(self):
        """左部件"""
        button1 = LeftButton(self.window.left_frame, "local", (1, 20))  # 本地音乐按钮
        button1.clicked.connect(lambda :self.rightFrameDisplay(self.window.local_frame))
        # 增加
        self.window.left_my_music_sheet_add.setStyleSheet(("border:0px;"))
        self.window.left_my_music_sheet_add.setIcon(QPixmap(IMG_PATH + "/add.png"))
        self.window.left_my_music_sheet_add.setIconSize(QSize(self.window.left_my_music_sheet_add.size()))

    def buttonFrame(self):
        """底部栏"""
        # 播放/暂停/上/下一首
        self.play_icon = QPixmap(IMG_PATH + "/play.png")  # 播放的图片
        self.pause_icon = QPixmap(IMG_PATH + "/pause.png")  # 暂停的图片
        self.window.cur_music_control.clicked.connect(self.playerControl)  # 播放/暂停
        self.window.cur_music_control.setStyleSheet(("border:0px;"))
        self.window.cur_music_control.setIcon(self.play_icon)
        self.window.cur_music_control.setIconSize(QSize(self.window.cur_music_control.size()))
        # 上一首
        self.window.cur_music_pro.clicked.connect(lambda :self.player.nextControl(MusicPlayer.DIRECTION_PREV))
        self.window.cur_music_pro.setStyleSheet(("border:0px;"))
        self.window.cur_music_pro.setIcon(QPixmap(IMG_PATH + "/previous.png"))
        self.window.cur_music_pro.setIconSize(QSize(self.window.cur_music_pro.size()))
        # 下一首
        self.window.cur_music_next.clicked.connect(lambda :self.player.nextControl(MusicPlayer.DIRECTION_NEXT))
        self.window.cur_music_next.setStyleSheet(("border:0px;"))
        self.window.cur_music_next.setIcon(QPixmap(IMG_PATH + "/next.png"))
        self.window.cur_music_next.setIconSize(QSize(self.window.cur_music_next.size()))
        # 音量
        self.volume_icon1 = QPixmap(IMG_PATH + "/volume1.png")  # 有音量的图标
        self.volume_icon2 = QPixmap(IMG_PATH + "/volume2.png")  # 无音量的图标
        self.window.volume_icon.setScaledContents(True)  # 音量图标大小自适应
        self.window.volume_icon.setPixmap(self.volume_icon1)
        self.window.volume.setValue(self.player.getVolume())  # 初始设定音量
        self.window.volume.valueChanged.connect(self.volumeChange)  # 音量改变
        style = """QSlider:add-page{
                    background-color: rgb(230, 230, 232);
                    height:4px;
                 }
                 QSlider:sub-page{
                    background-color: rgb(232, 60, 60);
                    height:4px;
                 }
                 QSlider:groove{
                    background:transparent;
                    height:%dpx;
                 }
                 QSlider:handle{
                    background:white;
                    border: 1px solid #777;
                    width:10px;
                    margin-top: -3px;
                    margin-bottom: -3px;
                    border-radius: 5px;
        }"""  # 滑条样式
        self.window.volume.setStyleSheet(style % 5)
        # 播放进度
        self.window.progress.setStyleSheet(style % 6)
        self.window.progress.sliderReleased.connect(self.ProgressSlider)  # 进度改变
        # 播放模式
        mode = PlayModeFrame(self.window.button_frame, (960, 10))
        # 专辑图片
        self.window.cur_music_pic.setScaledContents(True)  # 大小自适应

    def localMusicFrame(self):
        """本地音乐"""
        self.window.local_frame.setVisible(False)
        self.window.local_add_file.clicked.connect(self.openLocalFile)  # 文件
        self.window.local_add_file.setStyleSheet(("border:0px;"))
        self.window.local_add_file.setIcon(QPixmap(IMG_PATH + "/local_add_file.png"))
        self.window.local_add_file.setIconSize(QSize(self.window.local_add_file.size()))
        self.window.local_add_files.clicked.connect(self.openLocalFiles)  # 文件夹
        self.window.local_add_files.setStyleSheet(("border:0px;"))
        self.window.local_add_files.setIcon(QPixmap(IMG_PATH + "/local_add_files.png"))
        self.window.local_add_files.setIconSize(QSize(self.window.local_add_files.size()))

    def searchMusicFrame(self):
        """搜索音乐"""
        self.window.search_frame.setVisible(False)

    def searchMusic(self):
        """搜索歌曲"""
        MusicRow.search_all.clear()
        self.rightFrameDisplay(self.window.search_frame)
        self.window.search_frame.setVisible(True)
        search_content = self.window.search_text.text()  # 获取输入内容
        if search_content:  # 有值
            self.search_music_count = 0
            self.music_scrapy.search(search_content, MusicScrapyTongzan.ORIGIN_NETEASE, 1, self.searchAddMusicRow)

    def rightFrameDisplay(self, frame:QWidget):
        """右部件显示"""
        # 全部不显示
        self.window.local_frame.setVisible(False)
        self.window.search_frame.setVisible(False)
        frame.setVisible(True)

    def openLocalFile(self):
        """导入本地歌曲"""
        file_path = QFileDialog.getOpenFileName(self.window, '打开文件', './')[0]
        file_format = findall(".*\.(.+)", file_path)[0]
        if file_format in ALLOWED_FORMAT:  # 如果文件后缀为允许的格式
            song = get_local_music(file_path)  # 获得歌曲信息
            self.local_music_count += 1  # 计数+1
            MusicRow(self.window.local_list_frmae, self.local_music_count, song, MusicRow.TYPE_LOCAL)
            with open(INI_LOCAL_MUSIC_PATH, "a+") as info_file:  # 写入配置文件
                info_file.write("{};{};{};{};{};\n".format(song.title, song.songers, song.album, song.length, song.path))
        else:
            writeLog("导入不允许的本地歌曲格式:{}".format(file_format), "msg")

    def openLocalFiles(self):
        """导入本地文件夹"""
        file_path = QFileDialog.getExistingDirectory(self.window, '选择文件夹', './')
        paths = listdir(file_path)
        for path in paths:
            file_format = findall(".*\.(.+)", path)[0]
            if file_format in ALLOWED_FORMAT:
                music_path = file_path + "/{}".format(path)
                song = get_local_music(music_path)  # 获取信息
                self.local_music_count += 1  # 计数+1
                MusicRow(self.window.local_list_frmae, self.local_music_count, song, MusicRow.TYPE_LOCAL)
                with open(INI_LOCAL_MUSIC_PATH, "a+") as info_file:  # 写入配置文件
                    info_file.write(
                        "{};{};{};{};{};\n".format(song.title, song.songers, song.album, song.length, song.path))
            else:
                writeLog("导入不允许的本地歌曲格式:{}".format(file_format), "msg")

    def searchAddMusicRow(self, title:str, songers:str, length:int, url:str, album:str, pic_url:str):
        """搜索歌曲时新建歌曲行"""
        for row in MusicRow.search_all:
            if row.song.title == title and row.song.songers == songers:
                return
        self.search_music_count += 1  # 计数+1
        song = MusicSong(title=title, songers=songers, length=length, album=album, url=url, pic_url=pic_url)
        MusicRow(self.window.search_list_frmae, self.search_music_count, song, MusicRow.TYPE_SEARCH)

    def ProgressSlider(self):
        """设置播放进度"""
        value = round(self.window.progress.value() / 100 * self.player.getMusicLength())
        self.player.setPlayProcess(value)

    def showProgressSlider(self):
        """播放进度条设置"""
        length = self.player.getMusicLength()
        if length != 0:
            position = self.player.getPlayProcess()
            progress = round(position / length, 2) * 100
            self.window.progress.setValue(progress)
            minute = int(position / 1000 // 60)
            second = round(((position / 1000 / 60) - minute) * 60)
            cur_lengtn = "{}:{}".format(minute, second)
            self.window.cur_length.setText(cur_lengtn)  # 已播放时长
        else:
            self.window.progress.setValue(0)
            self.window.cur_length.setText("00:00")  # 已播放时长

    def showPlayInfos(self):
        """设置播放歌曲的信息"""
        song = self.player.cur_song
        self.window.cur_music_title.setText(song.title)  # 标题
        self.window.cur_music_songers.setText(song.songers)  # 歌手
        self.window.all_length.setText(song.getLength())  # 总时长
        if song.pic_path:  # 如果有图片
            pic_path = song.pic_path
        else:  # 如果没图片
            pic_path = IMG_PATH + "/album_pic.png"
        self.window.cur_music_pic.setPixmap(QPixmap(pic_path))

    def playerControl(self):
        """音乐播放器播放/暂停控制"""
        stuts = self.player.getStuts()
        if stuts == MusicPlayer.STUTS_PLAYING:  # 播放时
            self.player.pause()
        elif stuts == MusicPlayer.STUTS_PAUSING:  # 暂停时
            self.player.play()
        elif stuts == MusicPlayer.STUTS_STOPPING:  # 停止时
            pass

    def showPlayerControl(self):
        """显示音乐播放器播放/暂停控制"""
        stuts = self.player.getStuts()
        if stuts == MusicPlayer.STUTS_PLAYING:  # 播放时
            self.window.cur_music_control.setIcon(self.pause_icon)
        elif stuts == MusicPlayer.STUTS_PAUSING:  # 暂停时
            self.window.cur_music_control.setIcon(self.play_icon)
        elif stuts == MusicPlayer.STUTS_STOPPING:  # 停止时
            pass

    def volumeChange(self):
        """音量改变"""
        value = self.window.volume.value()
        if value == 0:
            self.window.volume_icon.setPixmap(self.volume_icon2)
            self.player.setMuted(True)  # 静音
        else:
            self.window.volume_icon.setPixmap(self.volume_icon1)
            self.player.setMuted(False)  # 不静音
        self.player.setVolume(value)

    def closed(self):
        """主程序关闭时调用"""
        # 写入配置文件
        writeIni("mode", self.player.mode)  # 播放模式
        writeIni("volume", str(self.player.getVolume()))  # 音量


class GetSongListWindow(object):
    """用来获取歌单的小窗口"""
    def __init__(self):
        self.app = QApplication(sys.argv)  # 底层
        # 读取主窗口ui
        ui_file = QFile(UI_PATH + "/main.ui")
        ui_file.open(QFile.ReadOnly)
        ui_file.close()
        self.window = QUiLoader().load(ui_file)
        # 主窗口设置
        self.mainWindow()
        # 加载配置文件
        self.startValue()  # 初始化参数
        self.getInfos()  # 获取配置文件
        # 各个部件
        self.topFrame()  # 顶部栏
        self.leftFrame()  # 左边栏
        self.buttonFrame()  # 底部栏
        self.localMusicFrame()  # 本地音乐
        # 显示
        self.window.show()  # 显示主窗口
        sys.exit(self.app.exec_())  # 主循环


if __name__ == '__main__':
    try:
        Main()
    except Exception as e:
        out_str = "程序错误！:{}\n{}".format(e.args, printErrer)
        writeLog(out_str, "error")