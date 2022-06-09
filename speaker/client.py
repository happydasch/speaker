import pulsectl
import time

from .overlay import (
    Overlay, OverlayIconSnapcast, OverlayIconAirplay, OverlayIconBluetooth)
from .icon import (Icon, IconSnapcast, IconAirplay, IconBluetooth)


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

    def update(self):
        return

    def update_event(self, event):
        return

    def is_active(self):
        return self._active

    def get_speaker(self):
        return self._speaker

    def is_playing(self):
        return False

    def toggle_play(self):
        pass

    def next(self):
        pass

    def volume_down(self):
        pass

    def volume_up(self):
        pass


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
        self._last_update = cur_time

        bluetooth_device = None
        for c in self._pulse.card_list():
            props = c.proplist
            if props.get('device.api') == 'bluez':
                bluetooth_device = c
                break
        self._active = (bluetooth_device is not None)

    def update_event(self, event):
        #print(event)
        pass


class ClientAirplay(Client):

    OVERLAY = OverlayIconAirplay
    ICON = IconAirplay

    def update_event(self, event):
        pass


class ClientSnapcast(Client):

    OVERLAY = OverlayIconSnapcast
    ICON = IconSnapcast

    def update_event(self, event):
        pass
