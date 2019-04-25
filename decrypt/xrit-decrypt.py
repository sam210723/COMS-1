"""
xrit-decrypt.py
https://github.com/sam210723/COMS-1

Decrypts xRIT file into a plain-text xRIT file using single layer DES
"""

import argparse
import pyDes

argparser = argparse.ArgumentParser(description="Decrypts xRIT file into a plain-text xRIT file using single layer DES")
argparser.add_argument("KEY", action="store", help="Decryption key")
argparser.add_argument("XRIT", action="store", help="xRIT file to decrypt")
args = argparser.parse_args()

xritFile = None
xritBytes = None


def load_xrit():
    """
    Loads xRIT file from disk
    """

    print("Loading xRIT file \"{}\"...".format(args.XRIT))

    xritFile = open(args.XRIT, 'rb')
    xritBytes = xritFile.read()
    xritFile.close()

    parse_primary(xritBytes)


def parse_primary(data):
    """
    Parses xRIT primary header to get field lengths
    """

    print("Parsing primary xRIT header...\n")

    primaryHeader = data[:16]

    # Header fields
    HEADER_TYPE = get_bits_int(primaryHeader, 0, 8, 128)               # File Counter (always 0x00)
    HEADER_LEN = get_bits_int(primaryHeader, 8, 16, 128)               # Header Length (always 0x10)
    FILE_TYPE = get_bits_int(primaryHeader, 24, 8, 128)                # File Type
    TOTAL_HEADER_LEN = get_bits_int(primaryHeader, 32, 32, 128)        # Total xRIT Header Length
    DATA_LEN = get_bits_int(primaryHeader, 64, 64, 128)                # Data Field Length

    print("  Header Length: {} bits".format(TOTAL_HEADER_LEN))
    print("  Data Length: {} bits\n".format(DATA_LEN))

    headerField = data[:TOTAL_HEADER_LEN]
    dataField = data[TOTAL_HEADER_LEN:]
    decrypt(headerField, dataField)


def decrypt(headers, data):
    print("Decrypting...")

    keyBytes = bytes.fromhex(args.KEY)
    desObj = pyDes.des(keyBytes, mode=pyDes.ECB)
    decData = desObj.decrypt(data, padmode=pyDes.PAD_NORMAL)
    
    decFile = open(args.XRIT + ".dec", 'wb')
    decFile.write(headers)
    decFile.write(decData)
    decFile.close()
    print("Output file: {}".format(args.XRIT + ".dec"))


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


load_xrit()
