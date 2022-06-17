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
        self.position = int(res.get('Position')) / 1000
        track = res.get('Track')
        if track:
            self.duration = int(track.get('Duration')) / 1000
            self.artist = track.get('Artist', '')
            self.title = track.get('Title', '')
            self.album = track.get('Album', '')


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
        self._init_volume = None

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
        if self._player_iface:
            self._fn_play = self._player_iface.get_dbus_method('Play')
            self._fn_pause = self._player_iface.get_dbus_method('Pause')
            self._fn_prev = self._player_iface.get_dbus_method('Prev')
            self._fn_next = self._player_iface.get_dbus_method('Next')
            self._fn_voldown = self._player_iface.get_dbus_method('VolumeDown')
            self._fn_volup = self._player_iface.get_dbus_method('VolumeUp')
        else:
            self._fn_play = None
            self._fn_pause = None
            self._fn_prev = None
            self._fn_next = None
            self._fn_voldown = None
            self._fn_volup = None

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

    def get_info(self):
        res = None
        try:
            res = self._transport_iface.GetAll("org.bluez.MediaPlayer1")
        except Exception:
            pass
        info = BluetoothClientInfo(res)
        info.volume = self.get_volume()
        return info

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
        super().volume_down()
        try:
            self._fn_voldown()
        except Exception:
            pass

    def volume_up(self):
        super().volume_up()
        try:
            self._fn_volup()
        except Exception:
            pass

    def update_event(self, event, pulse):
        if event.facility != 'card':
            return
        self._check_pulse(pulse)

    def update(self):
        cur_time = time.time()
        if cur_time - self._last_update < self.UPDATE_INTERVAL:
            return

        active = self._player_iface is not None
        self._active = active
        if active != self.is_active():
            self._active = self._sink_input is not None
            if self._active:
                self._start_client()
            else:
                self._stop_client()

        if self.is_active():
            info = self.get_info()
            if info.status == ClientInfo.STATUS_PLAYING:
                print("BT", info)

        self._last_update = cur_time
