import pulsectl
import time
import dbus

from ..draw import OverlayIconBluetooth, IconBluetooth

from .client import Client, ClientInfo


class BluetoothClientInfo(ClientInfo):

    def __init__(self, res):
        if not res:
            return
        self.status = (
            ClientInfo.STATUS_PLAYING if res.get('Status') == 'playing'
            else ClientInfo.STATUS_STOPPED)
        self.position = int(res.get('Position'))
        track = res.get('Track')
        if track:
            self.duration = int(track.get('Duration'))
            self.artist = track.get('Artist')
            self.title = track.get('Title')
            self.album = track.get('Album')


class ClientBluetooth(Client):

    '''
    Client for bluetooth connections
    '''

    PRIORITY = 50
    OVERLAY = OverlayIconBluetooth
    ICON = IconBluetooth
    UPDATE_INTERVAL = 1

    def __init__(self, speaker):
        super().__init__(speaker)
        self._last_update = 0
        self._path = None
        self._player_iface = None
        self._transport_iface = None

    def _update_dbus(self, path):
        self._player_iface = None
        self._transport_iface = None
        self._path = None
        try:
            bus = dbus.SystemBus()
            obj = bus.get_object(
                'org.bluez', f'{path}/player0')
            self._player_iface = dbus.Interface(
                obj, 'org.bluez.MediaPlayer1')
            self._transport_iface = dbus.Interface(
                obj, "org.freedesktop.DBus.Properties")
            self._path = path
        except Exception:
            pass

    def _check_pulse(self, pulse):
        path = None
        for c in pulse.card_list():
            props = c.proplist
            if props.get('device.api') == 'bluez':
                path = props.get('bluez.path')
                if path != self._path:
                    break
        if self._path != path:
            self._update_dbus(path)
            self._path = path

    def update_event(self, event, pulse):
        self._check_pulse(pulse)

    def get_info(self):
        res = None
        try:
            res = self._transport_iface.GetAll("org.bluez.MediaPlayer1")
        except Exception:
            pass
        info = BluetoothClientInfo(res)
        info.volume = self.get_volume()
        return info

    def update(self):
        cur_time = time.time()
        if cur_time - self._last_update < self.UPDATE_INTERVAL:
            return

        self._active = self._player_iface is not None
        if self.is_active():
            info = self.get_info()
            if info.status == ClientInfo.STATUS_PLAYING:
                print(
                    info.volume,
                    round(info.position/1000/60, 2),
                    round(info.duration/1000/60, 2),
                    info.position,
                    info.duration,
                    info.artist,
                    info.title,
                    info.album)

        self._last_update = cur_time

    def play(self):
        try:
            self._player_iface.Play()
        except Exception:
            pass

    def pause(self):
        try:
            self._player_iface.Pause()
        except Exception:
            pass

    def prev(self):
        try:
            self._player_iface.Prev()
        except Exception:
            pass

    def next(self):
        try:
            self._player_iface.Next()
        except Exception:
            pass

    def volume_down(self):
        super().volume_down()
        try:
            self._player_iface.VolDown()
        except Exception:
            pass

    def volume_up(self):
        super().volume_up()
        try:
            self._player_iface.VolUp()
        except Exception:
            pass
