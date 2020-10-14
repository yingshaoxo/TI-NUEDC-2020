from __future__ import print_function
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np
import json

def char_to_pixels(text, path='arialbd.ttf', fontsize=14):
    """
    Based on https://stackoverflow.com/a/27753869/190597 (jsheperd)
    """
    font = ImageFont.truetype(path, fontsize) 
    w, h = font.getsize(text)  
    h *= 2
    image = Image.new('L', (w, h), 1)  
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font) 
    arr = np.asarray(image)
    arr = np.where(arr, 0, 1)
    arr = arr[(arr != 0).any(axis=1)]
    return arr.tolist()

def display(arr):
    result = np.where(arr, '#', ' ')
    print('\n'.join([''.join(row) for row in result]))

string = """
距离 形状 尺寸 边长 品种 直径 足球 排球 篮球 圆 正三角形 正方形 : ：
"""
the_dict = dict()
for c in list(set(string.strip())):
    arr = char_to_pixels(
        c, 
        path='chinese.ttf', 
        fontsize=20)
    the_dict[c] = arr
    display(arr)
    #print(arr)
    print()

text = json.dumps(the_dict)
with open("font_pixels.json", "w") as f:
    f.write(text)