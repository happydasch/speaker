import os
import time

from PIL import Image

from .scene import Scene
from ..draw import ImageMap


class SceneClient(Scene):

    def __init__(self, display, **kwargs):
        super().__init__(display, **kwargs)
        image_dir = os.path.join(
            os.path.dirname(__file__), '..', 'images')
        file = os.path.join(image_dir, 'buttons_32.png')
        self._buttons_map = ImageMap(file)
        self._image_back = Image.new('RGBA', display.get_size())
        self._image_text = Image.new('RGBA', display.get_size())
        self._image_controls = Image.new('RGBA', display.get_size())

    def _draw_controls(self, image):
        pass

    def _draw_text(self, image):
        pass

    def _draw_back(self, image):
        pass

    def update(self):
        if not self.get_speaker().client:
            self.set_active(False)

        if self._timer == 0:
            icon = self.get_client().ICON().get_image().resize((32, 32))
            self._image = Image.blend(self._image_back, self._image_controls, 0.5)
            self._image = Image.blend(self._image, self._image_text, 0.5)
            self._image.alpha_composite(icon, (5, 5))
            self._timer = time.time()
            return True
        return False
