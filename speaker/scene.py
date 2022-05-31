import os
import time
import playsound

from subprocess import call
from PIL import Image, ImageDraw, ImageChops


class Scene:

    '''
    Represents a scene to be drawn
    '''

    def __init__(self, display, active=True, overlay=True, background='#000'):
        self._image = Image.new('RGBA', display.get_size(), background)
        self._background = background
        self._timer = 0
        self._draw = True
        self._active = active
        self._display = display
        self._overlay = overlay
        print(f'creating scene {self}')

    def get_display(self):
        return self._display

    def get_image(self):
        return self._image

    def is_active(self):
        return self._active

    def use_overlay(self):
        return self._overlay

    def set_active(self, active=True):
        self._active = active

    def update(self):
        if self._draw:
            self._draw = False
            return True
        return False


class SceneDefault(Scene):

    def __init__(self, display, **kwargs):
        super().__init__(display, active=False)


class SceneIntro(Scene):

    def __init__(self, display, **kwargs):
        super().__init__(display, background='#fff', overlay=False, **kwargs)
        self._draw_logo(self._image)
        self._orig_image = self._image.copy()
        self._inv_image = ImageChops.invert(self._image)
        self._mask = self._image.copy().convert('L')
        self._duration = 5  # length of startup audio
        self._anim = 3
        self._factor = 0
        self._draw_mask(self._mask, self._factor)

    def _begin(self):
        self._timer = time.time()
        self._set_volume(30)
        playsound.playsound('misc/startup.wav', False)

    def _end(self):
        self._set_volume(100)
        self.set_active(False)

    def _set_volume(self, volume):
        call(['amixer', 'sset', 'Master', f'{volume}%', '-q'])

    def _draw_logo(self, image, factor=0.8):
        image_draw = ImageDraw.Draw(image, 'RGBA')
        iw, ih = image.size             # image width and height
        u = (iw * factor) * 0.25        # unit (1/4 of scaled width)

        # outer body
        ow, oh = u * 4, u * 2           # total width and height using units
        pos_x = (iw - ow) / 2           # x position
        pos_y = (ih - oh) / 2           # y position
        xy = (pos_x, pos_y, pos_x + ow, pos_y + oh)
        r = oh / 2
        w = max(int(ih * 0.01), 1)
        image_draw.rounded_rectangle(xy=xy, radius=r, outline='#000', width=w)

        # inner body
        i_u = max(int(oh * 0.1), 1)     # unit (1/10 of outer body height)
        i_r = (oh - (2 * i_u)) / 2      # inner radius
        i_xy = (xy[0] + i_u, xy[1] + i_u, xy[2] - i_u, xy[3] - i_u)
        image_draw.rounded_rectangle(xy=i_xy, radius=i_r, fill='#000')

        # feet
        f_u = max(int(oh * 0.2), 1)
        f_pos_x, f_pos_y = pos_x + r, pos_y + oh
        f_xy_left = [
            (f_pos_x, f_pos_y),
            (f_pos_x + f_u, f_pos_y),
            (f_pos_x + (f_u/2), f_pos_y + f_u),
            (f_pos_x - (f_u/2), f_pos_y + f_u)
        ]
        f_xy_right = [
            (f_pos_x + oh - f_u, f_pos_y),
            (f_pos_x + oh, f_pos_y),
            (f_pos_x + oh + (f_u/2), f_pos_y + f_u),
            (f_pos_x + oh - (f_u/2), f_pos_y + f_u)
        ]
        image_draw.polygon(f_xy_left, fill='#000')
        image_draw.polygon(f_xy_right, fill='#000')

    def _draw_mask(self, image, factor):
        image_draw = ImageDraw.Draw(image, 'L')
        iw, ih = image.size             # image width and height
        radius = int(iw * factor)
        image_draw.rectangle((0, 0, iw, ih), '#fff')
        if radius > 0:
            radius *= 2
            image_draw.ellipse(((-radius, -radius), (radius, radius)), '#000')

    def update(self):
        if not self._timer:
            self._begin()

        current_time = time.time()
        current_duration = current_time - self._timer
        factor = 0

        # update mask
        if current_duration > (self._duration - self._anim):
            duration = current_duration - (self._duration - self._anim)
            factor = round(duration/self._anim, 2)
            if factor != self._factor:
                self._draw_mask(self._mask, factor)
                self._factor = factor
                self._draw = True

        # disable animation after n seconds
        if current_time - self._timer > self._duration:
            self._end()

        # redraw frame if needed
        if self._draw:
            self._image = Image.composite(
                self._orig_image, self._inv_image, self._mask)
            self._draw = False
            return True
        return False


class SceneOutro(Scene):

    def __init__(self, display, **kwargs):
        super().__init__(display, overlay=False, **kwargs)


class SceneClient(Scene):

    def __init__(self, display, **kwargs):
        super().__init__(display, **kwargs)
        self._image_dir = os.path.join(os.path.dirname(__file__), 'images')
        self._buttons = Image\
            .open(os.path.join(self._image_dir, 'buttons_32.png'))\
            .convert('RGBA')
