"""
lrit-img.py
https://github.com/sam210723/coms-1

Adds overlays and text to COMS-1 Meteorological Imager images.
"""

import argparse
from PIL import Image, ImageFont, ImageDraw
import shapefile
from coms import COMS

argparser = argparse.ArgumentParser(description="Adds overlays and text to COMS-1 Meteorological Imager images.")
argparser.add_argument("INPUT", action="store", help="Input BMP file")
argparser.add_argument('OUTPUT', action="store", help="Output BMP file")
argparser.add_argument('LEFT', action="store", help="Left text")
argparser.add_argument('RIGHT', action="store", help="Right text")
argparser.add_argument('-m', action="store_true", help="Enable map overlay")
argparser.add_argument('-f', action="store", help="Text fill colour", default="white")
argparser.add_argument('-s', action="store", help="Text font size", default="32")
args = argparser.parse_args()
shapefileName = "shp/ne_50m_coastline_geos_128.2e.shp"
lineWidth = 2  # Line width in px
wOff = 48
hOff = 71
lastPx = 0
lastPy = 0

# Source Image
sourceImage = Image.open(args.INPUT)
outputImage = Image.new("RGB", (sourceImage.width, sourceImage.height + 50 - 50))
outputImage.paste(sourceImage, (0, 0))
draw = ImageDraw.Draw(outputImage)

# Map overlay
# Shapefiles from NaturalEarthData.com (http://naciscdn.org/naturalearth/50m/physical/ne_50m_coastline.zip)
if args.m:
    print("Loading shapefile \"{0}\"".format(shapefileName))
    r = shapefile.Reader(shapefileName)
    # Geographic x & y distance
    r.bbox[2] = 5420803.776769789
    r.bbox[3] = 5391827.470781375
    xdist = r.bbox[2] - r.bbox[0]
    ydist = r.bbox[3] - r.bbox[1]
    # Image width & height
    iwidth = sourceImage.width-wOff
    iheight = sourceImage.height-hOff
    xratio = iwidth / xdist
    yratio = iheight / ydist
    pixels = []
    mapImage = Image.new("RGBA", (iwidth, iheight))
    mapDraw = ImageDraw.Draw(mapImage)
    for i in r.shapes():
        for x, y in i.points:
            try:
                px = int(iwidth - ((r.bbox[2] - x) * xratio))
                py = int((r.bbox[3] - y) * yratio)

                # Filter random straight lines longer than 1200px on either axis
                if abs(px-lastPx) > 200 or abs(py-lastPy) > 200:
                    print("{0}:{1}".format(abs(px-lastPx), abs(py-lastPy)))
                else:
                    pixels.append((px, py))

                lastPx = px
                lastPy = py
            except OverflowError:  # Handle points that extend off the side of the projection (Inf)
                pass
        mapDraw.line(pixels, "rgb(0, 255, 0)", lineWidth)
        pixels = []
    #mapImage.save("bmp/map.png")
    outputImage.paste(mapImage, (int(wOff/2), int(hOff/2)), mask=mapImage)

    print("{0}Map overlay generated{1}\n".format(COMS.colours['OKGREEN'], COMS.colours['ENDC']))


# Info Text
font = ImageFont.truetype("Arial.ttf", int(args.s))
textL = args.LEFT
textR = args.RIGHT
textLs = draw.textsize(textL, font)
textRs = draw.textsize(textR, font)
draw.text((10, outputImage.height-textLs[1]-8), text=textL, font=font, fill=args.f)
draw.text(((outputImage.width-textRs[0]-10), outputImage.height-textRs[1]-14), text=textR, font=font, fill=args.f)
print("Left text: \"{0}\"\nRight text: \"{1}\"".format(textL, textR))

outputImage.save(args.OUTPUT)
print("{1}Modified image saved to {0}{2}\n".format(args.OUTPUT, COMS.colours['OKGREEN'], COMS.colours['ENDC']))
