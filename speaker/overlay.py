import os
import time

from PIL import Image

from .utils import image_tint


class Overlay:

    '''
    Represents a overlay to be drawn
    '''

    image = None
    opacity = None

    def __init__(
            self, display, image, opacity=1.0, duration=0.5, fade_duration=0,
            fade_in=False, fade_out=False, active=True, background='#000000'):
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
        self._opacity = opacity
        self._duration = duration
        self._fade_duration = fade_duration
        self._fade_in = fade_in
        self._fade_out = fade_out
        self._background = background

    def get_display(self):
        return self._display

    def is_active(self):
        return self._active

    def set_active(self, active=True):
        self._active = active

    def update(self):
        current_time = time.time()
        start = self._timer
        duration = self._duration
        fade_duration = self._fade_duration
        opacity = self._opacity

        # get correct durations
        if self._fade_in and self._fade_out:
            if fade_duration == 0:
                fade_duration = duration / 2
            duration = max(duration, fade_duration * 2)
        elif self._fade_in or self._fade_out:
            if fade_duration == 0:
                fade_duration = duration
            duration = max(duration, fade_duration)

        # check for fade effect
        current_duration = current_time - start
        if (self._fade_in
                and current_duration < fade_duration):
            opacity = current_duration / fade_duration
            opacity = opacity * self._opacity
        elif (self._fade_out
                and current_duration >= duration - fade_duration):
            opacity = (duration-current_duration) / fade_duration
            opacity = opacity * self._opacity
        opacity = min(max(opacity, 0), 1)
        opacity = round(opacity, 2)

        # check if overlay is finished
        if duration > 0 and current_time - duration > start:
            self.set_active(False)

        # check if overlay should be redrawn
        if self._draw or self.opacity != opacity:
            self.opacity = opacity
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
