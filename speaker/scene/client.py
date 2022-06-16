import os
import time

from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..client import ClientInfo
from .scene import Scene
from ..draw import ImageMap


class SceneClient(Scene):

    UPDATE_INTERVAL = 0.5

    def __init__(self, display, **kwargs):
        super().__init__(display, **kwargs)
        image_dir = os.path.join(
            os.path.dirname(__file__), '..', 'images')
        file = os.path.join(image_dir, 'buttons_32.png')
        self._blur = True
        self._font = ImageFont.truetype(UserFont, 20)
        self._font_big = ImageFont.truetype(UserFont, 42)
        self._buttons_map = ImageMap(file)
        self._image_back = Image.new('RGBA', display.get_size())
        self._image_controls = Image.new('RGBA', display.get_size())
        self._image_text = Image.new('RGBA', display.get_size())
        self._info_back = {}
        self._info_controls = {}
        self._info_text = {}

    def _draw(self):
        res = (self._draw_back(), self._draw_controls(), self._draw_text())
        return any(res)

    def _draw_text(self):
        icon = self.get_client().ICON().get_image().resize((32, 32))
        self._image_text.alpha_composite(icon, (5, 5))
        return True

    def _draw_back(self):
        client = self.get_client()
        if not client:
            return False
        info = client.get_info()
        image_draw = ImageDraw.Draw(self._image_back)
        image_draw.rectangle((0, 0, * self._image_back.size), '#000')
        if info.album_art:
            print(info.album_art)
            #image = Image.frombytes('RGBA', data=info.album_art, size=(250,250))
        return True

    def _draw_controls(self):
        client = self.get_client()
        if not client:
            return False
        info = client.get_info()
        if info.status == ClientInfo.STATUS_PLAYING:
            index_image = 'image_playing'
        else:
            index_image = 'image_stopped'
        if self._info_controls.get('current') == index_image:
            return False

        image = None
        iw, ih = self._image_controls.size
        ibw = int(iw * 0.12)
        ibh = int(ih * 0.12)
        ibs = min(ibw, ibh)

        if index_image in self._info_controls:
            image = self._info_controls[index_image]
        else:
            icon, xy = [], []
            # play / pause button
            icon.append(self._buttons_map
                        .get(2 if info.status == ClientInfo.STATUS_PLAYING
                             else 1)
                        .resize((ibs, ibs)))
            xy.append((
                int(ibw * 0.5),
                int(ih * 0.25 - ibh * 0.5)))
            # next
            icon.append(
                self._buttons_map.get(6).resize((ibs, ibs)))
            xy.append((
                int(iw - ibw * 1.5),
                int(ih * 0.25 - ibh * 0.5)))
            # vol down
            icon.append(
                self._buttons_map.get(3).resize((ibs, ibs)))
            xy.append(
                (int(ibw * 0.5),
                 int(ih * 0.75 - ibh * 0.5)))
            # vol up
            icon.append(
                self._buttons_map.get(4).resize((ibs, ibs)))
            xy.append(
                (int(iw - ibw * 1.5),
                 int(ih * 0.75 - ibh * 0.5)))
            image = Image.new('RGBA', self._image_controls.size, (0, 0, 0, 0))
            for i, pos in zip(icon, xy):
                i.putalpha(96)
                image.alpha_composite(i, pos)

        self._image_controls = image
        self._info_controls[index_image] = image
        self._info_controls['current'] = index_image

        return True

    def update(self):
        current_time = time.time()
        current_duration = current_time - self._timer
        redraw = False

        if not self.get_client():
            self.set_active(False)
            return False

        redraw = self._draw()
        if redraw or current_duration <= self.UPDATE_INTERVAL:
            self._image = Image.alpha_composite(
                self._image_back, self._image_controls)
            self._image = Image.alpha_composite(
                self._image, self._image_text)
            self._timer = current_time
            return True
        return False
