"""
hrit-img.py
https://github.com/sam210723/coms-1

Extracts image data from HRIT IMG file.
"""

import argparse
from coms import COMS as comsClass
import glob
from PIL import Image
import numpy as np
import os
from subprocess import call

argparser = argparse.ArgumentParser(description="Extracts Meteorological Imager data from HRIT Image (IMG) files.")
argparser.add_argument("INPUT", action="store", help="Input HRIT file/folder path")
argparser.add_argument('OUTPUT', action="store", help="Output BIN file path")
argparser.add_argument('-i', action="store_true", help="Generate BMP from BIN file")
argparser.add_argument('-o', action="store_true", help="Add info text to generated BMP (assumes -i)")
argparser.add_argument('-m', action="store_true", help="Add map overlay to generated BMP (assumes -i)")
argparser.add_argument('-f', action="store", help="Overlay text fill colour", default="white")
args = argparser.parse_args()

segments = []  # List of IMG files
totalWidth = 0
totalHeight = 0

if os.path.isdir(args.INPUT):  # If input is a directory
    multipleSegments = True
    print("Detecting IMG segments...")

    # Loop through files with .hrit extension in input folder
    for file in glob.glob(args.INPUT + "/*.hrit"):
        COMS = comsClass(file)
        COMS.parsePrimaryHeader()
        COMS.parseImageStructureHeader()

        if COMS.primaryHeader['file_type'] == 0:  # Check HRIT file has IMG file type
            segments.append(file)  # Add to list of valid IMG files
            totalHeight += COMS.imageStructureHeader['num_lines']
            totalWidth = COMS.imageStructureHeader['num_cols']

    if segments.__len__() <= 0:
        print("No valid IMG files found")
        exit(1)

    print("Found {0} segments: ".format(segments.__len__()))
    for segment in segments:  # List detected segments
        print(" - {0}".format(segment))

elif os.path.isfile(args.INPUT):  # If input is a single file
    multipleSegments = False
    COMS = comsClass(args.INPUT)
    COMS.parsePrimaryHeader()
    COMS.parseImageStructureHeader()

    if COMS.primaryHeader['file_type'] == 0:  # Check HRIT file has IMG file type
        segments.append(args.INPUT)  # Add to list of valid IMG files
        totalHeight += COMS.imageStructureHeader['num_lines']
        totalWidth = COMS.imageStructureHeader['num_cols']

print()
# Delete output BIN file if it exists
if os.path.isfile(args.OUTPUT):
    os.remove(args.OUTPUT)
    print("Deleted existing BIN file: {0}".format(args.OUTPUT))

# Loop through each segment
for hritFile in segments:
    # Create COMS class instance and load HRIT file
    COMS = comsClass(hritFile)

    # Primary Header (type 0, required)
    COMS.parsePrimaryHeader()

    # START OPTIONAL HEADERS
    printOptHeaders = False
    COMS.parseImageStructureHeader(printOptHeaders)

    COMS.parseImageNavigationHeader(printOptHeaders)

    COMS.parseImageDataFunctionHeader(printOptHeaders)

    COMS.parseAnnotationTextHeader(printOptHeaders)

    COMS.parseTimestampHeader(printOptHeaders)

    COMS.parseKeyHeader(printOptHeaders)

    COMS.parseImageSegmentationInformationHeader(printOptHeaders)

    # BEGIN DATA DUMPING
    binFile = open(args.OUTPUT, "ab")
    binFile.write(COMS.readbytes(0+135, COMS.primaryHeader['data_field_len']))  # Dump image bytes to binary BIN file

print("{1}Image data dumped to \"{0}\"{2}".format(args.OUTPUT, COMS.colours['OKGREEN'], COMS.colours['ENDC']))

if args.i or args.o or args.m:
    # See GitHub Issue 1 for details
    bmpName = args.OUTPUT[:args.OUTPUT.index('.')] + ".bmp"
    binFile = open(args.OUTPUT, 'rb')
    z = np.fromfile(binFile, dtype=np.uint16, count=totalWidth * totalHeight)
    z = z / 4
    img = Image.frombuffer("L", [totalWidth, totalHeight], z.astype('uint8'), 'raw', 'L', 0, 1)
    img.save(bmpName)
    print("{0}\nBMP image generated\n{1}".format(COMS.colours['OKGREEN'], COMS.colours['ENDC']))

    if args.o:  # Overlay flag
        overlayName = bmpName[:bmpName.index('.')] + "_overlay.bmp"
        channel = COMS.imageDataFunctionHeader['data_definition_block'][9:COMS.imageDataFunctionHeader['data_definition_block'].index("\n")]
        leftText = "COMS-1 HRIT {0} - {1}".format(COMS.imageTypes[COMS.imageStructureHeader['image_type']], channel)
        rightText = "{0} {1} UTC".format(COMS.timestampHeader['t_field_current_date'], COMS.timestampHeader['t_field_current_time'])

        if args.m:  # Map flag
            call(["python3", "overlay.py", "-s", "60", "-m", "-f", args.f, bmpName, overlayName, leftText, rightText])
            print("Map overlay and info text added to BMP")
        else:
            call(["python3", "overlay.py", "-s", "60", "-f", args.f, bmpName, overlayName, leftText, rightText])
            print("{0}Info text added to BMP{1}".format(COMS.colours['OKGREEN'], COMS.colours['ENDC']))
