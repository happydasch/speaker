from .scene import Scene


class SceneOutro(Scene):

    def __init__(self, display, **kwargs):
        super().__init__(display, overlay=False, **kwargs)
