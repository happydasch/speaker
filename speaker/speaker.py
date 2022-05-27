import time

from .control import ControlPirateAudio
from .display import DisplayST7789
from .scene import SceneDefault, SceneIntro


class Speaker:

    '''
    Represents the speaker
    '''

    MIN_BRIGHTNESS = 0
    MAX_BRIGHTNESS = 80

    client = None
    display = None
    control = None

    def __init__(
            self, update_interval=1, display_timeout=8, fps=30,
            intro=True, outro=True):

        self.client = None
        self.display = DisplayST7789(self)
        self.control = ControlPirateAudio(self)

        self._clients = None
        self._running = False
        self._active = False
        self._active_timer = 0
        self._update_interval = update_interval
        self._display_timeout = display_timeout
        self._fps = fps
        self._intro = intro
        self._outro = outro

    def is_active(self):
        return self._active

    def set_active(self, active=True):
        self._active_timer = time.time()
        self._active = active

    def update(self):
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
        scene = self.display.get_scene()
        if scene:
            if (not scene.is_active() and not isinstance(scene, SceneDefault)):
                self.display.set_scene(SceneDefault)
        else:
            if self._intro:
                self.display.set_scene(SceneIntro)
            else:
                self.display.set_scene(SceneDefault)
