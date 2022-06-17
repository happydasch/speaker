import os
import select

from ..draw import Icon, Overlay


class FIFO:

    '''
    Basic fifo handler.

    src: pidi
    '''

    def __init__(self, fifo_name, eol='\n', skip_create=False):
        self.fifo_name = fifo_name
        self.eol = eol

        if not skip_create:
            self._create()

        self._f = None
        self._buf = ''

    def _create(self):
        try:
            os.unlink(self.fifo_name)
        except (IOError, OSError):
            pass

        os.mkfifo(self.fifo_name)
        os.chmod(self.fifo_name, 0o777)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._f is not None:
            os.close(self._f)
            self._f = None

    def read(self):
        if self._f is None:
            self._f = os.open(self.fifo_name, os.O_RDONLY | os.O_NONBLOCK)
        fifos, _, _ = select.select([self._f], [], [], 0)
        if self._f in fifos:
            while True:
                try:
                    char = os.read(self._f, 1).decode('UTF-8')
                except BlockingIOError:
                    return None
                if len(char) == 0:
                    return None
                self._buf += char
                if self._buf.endswith(self.eol):
                    buf = self._buf
                    self._buf = ''
                    return buf.strip()
        else:
            return None


class ClientInfo:

    STATUS_STOPPED = 0
    STATUS_PLAYING = 1

    volume = None
    muted = False
    position = -1
    duration = -1
    status = STATUS_STOPPED
    artist = ''
    title = ''
    album = ''
    album_art = None

    def __str__(self) -> str:
        res = ''
        for x, i in [
            ('Status', self.status),
            ('Artist', self.artist),
            ('Title', self.title),
            ('Album', self.album),
            ('Album Art', self.album_art is not None),
            ('Volume', self.volume),
            ('Muted', self.muted),
            ('Position', self.position),
            ('Duration', self.duration),
        ]:
            if res != '':
                res += ' - '
            res += f'{x}: {i}'
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

    def mute(self):
        return

    def unmute(self):
        return

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

    def update_event(self, event, pulse):
        return

    def start(self):
        return

    def stop(self):
        return
