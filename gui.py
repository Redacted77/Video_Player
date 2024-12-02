import sys
import vlc
import time
from playback_vlc import VideoPlayer
from PySide6.QtWidgets import (QMainWindow, QHBoxLayout, QVBoxLayout, QWidget,
                                QFileDialog, QLabel, QPushButton, QSlider)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QFont

######## GUI aspact ########
class MainWindow(QMainWindow):
    def __init__(self, app, video_path = None):
        super().__init__()
        self.app = app
        self.setWindowTitle("Video Player")
        self.setGeometry(450, 200, 800, 600)
        self.time_value = 0.0

        # center widget
        self.player = None
        self.center_widget = QWidget(self)
        self.center_widget.setStyleSheet("background-color: rgb(115, 18, 18)")
        self.v_video_line = QVBoxLayout()
        self.v_video_line.setContentsMargins(0, 0, 0, 0)
        self.h_options_line = QHBoxLayout()
        self.h_seek_line = QHBoxLayout()
        self.setCentralWidget(self.center_widget)
        self.center_widget.setLayout(self.v_video_line)

        # Video Widget
        self.video_widget = QWidget(self)
        self.video_widget.setStyleSheet("background: rgb(13, 13, 13);")
        self.v_video_line.addWidget(self.video_widget, Qt.AlignmentFlag.AlignCenter)

        # Menubar
        self.menu_bar = self.menuBar()
        self.menu_bar.setStyleSheet("background-color: rgb(115, 18, 18)")
        file = self.menu_bar.addMenu("File")
        self.open_v = file.addAction("Open Video")
        self.open_v.triggered.connect(self.open_video)
        self.add_subtitle = file.addAction("Add subtitles")
        self.add_subtitle.triggered.connect(self.subtitle_list)
        self.add_audio_track = file.addAction("Add audio tracks")
        self.add_audio_track.triggered.connect(self.audio_track_list)
        self.subtitle = self.menu_bar.addMenu("Subtitle")
        self.subtitle_flage = False
        self.audio = self.menu_bar.addMenu("Audio")
        self.audio_track_flage = False
        self.add_subtitle_shortcut = QShortcut(QKeySequence("s"), self)
        self.add_subtitle_shortcut.activated.connect(self.subtitle_list)
        self.add_audio_shortcut = QShortcut(QKeySequence("a"), self)
        self.add_audio_shortcut.activated.connect(self.audio_track_list)


        # Video controls layout #
        # seeker slider
        self.video_slider = QSlider(Qt.Orientation.Horizontal)
        self.video_slider.setDisabled(True)
        self.video_slider.valueChanged.connect(self.seek_slider)
        self.seek_time = QLabel("00:00")
        self.right_seeker = QShortcut(QKeySequence("right"), self)
        self.left_seeker = QShortcut(QKeySequence("left"), self)
        self.right_seeker.activated.connect(self.add_to_seeker)
        self.left_seeker.activated.connect(self.sub_from_seeker)
        self.show_seek_full = QLabel("", self)
        self.show_seek_full.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.show_seek_full.setStyleSheet(
            """ 
            background-color: rgb(140, 31, 40);
            color: white;
            border-radius: 10px;
            padding: 5px;
            """
       )
        self.show_seek_full.setFont(QFont("Arial", 14, QFont.Bold))
        self.show_seek_full.setFixedSize(70, 40)
        self.show_seek_full.move(self.width() - 775, self.height() + 100)
        self.show_seek_full.hide()

        # play button
        self.play_button = QPushButton("play")
        self.play_button.clicked.connect(self.button_player)
        self.pause_shortcut = QShortcut(QKeySequence("space"), self)
        self.pause_shortcut.activated.connect(self.button_player)
        self.play_button.setDisabled(True)
        self.play_button.setStyleSheet("background-color: rgb(140, 31, 40)")

        # volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0,200)
        self.volume_slider.setValue(100)
        self.volume_slider.setDisabled(True)
        self.volume_slider.valueChanged.connect(self.audio_volume)
        self.volume_value = QLabel(f"{self.volume_slider.value()}%")
        self.show_volume = QLabel(f"Volume: {self.volume_slider.value()}%", self)
        self.show_volume.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.show_volume.setStyleSheet(
            """ 
            background-color: rgb(140, 31, 40);
            color: white;
            border-radius: 10px;
            padding: 5px;
            """
       )
        self.show_volume.setFont(QFont("Arial", 14, QFont.Bold))
        self.show_volume.setFixedSize(150, 40)
        self.show_volume.move(self.width() + 575, self.height() + 100)
        self.show_volume.hide()
        self.up_volume = QShortcut(QKeySequence("up"), self)
        self.up_volume.activated.connect(self.add_to_volume)
        self.down_volume = QShortcut(QKeySequence("down"), self)
        self.down_volume.activated.connect(self.sub_from_volume)
        
        # fullscreen button
        self.full_screen = QPushButton("Fullscreen")
        self.full_screen.clicked.connect(self.fullscreen_toggle)
        self.fullscreen_shortcut = QShortcut(QKeySequence("f"), self)
        self.fullscreen_shortcut.activated.connect(self.fullscreen_toggle)
        self.full_screen_flage = False
        self.full_screen.setStyleSheet("background-color: rgb(140, 31, 40)")

        # Layout
        self.h_seek_line.addWidget(self.seek_time, 0 , Qt.AlignmentFlag.AlignLeft)
        self.h_seek_line.addWidget(self.video_slider, Qt.AlignmentFlag.AlignLeft)
        self.h_options_line.addWidget(self.play_button, 0, Qt.AlignmentFlag.AlignJustify)
        self.h_options_line.addWidget(self.volume_slider, 0, Qt.AlignmentFlag.AlignJustify)
        self.h_options_line.addWidget(self.volume_value, 1, Qt.AlignmentFlag.AlignLeft)
        self.h_options_line.addWidget(self.full_screen, 1, Qt.AlignmentFlag.AlignRight)
        self.v_video_line.addLayout(self.h_seek_line)
        self.v_video_line.addLayout(self.h_options_line)
        self.h_seek_line.setContentsMargins(0,0,0,0)
        self.h_options_line.setContentsMargins(0,0,0,0)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.repeat_call)
        self.timer_running_flage = False
        self.widget_timer = QTimer(self)
        self.widget_timer.timeout.connect(self.hide_all)
        self.widget_timer_running_flage = False
        self.full_volume_seek_timer = QTimer(self)
        self.full_volume_seek_timer.timeout.connect(self.full_volume_seek)

        # VLC instance
        self.instance = vlc.Instance()
        self.player = vlc.Instance.media_player_new(self.instance)

        # For "Open with" function
        if video_path:
            self.open_with(video_path)

    # Opens a menu to select the video and starts playing it
    def open_video(self):
        video_path = QFileDialog.getOpenFileName(self,
                                                  "Open Media File",
                                                    "",
                                                  "Media Files (*.mp4 *.mkv *.amv *.m4v)",
                                                  )
        if video_path:
            self.video_worker = VideoPlayer(video_path[0], self.instance, self.player)
            if sys.platform == "win32":
                self.player.set_hwnd(self.video_widget.winId())
            self.video_worker.start()
            self.video_slider.setEnabled(True)
            self.volume_slider.setEnabled(True)
            self.play_button.setEnabled(True)
            self.video_worker.seek_length.connect(self.seek_config)
            self.video_worker.video_finished.connect(self.video_ended)
            self.subtitle_flage = False
            self.subtitle.clear()
            self.audio_track_flage = False
            self.audio.clear()
    
    # starts an update timer for every second
    def timer_set(self, fps_value):
        self.timer.start(1000)
        self.timer_running_flage = True

    # functionality of the play button
    def button_player(self):
        try:
            self.video_worker.pause_video()
        except AttributeError:
            return
        if self.video_worker.player.get_state() == vlc.State.Paused:
            self.play_button.setText("Paused")
        elif self.video_worker.player.get_state() == vlc.State.Playing:
            self.play_button.setText("play")
        if self.timer_running_flage:
            self.widget_timer.stop()
            self.widget_timer_running_flage = False
            self.show_volume.hide()
            self.show_all()
        elif self.timer_running_flage == False and self.isFullScreen():
            self.widget_timer.start(3000)
            self.widget_timer_running_flage = True
        self.timer_running_flage = not self.timer_running_flage
        if self.video_worker.player.get_state() == vlc.State.Paused:
            self.play_button.setText("Paused")
        elif self.video_worker.player.get_state() == vlc.State.Playing:
            self.play_button.setText("play")
    
    # functionality of the volume slider
    def audio_volume(self):
        try:
            self.volume_value.setText(f"{self.volume_slider.value()}%")
            self.video_worker.volume_func(self.volume_slider.value())
            if self.widget_timer_running_flage:
                self.show_volume.setText(f"Volume: {self.volume_slider.value()}%")
                self.show_volume.show()
        except AttributeError:
            return
    
    def add_to_volume(self):
        if not self.volume_slider.value() + 10 > 200 and self.volume_slider.isEnabled():
            self.volume_slider.setValue(self.volume_slider.value() + 10)
            self.audio_volume()
        elif self.volume_slider.isEnabled():
            self.volume_slider.setValue(200)
            self.audio_volume()
        
    
    def sub_from_volume(self):
        if not self.volume_slider.value() - 10 < 0 and self.volume_slider.isEnabled():
            self.volume_slider.setValue(self.volume_slider.value() - 10)
            self.audio_volume()
        elif self.volume_slider.isEnabled():
            self.volume_slider.setValue(0)
            self.audio_volume()
        
    #functionality of fullscreen button
    def fullscreen_toggle(self):
        if self.full_screen_flage:
            self.showMaximized()
            self.menu_bar.show()
            self.full_screen_flage = not self.full_screen_flage
            self.widget_timer.stop()
            self.widget_timer_running_flage = False
            self.show_volume.hide()
            self.show_seek_full.hide()
            self.show_all()
        else:
            self.showFullScreen()
            self.menu_bar.hide()
            self.full_screen_flage = not self.full_screen_flage
            if self.video_slider.isEnabled():
                self.widget_timer.start(3000)
                self.widget_timer_running_flage = True
                self.full_volume_seek_timer.start(1500)
    
    # seeker functions
    def seek_config(self, time_in_ms):
        self.video_slider.setRange(0, time_in_ms)

    def seek_slider(self):
        self.video_worker.change_seek(self.video_slider.value())
    
    def repeat_call(self):
        if self.video_slider.isEnabled() and self.timer_running_flage:
            time = self.video_worker.seek_in_min()
            self.seek_time.setText(f"{time[0]:02}:{time[1]:02}")
            self.video_slider.blockSignals(True)
            self.video_slider.setValue(time[2])
            self.video_slider.blockSignals(False)
    
    def add_to_seeker(self):
        try: 
            self.video_worker.player.get_length()
        except AttributeError:
            return
        self.show_seek_full.hide()
        if not self.video_slider.value() + 10 > self.video_worker.player.get_length() and self.video_slider.isEnabled():
            self.video_slider.setValue(self.video_slider.value() + 10000)
            self.seek_slider()
            self.repeat_call()
            if self.widget_timer_running_flage:
                self.show_seek_full.setText("+10")
                self.show_seek_full.show()
        elif self.video_slider.isEnabled():
            self.video_slider.setValue(self.video_worker.player.get_length())
            self.seek_slider()
            self.repeat_call()
            if self.widget_timer_running_flage:
                self.show_seek_full.setText("+10")
                self.show_seek_full.show()
    
    def sub_from_seeker(self):
        try: 
            self.video_worker.player.get_length()
        except AttributeError:
            return
        self.show_seek_full.hide()
        if not self.video_slider.value() - 10 < 0 and self.video_slider.isEnabled():
            self.video_slider.setValue(self.video_slider.value() - 10000)
            self.seek_slider()
            self.repeat_call()
            if self.widget_timer_running_flage:
                self.show_seek_full.setText("-10")
                self.show_seek_full.show()
        elif self.video_slider.isEnabled():
            self.video_slider.setValue(0)
            self.seek_slider()
            self.repeat_call()
            if self.widget_timer_running_flage:
                self.show_seek_full.setText("-10")
                self.show_seek_full.show()

    # add and display subtitle if selected
    def subtitle_list(self):
        try:
            if self.subtitle_flage:
                return
            tracks = self.video_worker.sub_tracks()
            for track in tracks:
                action = self.subtitle.addAction(f"{track[1]}")
                action.triggered.connect(lambda checked, id = track[0]: self.video_worker.add_track(id))
                self.subtitle_flage = True 
        except AttributeError:
            pass
    
    # add and display audio tracks if selected
    def audio_track_list(self):
        try:
            if self.audio_track_flage:
                return
            tracks = self.video_worker.audio_tracks()
            for track in tracks:
                audio_action = self.audio.addAction(f"{track[1]}")
                audio_action.triggered.connect(lambda checked, id = track[0]: self.video_worker.set_audio_track(id))
                self.audio_track_flage = True 
        except AttributeError:
            pass
    
    def show_all(self):
        self.seek_time.show()
        self.video_slider.show()
        self.play_button.show()
        self.volume_slider.show()
        self.volume_value.show()
        self.full_screen.show()

    def hide_all(self):
        self.seek_time.hide()
        self.video_slider.hide()
        self.play_button.hide()
        self.volume_slider.hide()
        self.volume_value.hide()
        self.full_screen.hide()
        
    def full_volume_seek(self):
        self.show_volume.hide()
        self.show_seek_full.hide()


    def open_with(self, video_path):
        self.video_worker = VideoPlayer(video_path, self.instance, self.player)
        if sys.platform == "win32":
            self.player.set_hwnd(self.video_widget.winId())
        self.video_worker.start()
        self.video_slider.setEnabled(True)
        self.volume_slider.setEnabled(True)
        self.play_button.setEnabled(True)
        self.video_worker.seek_length.connect(self.seek_config)
        self.video_worker.fps_signle.connect(self.timer_set)
        self.video_worker.video_finished.connect(self.video_ended)
        self.subtitle_flage = False
        self.subtitle.clear()
        self.audio_track_flage = False
        self.audio.clear()

    # event functions, handles app closing and video ending ect.
    def video_ended(self):
        self.video_slider.setValue(0)
        self.seek_time.setText("00:00")
        self.video_slider.setDisabled(True)
        self.timer.stop()
        self.timer_running_flage = False
        self.volume_slider.setValue(100)
        self.volume_slider.setDisabled(True)
        self.play_button.setDisabled(True)
        self.widget_timer.stop()
        self.widget_timer_running_flage = False
        self.show_all()
    
    def closeEvent(self, event):
        try:
            if self.video_worker.isRunning():
                self.video_worker.stop_playback()
                self.video_worker.quit()
                self.video_worker.wait()
                event.accept()   
        except AttributeError:
            event.accept()