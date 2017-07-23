import argparse

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

# Primary header (type 0)
if readbytes(filepos, 3) == b'\x00\x00\x10':
    print("Primary Header (type 0):\n\tHeader length:         16")
else:
    print("Error: Primary header not found")
    print("\nExiting...")
    exit(1)

# File type
if readbytes(filepos + 3) == b'\x00':
    fType = "0, Image data file"
elif readbytes(filepos + 3) == b'\x01':
    fType = "1, Telecommunication System (GTS) message"  # Not used in COMS LRIT
elif readbytes(filepos + 3) == b'\x02':
    fType = "2, Alpha-numeric text (ANT)"
elif readbytes(filepos + 3) == b'\x03':
    fType = "3, Encryption key message"
elif readbytes(filepos + 3) == b'\x80':
    fType = "128, COMS Meteorological Data Processing System (CMDPS) analysis data"
elif readbytes(filepos + 3) == b'\x81':
    fType = "129, Numerical Weather Prediction (NWP) data"
elif readbytes(filepos + 3) == b'\x82':
    fType = "130, Geostationary Ocean Color Imager (GOCI) data"
else:
    print("\tFile type:             {0}, Unknown".format(int.from_bytes(readbytes(filepos + 3), byteorder='little')))
    print("\nExiting...")
    exit(1)
print("\tFile type:             {0}".format(fType))

# Total header length
totalHeaderLengthBytes = readbytes(filepos + 4, 4)
totalHeaderLengthInt = int.from_bytes(totalHeaderLengthBytes, byteorder='big')
totalHeaderLengthHexString = "0x" + hex(totalHeaderLengthInt).upper()[2:]
print("\tTotal header length:   {0} ({1})".format(totalHeaderLengthInt, totalHeaderLengthHexString))

# Data field length
dataLengthBytes = readbytes(filepos + 8, 8)
dataLengthInt = int.from_bytes(dataLengthBytes, byteorder='big')
dataLengthHex = "0x" + hex(dataLengthInt).upper()[2:]
print("\tData length:           {0} ({1})".format(dataLengthInt, dataLengthHex))

filepos += 16

# Image structure header (type 1)
if readbytes(filepos, 3) == b'\x01\x00\x09':
    print("\nImage Structure Header (type 1):\n\tHeader length:         9")

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
    if colsInt == 2200 and linesInt == 200:
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