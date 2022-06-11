import time
from fonts.ttf import RobotoMedium as UserFont

from PIL import Image, ImageDraw, ImageFont

from .scene import Scene
from ..utils import text_in_rect


class SceneOutro(Scene):

    def __init__(self, display, **kwargs):
        kwargs |= {'overlay': False, 'active': True}
        super().__init__(display, **kwargs)
        self._duration = 3  # length of outro duration
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

        # update image
        if current_duration <= self._duration:
            opacity = 1 - round(current_duration / self._duration, 2)
            if opacity != self._opacity:
                print(f'new opacity: {opacity} - was: {self._opacity}')
                self._image = Image.blend(
                    self._image_background,
                    self._image_text,
                    opacity)
                self._opacity = opacity
                redraw = True
        else:
            # disable animation after n seconds
            self.set_active(False)
            self.get_speaker().set_active(False)

        # redraw frame if needed
        return redraw
