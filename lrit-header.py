import argparse
import coms
from datetime import datetime, timedelta

argparser = argparse.ArgumentParser(description="Extract LRIT header information from COMS-1 .lrit file")
argparser.add_argument('-f', action="store", dest="path", help="Input LRIT file")
args = argparser.parse_args()

if args.path is None:
    print("No LRIT file provided. Use -f [PATH]\n")
    exit(1)

# Open file
file = open(args.path, mode='rb')
fileString = file.read()


def readbytes(start, length=1):
    return fileString[start:start+length]


# Byte counter for tracking progress through file
filepos = 0

# Primary Header (type 0, required)
if readbytes(filepos, 3) == b'\x00\x00\x10':
    print("{2}[Type 0 : Offset {0}] {1}:{3}".format("0x" + hex(filepos).upper()[2:], coms.headerTypes[0], coms.colours['OKGREEN'], coms.colours['ENDC']))
    print("\tHeader length:         16")  # Fixed length
else:
    print("Error: Primary header not found")
    print("\nExiting...")
    exit(1)

# File type
fTypeInt = int.from_bytes(readbytes(filepos + 3), byteorder='big')
fTypeStr = coms.fileTypes[fTypeInt]
print("\tFile type:             {0}, {1}".format(fTypeInt, fTypeStr))

# Total header length
totalHeaderLengthBytes = readbytes(filepos + 4, 4)
totalHeaderLengthInt = int.from_bytes(totalHeaderLengthBytes, byteorder='big')
totalHeaderLengthHexString = "0x" + hex(totalHeaderLengthInt).upper()[2:]
print("\tTotal header length:   {0} ({1})".format(totalHeaderLengthInt, totalHeaderLengthHexString))

# Data field length
dataLengthBytes = readbytes(filepos + 8, 8)
dataLengthInt = int.from_bytes(dataLengthBytes, byteorder='big')
dataLengthHex = hex(dataLengthInt).upper()[2:]
print("\tData length:           {0} (0x{1})".format(dataLengthInt, dataLengthHex))

filepos += 16


# START OPTIONAL HEADERS

# Image Structure Header (type 1)
if readbytes(filepos, 3) == b'\x01\x00\x09':
    print("\n{2}[Type 1 : Offset {0}] {1}:{3}".format("0x" + hex(filepos).upper()[2:], coms.headerTypes[1], coms.colours['OKGREEN'], coms.colours['ENDC']))
    print("\tHeader length:         9")  # Fixed length

    # Bits per pixel (Always 8 for LRIT)
    bppBytes = readbytes(filepos + 3)
    bppInt = int.from_bytes(bppBytes, byteorder='big')
    if bppInt != 8: bppInt = str(bppInt) + " (WARNING: Should be 8 for LRIT)"
    print("\tBits per pixel:        {0}".format(bppInt))

    # Number of columns
    colsBytes = readbytes(filepos + 4, 2)
    colsInt = int.from_bytes(colsBytes, byteorder='big')

    # Number of lines
    linesBytes = readbytes(filepos + 6, 2)
    linesInt = int.from_bytes(linesBytes, byteorder='big')

    # Image type based on column and line count
    if colsInt == 2200 and linesInt == 2200:
        imageType = "Full Disk (FD)"
    elif colsInt == 1547 and (linesInt == 308 or linesInt == 309):
        imageType = "Extended Northern Hemisphere (ENH)"
    elif colsInt == 1547 and linesInt == 318:
        imageType = "Limited Southern Hemisphere (LSH)"
    elif colsInt == 810 and linesInt == 611:
        imageType = "Asia and Pacific in Northern Hemisphere (APNH)"

    print("\tImage:                 {0}".format(imageType))
    print("\t  - Columns: {0}".format(colsInt))
    print("\t  - Lines:   {0}".format(linesInt))

    # Image compression
    compressionBytes = readbytes(filepos + 8)
    compressionInt = int.from_bytes(compressionBytes, byteorder='big')
    if compressionInt == 0:
        compressionType = "0, None"
    elif compressionInt == 1:
        compressionType = "1, Lossless"
    elif compressionInt == 2:
        compressionType = "2, Lossy"
    else:
        compressionType = "{0}, Unknown".format(compressionInt)

    print("\tCompression:           {0}".format(compressionType))

    filepos += 9


