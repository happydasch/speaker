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
    UPDATE_INTERVAL = 0.5

    def __init__(self, speaker):
        super().__init__(speaker)
        self._last_update = 0
        self._path = None

    def _get_dbus(self):
        player_iface = None
        transport_iface = None
        try:
            bus = dbus.SystemBus()
            obj = bus.get_object(
                'org.bluez', f'{self._path}/player0')
            player_iface = dbus.Interface(
                obj, 'org.bluez.MediaPlayer1')
            transport_iface = dbus.Interface(
                obj, "org.freedesktop.DBus.Properties")
        except Exception:
            pass
        return player_iface, transport_iface

    def _check_pulse(self):
        with pulsectl.Pulse() as pulse:
            bluetooth_device = None
            for c in pulse.card_list():
                props = c.proplist
                if props.get('device.api') == 'bluez':
                    bluetooth_device = c
                    self._path = props.get('bluez.path')
                    break
            self.set_active(bluetooth_device is not None)

    def set_active(self, active=True):
        self._active = active

    def get_info(self):
        res = None
        try:
            _, transport = self._get_dbus()
            res = transport.GetAll("org.bluez.MediaPlayer1")
        except Exception:
            pass
        info = BluetoothClientInfo(res)
        info.volume = self.get_volume()
        return info

    def update(self):
        cur_time = time.time()
        if cur_time - self._last_update < self.UPDATE_INTERVAL:
            return

        self._check_pulse()
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

    def update_event(self, event):
        #print(event)
        pass

    def play(self):
        try:
            player_iface, _ = self._get_dbus()
            player_iface.Play()
        except Exception:
            pass

    def pause(self):
        try:
            player_iface, _ = self._get_dbus()
            player_iface.Pause()
        except Exception:
            pass

    def prev(self):
        try:
            player_iface, _ = self._get_dbus()
            player_iface.Prev()
        except Exception:
            pass

    def next(self):
        try:
            player_iface, _ = self._get_dbus()
            player_iface.Next()
        except Exception:
            pass

    def volume_down(self):
        super().volume_down()
        try:
            player_iface, _ = self._get_dbus()
            player_iface.VolDown()
        except Exception:
            pass

    def volume_up(self):
        super().volume_up()
        try:
            player_iface, _ = self._get_dbus()
            player_iface.VolUp()
        except Exception:
            pass
