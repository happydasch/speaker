import time
import os

from PIL import Image, ImageDraw

from .utils import image_tint, draw_progress_bar


'''
Primitives
'''


class Icon:

    def __init__(self, idx=None):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        icons = os.path.join(image_dir, 'icons_256.png')
        image_map = ImageMap(icons)
        if idx is not None:
            self._image = image_map.get(idx)
        else:
            self._image = image_map.new()

    def get_image(self):
        return self._image


class ImageMap:

    def __init__(self, file, foreground=None):
        image = Image.open(file)
        if not foreground:
            self.image = image
        else:
            self.image = image_tint(image, tint=foreground)

    def get(self, idx):
        height = self.image.size[1]
        cropped = self.image.crop(
            (height * idx, 0, height * idx + height, height))
        return cropped

    def new(self, color='#fff'):
        size = self.image.size[1]
        new = Image.new('RGBA', (size, size), color)
        return new


class Overlay:

    '''
    Represents a overlay to be drawn
    '''

    def __init__(
            self, display, opacity=1.0, duration=0.5, fade_duration=0,
            fade_in=False, fade_out=False, active=True, background='#000'):
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

    def get_speaker(self):
        return self._display.get_speaker()

    def get_client(self):
        return self.get_speaker().client

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


class OverlayImageMap(Overlay):

    def __init__(self, display, file, idx, foreground='#fff', **kwargs):
        super().__init__(display=display, **kwargs)
        self._overlay = ImageMap(file, foreground=foreground)
        self._idx = idx
        self._image = self._draw_overlay(self._overlay.get(idx))

    def _draw_overlay(self, image):
        size = image.size
        overlay_size = (int(size[0] * 1.5), int(size[1] * 1.5))
        dest_pos = (int(size[0] * 0.25), int(size[1] * 0.25))
        overlay = Image.new('RGBA', overlay_size, self._background)
        overlay.alpha_composite(image, dest_pos)
        return overlay.resize(self._display.get_size())


'''
Overlays
'''


class OverlayNotSupported(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'buttons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['idx'] = 0
        super().__init__(**kwargs)


class OverlayButtonPlay(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'buttons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['idx'] = 1
        super().__init__(**kwargs)


class OverlayButtonPause(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'buttons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['idx'] = 2
        super().__init__(**kwargs)


class OverlayButtonVolumeDown(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'buttons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['idx'] = 3
        super().__init__(**kwargs)

    def _draw_overlay(self, image):
        overlay = super()._draw_overlay(image)
        overlay_draw = ImageDraw.Draw(overlay, 'RGBA')
        max_volume = self.get_speaker().MAX_VOLUME
        volume = self.get_client().get_volume()
        ow, oh = overlay.size
        ob = ow * 0.02
        rect = (ob, 2 * ob, ow - ob, 3 * ob)
        draw_progress_bar(
            overlay_draw, volume, max_volume, rect, (255, 255, 255))
        return overlay

    def update(self):
        res = super().update()
        if res:
            self._image = self._draw_overlay(
                self._overlay.get(self._idx))
        return res


class OverlayButtonVolumeUp(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'buttons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['idx'] = 4
        super().__init__(**kwargs)

    def _draw_overlay(self, image):
        overlay = super()._draw_overlay(image)
        overlay_draw = ImageDraw.Draw(overlay, 'RGBA')
        max_volume = self.get_speaker().MAX_VOLUME
        volume = self.get_client().get_volume()
        ow, oh = overlay.size
        ob = ow * 0.02
        rect = (ob, 2 * ob, ow - ob, 3 * ob)
        draw_progress_bar(
            overlay_draw, volume, max_volume, rect, (255, 255, 255))
        return overlay

    def update(self):
        res = super().update()
        if res:
            self._image = self._draw_overlay(
                self._overlay.get(self._idx))
        return res


class OverlayButtonPrevious(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'buttons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['idx'] = 5
        super().__init__(**kwargs)


class OverlayButtonNext(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'buttons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['idx'] = 6
        super().__init__(**kwargs)


class OverlayIconSnapcast(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'icons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['foreground'] = kwargs.get('foreground', None)
        kwargs['idx'] = 0
        super().__init__(**kwargs)


class OverlayIconBluetooth(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'icons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['foreground'] = kwargs.get('foreground', None)
        kwargs['idx'] = 1
        super().__init__(**kwargs)


class OverlayIconAirplay(OverlayImageMap):

    def __init__(self, display, **kwargs):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        file = os.path.join(image_dir, 'icons_256.png')
        kwargs['display'] = display
        kwargs['file'] = file
        kwargs['foreground'] = kwargs.get('foreground', None)
        kwargs['idx'] = 2
        super().__init__(**kwargs)


'''
Icons
'''


class IconSnapcast(Icon):

    def __init__(self):
        super().__init__(0)


class IconBluetooth(Icon):

    def __init__(self):
        super().__init__(1)


class IconAirplay(Icon):

    def __init__(self):
        super().__init__(2)
