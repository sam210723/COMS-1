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


# Primary header (type 0)
if readbytes(0, 3) == b'\x00\x00\x10':
    print("Primary Header (type 0):\n\tPrimary header length:   16")
else:
    print("Error: Primary header not found")
    print("\nExiting...")
    exit(1)

# File type
if readbytes(3) == b'\x00':
    print("\tFile type:               0, Image data file")
elif readbytes(3) == b'\x01':
    print("\tFile type:               1, Telecommunication System (GTS) message")  # Not used in COMS LRIT
elif readbytes(3) == b'\x02':
    print("\tFile type:               2, Alpha-numeric text (ANT)")
elif readbytes(3) == b'\x03':
    print("\tFile type:               3, Encryption key message")
elif readbytes(3) == b'\x80':
    print("\tFile type:               128, COMS Meteorological Data Processing System (CMDPS) analysis data")
elif readbytes(3) == b'\x81':
    print("\tFile type:               129, Numerical Weather Prediction (NWP) data")
elif readbytes(3) == b'\x82':
    print("\tFile type:               130, Geostationary Ocean Color Imager (GOCI) data")
else:
    print("\tFile type:               {0}, Unknown".format(int.from_bytes(readbytes(3), byteorder='little')))
    print("\nExiting...")
    exit(1)

# Header length
headerLengthBytes = readbytes(4, 4)
headerLengthInt = int.from_bytes(headerLengthBytes, byteorder='big')
headerLengthHexString = "0x" + hex(headerLengthInt).upper()[2:]
print("\tHeader length:           {0} ({1})".format(headerLengthInt, headerLengthHexString))

# Data field length
dataLengthBytes = readbytes(8, 8)
dataLengthInt = int.from_bytes(dataLengthBytes, byteorder='big')
dataLengthHexString = "0x" + hex(dataLengthInt).upper()[2:]
print("\tData length:             {0} ({1})".format(dataLengthInt, dataLengthHexString))
