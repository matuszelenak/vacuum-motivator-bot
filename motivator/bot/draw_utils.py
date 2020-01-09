import math
import os
from typing import List

from PIL import ImageFont, ImageDraw, Image
from django.conf import settings


def rotate_point(point: tuple, pivot: tuple, angle: float):
    s = math.sin(angle)
    c = math.cos(angle)

    x, y = point[0], point[1]

    x -= pivot[0]
    y -= pivot[1]

    xnew = x * c - y * s
    ynew = x * s + y * c

    return xnew + pivot[0], ynew + pivot[1]


def is_point_inside_polygon(point: tuple, polygon: List[tuple]):
    x, y = point[0], point[1]

    inside = False
    for (a_x, a_y), (b_x, b_y) in zip(polygon, polygon[1:] + [polygon[0]]):
        intersect = ((b_y > y) != (a_y > y)) and (x < (a_x - b_x) * (y - b_y) / (a_y - b_y) + b_x)
        if intersect:
            inside = not inside

    return inside


def get_text_hitbox(text, origin_position, angle, bounding_box, font_size):
    font = ImageFont.truetype('SourceSansPro-Bold.ttf', font_size)
    draw_txt = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    width, height = draw_txt.textsize(text, font)
    text_box = [(0, 0), (width, 0), (width, height), (0, height)]
    text_box = [(x + origin_position[0], y + origin_position[1] - height // 2) for x, y in text_box]
    text_box = [rotate_point(x, origin_position, angle) for x in text_box]
    return text_box if all(is_point_inside_polygon(p, bounding_box) for p in text_box) else None


def get_fitting_text_size(text, origin_position, angle, bounding_box):
    prev_size, hitbox = 1, get_text_hitbox(text, origin_position, angle, bounding_box, 1)
    size = 2
    while True:
        new_hitbox = get_text_hitbox(text, origin_position, angle, bounding_box, size + 1)
        if not new_hitbox:
            return size, hitbox
        hitbox = new_hitbox
        size += 1


def overlay_text(image, text, origin, angle, bound_box):
    angle_radians = angle * math.pi / 180

    font_size, hitbox = get_fitting_text_size(text, origin, angle_radians, bound_box)
    font = ImageFont.truetype(os.path.join(settings.BASE_DIR, 'SourceSansPro-Bold.ttf'), font_size)
    w, h = ImageDraw.Draw(image).textsize(text, font)
    m = max(w, h)
    txt = Image.new('RGBA', (m * 2, m * 2))
    ImageDraw.Draw(txt).text((m, m - h // 2), text,  font=font)
    rotated = txt.rotate(-angle)

    image.paste(rotated, (origin[0] - m, origin[1] - m), rotated)
