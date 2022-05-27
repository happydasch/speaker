import pathlib
import base64

from PIL import Image
from PIL.ImageColor import getcolor, getrgb
from PIL.ImageOps import grayscale


def image_tint(src, tint='#ffffff'):

    '''
    Tints a image

    src:
    https://stackoverflow.com/questions/29332424/changing-colour-of-an-image/29379704#29379704
    '''

    if src.mode not in ['RGB', 'RGBA']:
        raise TypeError('Unsupported source image mode: {}'.format(src.mode))
    tr, tg, tb = getrgb(tint)
    tl = getcolor(tint, "L")  # tint color's overall luminosity
    if not tl:
        tl = 1  # avoid division by zero
    tl = float(tl)  # compute luminosity preserving tint factors
    sr, sg, sb = map(lambda tv: tv/tl, (tr, tg, tb))
    # create look-up tables to map luminosity to adjusted tint
    # (using floating-point math only to compute table)
    luts = (tuple(map(lambda lr: int(lr*sr + 0.5), range(256))) +
            tuple(map(lambda lg: int(lg*sg + 0.5), range(256))) +
            tuple(map(lambda lb: int(lb*sb + 0.5), range(256))))
    l = grayscale(src)  # 8-bit luminosity version of whole image
    if Image.getmodebands(src.mode) < 4:
        merge_args = (src.mode, (l, l, l))  # for RGB verion of grayscale
    else:  # include copy of src image's alpha layer
        a = Image.new("L", src.size)
        a.putdata(src.getdata(3))
        merge_args = (src.mode, (l, l, l, a))  # for RGBA verion of grayscale
        luts += tuple(range(256))  # for 1:1 mapping of copied alpha values
    return Image.merge(*merge_args).point(luts)


def sum_pos(pos1, pos2):
    return [a+b for (a, b) in zip(pos1, pos2)]


def bytes_to_file(input_data, output_file):

    '''
    Saves bytes to a file.
    '''

    pathlib.Path(output_file.parent).mkdir(parents=True, exist_ok=True)

    with open(output_file, "wb") as file:
        file.write(input_data)


def default_album_art():

    '''
    Returns binary version of default album art.
    '''

    return base64.b64decode("""
iVBORw0KGgoAAAANSUhEUgAAAOYAAADmAQMAAAD7pGv4AAAABlBMVEX///8AAABVwtN+AAAChUlE
QVRYw6XZsW0jMRCFYRoXTMYKWIRClsXQ4WXX1lVwNbAQB5YXgiBpZ77gRNiAtZS5/HfJmTePrb3R
Luyb6F1toHe3Xnd+/G1R9/76/fNTtTj+vWr9uHXVxjHtqs3bb4XbALxv965wWw18sJbAcR+gwq2B
x33iFW4NvB5GyHFL4NtsA7glcDwNkeNWwONp6jluBbxexshwC+D7XAO4BXCcBslwc+BxmnyGmwOv
ZJSW3K0DNwV+oEyAIx0mu9kGbgY8i7/P3x/ATYCf5hnATYCjHOh8qw3cM/DEp9dvD+CegF9mGcA9
fQwO1TmNQYRJ/MVHt/XYTy8lml7o04XgUulcZoNLdHJ5L26NrW2VbLpo2rAPl4KhoDOMDIagyfC1
GPq2wmYaVKMpIN8vBkN9Z5oYTDGT6WkxtW2lxSJpRlPCvV0OpvJOGTAoISblx6J02ZI9pSiKJkF1
dASlWqfMG5SIk/JyUZpuyVqI3mgSzNeuoBTvlPGDJYAKhAncH+CN3g7cKzBwr8B/VPB8/GM99MXe
zzd6v/5/Viby0/CT9FvwG/Tb58rxqvOK9Wr3TvEu8w717mZkcFRxRHI0cyR0FHUEdvRm5HfWcMZx
tnKmc5Z0hnV2Zma3KrCisBqxkrEKsoKy+qJys+qzYrTatFK1yrVCtrqmMreqd0XgasKViKsYV0Cu
nlh5uWpzxedq0ZWmq1RXuK6OWVm7KndFbzfAToJdCDsYdj/onNh1sWNjt8dOkV0mO1R2t+iM2VWz
I2c3z06gXUQ7kIvJayvx2TW142q31k6vXWI7zIviZEvY2BW3o2433k6+TwF8grAoPreEq089fGLi
0xaf1PiUxydEF/Re2hvtG6k8p7n4F+LQAAAAAElFTkSuQmCC
""")
