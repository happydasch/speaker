
class Client:

    def __init__(self, speaker):
        self._speaker = speaker

    def toggle_play(self):
        pass

    def next(self):
        pass

    def volume_up(self):
        pass

    def volume_down(self):
        pass


class ClientBluetooth(Client):
    pass


class ClientAirplay(Client):
    pass


class ClientSnapcast(Client):
    pass


class ClientMPD(Client):
    pass
