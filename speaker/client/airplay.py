import time
import pulsectl

from ..draw import OverlayIconAirplay, IconAirplay

from .client import Client


class ClientAirplay(Client):

    OVERLAY = OverlayIconAirplay
    ICON = IconAirplay
    UPDATE_INTERVAL = 1

    def __init__(self, speaker):
        super().__init__(speaker)
        self._last_update = 0
        self._sink_input = None

    def _check_pulse(self, pulse):
        found = False
        for s in pulse.sink_input_list():
            if s.proplist.get('application.name') == 'Shairport Sync':
                found = True
                self._sink_input = s.index
        if not found:
            self._sink_input = None

    def update_event(self, event, pulse):
        self._check_pulse(pulse)

    def update(self):
        cur_time = time.time()
        if cur_time - self._last_update < self.UPDATE_INTERVAL:
            return
        self._active = self._sink_input is not None
        self._last_update = cur_time
