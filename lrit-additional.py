"""
lrit-additional.py
https://github.com/sam210723/coms-1

Extracts data from LRIT Additional Data files.
Data includes Alpha-numeric text (ANT), CMDPS (CT/CTT/CTH), and GOCI.
"""

import argparse
import coms
from datetime import datetime, timedelta

argparser = argparse.ArgumentParser(description="Extract data from COMS-1 Additional Data (ADD) .lrit file")
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
primaryHeader = coms.parsePrimaryHeader(readbytes(filepos, 16))

if primaryHeader['valid']:
    print("{3}[Type {0} : Offset {1}] {2}:{4}".format(primaryHeader['header_type'], coms.intToHex(filepos), coms.headerTypes[primaryHeader['header_type']], coms.colours['OKGREEN'], coms.colours['ENDC']))
    print("\tHeader length:         16")  # Fixed length
    print("\tFile type:             {0}, {1}".format(primaryHeader['file_type'], coms.fileTypes[primaryHeader['file_type']]))
    print("\tTotal header length:   {0} ({1})".format(primaryHeader['total_header_len'], coms.intToHex(primaryHeader['total_header_len'])))
    print("\tData length:           {0} ({1})".format(primaryHeader['data_field_len'], coms.intToHex(primaryHeader['data_field_len'])))
    filepos += 16
else:
    print("Error: Primary header not found")
    print("\nExiting...")
    exit(1)


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

# BEGIN DATA DUMPING
data = readbytes(filepos, primaryHeader['data_field_len'])

if primaryHeader['file_type'] == 2:  # Alphanumeric Text (ANT)
    dumpExtension = "txt"
elif primaryHeader['file_type'] == 128:  # CMDPS Data (CT, CTT, CTH)
    dumpExtension = "png"

dumpFileName = args.path[:-5] + "_DATA.{0}".format(dumpExtension)
dumpFile = open(dumpFileName, 'wb')
dumpFile.write(data)
dumpFile.close()
print("\nAdditional Data dumped to \"{0}\"".format(dumpFileName))
