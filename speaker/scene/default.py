import time

from fonts.ttf import RobotoMedium as UserFont

from PIL import ImageDraw
from PIL import ImageFont

from .scene import Scene
from ..utils import text_in_rect


class SceneDefault(Scene):

    '''
    Default scene

    This scene shows all available clients and some help text.
    This scene will be used if there is no active client.
    '''

    WAKE_UP_TIME = 32
    WAKE_UP_DURATION = 8
    ICON_FACTOR = 0.65

    def __init__(self, display, **kwargs):
        kwargs |= {'active': False}
        super().__init__(display, **kwargs)
        self._brightness = self.get_speaker().MAX_BRIGHTNESS
        self._font_time = ImageFont.truetype(UserFont, 64)
        self._font_text = ImageFont.truetype(UserFont, 20)
        self._last_time = 0
        self._brightness = 0

    def _draw_default(self, image):
        iw, ih = image.size
        # prepare image to draw
        image_draw = ImageDraw.Draw(image, 'RGBA')
        image_draw.rectangle(((0, 0), (iw, ih)), '#000')
        # calc dimensions
        ib = int((iw+ih)/75)
        rect_time_big = (ib, ib, iw-(iw/8)+ib, (ih/2))
        rect_time_small = (((iw/8)*7)-(ib*2), ib, iw-(ib*2), (ih/2))
        rect_text = (ib, (ih/2), iw-ib, (ih/3)*2)
        # client icon dimensions
        cw = int(iw/len(self.get_speaker().get_clients()))
        ch = int(ih/3)
        csw, csh = int(cw*self.ICON_FACTOR), int(ch*self.ICON_FACTOR)
        ics = min(csw, csh)
        cdw, cdh = int((cw-ics)/2), int((ch-ics)/2)
        # draw scene
        text_in_rect(
            canvas=image_draw,
            text=time.strftime('%H:%M', time.localtime()),
            font=self._font_time, rect=rect_time_big)
        text_in_rect(
            canvas=image_draw,
            text=time.strftime('%S', time.localtime()),
            font=self._font_time, rect=rect_time_small)
        text_in_rect(
            canvas=image_draw, text="Connect to speaker by:",
            font=self._font_text, rect=rect_text)
        image_draw.line(((ib, (ih/3)*2), (iw-ib, (ih/3)*2)), '#fff', 1)
        for i, c in enumerate(self.get_speaker().get_clients()):
            icon = c.ICON().get_image().resize((ics, ics))
            image.alpha_composite(icon, (cw*i+cdw, (ch*2)+cdh))

    def update(self):
        cur_time = time.time()

        if self.get_speaker().is_active():
            self._timer = cur_time
        elif cur_time - self._timer > self.WAKE_UP_TIME:
            self._timer = cur_time
        elif cur_time - self._timer > self.WAKE_UP_DURATION:
            brightness = self.get_display().get_brightness()
            new_brightness = brightness
            if not self.get_speaker().is_anim():
                if new_brightness > 0:
                    new_brightness -= 1
                else:
                    new_brightness = 0
                if brightness != new_brightness:
                    self.get_display().set_brightness(new_brightness)
        elif cur_time - self._timer < self.WAKE_UP_DURATION:
            brightness = self.get_display().get_brightness()
            new_brightness = brightness
            if not self.get_speaker().is_anim():
                if new_brightness < 10:
                    new_brightness += 1
                elif new_brightness > 10:
                    new_brightness -= 1
                if brightness != new_brightness:
                    self.get_display().set_brightness(new_brightness)

        # redraw only once a second
        if int(self._last_time) != int(cur_time):
            self._draw_default(self._image)
            self._last_time = cur_time
            return True
        return False
