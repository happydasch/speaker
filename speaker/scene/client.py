import os
import time
import io

from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..client import ClientInfo
from ..draw import ImageMap
from ..utils import text_in_rect, draw_progress_bar
from .scene import Scene


class SceneClient(Scene):

    UPDATE_INTERVAL = 0.5

    def __init__(self, display, **kwargs):
        super().__init__(display, **kwargs)
        image_dir = os.path.join(
            os.path.dirname(__file__), '..', 'images')
        file = os.path.join(image_dir, 'buttons_32.png')
        self._blur = False
        self._font = ImageFont.truetype(UserFont, 20)
        self._font_big = ImageFont.truetype(UserFont, 42)
        self._buttons_map = ImageMap(file)
        self._image_back = Image.new('RGBA', display.get_size())
        self._image_controls = Image.new('RGBA', display.get_size())
        self._image_text = Image.new('RGBA', display.get_size())
        self._image_front = Image.new('RGBA', display.get_size())
        self._info_back = {}
        self._info_controls = {}
        self._info_text = {}
        self._info_front = {}

    def _draw(self):
        res = (self._draw_back(), self._draw_controls(),
               self._draw_text(), self._draw_front())
        return any(res)

    def _draw_back(self):
        client = self.get_client()
        if not client:
            return
        info = client.get_info()

        # default image if no album art
        image_draw = ImageDraw.Draw(self._image_back)
        image_draw.rectangle((0, 0, * self._image_back.size), '#000')
        if info.album_art:
            image = Image.open(io.BytesIO(info.album_art))
            image = image.resize(self._image_back.size).convert('RGBA')
            if self._blur:
                image = image.filter(ImageFilter.GaussianBlur(radius=5))
            image.putalpha(96)
            self._image_back.alpha_composite(image)
        return True

    def _draw_controls(self):
        client = self.get_client()
        if not client:
            return
        info = client.get_info()
        # check for current controls change
        if info.status == ClientInfo.STATUS_PLAYING:
            index_image = 'image_playing'
        else:
            index_image = 'image_stopped'
        if self._info_controls.get('current') == index_image:
            return False
        #

        if index_image in self._info_controls:
            image = self._info_controls[index_image]
        else:
            iw, ih = self._image_controls.size
            ibw = int(iw * 0.12)
            ibh = int(ih * 0.12)
            ibs = min(ibw, ibh)
            icons, xy = [], []
            # vol down
            icons.append(
                self._buttons_map.get(3).resize((ibs, ibs)))
            xy.append((
                int(ibw * 0.25),
                int(ih * 0.25 - ibh * 0.5)))
            # vol up
            icons.append(
                self._buttons_map.get(4).resize((ibs, ibs)))
            xy.append((
                int(iw - ibw * 1.25),
                int(ih * 0.25 - ibh * 0.5)))
            # play / pause button
            icons.append(
                self._buttons_map
                .get(2 if info.status == ClientInfo.STATUS_PLAYING else 1)
                .resize((ibs, ibs)))
            xy.append(
                (int(ibw * 0.25),
                 int(ih * 0.75 - ibh * 0.5)))
            # next
            icons.append(
                self._buttons_map.get(6).resize((ibs, ibs)))
            xy.append(
                (int(iw - ibw * 1.25),
                 int(ih * 0.75 - ibh * 0.5)))
            # create image with controls
            image = Image.new('RGBA', self._image_controls.size, (0, 0, 0, 0))
            for icon, pos in zip(icons, xy):
                olddata = icon.getdata()
                newdata = []
                for rgba in olddata:
                    newdata.append(
                        (rgba[0], rgba[1], rgba[2],
                         max(0, rgba[3] - int(255 * 0.65))))
                icon.putdata(newdata)
                image.alpha_composite(icon, pos)
        # store and set current image
        self._image_controls = image
        self._info_controls[index_image] = image
        self._info_controls['current'] = index_image
        return True

    def _draw_text(self):
        client = self.get_client()
        if not client:
            return
        info = client.get_info()
        redraw = False

        # check if a redraw is needed
        if (self._info_text.get('volume') != info.volume
                or self._info_text.get('position') != info.position
                or self._info_text.get('duration') != info.duration
                or self._info_text.get('artist') != info.artist
                or self._info_text.get('title') != info.title
                or self._info_text.get('album') != info.album):
            redraw = True

        # return if no redraw is required
        if not redraw:
            return False

        # redraw image
        self._image_text = Image.new('RGBA', self._image_text.size)
        image_draw = ImageDraw.Draw(self._image_text)
        iw, ih = self._image_text.size
        ib = int(min(iw, ih) * 0.02)
        ics = int(min(iw, ih) * 0.1)

        # draw progress
        position = info.position
        duration = info.duration
        if position == -1 or duration == -1:
            position = 0
            duration = 1
        pos_progress = (ib + 2 * ics, ih - 8 * ib, iw - ib - 2 * ics, ih - 6 * ib)
        draw_progress_bar(
            image_draw, position, duration, pos_progress, (255, 255, 255))
        remaining_min = int((duration - position) / 60)
        remaining_sec = int((duration - position) % 60)
        pos_remaining = (iw - 2 * ics + ib, ih - 2 * ics - 2 * ib, iw - ib, ih)
        text_in_rect(
            image_draw,
            f'-{remaining_min}:{remaining_sec:02}',
            self._font,
            pos_remaining,
            fill='#fff')
        self._info_text['position'] = position
        self._info_text['duration'] = duration

        # Artist
        box = text_in_rect(image_draw, info.artist, self._font, (ib, ics, iw - ib, int(2 * ics)))
        self._info_text['artist'] = info.artist

        # Album
        text_in_rect(image_draw, info.album, self._font, (ics, box[3], iw - ics, int(1.4 * ics + box[3])))
        self._info_text['album'] = info.album

        # Song title
        text_in_rect(image_draw, info.title, self._font_big, (ib, int(3.5 * ics), iw - ib, 8 * ics))
        self._info_text['title'] = info.title

        # draw volume
        if info.volume:
            volume = max(1, info.volume)
            pos_vol = (
                ib, 3 * ib, int(((iw - 2 * ib) / 100) * volume), 4 * ib)
            image_draw.rounded_rectangle(xy=pos_vol, radius=ib, fill='#fffa')
            self._info_text['volume'] = volume

        return True

    def _draw_front(self):
        client = self.get_client()
        if not client:
            return
        redraw = False
        iw, ih = self._image_front.size
        ib = int(min(iw, ih) * 0.02)
        ics = int(min(iw, ih) * 0.15)
        icon = self.get_client().ICON().get_image().resize((ics, ics))
        self._image_front.alpha_composite(icon, (ib, ih - 2 * ib - ics))
        return redraw

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
            self._image = Image.alpha_composite(
                self._image, self._image_front)
            self._timer = current_time
            return True
        return False
