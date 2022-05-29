import os
import time

from PIL import Image

from .utils import image_tint


class Overlay:

    '''
    Represents a overlay to be drawn
    '''

    def __init__(
            self, display, opacity=1.0, duration=0.5, fade_duration=0,
            fade_in=False, fade_out=False, active=True, background='#000000'):
        self._image = Image.new('RGBA', display.get_size(), background)
        self._timer = 0
        self._draw = True
        self._active = active
        self._display = display
        self._opacity = opacity
        self._src_opacity = opacity
        self._duration = duration
        self._fade_duration = fade_duration
        self._fade_in = fade_in
        self._fade_out = fade_out
        self._background = background
        print(f'creating overlay {self}')

    def get_display(self):
        return self._display

    def get_image(self):
        return self._image

    def get_opacity(self):
        return self._opacity

    def is_active(self):
        return self._active

    def set_active(self, active=True):
        self._active = active

    def update(self):
        if not self._timer:
            self._timer = time.time()
        current_time = time.time()
        duration = self._duration
        fade_duration = self._fade_duration

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
        current_duration = current_time - self._timer
        if (self._fade_in
                and current_duration < fade_duration):
            # fade in
            opacity = current_duration / fade_duration
            opacity = opacity * self._src_opacity
        elif (self._fade_out
                and current_duration >= duration - fade_duration):
            # fade out
            opacity = (duration - current_duration) / fade_duration
            opacity = opacity * self._src_opacity
        else:
            # default
            opacity = self._src_opacity
        opacity = min(max(opacity, 0), self._src_opacity)
        opacity = round(opacity, 2)

        # check if overlay is finished
        if duration > 0 and current_time - duration > self._timer:
            self.set_active(False)

        # check if overlay should be redrawn
        if self._draw or self._opacity != opacity:
            self._opacity = opacity
            self._draw = False
            return True
        return False


class OverlayButton(Overlay):

    def __init__(self, display, idx, foreground='#ffffff', **kwargs):
        super().__init__(display=display, **kwargs)
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        buttons = Image.open(os.path.join(image_dir, 'buttons_256.png'))
        self._buttons = image_tint(buttons, tint=foreground)
        self._image = self._get_overlay_by_button_idx(idx)

    def _get_overlay_by_button_idx(self, idx):
        height = self._buttons.size[1]
        button = self._buttons.crop(
            (height * idx, 0, height * idx + height, height))
        size = button.size
        overlay_size = (int(size[0] * 1.5), int(size[1] * 1.5))
        dest_pos = (int(size[0] * 0.25), int(size[1] * 0.25))
        image = Image.new('RGBA', overlay_size, self._background)
        image.alpha_composite(button, dest_pos)
        return image.resize(self._display.get_size())


class OverlayNotSupported(OverlayButton):

    def __init__(self, display, **kwargs):
        super().__init__(display=display, idx=0, **kwargs)


class OverlayPlay(OverlayButton):

    def __init__(self, display, **kwargs):
        super().__init__(display=display, idx=1, **kwargs)


class OverlayPause(OverlayButton):

    def __init__(self, display, **kwargs):
        super().__init__(display=display, idx=2, **kwargs)


class OverlayVolumeDown(OverlayButton):

    def __init__(self, display, **kwargs):
        super().__init__(display=display, idx=3, **kwargs)


class OverlayVolumeUp(OverlayButton):

    def __init__(self, display, **kwargs):
        super().__init__(display=display, idx=4, **kwargs)


class OverlayPrevious(OverlayButton):

    def __init__(self, display, **kwargs):
        super().__init__(display=display, idx=5, **kwargs)


class OverlayNext(OverlayButton):

    def __init__(self, display, **kwargs):
        super().__init__(display=display, idx=6, **kwargs)
