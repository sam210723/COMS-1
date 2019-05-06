"""
lrit-img.py
https://github.com/sam210723/COMS-1

Extracts image data from LRIT IMG file.
"""

import argparse
import glob
import io
import os
from PIL import Image, ImageFile
import sys

argparser = argparse.ArgumentParser(description="Extracts image data from LRIT IMG file.")
argparser.add_argument("INPUT", action="store", help="LRIT file (or folder) to process")
args = argparser.parse_args()
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Globals
files = []
groups = {}

def init():
    """
    Parse arguments then locate images and segments
    """

    # Check if input is a directory
    if os.path.isdir(args.INPUT):
        # Loop through files with .lrit.dec extension in input folder
        for f in glob.glob(args.INPUT + "/*.lrit.dec"):
            files.append(f)
        
        if files.__len__() <= 0:
            print("No LRIT files found")
            exit(1)
        
        # Print file list
        print("Found {} LRIT files: ".format(len(files)))
        for f in files:
            print("  {}".format(f))

        # Group image segments
        for f in files:
            img, mode, segment = parse_fname(f)

            # If group exists in group list
            if img not in groups.keys():
                groups[img] = []
            
            # Add file to group
            groups[img].append(f)
        
        # Print image list
        print("\n\nFound {} images:".format(len(groups.keys())))
        for img in list(groups):
            print("  {}".format(img))

            # Check for missing segments
            foundSegments = len(groups[img])
            name, mode, segment = parse_fname(groups[img][0])
            totalSegments = get_total_segments(mode)

            if totalSegments == None:
                print("    Unrecognised observation mode \"{}\"".format(mode))
            
            if foundSegments == totalSegments:
                print("    Found {} of {} segments".format(foundSegments, totalSegments))
            else:
                print("    MISSING {} SEGMENTS".format(totalSegments - foundSegments))
                print("    IMAGE GENERATION WILL BE SKIPPED")

                # Remove image group from list
                groups.pop(img, None)
            
            # Check image has not already been generated
            if os.path.isfile(args.INPUT + "\\" + name + ".jpg"):
                print("    IMAGE ALREADY GENERATED...SKIPPING")
                
                # Remove image group from list
                groups.pop(img, None)
            print()

        print("-----------------------------------------\n")

        # Load and combine segments
        for img in groups.keys():
            # Get group details
            name, mode, segment = parse_fname(groups[img][0])

            process_group(name, mode, groups[img])
            print("\n")
    else:
        # Load and process single file
        process_single_segment(args.INPUT)


def process_group(name, mode, files):
    """
    Load data field of each segment and combine into one JPEG
    """

    print("Processing {}...".format(name))
    print("  Loading segments", end='')

    segmentDataFields = []

    # Load each segment from disk
    for seg in files:
        # Load file
        headerField, dataField = load_lrit(seg)

        # Append data field to data field list
        segmentDataFields.append(dataField)
        print(".", end='')
        sys.stdout.flush()
    print()

    # Create new image
    finalResH, finalResV = get_image_resolution(mode)
    outImage = Image.new("RGB", (finalResH, finalResV))

    # Process segments into images
    print("  Joining segments", end='')

    segmentCount = get_total_segments(mode)
    segmentVRes = int(finalResV / segmentCount)
    for i, seg in enumerate(segmentDataFields):
        # Create image object
        buf = io.BytesIO(seg)
        img = Image.open(buf)
        
        # Calculate segment offset
        if mode == "ENH":
            if i == 0 or i == 1 or i == 2:
                vOffset = 309 * i
            else:
                # Last ENH segment
                vOffset = (309 * 2) + 308
        else:
            vOffset = segmentVRes * i

        # Append image to output image
        outImage.paste(img, (0, vOffset))

        print(".", end='')
        sys.stdout.flush()
    print()

    # Save output image to disk
    outFName = args.INPUT + "\\" + name + ".jpg"
    outImage.save(outFName, format='JPEG', subsampling=0, quality=100)
    print("  Saved image: \"{}\"".format(outFName))


