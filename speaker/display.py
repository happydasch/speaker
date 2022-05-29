import RPi.GPIO as GPIO
from ST7789 import ST7789
from PIL import Image


class Display:

    '''
    Represents a display
    '''

    WIDTH = 0
    HEIGHT = 0

    image = None

    def __init__(self, speaker):
        self.image = Image.new('RGBA', self.get_size(), (255, 255, 255))
        self._speaker = speaker
        self._brightness = 0
        self._scene = None
        self._overlay = None

    def get_speaker(self):
        return self._speaker

    def get_size(self):
        return (self.WIDTH, self.HEIGHT)

    def get_scene(self):
        return self._scene

    def set_scene(self, scene, *args, **kargs):
        self._scene = scene(self, *args, **kargs) if scene else None

    def get_overlay(self):
        return self._overlay

    def set_overlay(self, overlay, *args, **kargs):
        self._overlay = overlay(self, *args, **kargs) if overlay else None

    def get_brightness(self):
        return self._brightness

    def set_brightness(self, brightness):
        self._brightness = brightness

    def update(self):
        scene_update = False
        overlay_update = False
        scene = self.get_scene()
        overlay = self.get_overlay()
        if overlay:
            if overlay.update():
                overlay_update = True
            if not overlay.is_active():
                self.set_overlay(None)
                overlay = None
                overlay_update = True
        if scene:
            if overlay_update or scene.update():
                scene_image = scene.get_image()
                if scene_image:
                    self.image = scene_image
                scene_update = True
        if overlay and (overlay_update or scene_update):
            overlay_image = overlay.get_image()
            overlay_opacity = overlay.get_opacity()
            if overlay_image:
                self.image = Image.blend(
                    self.image, overlay_image, overlay_opacity)
        return scene_update or overlay_update

    def start(self):
        return

    def stop(self):
        return

    def redraw(self):
        return


class DisplayST7789(Display):

    SPI_SPEED_MHZ = 90
    WIDTH = 240
    HEIGHT = 240

    def __init__(self, speaker):
        super().__init__(speaker)
        # Standard display setup for Pirate Audio,
        # except omit the backlight pin
        self._st7789 = ST7789(
            rotation=90,     # Needed to display the right
                             # way up on Pirate Audio
            port=0,          # SPI port
            cs=1,            # SPI port Chip-select channel
            dc=9,            # BCM pin used for data/command
            backlight=None,  # Control the backlight manually
            spi_speed_hz=self.SPI_SPEED_MHZ * 1000 * 1000
        )
        # Set up backlight pin as a PWM output at 500Hz
        GPIO.setup(13, GPIO.OUT)
        self._backlight = GPIO.PWM(13, 500)

    def set_brightness(self, brightness):
        brightness = max(min(brightness, 100), 0)
        self._backlight.ChangeDutyCycle(brightness)
        self._brightness = brightness

    def redraw(self):
        if self.image:
            self._st7789.display(self.image)

    def start(self):
        self._backlight.start(self._brightness)

    def stop(self):
        self._backlight.stop()