# Image Navigation Header (type 2)
if readbytes(filepos, 3) == b'\x02\x00\x33':
    print("\n{2}[Type 2 : Offset {0}] {1}:{3}".format("0x" + hex(filepos).upper()[2:], coms.headerTypes[2], coms.colours['OKGREEN'], coms.colours['ENDC']))
    print("\tHeader length:         51")  # Fixed length

    # Map Projection name + longitude
    projectionBytes = readbytes(filepos + 3, 32)
    projectionString = projectionBytes.decode()
    if projectionString.__contains__("GEOS"):
        projection = "Normalized Geostationary Projection (GEOS)"
    longitude = projectionString[projectionString.index("(")+1:projectionString.index(")")]
    print("\tProjection:            {0}".format(projection))
    print("\tLongitude:             {0}° E".format(longitude))

    # Column scaling factor
    colScalingBytes = readbytes(filepos + 35, 4)
    colScalingInt = int.from_bytes(colScalingBytes, byteorder='big')
    print("\tColumn scaling factor: {0}".format(colScalingInt))

    # Line scaling factor
    lineScalingBytes = readbytes(filepos + 39, 4)
    lineScalingInt = int.from_bytes(lineScalingBytes, byteorder='big')
    print("\tLine scaling factor:   {0}".format(lineScalingInt))

    # Column offset
    colOffsetBytes = readbytes(filepos + 43, 4)
    colOffsetInt = int.from_bytes(colOffsetBytes, byteorder='big')
    print("\tColumn offset:         {0}".format(colOffsetInt))

    # Line offset
    lineOffsetBytes = readbytes(filepos + 47, 4)
    lineOffsetInt = int.from_bytes(lineOffsetBytes, byteorder='big')
    print("\tLine offset:           {0}".format(lineOffsetInt))

    filepos += 51


# Image Data Function Header (type 3)
if readbytes(filepos) == b'\x03':
    print("\n{2}[Type 3 : Offset {0}] {1}:{3}".format("0x" + hex(filepos).upper()[2:], coms.headerTypes[3], coms.colours['OKGREEN'], coms.colours['ENDC']))

    # Header length
    dataFuncLengthBytes = readbytes(filepos + 1, 2)
    dataFuncLengthInt = int.from_bytes(dataFuncLengthBytes, byteorder='big')
    dataFuncLengthHex = hex(dataFuncLengthInt).upper()[2:]
    print("\tHeader length:         {0} (0x{1})".format(dataFuncLengthInt, dataFuncLengthHex))

    # Data Definition Block
    ddbBytes = readbytes(filepos + 3, dataFuncLengthInt - 3)
    ddbString = ddbBytes.decode()

    ddbFileName = args.path[:-5] + "_IDF-DDB.txt"
    ddbFile = open(ddbFileName, 'w')
    ddbFile.write(ddbString)
    ddbFile.close()
    print("\tData Definition Block:\n\t  - dumped to \"{0}\"".format(ddbFileName))

    filepos += dataFuncLengthInt


# Annotation Text Header (type 4)
if readbytes(filepos) == b'\x04':
    print("\n{2}[Type 4 : Offset {0}] {1}:{3}".format("0x" + hex(filepos).upper()[2:], coms.headerTypes[4], coms.colours['OKGREEN'], coms.colours['ENDC']))

    # Header length
    annotationLengthBytes = readbytes(filepos + 1, 2)
    annotationLengthInt = int.from_bytes(annotationLengthBytes, byteorder='big')
    annotationLengthHex = hex(annotationLengthInt).upper()[2:]
    print("\tHeader length:         {0} (0x{1})".format(annotationLengthInt, annotationLengthHex))

    # Text data (usually .lrit filename)
    annotationTextBytes = readbytes(filepos + 3, annotationLengthInt - 3)
    annotationTextString = annotationTextBytes.decode()
    print("\tText data:             \"{0}\"".format(annotationTextString))

    filepos += annotationLengthInt


