import os
import time

from PIL import Image

from .utils import image_tint


class Overlay:

    '''
    Represents a overlay to be drawn
    '''

    image = None
    opacity = 0.5

    def __init__(
            self, display, image, duration=0, fadein=False, fadeout=False,
            active=True, background='#000000'):
        self.image = Image.new(
                'RGBA',
                display.get_size(),
                background)
        self.image = Image.alpha_composite(self.image, image)
        self._draw = True
        self._timer = time.time()
        self._active = active
        self._display = display
        self._image = image
        self._duration = duration
        self._fadein = fadein
        self._fadeout = fadeout
        self._background = background

    def get_display(self):
        return self._display

    def is_active(self):
        return self._active

    def set_active(self, active=True):
        self._active = active

    def update(self):
        if self._fadein or self._fadeout:
            # TODO add fade in / out
            pass
        if self._duration > 0 and time.time() - self._duration > self._timer:
            self.set_active(False)
        if self._draw:
            self._draw = False
            return True
        return False


class OverlayNotSupported(Overlay):

    def __init__(self, display, foreground='#ffffff', **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        image = Image.open(os.path.join(image_dir, 'not_supported_256.png'))
        image = image_tint(image, tint=foreground)
        image = image.resize(display.get_size(), resample=Image.LANCZOS)\
            .convert('RGBA')
        super().__init__(display=display, image=image, **kwargs)
