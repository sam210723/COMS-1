"""
lrit-img.py
https://github.com/sam210723/coms-1

Adds overlays and text to COMS-1 Meteorological Imager images.
"""

import argparse
from PIL import Image, ImageFont, ImageDraw

argparser = argparse.ArgumentParser(description="Adds overlays and text to COMS-1 Meteorological Imager images.")
argparser.add_argument("INPUT", action="store", help="Input BMP file")
argparser.add_argument('OUTPUT', action="store", help="Output BMP file")
argparser.add_argument('LEFT', action="store", help="Left text")
argparser.add_argument('RIGHT', action="store", help="Right text")
argparser.add_argument('-m', action="store_true", help="Enable map overlay")
argparser.add_argument('-f', action="store", help="Text fill colour", default="white")
argparser.add_argument('-s', action="store", help="Text font size", default="32")
args = argparser.parse_args()

sourceImage = Image.open(args.INPUT)
outputImage = Image.new(sourceImage.mode, (sourceImage.width, sourceImage.height + 50))
outputImage.paste(sourceImage, (0, 0))
draw = ImageDraw.Draw(outputImage)
font = ImageFont.truetype("Arial.ttf", int(args.s))

textL = args.LEFT
textR = args.RIGHT
textLs = draw.textsize(textL, font)
textRs = draw.textsize(textR, font)
draw.text((10, outputImage.height-textLs[1]-8), text=textL, font=font, fill=args.f)
draw.text(((outputImage.width-textRs[0]-10), outputImage.height-textRs[1]-14), text=textR, font=font, fill=args.f)
print("Left text: \"{0}\"\nRight text: \"{1}\"".format(textL, textR))

outputImage.save(args.OUTPUT)
print("Modified image saved to {0}".format(args.OUTPUT))
