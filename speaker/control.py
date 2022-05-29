import time

from RPi import GPIO

from .overlay import (
    OverlayNotSupported, OverlayPlay, OverlayPause, OverlayNext,
    OverlayVolumeDown, OverlayVolumeUp)


class Control:

    '''
    Represents controls
    '''

    def __init__(self, speaker):
        self._speaker = speaker

    def get_speaker(self):
        return self._speaker

    def start(self):
        return

    def stop(self):
        return


class ControlPirateAudio(Control):

    def __init__(
            self, speaker, pin_play=5, pin_next=16,
            pin_volume_down=6, pin_volume_up=24):
        super().__init__(speaker)
        self._pins = [pin_play, pin_next, pin_volume_down, pin_volume_up]
        self._last_press = 0
        self._pin_play = pin_play                   # button A
        self._pin_next = pin_next                   # button X
        self._pin_volume_down = pin_volume_down     # button B
        self._pin_volume_up = pin_volume_up         # button Y

    def start(self):
        GPIO.setup(self._pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for pin in self._pins:
            GPIO.add_event_detect(
                pin, GPIO.FALLING, self.handle_button)

    def stop(self):
        for pin in self._pins:
            GPIO.remove_event_detect(pin)

    def handle_button(self, pin):
        now = time.time()
        if self._last_press + 0.5 > now:
            return
        self._last_press = now
        speaker = self.get_speaker()
        active = speaker.is_active()
        speaker.set_active()
        if not active:
            return
        client = speaker.client
        if not client:
            speaker.display.set_overlay(
                OverlayNotSupported,
                duration=1.0,
                fade_duration=0.5,
                opacity=0.9,
                foreground='#c00',
                fade_out=True)
            return
        if pin == self._pin_play:
            if client.is_playing():
                speaker.display.set_overlay(
                    OverlayPause,
                    duration=1.0,
                    fade_duration=0.5,
                    opacity=0.9,
                    fade_out=True)
            else:
                speaker.display.set_overlay(
                    OverlayPlay,
                    duration=1.0,
                    fade_duration=0.5,
                    opacity=0.9,
                    fade_out=True)
            client.toggle_play()
        elif pin == self._pin_next:
            speaker.display.set_overlay(
                OverlayNext,
                duration=1.0,
                fade_duration=0.5,
                opacity=0.9,
                fade_out=True)
            client.next()
        elif pin == self._pin_volume_down:
            speaker.display.set_overlay(
                OverlayVolumeDown,
                duration=1.0,
                fade_duration=0.5,
                opacity=0.9,
                fade_out=True)
            client.volume_down()
        elif pin == self._pin_volume_up:
            speaker.display.set_overlay(
                OverlayVolumeUp,
                duration=1.0,
                fade_duration=0.5,
                opacity=0.9,
                fade_out=True)
            client.volume_up()