# CCSDS Time Stamp Header (type 5)
if readbytes(filepos, 3) == b'\x05\x00\x0A':
    print("\n{2}[Type 5 : Offset {0}] {1}:{3}".format("0x" + hex(filepos).upper()[2:], coms.headerTypes[5], coms.colours['OKGREEN'], coms.colours['ENDC']))
    print("\tHeader length:         10")

    # CDS P Field
    pFieldBytes = readbytes(filepos + 3)
    pFieldInt = int.from_bytes(pFieldBytes, byteorder='big')
    pFieldBin = bin(pFieldInt)[2:].zfill(8)
    pFieldStr = str(pFieldBin)
    print("\tP Field:               {0}".format(pFieldStr))

    # Bit 0 - Extension flag, Bits 1-3 - Time code ID, Bits 4-7 - Detail bits
    pField = [pFieldStr[0], pFieldStr[1:4], pFieldStr[4:8]]

    # Extension flag
    if pField[0] == "0":
        pField[0] += " (No extension)"
    else:
        pField[0] += " (Extended field)"
    print("\t  - Extension flag:    {0}".format(pField[0]))

    # Time code ID
    if pField[1] == "100":
        pField[1] += " (1958 January 1 epoch - Level 1 Time Code)"
    elif pField[1] == "010":
        pField[1] += " (Agency-defined epoch - Level 2 Time Code)"
    print("\t  - Time code ID:      {0}".format(pField[1]))

    print("\t  - Detail bits:       {0}".format(pField[2]))


    # CDS T Field
    tFieldBytes = readbytes(filepos + 4, 6)
    tFieldInt = int.from_bytes(tFieldBytes, byteorder='big')
    tFieldBin = bin(tFieldInt)[2:].zfill(48)
    tFieldStr = str(tFieldBin)

    print("\tT Field:               {0}".format(tFieldStr))

    # Bits 0-16 - Days since epoch, Bits 16-48 - Milliseconds of day
    tField = [int(tFieldStr[0:16], 2), int(tFieldStr[16:48], 2)]

    epoch = datetime.strptime("01/01/1958", '%d/%m/%Y')
    currentDate = epoch + timedelta(days=tField[0] + 1)
    print("\t  - Day counter:       {0} ({1})".format(tField[0], currentDate.strftime('%d/%m/%Y') + " - DD/MM/YYYY"))

    currentDate = currentDate + timedelta(milliseconds=tField[1])
    print("\t  - Milliseconds:      {0} ({1})".format(tField[1], currentDate.strftime('%H:%M:%S') + " - HH:MM:SS"))

    filepos += 10


# Ancillary Text Header (type 6)
if readbytes(filepos) == b'\x06':
    print("\n{2}[Type 6 : Offset {0}] {1}:{3}".format("0x" + hex(filepos).upper()[2:], coms.headerTypes[6], coms.colours['OKGREEN'], coms.colours['ENDC']))

    # Header type unused. Allows for future LRIT expansion
    filepos += 0


# Key Header (type 7)
if readbytes(filepos, 3) == b'\x07\x00\x07':
    print("\n{2}[Type 7 : Offset {0}] {1}:{3}".format("0x" + hex(filepos).upper()[2:], coms.headerTypes[7], coms.colours['OKGREEN'], coms.colours['ENDC']))
    print("\tHeader length:         7")

    encKeyBytes = readbytes(filepos + 3, 4)
    encKeyInt = int.from_bytes(encKeyBytes, byteorder='big')
    encKeyHex = hex(encKeyInt).upper()[2:]

    if encKeyHex == "0":
        encKeyHex += " (disabled)"

    print("\tEncryption key:        0x{0}".format(encKeyHex))

    filepos += 7


# Image Segmentation Information Header (type 128)
if readbytes(filepos, 3) == b'\x80\x00\x07':
    print("\n{2}[Type 128 : Offset {0}] {1}:{3}".format("0x" + hex(filepos).upper()[2:], coms.headerTypes[128], coms.colours['OKGREEN'], coms.colours['ENDC']))
    print("\tHeader length:         7")

    # Image Segment Sequence Number
    segSeqNumByte = readbytes(filepos + 3)
    segSeqNumInt = int.from_bytes(segSeqNumByte, byteorder='big')

    # Image Segment Total
    segTotalByte = readbytes(filepos + 4)
    segTotalInt = int.from_bytes(segTotalByte, byteorder='big')

    print("\tSegment number:        {0} of {1}".format(segSeqNumInt, segTotalInt))

    # Line number of Image Segment
    lineNumSegBytes = readbytes(filepos + 5, 2)
    lineNumSegInt = int.from_bytes(lineNumSegBytes, byteorder='big')
    print("\tLine num of segment:   {0}".format(lineNumSegInt))


print()
