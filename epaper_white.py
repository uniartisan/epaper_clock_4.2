# coding: utf-8

from PIL import Image, ImageDraw, ImageFont
from lib import epd4in2bc

epd = epd4in2bc.EPD()
epd.init()
epd.Clear()
epd.sleep()
print('Clear epaper successfully')