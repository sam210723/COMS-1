"""
MPDU.py
https://github.com/sam210723/COMS-1

Parses xRIT Multiplexing Protocol Data Unit (M_PDU) and returns part of a CCSDS Path Protocol Data Unit (CP_PDU)
"""

from tools import getBits

def parseMPDU(data):
    headerBytes = data[0:2]

    # Header Fields
    #SPARE = getBits(headerBytes, 0, 5, 16)                 # Spare field (always b00000)
    POINTER = int(getBits(headerBytes, 5, 11, 16), 2)       # First Header Pointer

    if POINTER != 2047:  # 0x07FF
        NEW = True
    else:
        NEW = False

    FRAME = data[2:]
    return NEW, POINTER, FRAME
