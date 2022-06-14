import tkinter

from .display import Display

from PIL import ImageTk


class DisplayTK(Display):

    WIDTH = 240
    HEIGHT = 240

    def __init__(self, speaker):
        super().__init__(speaker)
        self._tk = tkinter.Tk()
        self._tk.geometry(f'{self.WIDTH}x{self.HEIGHT}')
        self._tk.resizable(False, False)
        self._tk.title('Speaker')

    def redraw(self):
        imagetk = ImageTk.PhotoImage(self._image)
        label_image = tkinter.Label(self._root, image=imagetk)
        label_image.place(x=0, y=0, width=self.WIDTH, height=self.HEIGHT)
        self._tk.update()
