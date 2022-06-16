import pathlib
import base64
import math

from PIL import Image, ImageFont
from PIL.ImageColor import getcolor, getrgb
from PIL.ImageOps import grayscale


def text_in_rect(canvas, text, font, rect, line_spacing=1.1, fill=None):
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    # Given a rectangle, reflow and scale text to fit, centred
    while font.size > 0:
        line_height = int(font.size * line_spacing)
        max_lines = math.floor(height / line_height)
        lines = []

        # Determine if text can fit at current scale.
        words = text.split(" ")

        while len(lines) < max_lines and len(words) > 0:
            line = []
            while len(words) > 0 and font.getsize(" ".join(line + [words[0]]))[0] <= width:
                line.append(words.pop(0))
            lines.append(" ".join(line))

        if(len(lines)) <= max_lines and len(words) == 0:
            # Solution is found, render the text.
            y = int(rect[1] + (height / 2) - (len(lines) * line_height / 2) - (line_height - font.size) / 2)
            bounds = [rect[2], y, rect[0], y + len(lines) * line_height]
            for line in lines:
                line_width = font.getsize(line)[0]
                x = int(rect[0] + (width / 2) - (line_width / 2))
                bounds[0] = min(bounds[0], x)
                bounds[2] = max(bounds[2], x + line_width)
                canvas.text((x, y), line, font=font, fill=fill)
                y += line_height
            return tuple(bounds)

        font = ImageFont.truetype(font.path, font.size - 1)


def draw_progress_bar(canvas, progress, max_progress, rect, colour):
    unfilled_opacity = 0.5  # Factor to scale down colour/opacity of unfilled bar.

    # Calculate bar widths.
    rect = tuple(rect)  # Space which bar occupies.
    full_width = rect[2] - rect[0]
    bar_width = int((progress / max_progress) * full_width)
    progress_rect = (rect[0], rect[1], rect[0] + bar_width, rect[3])

    # Knock back unfilled part of bar.
    unfilled_colour = tuple(int(c * unfilled_opacity) for c in colour)

    # Draw bars.
    canvas.rectangle(rect, unfilled_colour)
    canvas.rectangle(progress_rect, colour)


def image_tint(src, tint='#fff'):

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


def translate(value, left_min, left_max, right_min, right_max):
    '''
    https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
    '''
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (float)
    scaled_value = float(value - left_min) / float(left_span)

    # Convert the 0-1 range into a value in the right range.
    return right_min + (scaled_value * right_span)
