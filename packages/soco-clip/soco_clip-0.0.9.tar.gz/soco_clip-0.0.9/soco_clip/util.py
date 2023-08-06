import io
import base64
from PIL import ImageDraw, Image

def cropbox(xmin, ymin, xmax, ymax, img_size, ratio=1.5, make_square=False):
    if xmin < 0 or ymin <0 or xmax < 0 or ymax < 0:
        raise Exception
    w, h = img_size
    if xmin > w or ymin > h or xmax > w or ymax > h:
        raise Exception

    xc = xmin + (xmax - xmin) / 2
    yc = ymin + (ymax - ymin) / 2
    w = xmax - xmin
    h = ymax - ymin
    nw = w * ratio
    nh = h * ratio

    if make_square:
        if nw > nh:
            nh = nw
        else:
            nw = nh

    nxmin = max(xc - (nw / 2), 0)
    nymin = max(yc - (nh / 2), 0)

    nxmax = min(xc + (nw / 2), img_size[0])
    nymax = min(yc + (nh / 2), img_size[1])

    return nxmin, nymin, nxmax, nymax


def image_to_base64(img):
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='JPEG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str

def base64_to_image(base64_str):
    return Image.open(io.BytesIO(base64.b64decode(base64_str)))

def draw_bounding_box_on_image(image, xmin, ymin, xmax, ymax,
                               color='red',
                               text='',
                               thickness=4):
    draw = ImageDraw.Draw(image)
    draw.rectangle([(xmin, ymin), (xmax, ymax)], outline=color, width=thickness)
    draw.text((xmin, ymin), text)
    return image
