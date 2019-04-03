"""
MPDU.py
https://github.com/sam210723/COMS-1

Parses xRIT Multiplexing Protocol Data Unit (M_PDU) and returns part of a CCSDS Path Protocol Data Unit (CP_PDU)
"""

from tools import getBits

def parseMPDU(data):
    headerBytes = data[:2]

    # Header Fields
    #SPARE = getBits(headerBytes, 0, 5, 16)                 # Spare Field (always b00000)
    POINTER = int(getBits(headerBytes, 5, 11, 16), 2)       # First Header Pointer

    # Detect of M_PDU contains M_SDU header
    if POINTER != 2047:  # 0x07FF
        HEADER = True
    else:
        HEADER = False

    FRAME = data[2:]
    return HEADER, POINTER, FRAME
