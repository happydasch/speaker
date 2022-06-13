from ..draw import OverlayIconSnapcast, IconSnapcast

from .client import Client


class ClientSnapcast(Client):

    OVERLAY = OverlayIconSnapcast
    ICON = IconSnapcast

    def update_event(self, event, pulse):
        if event.facility != 'client':
            return
        client = None
        for c in pulse.client_list():
            if c.index == event.index:
                client = c
                break
        if not client:
            print('NO CLIENT', event)
            return
