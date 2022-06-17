import os
import time
import untangle
import xml
import dbus

from base64 import decodebytes

from ..utils import bytes_to_file, translate
from ..draw import OverlayIconAirplay, IconAirplay
from .client import Client, FIFO, ClientInfo


class ClientAirplay(Client):

    OVERLAY = OverlayIconAirplay
    ICON = IconAirplay
    UPDATE_INTERVAL = 1
    PIPE = '/tmp/shairport-sync-metadata'

    def __init__(self, speaker):
        super().__init__(speaker)
        self._last_update = 0
        self._sink_input = None
        self._init_volume = None
        self._client_info = ClientInfo()
        self.fifo = FIFO(self.PIPE, eol='</item>', skip_create=True)
        self._init_dbus()

    def _check_pulse(self, pulse):
        found = False
        for s in pulse.sink_input_list():
            if s.proplist.get('application.name') == 'Shairport Sync':
                found = True
                self._sink_input = s.index
        if not found:
            self._sink_input = None

    def _init_dbus(self):
        bus = dbus.SystemBus()
        proxy = bus.get_object(
            "org.gnome.ShairportSync",
            "/org/gnome/ShairportSync")
        interface = dbus.Interface(
            proxy, dbus_interface="org.gnome.ShairportSync.RemoteControl"
        )
        self._fn_playpause = interface.get_dbus_method("PlayPause")
        self._fn_play = interface.get_dbus_method("Play")
        self._fn_pause = interface.get_dbus_method("Pause")
        self._fn_prev = interface.get_dbus_method("Prev")
        self._fn_next = interface.get_dbus_method("Next")
        self._fn_volup = interface.get_dbus_method("VolumeUp")
        self._fn_voldown = interface.get_dbus_method("VolumeDown")

    def _update_info(self):
        while True:
            data = self.fifo.read()
            if data is None or len(data) == 0:
                return
            else:
                self._parse_data(data)

    def _parse_data(self, data):
        try:
            data = untangle.parse(data)
        except (xml.sax.SAXException, AttributeError):
            return

        dtype = bytes.fromhex(data.item.type.cdata).decode('ascii')
        dcode = bytes.fromhex(data.item.code.cdata).decode('ascii')

        data = getattr(data.item, 'data', None)
        if data is not None:
            encoding = data['encoding']
            data = data.cdata
            if encoding == 'base64':
                data = decodebytes(data.encode('ascii'))

        if (dtype, dcode) == ('ssnc', 'PICT'):
            dir = self.get_speaker().get_cache_dir()
            file = os.path.join(dir, 'airplay_current.jpg')
            if data is not None:
                bytes_to_file(data, file)
            self._client_info.album_art = data

        elif (dtype, dcode) == ('core', 'asal'):  # Album
            self._client_info.album = (
                '' if data is None else data.decode('utf-8'))

        elif (dtype, dcode) == ('core', 'asar'):  # Artist
            self._client_info.artist = (
                '' if data is None else data.decode('utf-8'))

        elif (dtype, dcode) == ('core', 'minm'):  # Song Name / Item
            self._client_info.title = (
                '' if data is None else data.decode('utf-8'))

        elif (dtype, dcode) == ('ssnc', 'prsm'):
            self._client_info.status = ClientInfo.STATUS_PLAYING

        elif (dtype, dcode) == ('ssnc', 'pend'):
            self._client_info.status = ClientInfo.STATUS_STOPPED

        elif (dtype, dcode) == ('ssnc', 'prgr'):
            times = ('' if data is None else data.decode('utf-8'))
            if times:
                times = times.split('/')
                times = [int(x) for x in times]

                self._client_info.duration = (times[2]-times[0])/44100
                self._client_info.position = (times[1]-times[0])/44100

        elif (dtype, dcode) == ('ssnc', 'pvol'):
            volumes = '' if data is None else data.decode('utf-8')
            if volumes:
                volumes = volumes.split(',')
                volumes = [float(x) for x in volumes]
                volume = translate(
                    volumes[1],
                    volumes[2], volumes[3],
                    0, 100)
                self._client_info.volume = int(volume)
                if volume < 5:
                    self._client_info.muted = True
                else:
                    self._client_info.muted = False

    def get_info(self) -> ClientInfo:
        return self._client_info

    def play(self):
        try:
            if not self.is_playing():
                self._fn_play()
                self._client_info.status = ClientInfo.STATUS_PLAYING
        except Exception:
            pass

    def pause(self):
        try:
            if self.is_playing():
                self._fn_pause()
                self._client_info.status = ClientInfo.STATUS_STOPPED
        except Exception:
            pass

    def prev(self):
        try:
            self._fn_prev()
        except Exception:
            pass

    def next(self):
        try:
            self._fn_next()
        except Exception:
            pass

    def get_volume(self):
        return self._client_info.volume

    def volume_down(self):
        try:
            self._fn_voldown()
        except Exception:
            pass

    def volume_up(self):
        try:
            self._fn_volup()
        except Exception:
            pass

    def update_event(self, event, pulse):
        if event.facility != 'sink_input':
            return
        self._check_pulse(pulse)

    def update(self):
        cur_time = time.time()
        if cur_time - self._last_update < self.UPDATE_INTERVAL:
            return

        self._update_info()
        if self.is_active():
            info = self.get_info()
            if info.status == ClientInfo.STATUS_PLAYING:
                info.position += cur_time - self._last_update
                if info.position > info.duration:
                    info.position = info.duration
        active = self._sink_input is not None
        if active != self.is_active():
            self._active = active
            if active:
                self._start_client()
            else:
                self._stop_client()
        self._last_update = cur_time

    def _start_client(self):
        self._client_info.album_art = None
        self._client_info.album = ''
        self._client_info.title = ''
        self._client_info.artist = ''
        self._client_info.position = -1
        self._client_info.duration = -1
        self.get_speaker().mixer.setvolume(100)

    def _stop_client(self):
        volume = self.get_volume()
        if volume:
            self.get_speaker().mixer.setvolume(volume)