def process_single_segment(fpath):
    """
    Processes a single LRIT segment into an image
    """

    name, mode, segment = parse_fname(fpath)
    print("Processing {}...".format(fpath))

    # Load file
    headerField, dataField = load_lrit(fpath)

    # Create image and save to disk
    buf = io.BytesIO(dataField)
    img = Image.open(buf)
    outFName = args.INPUT + ".jpg"
    img.save(outFName)
    print("Saved image: \"{}\"".format(outFName))


def load_lrit(fpath):
    """
    Load LRIT file and return data field
    """

    # Read file bytes from disk
    file = open(fpath, mode="rb")
    fileBytes = file.read()
    headerLen, dataLen = parse_primary(fileBytes)

    # Split file bytes into fields
    headerField = fileBytes[:headerLen]
    dataField = fileBytes[headerLen : headerLen + dataLen]

    return headerField, dataField


def parse_primary(data):
    """
    Parses LRIT primary header to get field lengths
    """

    #print("Parsing primary LRIT header...")

    primaryHeader = data[:16]

    # Header fields
    HEADER_TYPE = get_bits_int(primaryHeader, 0, 8, 128)               # File Counter (always 0x00)
    HEADER_LEN = get_bits_int(primaryHeader, 8, 16, 128)               # Header Length (always 0x10)
    FILE_TYPE = get_bits_int(primaryHeader, 24, 8, 128)                # File Type
    TOTAL_HEADER_LEN = get_bits_int(primaryHeader, 32, 32, 128)        # Total LRIT Header Length
    DATA_LEN = get_bits_int(primaryHeader, 64, 64, 128)                # Data Field Length

    #print("    Header Length: {} bits ({} bytes)".format(TOTAL_HEADER_LEN, TOTAL_HEADER_LEN/8))
    #print("    Data Length: {} bits ({} bytes)".format(DATA_LEN, DATA_LEN/8))

    return TOTAL_HEADER_LEN, DATA_LEN


def parse_fname(fpath):
    """
    Parse LRIT file name into components
    """

    split = fpath.split("_")
    mode = split[1]
    name = fpath.replace(".lrit.dec", "")[:-3]
    name = "IMG_" + name.split("IMG_")[1]
    segment = int(split[6][:2])

    return name, mode, segment


def get_total_segments(mode):
    """
    Returns the total number of segments in the given observation mode
    """

    if mode == "FD":
        totalSegments = 10
    elif mode == "ENH":
        totalSegments = 4
    elif mode == "LSH":
        totalSegments = 2
    elif mode == "APNH":
        totalSegments = 1
    else:
        totalSegments = None
    
    return totalSegments


def get_image_resolution(mode):
    """
    Returns the horizontal and vertical resolution of the given observation mode
    """

    if mode == "FD":
        outH = 2200
        outV = 2200
    elif mode == "ENH":
        outH = 1547
        outV = 1234
    elif mode == "LSH":
        outH = 1547
        outV = 636
    elif mode == "APNH":
        outH = 810
        outV = 611
    
    return outH, outV


def get_bits(data, start, length, count):
    """
    Get bits from bytes

    :param data: Bytes to get bits from
    :param start: Start offset in bits
    :param length: Number of bits to get
    :param count: Total number of bits in bytes (accounts for leading zeros)
    """

    dataInt = int.from_bytes(data, byteorder='big')
    dataBin = format(dataInt, '0' + str(count) + 'b')
    end = start + length
    bits = dataBin[start : end]

    return bits

def get_bits_int(data, start, length, count):
    """
    Get bits from bytes as integer

    :param data: Bytes to get bits from
    :param start: Start offset in bits
    :param length: Number of bits to get
    :param count: Total number of bits in bytes (accounts for leading zeros)
    """

    bits = get_bits(data, start, length, count)

    return int(bits, 2)


try:
    init()
except KeyboardInterrupt:
    print("Exiting...")
    exit(0)
