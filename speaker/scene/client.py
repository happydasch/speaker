import os

from PIL import Image

from .scene import Scene


class SceneClient(Scene):

    def __init__(self, display, **kwargs):
        super().__init__(display, **kwargs)
        self._image_dir = os.path.join(
            os.path.dirname(__file__), '..', 'images')
        self._buttons = Image\
            .open(os.path.join(self._image_dir, 'buttons_32.png'))\
            .convert('RGBA')

    def update(self):
        if not self.get_speaker().client:
            self.set_active(False)
