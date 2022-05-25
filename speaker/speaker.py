
class Speaker:

    def __init__(self):
        self._client = None
        self._song = None
        self._state = None
        self._clients = None
        self._controls = None

    def get_client(self):
        return self._client

    def get_song(self):
        return self._song

    def get_state(self):
        return self._state

    def start(self):
        pass

    def stop(self):
        pass

