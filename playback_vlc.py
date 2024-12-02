import vlc
import time
from PySide6.QtCore import QThread, Signal

######## playback functionality ########
class VideoPlayer(QThread):
    # all signals
    video_finished = Signal()
    seek_length = Signal(float, float)

    def __init__(self, video_path, instance, player):
        super().__init__()
        self.video_path = video_path
        self.instance = instance
        self.player = player
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.video_end)
        self.video_running_flag = False

    # run is the first to start when .start() is used
    def run(self):
        self.video = self.instance.media_new(self.video_path)
        self.video.add_option("avcodec-hw=dxva2")
        self.video.add_option("avcodec-hw=nvdec")
        self.player.set_media(self.video)
        self.player.play()
        time.sleep(1)
        self.volume_func(self.player.audio_get_volume())
        self.video_running_flag = True
        self.seek_length.emit(self.player.get_length(),(self.player.get_time()/60000))
    
    # pausesthe video
    def pause_video(self):
        self.player.pause()
    
    # sets the volume
    def volume_func(self, current_value):
        self.player.audio_set_volume(current_value)
    
    # changes where we are in the video
    def change_seek(self, current_value):
        self.player.set_time(current_value)
    
    # resturns the time in 00:00 format
    def seek_in_min(self):
        time_ms = self.player.get_time()
        if time_ms != -1:
            seconds = time_ms // 1000
            minutes = seconds // 60
            seconds %= 60
        time_list = (minutes, seconds, time_ms)
        return time_list
    
    # gets a list of imbedded subtitles
    def sub_tracks(self):
        s_tracks = self.player.video_get_spu_description()
        return s_tracks

    def add_track(self, id):
        self.player.video_set_spu(id)
    
    # gets a list of imbedded audio tracks
    def audio_tracks(self):
        a_tracks = self.player.audio_get_track_description()
        return a_tracks

    def set_audio_track(self, id):
        self.player.audio_set_track(id)
    
    # sends a signle when the video ends
    def video_end(self, event):
        self.video_finished.emit()

    # clean up process
    def stop_playback(self):
        self.video_running_flag = False
        self.video.release()
        self.player.release()
        self.instance.release()