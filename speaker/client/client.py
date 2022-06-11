from ..draw import Icon, Overlay


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

    def get_speaker(self):
        return self._speaker

    def update(self):
        return

    def update_event(self, event):
        return

    def is_active(self):
        return self._active

    def is_playing(self):
        return False

    def toggle_play(self):
        return

    def next(self):
        return

    def volume_down(self):
        return

    def volume_up(self):
        return
