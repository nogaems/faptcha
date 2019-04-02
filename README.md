# faptcha

Simple, lightweight and customizable CAPTCHA.

## Usage

```
from faptcha import captcha

c = captcha.Captcha()
img, id = c.get()
```

After that `img` gets serialized captcha image (of type `bytes`) which contains some random text. `id` stores the `sha256-hash` of captcha text.

For example:

>![faptcha](https://raw.githubusercontent.com/nogaems/faptcha/assets/default_sample.png)

To verify if the captcha text was recognized correctly:

```
c.check(id, key)
```

where `key` is the user-entered text of the captcha. If the captcha is recognized correctly, the function returns `True`, `False` otherwise.


`Captcha` class signature with default values:

```
Captcha(size=(150, 50), length=4, font_name='terminus.ttf', font_size=40, color=(0, 0, 0, 255)):
```

Alphabet (with default `terminus` font):

>![faptcha](https://raw.githubusercontent.com/nogaems/faptcha/assets/alphabet.png)
