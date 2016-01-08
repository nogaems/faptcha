# faptcha

Simple and lightweight CAPTCHA with the ability to configure.

## Usage

```
from faptcha import captcha

c = captcha.Captcha()
img, id = c.get()
```

In this case variable "img" will get a value of serialized captcha 
image (of type "bytes) which contains a random text. In variable 
"id" will be stored sha256-hash of captcha text.

For example:

>![faptcha](https://raw.githubusercontent.com/nogaems/faptcha/master/default_sample.png)

`Captcha` class signature with default values:

```
Captcha(size=(150, 50), length=4, font_name='terminus.ttf', font_size=40, color=(0, 0, 0, 255)):
```

