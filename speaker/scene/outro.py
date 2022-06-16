import time

from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont

from .scene import Scene
from ..utils import text_in_rect


class SceneOutro(Scene):

    DURATION = 4
    ANIM_DURATION = 3

    def __init__(self, display, **kwargs):
        kwargs |= {'overlay': False, 'active': True}
        super().__init__(display, **kwargs)
        self._opacity = None
        self._font = ImageFont.truetype(UserFont, 96)
        self._image_background = Image.new('RGBA', display.get_size(), '#000')
        self._image_text = Image.new('RGBA', display.get_size())
        self._draw_text(self._image_text)

    def _draw_text(self, image):
        iw, ih = image.size
        # prepare image to draw
        image_draw = ImageDraw.Draw(image, 'RGBA')
        text_in_rect(
            image_draw,
            text='Bye!',
            font=self._font,
            rect=(0, 0, iw, ih),
            fill='#fff')

    def update(self):
        if not self._timer:
            self._timer = time.time()

        current_time = time.time()
        current_duration = current_time - self._timer
        opacity = 0
        redraw = False

        if current_duration < self.DURATION:
            duration = max(
                0,
                current_duration - (self.DURATION - self.ANIM_DURATION))
            opacity = 1 - round(duration / self.DURATION, 2)
            if opacity != self._opacity:
                self._image = Image.blend(
                    self._image_background,
                    self._image_text,
                    opacity)
                self._opacity = opacity
                redraw = True
        else:
            self.set_active(False)


        return redraw
