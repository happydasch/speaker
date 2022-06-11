from ..draw import OverlayIconSnapcast, IconSnapcast

from .client import Client


class ClientSnapcast(Client):

    OVERLAY = OverlayIconSnapcast
    ICON = IconSnapcast

    def update_event(self, event):
        pass
