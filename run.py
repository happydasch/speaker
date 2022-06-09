from speaker import Speaker
from speaker.client import ClientAirplay, ClientBluetooth, ClientSnapcast


def main():
    sp = Speaker()
    sp.add_client(ClientBluetooth)
    sp.add_client(ClientAirplay)
    sp.add_client(ClientSnapcast)
    try:
        sp.start()
    except KeyboardInterrupt:
        sp.stop()


if __name__ == '__main__':
    main()
