from speaker import Speaker
from speaker.client import ClientAirplay, ClientBluetooth, ClientSnapcast
from speaker.display import DisplayST7789
from speaker.control import ControlPirateAudio


def main():
    sp = Speaker(
        intro=True, outro=True,
        display=DisplayST7789,
        control=ControlPirateAudio)
    sp.add_client(ClientBluetooth)
    sp.add_client(ClientSnapcast)
    sp.add_client(ClientAirplay)
    try:
        sp.start()
    except KeyboardInterrupt:
        sp.stop()


if __name__ == '__main__':
    main()
