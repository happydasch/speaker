from speaker import Speaker


def main():
    sp = Speaker()
    try:
        sp.start()
    except KeyboardInterrupt:
        sp.stop()


if __name__ == '__main__':
    main()
