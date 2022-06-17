import time

from RPi import GPIO

from ..draw import (
    OverlayNotSupported, OverlayButtonPlay, OverlayButtonPause,
    OverlayButtonNext, OverlayButtonVolumeDown, OverlayButtonVolumeUp)

from .control import Control


class ControlPirateAudio(Control):

    def __init__(
            self, speaker, pin_play=6, pin_next=24,
            pin_volume_down=5, pin_volume_up=16):
        super().__init__(speaker)
        self._pins = [pin_play, pin_next, pin_volume_down, pin_volume_up]
        self._last_press = 0
        self._pin_play = pin_play
        self._pin_next = pin_next
        self._pin_volume_down = pin_volume_down
        self._pin_volume_up = pin_volume_up

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
                    OverlayButtonPause,
                    duration=1.0,
                    fade_duration=0.5,
                    opacity=0.9,
                    fade_out=True)
            else:
                speaker.display.set_overlay(
                    OverlayButtonPlay,
                    duration=1.0,
                    fade_duration=0.5,
                    opacity=0.9,
                    fade_out=True)
            client.toggle_play()
        elif pin == self._pin_next:
            speaker.display.set_overlay(
                OverlayButtonNext,
                duration=1.0,
                fade_duration=0.5,
                opacity=0.9,
                fade_out=True)
            client.next()
        elif pin == self._pin_volume_down:
            speaker.display.set_overlay(
                OverlayButtonVolumeDown,
                duration=1.0,
                fade_duration=0.5,
                opacity=0.9,
                fade_out=True)
            client.volume_down()
        elif pin == self._pin_volume_up:
            speaker.display.set_overlay(
                OverlayButtonVolumeUp,
                duration=1.0,
                fade_duration=0.5,
                opacity=0.9,
                fade_out=True)
            client.volume_up()
