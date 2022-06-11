from PIL import Image


class Display:

    '''
    Represents a display
    '''

    WIDTH = 0
    HEIGHT = 0

    def __init__(self, speaker):
        self._image = Image.new('RGBA', self.get_size(), (255, 255, 255))
        self._speaker = speaker
        self._brightness = 0
        self._scene = None
        self._overlay = None

    def get_speaker(self):
        return self._speaker

    def get_size(self):
        return (self.WIDTH, self.HEIGHT)

    def get_scene(self):
        return self._scene

    def set_scene(self, scene, *args, **kargs):
        self._scene = scene(self, *args, **kargs) if scene else None
        return self._scene

    def get_overlay(self):
        return self._overlay

    def set_overlay(self, overlay, *args, **kargs):
        self._overlay = overlay(self, *args, **kargs) if overlay else None

    def get_brightness(self):
        return self._brightness

    def set_brightness(self, brightness):
        self._brightness = brightness

    def update(self):
        scene_update = False
        overlay_update = False
        scene = self.get_scene()
        overlay = self.get_overlay()
        if overlay and scene and scene.use_overlay():
            if overlay.update():
                overlay_update = True
            if not overlay.is_active():
                self.set_overlay(None)
                overlay = None
                overlay_update = True
        if scene:
            if overlay_update or scene.update():
                scene_image = scene.get_image()
                if scene_image:
                    self._image = scene_image
                scene_update = True
        if (overlay and scene and scene.use_overlay()
                and (overlay_update or scene_update)):
            overlay_image = overlay.get_image()
            overlay_opacity = overlay.get_opacity()
            self._image = Image.blend(
                self._image, overlay_image, overlay_opacity)
        return scene_update or overlay_update

    def start(self):
        return

    def stop(self):
        return

    def redraw(self):
        return
