import os

from PIL import Image


class ImageMap:

    def __init__(self, image):
        self._image = Image.open(image)

    def get_image(self):
        return self._image

    def get(self, idx):
        height = self._image.size[1]
        cropped = self._image.crop(
            (height * idx, 0, height * idx + height, height))
        return cropped

    def new(self, color='#fff'):
        size = self._image.size[1]
        new = Image.new('RGBA', (size, size), color)
        return new


class Icon:

    def __init__(self, idx=None):
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        icons = os.path.join(image_dir, 'icons_256.png')
        image_map = ImageMap(icons)
        if idx:
            self._image = image_map.get(idx)
        else:
            self._image = image_map.new()

    def get_image(self):
        return self._image


class IconSnapcast(Icon):

    def __init__(self):
        super().__init__(0)


class IconBluetooth(Icon):

    def __init__(self):
        super().__init__(1)


class IconAirplay(Icon):

    def __init__(self):
        super().__init__(2)
