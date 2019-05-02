"""
xrit-decrypt.py
https://github.com/sam210723/COMS-1

Decrypts xRIT file into a plain-text xRIT file using single layer DES
"""

import argparse
import glob
import os
import pyDes

argparser = argparse.ArgumentParser(description="Decrypts xRIT file into a plain-text xRIT file using single layer DES")
argparser.add_argument("KEY", action="store", help="Decryption key")
argparser.add_argument("XRIT", action="store", help="xRIT file (or folder) to decrypt")
args = argparser.parse_args()

xritFile = None
xritBytes = None
files = []

def init():
    # If input is a directory
    if os.path.isdir(args.XRIT):
        # Loop through all .lrit/.hrit files in directory
        print("Finding xRIT segments...\n")

        # Loop through files with .lrit extension in input folder
        for f in glob.glob(args.XRIT + "/*.lrit"):
            files.append(f)
        
        # Loop through files with .hrit extension in input folder
        for f in glob.glob(args.XRIT + "/*.hrit"):
            files.append(f)
            print(" - {}".format(f))

        if files.__len__() <= 0:
            print("No LRIT/HRIT files found")
            exit(1)
        
        # Print file list
        print("Found {} files: ".format(len(files)))
        for f in files:
            print("  {}".format(f))
        
        print("\nDecrypting files...")
        print("-----------------------------------------")
        for f in files:
            if os.path.isfile(f + ".dec"):
                print("Skipping {}\nFile already decrypted\n".format(f))
            else:
                load_xrit(f)
            
            print("-----------------------------------------")

        print("\nFinished decryption\nExiting...")
        exit(0)

    else:
        # Load and decrypt single file
        load_xrit(args.XRIT)


def load_xrit(fpath):
    """
    Loads xRIT file from disk
    """

    print("\nLoading xRIT file \"{}\"...".format(args.XRIT))

    xritFile = open(fpath, 'rb')
    xritBytes = xritFile.read()
    xritFile.close()

    parse_primary(xritBytes, fpath)


def parse_primary(data, fpath):
    """
    Parses xRIT primary header to get field lengths
    """

    print("Parsing primary xRIT header...")

    primaryHeader = data[:16]

    # Header fields
    HEADER_TYPE = get_bits_int(primaryHeader, 0, 8, 128)               # File Counter (always 0x00)
    HEADER_LEN = get_bits_int(primaryHeader, 8, 16, 128)               # Header Length (always 0x10)
    FILE_TYPE = get_bits_int(primaryHeader, 24, 8, 128)                # File Type
    TOTAL_HEADER_LEN = get_bits_int(primaryHeader, 32, 32, 128)        # Total xRIT Header Length
    DATA_LEN = get_bits_int(primaryHeader, 64, 64, 128)                # Data Field Length

    print("  Header Length: {} bits ({} bytes)".format(TOTAL_HEADER_LEN, TOTAL_HEADER_LEN/8))
    print("  Data Length: {} bits ({} bytes)".format(DATA_LEN, DATA_LEN/8))

    headerField = data[:TOTAL_HEADER_LEN]
    dataField = data[TOTAL_HEADER_LEN: TOTAL_HEADER_LEN + DATA_LEN]

    # Append null bytes to data field to fill last 8 byte DES block
    dFMod8 = len(dataField) % 8
    if dFMod8 != 0:
        for i in range(dFMod8):
            dataField += b'x00'
        print("\nAdded {} null bytes to fill last DES block\n".format(dFMod8))

    decrypt(headerField, dataField, fpath)


def decrypt(headers, data, fpath):
    print("Decrypting...")

    keyBytes = bytes.fromhex(args.KEY)
    desObj = pyDes.des(keyBytes, mode=pyDes.ECB)
    decData = desObj.decrypt(data, padmode=pyDes.PAD_NORMAL)
    
    decFile = open(fpath + ".dec", 'wb')
    decFile.write(headers)
    decFile.write(decData)
    decFile.close()
    print("Output file: {}".format(fpath + ".dec"))


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
