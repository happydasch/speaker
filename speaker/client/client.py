from ..draw import Icon, Overlay


class ClientInfo:

    STATUS_STOPPED = 0
    STATUS_PLAYING = 1

    volume = None
    position = 0
    duration = 0
    status = STATUS_STOPPED
    artist = None
    title = None
    album = None

    def __str__(self) -> str:
        res = ''
        for x, i in [
            ('Volume', self.volume),
            ('Position', self.position),
            ('Duration', self.duration),
            ('Status', self.status),
            ('Artist', self.artist),
            ('Title', self.title),
            ('Album', self.album),
        ]:
            res += f'{x}: {i}\n'
        return res


class Client:

    '''
    Represents a client
    '''

    PRIORITY = 100
    OVERLAY = Overlay
    ICON = Icon

    def __init__(self, speaker):
        self._speaker = speaker
        self._active = False

    def get_speaker(self):
        return self._speaker

    def is_active(self):
        return self._active

    def is_playing(self):
        info = self.get_info()
        if info.status == ClientInfo.STATUS_PLAYING:
            return True
        return False

    def get_info(self) -> ClientInfo:
        return ClientInfo()

    def get_volume(self):
        mixer = self.get_speaker().mixer
        volume = mixer.getvolume()[0]
        return volume

    def set_volume(self, volume):
        mixer = self.get_speaker().mixer
        mixer.setvolume(volume)

    def volume_down(self):
        volume = min(100, self.get_volume()-10)
        mixer = self.get_speaker().mixer
        mixer.setvolume(volume)

    def volume_up(self):
        volume = min(100, self.get_volume()+10)
        mixer = self.get_speaker().mixer
        mixer.setvolume(volume)

    def toggle_play(self):
        self.pause() if self.is_playing() else self.play()

    def play(self):
        return

    def pause(self):
        return

    def prev(self):
        return

    def next(self):
        return

    def update(self):
        return

    def update_event(self, event):
        return
