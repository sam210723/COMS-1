import errno
import os

def getBits(data, start, length, count):
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


def newDirExists(path):
    """
    Create new directory if it doesn't exist already
    :param path: Absolute directory path
    """

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
            return True
        except OSError as e:
            return e.errno
    else:
        return True
