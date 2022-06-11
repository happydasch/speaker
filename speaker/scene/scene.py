from PIL import Image


class Scene:

    '''
    Represents a scene to be drawn
    '''

    def __init__(self, display, active=True, overlay=True, background='#000'):
        self._image = Image.new('RGBA', display.get_size(), background)
        self._background = background
        self._timer = 0
        self._active = active
        self._display = display
        self._overlay = overlay
        print(f'creating scene {self}')

    def get_display(self):
        return self._display

    def get_speaker(self):
        return self._display.get_speaker()

    def get_image(self):
        return self._image

    def is_active(self):
        return self._active

    def set_active(self, active=True):
        self._active = active

    def use_overlay(self):
        return self._overlay

    def update(self):
        return False
