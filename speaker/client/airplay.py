import time
import untangle
import xml
import dbus

from base64 import decodebytes

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
            self._client_info.album_art = data

        elif (dtype, dcode) == ('core', 'asal'):  # Album
            self._client_info.album = '' if data is None else data.decode('utf-8')

        elif (dtype, dcode) == ('core', 'asar'):  # Artist
            self._client_info.artist = '' if data is None else data.decode('utf-8')

        elif (dtype, dcode) == ('core', 'minm'):  # Song Name / Item
            self._client_info.title = '' if data is None else data.decode('utf-8')

        elif (dtype, dcode) == ('ssnc', 'prsm'):
            self._client_info.status = ClientInfo.STATUS_PLAYING

        elif (dtype, dcode) == ('ssnc', 'pend'):
            self._client_info.status = ClientInfo.STATUS_STOPPED

        else:
            print(f'unknown msg {dtype} {dcode} {data}')

    def get_info(self) -> ClientInfo:
        return self._client_info

    def play(self):
        try:
            self._fn_play()
        except Exception:
            pass

    def pause(self):
        try:
            self._fn_pause()
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
                print(
                    info.volume,
                    info.position,
                    info.duration,
                    info.artist,
                    info.title,
                    info.album)

        self._active = self._sink_input is not None
        self._last_update = cur_time
