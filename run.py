import os

from speaker import Speaker
from speaker.client import ClientAirplay, ClientBluetooth
from speaker.display import DisplayST7789
from speaker.control import ControlPirateAudio


def main():
    cache_dir = os.path.realpath('./cache')
    os.makedirs(cache_dir, exist_ok=True)
    sp = Speaker(
        display=DisplayST7789,
        control=ControlPirateAudio,
        intro=True, outro=True,
        cache_dir=cache_dir)
    sp.add_client(ClientBluetooth)
    sp.add_client(ClientAirplay)
    sp.run()



if __name__ == '__main__':
    main()
