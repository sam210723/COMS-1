"""
overlay.py
https://github.com/sam210723/COMS-1

Adds overlays and text to COMS-1 Meteorological Imager images.
"""

import argparse
from PIL import Image, ImageDraw

argparser = argparse.ArgumentParser(description="Adds overlays and text to COMS-1 Meteorological Imager images.")
argparser.add_argument("INPUT", action="store", help="LRIT file to process")
argparser.add_argument("-c", action="store_true", help="Enable coastline overlay", default=False)
argparser.add_argument("-tl", action="store", help="Left text value", default=None)
argparser.add_argument("-tr", action="store", help="Right text value", default=None)
argparser.add_argument("-tc", action="store", help="Text colour", default="white")
args = argparser.parse_args()

def init():
    # Print arguments
    if args.tl != None:
        print("LEFT TEXT:   \"{}\"".format(args.tl))
    if args.tr != None:
        print("RIGHT TEXT:  \"{}\"".format(args.tr))

    # Load input image
    sourceImage = Image.open(args.INPUT)
    sourceWidth = sourceImage.width
    sourceHeight = sourceImage.height
    outputImage = Image.new("RGB", (sourceWidth, sourceHeight))
    outputImage.paste(sourceImage, (0, 0))
    draw = ImageDraw.Draw(outputImage)

    if sourceHeight == 2200 and sourceWidth == 2200:
        imageType = "Full Disk (FD)"
    elif sourceWidth == 1547 and sourceHeight == 1234:
        imageType = "Enhanced Northern Hemisphere (ENH)"
    elif sourceWidth == 1547 and sourceHeight == 636:
        imageType = "Limited Southern Hemisphere (LSH)"
    elif sourceWidth == 810 and sourceHeight == 611:
        imageType = "Asia-Pacific Northern Hemisphere (APNH)"
    else:
        imageType = "UNRECOGNISED"
    print("IMAGE TYPE:  {}".format(imageType))

try:
    init()
except KeyboardInterrupt:
    print("Exiting...")
    exit(0)
