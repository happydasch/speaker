from PIL import ImageDraw

from .scene import Scene


class SceneDefault(Scene):

    '''
    Default scene

    This scene shows all available clients and some help text.
    This scene will be used if there is no active client.
    '''

    def __init__(self, display, **kwargs):
        super().__init__(display, background='#000', active=False, **kwargs)
        self._draw_default(self._image)

    def _draw_default(self, image):
        image_draw = ImageDraw.Draw(image, 'RGBA')
        image_draw.text((28, 36), "nice Car", fill='#fff')
        image_draw.line((1, 30), '#fff')
