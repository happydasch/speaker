from ..draw import OverlayIconAirplay, IconAirplay

from .client import Client


class ClientAirplay(Client):

    OVERLAY = OverlayIconAirplay
    ICON = IconAirplay

    def update_event(self, event):
        pass
