import time
import simpleaudio as sa

from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont, ImageChops

from ..utils import text_in_rect
from .scene import Scene


class SceneIntro(Scene):

    '''
    Intro scene

    This scene shows an introduction with an animation and sound.
    While this scene is active, no overlays will be shown.
    '''

    DURATION = 6
    ANIM_DURATION = 4

    def __init__(self, display, **kwargs):
        kwargs |= {'background': '#fff', 'overlay': False}
        super().__init__(display, **kwargs)
        self._draw_logo(self._image)
        self._font = ImageFont.truetype(UserFont, 96)
        self._orig_image = self._image.copy()
        self._inv_image = ImageChops.invert(self._image)
        self._mask = self._image.copy().convert('L')
        self._factor = 0
        self._volume = self.get_speaker().mixer.getvolume()[0]
        self._draw_text(self._inv_image)
        self._draw_mask(self._mask, self._factor)
        self._wave_object = sa.WaveObject.from_wave_file('misc/startup.wav')
        self._song = None

    def _begin(self):
        self._timer = time.time()
        mixer = self.get_speaker().mixer
        mixer.setvolume(30)
        self._song = self._wave_object.play()

    def _end(self):
        mixer = self.get_speaker().mixer
        mixer.setvolume(self._volume)
        self.set_active(False)

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

    def _draw_text(self, image, factor=0.8):
        image_draw = ImageDraw.Draw(image, 'RGBA')
        iw, ih = image.size             # image width and height
        u = (iw * factor) * 0.25        # unit (1/4 of scaled width)
        ow, oh = u * 4, u * 2           # total width and height using units
        pos_x = (iw - ow) / 2           # x position
        pos_y = (ih - oh) / 2           # y position
        xy = (pos_x + oh/4, pos_y, pos_x + ow - oh/4, pos_y + oh)
        text_in_rect(
            image_draw,
            text='Hello!',
            font=self._font,
            rect=xy,
            fill='#000')

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
        redraw = False

        if current_duration < self.ANIM_DURATION:
            factor = round(current_duration / self.ANIM_DURATION, 2)
            if factor != self._factor:
                self._draw_mask(self._mask, factor)
                self._factor = factor
                redraw = True

        if (not self._song.is_playing()
                and (current_time - self._timer > self.DURATION)):
            self._end()

        if redraw:
            self._image = Image.composite(
                self._orig_image, self._inv_image, self._mask)
        return redraw
