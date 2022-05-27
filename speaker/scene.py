import os

from PIL import Image


class Scene:

    '''
    Represents a scene to be drawn
    '''

    image = None

    def __init__(self, display, active=False):
        self.image = Image.new(
            'RGBA', display.get_size(), (255, 255, 255, 255))
        self._draw = True
        self._active = active
        self._display = display
        print(f'creating scene {self}')

    def get_display(self):
        return self._display

    def is_active(self):
        return self._active

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

    def update(self):
        return True


class SceneOutro(Scene):

    def update(self):
        return True


class SceneClient(Scene):

    def __init__(self, display, **kwargs):
        super().__init__(display, **kwargs)
        self._image_dir = os.path.join(os.path.dirname(__file__), 'images')
        self._buttons = Image\
            .open(os.path.join(self._image_dir, 'buttons_32.png'))\
            .convert('RGBA')
