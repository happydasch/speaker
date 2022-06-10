from threading import Thread
import pulsectl
import time

from .control import ControlPirateAudio
from .display import DisplayST7789
from .scene import SceneClient, SceneDefault, SceneIntro


__version__ = '0.0.1'


class Speaker:

    '''
    Represents the speaker
    '''

    MIN_BRIGHTNESS = 0
    MAX_BRIGHTNESS = 80

    client = None
    display = None
    control = None
    volume = 100

    def __init__(
            self, update_interval=1, display_timeout=8, fps=30,
            intro=True, outro=True):

        self.client = None
        self.display = DisplayST7789(self)
        self.control = ControlPirateAudio(self)

        self._thread = Thread(target=self._thread_fn, daemon=True)
        self._clients = []
        self._event = None
        self._running = False
        self._active = False
        self._active_timer = 0
        self._update_interval = update_interval
        self._display_timeout = display_timeout
        self._fps = fps
        self._intro = intro
        self._outro = outro

    def _thread_fn(self):
        with pulsectl.Pulse() as pulse:
            pulse.event_mask_set('all')
            pulse.event_callback_set(self._event_handler)
            while self._running:
                pulse.event_listen()
                event = self._event
                client = None
                for c in sorted(self._clients, key=lambda c: c.PRIORITY):
                    c.update_event(event)
                    if not client and c.is_active():
                        client = c
                if client != self.client:
                    print(f'setting client {client}')
                    self.set_client(client)

    def _event_handler(self, ev):
        self._event = ev
        raise pulsectl.PulseLoopStop

    def is_active(self):
        return self._active

    def set_active(self, active=True):
        self._active_timer = time.time()
        self._active = active

    def add_client(self, client, *args, **kwargs):
        self._clients.append(client(self, *args, **kwargs))

    def set_client(self, client):
        if client and client != self.client:
            self.display.set_overlay(
                    client.OVERLAY,
                    duration=4.0,
                    fade_duration=1.0,
                    opacity=1.0,
                    fade_out=True)
        self.client = client

    def update(self):
        for c in self._clients:
            c.update()
        self._check_display_timeout()
        self._check_scene()
        if not self._check_display_brightness():
            return True
        return False

    def start(self):
        if self._running:
            return
        last_update = 0
        self._running = True
        self._thread.start()
        self.control.start()
        self.display.start()
        self.set_active()
        while self._running:
            self.update()
            display_update = self.display.update()
            if not display_update:
                if time.time() - last_update < float(self._update_interval):
                    time.sleep(1.0 / self._fps)
                    continue
            if display_update or self.is_active():
                self.display.redraw()
            last_update = time.time()

    def stop(self):
        last_update = 0
        self.set_active(False)
        while self.update():
            display_update = self.display.update()
            if not display_update:
                if time.time() - last_update < float(self._update_interval):
                    time.sleep(1.0 / self._fps)
                    continue
            if display_update:
                self.display.redraw()
            last_update = time.time()
        self.control.stop()
        self.display.stop()
        self._running = False
        if self._thread.is_alive():
            self._thread.join(timeout=1)

    def _check_display_brightness(self):
        brightness = self.display.get_brightness()
        if self.is_active() and brightness < self.MAX_BRIGHTNESS:
            brightness += 10
        elif not self.is_active() and brightness > self.MIN_BRIGHTNESS:
            brightness -= 10
        brightness = max(
            min(brightness, self.MAX_BRIGHTNESS),
            self.MIN_BRIGHTNESS)
        if brightness != self.display.get_brightness():
            self.display.set_brightness(brightness)
            return False
        return True

    def _check_display_timeout(self):
        scene = self.display.get_scene()
        if not self.is_active():
            if scene and scene.is_active():
                self.set_active(True)
        if time.time() - self._active_timer > float(self._display_timeout):
            if self.display._scene and not self.display._scene.is_active():
                self.set_active(False)

    def _check_scene(self):
        cur_scene = self.display.get_scene()
        scene = None

        if cur_scene:
            if not cur_scene.is_active():
                if self.client:
                    scene = SceneClient
                else:
                    scene = SceneDefault
        else:
            if self._intro:
                scene = SceneIntro

        if scene and not isinstance(cur_scene, scene):
            self.display.set_scene(scene)
