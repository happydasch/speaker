import pulsectl
import time

from ..draw import (OverlayIconBluetooth, IconBluetooth)

from .client import Client


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
        self._pulse = pulsectl.Pulse('client-bluetooth')

    def update(self):
        cur_time = time.time()
        if cur_time - self._last_update < self.UPDATE_INTERVAL:
            return

        with pulsectl.Pulse() as pulse:
            bluetooth_device = None
            for c in pulse.card_list():
                props = c.proplist
                if props.get('device.api') == 'bluez':
                    bluetooth_device = c
                    break
            self._active = (bluetooth_device is not None)

        self._last_update = cur_time

    def update_event(self, event):
        #print(event)
        pass

        '''method = f"org.freedesktop.DBus.Properties.Set string:org.bluez.MediaTransport1 string:Volume variant:uint16:{vol}"
        with Pulse() as pulse:
            for sink in pulse.sink_list():
                bluez_path = sink.proplist.get("bluez.path")
                if bluez_path:
                    args = f"dbus-send --print-reply --system \
                    --dest=org.bluez {bluez_path}/sep1/fd0 {method}"

                    subprocess.run(args, stderr=subprocess.STDOUT, shell=True, check=True)
                else:
                    pulse.volume_change_all_chans(sink, diff)'''
