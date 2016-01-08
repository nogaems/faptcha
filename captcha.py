from hashlib import sha256
from random import random, uniform, randrange
from os import path
from io import BytesIO
from math import sin, pi
from PIL import Image, ImageDraw, ImageFont
from importlib.util import find_spec


class Captcha:
    storage = {}

    def __init__(self, size=(150, 50), length=4, font_name='terminus.ttf', font_size=40, color=(0, 0, 0, 255)):
        if not isinstance(size, tuple):
            raise TypeError('\'size\' must be \'tuple\'')
        elif not len(size) == 2:
            raise TypeError('\'size\' must be a tuple of two values ({} given)'.format(len(size)))
        elif not isinstance(size[0], int):
            raise TypeError('\'width\' must be \'int\'')
        elif not isinstance(size[1], int):
            raise TypeError('\'height\' must be \'int\'')
        else:
            self.size = size

        if not isinstance(length, int):
            raise TypeError('\'length\' must be \'int\'')
        elif length > 64:
            raise ValueError('length must be <= 64.')
        else:
            self.length = length

        if not isinstance(font_name, str):
            raise TypeError('\'font_name\' must be \'str\'')
        if font_name == 'terminus.ttf':
            if __name__ == '__main__':
                d = ''
            else:
                d = '/'.join(find_spec('faptcha').origin.split('/')[:-1]) + '/'
            font_name = d + 'terminus.ttf'
        if not path.exists(font_name):
            raise FileNotFoundError('\'{}\' font file does not exist'.format(font_name))

        if not isinstance(font_size, int):
            raise TypeError('\'font_size\' must be \'int\'')

        self.font = ImageFont.truetype(font_name, font_size)

        if not isinstance(color, tuple):
            raise TypeError('\'color\' must be \'tuple\'')
        elif not len(color) == 4:
            raise TypeError('\'color\' must be a tuple of 4 values ({} given)'.format(len(size)))
        elif not isinstance(color[0], int):
            raise TypeError('\'red\' must be \'int\'')
        elif not isinstance(color[1], int):
            raise TypeError('\'green\' must be \'int\'')
        elif not isinstance(color[2], int):
            raise TypeError('\'blue\' must be \'int\'')
        elif not isinstance(color[3], int):
            raise TypeError('\'alpha\' must be \'int\'')
        elif not (0 <= color[0] <= 255):
            raise TypeError('\'red\' value should be in the range from 0 to 255')
        elif not (0 <= color[1] <= 255):
            raise TypeError('\'green\' value should be in the range from 0 to 255')
        elif not (0 <= color[2] <= 255):
            raise TypeError('\'blue\' value should be in the range from 0 to 255')
        elif not (0 <= color[3] <= 255):
            raise TypeError('\'alpha\' value should be in the range from 0 to 255')
        else:
            self.color = color

    def get(self):
        key = sha256(random().hex().encode('utf8')).hexdigest()[-self.length:]
        id = sha256(key.encode('utf8')).hexdigest()
        self.storage.update({id: key})

        base = Image.new('RGBA', self.size, (255, 255, 255, 0))
        text = Image.new('RGBA', self.size)

        draw = ImageDraw.Draw(text)

        while True:
            text_w, text_h = draw.textsize(key, font=self.font)
            base_w, base_h = base.size
            if text_h >= base_h or text_w >= base_w:
                self.font = ImageFont.truetype(self.font.path, self.font.size - 1)
            else:
                break

        draw.text(((base_w - text_w) / 2, (base_h - text_h) / 2), key,
                  font=self.font, fill=self.color)

        text = self._transform(text)
        out = Image.alpha_composite(base, text)
        out = self._noise(out)

        # for debug
        out.show()
        print(key)

        f = BytesIO()
        out.save(f, 'PNG')
        raw = f.getvalue()

        return raw, id

    def _transform(self, img):
        ph = uniform(0, 1000)
        amp = uniform(1.0, 2.0)
        fr = uniform(pi/2, pi)

        def deform(pixel_map, w, h):
            for y in range(h):
                for x in range(w):
                    new_y = int(y + sin(x / fr + ph) * amp - amp)
                    if 0 <= new_y < h:
                        pixel_map[x, new_y] = pixel_map[x, y]

        pixel_map = img.load()
        deform(pixel_map, self.size[0], self.size[1])
        img = img.rotate(90)
        pixel_map = img.load()
        deform(pixel_map, self.size[1], self.size[0])
        img = img.rotate(270)

        return img

    def _noise(self, img):
        draw = ImageDraw.Draw(img)
        w, h = img.size
        draw.line((randrange(0, w/2), randrange(0, h/2),
                   randrange(w/2, w), randrange(h/2, h)),
                  fill=self.color, width=3)
        draw.line((randrange(w/2, w), randrange(0, h/2),
                   randrange(0, w/2), randrange(h/2, h)),
                  fill=self.color, width=3)
        del draw
        return img

    def check(self, id, key):
        if self.storage[id] == key:
            self.storage.pop(id)
            return True
        else:
            return False

c = Captcha()
c.get()
