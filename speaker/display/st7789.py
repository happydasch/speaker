import RPi.GPIO as GPIO
from ST7789 import ST7789

from .display import Display

from PIL import Image


class DisplayST7789(Display):

    SPI_SPEED_MHZ = 50
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
        self._st7789.display(
            Image.new('RGB', (self._st7789.width, self._st7789.height)))
        # Set up backlight pin as a PWM output at 500Hz
        GPIO.setup(13, GPIO.OUT)
        self._backlight = GPIO.PWM(13, 500)

    def set_brightness(self, brightness):
        brightness = max(min(brightness, 100), 0)
        self._brightness = brightness
        self._backlight.ChangeDutyCycle(brightness)

    def redraw(self):
        if self._image:
            self._st7789.display(self._image)

    def start(self):
        self._backlight.start(self._brightness)

    def stop(self):
        self._backlight.stop()
