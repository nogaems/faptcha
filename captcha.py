from hashlib import sha256
from random import uniform, randrange
import random
from os import path
from io import BytesIO
from math import sin, pi
from PIL import Image, ImageDraw, ImageFont
from importlib.util import find_spec
from collections import OrderedDict


class Captcha:
    storage = OrderedDict()

    def __init__(self, size=(150, 50), length=4, font_name='terminus.ttf', font_size=40,
                 color=(0, 0, 0, 255), bg_color=(255, 255, 255, 0), storage_size=2**20,
                 random_seed=None):
        if not isinstance(size, tuple):
            raise TypeError('\'size\' must be \'tuple\'')
        elif not len(size) == 2:
            raise TypeError(
                '\'size\' must be a tuple of two values ({} given)'.format(len(size)))
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
            spec = find_spec('faptcha')
            if not spec:
                # this package is not installed
                spec = __spec__
            d = '/'.join(spec.origin.split('/')[:-1]) + '/'
            font_name = d + 'terminus.ttf'
        if not path.exists(font_name):
            raise FileNotFoundError(
                '\'{}\' font file does not exist'.format(font_name))

        if not isinstance(font_size, int):
            raise TypeError('\'font_size\' must be \'int\'')

        self.font = ImageFont.truetype(font_name, font_size)

        self._validate_color(color)
        self._validate_color(bg_color)

        self.color = color
        self.bg_color = bg_color

        if not isinstance(storage_size, int) or storage_size <= 0:
            raise TypeError('\'storage_size\' must be a non-negative integer')
        self.storage_size = storage_size
        random.seed(random_seed)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               repr(self.__dict__))

    def get(self):
        code = sha256(random.random().hex().encode(
            'utf8')).hexdigest()[-self.length:]
        id = sha256(code.encode('utf8')).hexdigest()

        # If we're exeeding the maximum size of the storage, we got to manually
        # free some space for another entry. Generally space will be freed after
        # attempts to solve issued captchas (regardless of the result), and this
        # workaround only needs to be implemented because of possible DDOS
        # attacks on captcha service. I agree that this approach is pretty dumb
        # and straightforward, but after some research I believe that there's no
        # better way to do this. Even if I implement expiration mechanism, it
        # won't be possible to get rid of the limitation of the storage size
        # (without that limitation it's pretty simple to go OOM during DDOS).
        if len(self.storage) >= self.storage_size:
            # The method below is better than
            # self.storage.pop(list(self.storage)[0])
            # because it won't create a duplicate
            # of the storage.
            first_item_key = next(iter(self.storage))
            self.storage.move_to_end(first_item_key)
            self.storage.popitem()

        self.storage.update({id: code})

        base = Image.new('RGBA', self.size, self.bg_color)
        text = Image.new('RGBA', self.size)

        draw = ImageDraw.Draw(text)

        while True:
            text_w, text_h = draw.textsize(code, font=self.font)
            base_w, base_h = base.size
            if text_h >= base_h or text_w >= base_w:
                self.font = ImageFont.truetype(
                    self.font.path, self.font.size - 1)
            else:
                break

        draw.text(((base_w - text_w) / 2, (base_h - text_h) / 2), code,
                  font=self.font, fill=self.color)

        text = self._transform(text)
        out = Image.alpha_composite(base, text)
        out = self._noise(out)

        # for debug
        # out.show()
        # print({'id': id, 'code': code})

        f = BytesIO()
        out.save(f, 'PNG')
        raw = f.getvalue()

        return raw, id

    def _transform(self, img):
        ph = uniform(0, 1000)
        amp = uniform(1.0, 2.0)
        fr = uniform(pi / 2, pi)

        def deform(img, w, h):
            for y in range(h):
                for x in range(w):
                    new_y = int(y + sin(x / fr + ph) * amp - amp)
                    if 0 <= new_y < h:
                        pixel = img.getpixel((x, y))
                        img.putpixel((x, new_y), pixel)

        deform(img, self.size[0], self.size[1])
        img = img.rotate(90, expand=True)
        deform(img, img.size[0], img.size[1])
        img = img.rotate(270, expand=True)

        return img

    def _noise(self, img):
        draw = ImageDraw.Draw(img)
        w, h = img.size
        draw.line((randrange(0, w / 2), randrange(0, h / 2),
                   randrange(w / 2, w), randrange(h / 2, h)),
                  fill=self.color, width=3)
        draw.line((randrange(w / 2, w), randrange(0, h / 2),
                   randrange(0, w / 2), randrange(h / 2, h)),
                  fill=self.color, width=3)
        del draw
        return img

    def _validate_color(self, color):
        if not isinstance(color, tuple):
            raise TypeError('\'color\' must be \'tuple\'')
        elif not len(color) == 4:
            raise TypeError(
                '\'color\' must be a tuple of 4 values ({} given)'.format(len(size)))
        elif not isinstance(color[0], int):
            raise TypeError('\'red\' must be \'int\'')
        elif not isinstance(color[1], int):
            raise TypeError('\'green\' must be \'int\'')
        elif not isinstance(color[2], int):
            raise TypeError('\'blue\' must be \'int\'')
        elif not isinstance(color[3], int):
            raise TypeError('\'alpha\' must be \'int\'')
        elif not (0 <= color[0] <= 255):
            raise TypeError(
                '\'red\' value should be in the range from 0 to 255')
        elif not (0 <= color[1] <= 255):
            raise TypeError(
                '\'green\' value should be in the range from 0 to 255')
        elif not (0 <= color[2] <= 255):
            raise TypeError(
                '\'blue\' value should be in the range from 0 to 255')
        elif not (0 <= color[3] <= 255):
            raise TypeError(
                '\'alpha\' value should be in the range from 0 to 255')

    def check(self, id, code, delete=True):
        if id not in self.storage:
            return False
        result = True if self.storage[id] == code else False
        if delete:
            self.storage.pop(id)
        return result

    def is_issued(self, id):
        return id in self.storage

    def remove_from_storage(self, id):
        self.storage.pop(id) if id in self.storage else None
