"""
CPPDU.py
https://github.com/sam210723/COMS-1

Parses xRIT CCSDS Path Protocol Data Unit (CP_PDU) header and returns associated chunks of CP_PDU
"""

from tools import getBits

def parseCPPDU(data, offset):
    headerBytes = data[offset : offset + 6]

    # Header Fields
    #VER = getBits(headerBytes, 0, 3, 48)                    # Version (always b000)
    #TYPE = getBits(headerBytes, 3, 1, 48)                   # Type (always b0)
    SHF = getBits(headerBytes, 4, 1, 48)                    # Secondary Header Flag
    APID = int(getBits(headerBytes, 5, 11, 48), 2)          # APID
    SEQ = int(getBits(headerBytes, 16, 2, 48), 2)           # Sequence Flag
    COUNT = int(getBits(headerBytes, 18, 14, 48), 2)        # Packet Sequence Counter
    LENGTH = int(getBits(headerBytes, 32, 16, 48), 2)       # Packet Length

    if SEQ == 3:
        SEQ = "SINGLE"
    elif SEQ == 1:
        SEQ = "FIRST"
    elif SEQ == 0:
        SEQ = "CONTINUE"
    elif SEQ == 2:
        SEQ = "LAST"

    #print("\n  [CP_PDU] SHF: {}   APID: {}   SEQ: {}   COUNT: {}   LENGTH: {}".format(SHF, APID, SEQ, COUNT, LENGTH))

    PRECHUNK = data[0:offset]           # Data before CP_PDU header
    POSTCHUNK = data[offset + 6:]       # Data after CP_PDU header
    
    return APID, SEQ, COUNT, PRECHUNK, POSTCHUNK


def checkCRC(data, txCRC, lut):
    """
    Calculate CRC-16/CCITT-FALSE 
    """

    initial = 0xFFFF
    crc = initial

    # Calculate CRC
    for i in range(len(data)):
        lutPos = ((crc >> 8) ^ data[i]) & 0xFFFF
        crc = ((crc << 8) ^ lut[lutPos]) & 0xFFFF
    
    # Compare CRC from CP_PDU and calculated CRC
    if int(crc) == int.from_bytes(txCRC, byteorder='big'):
        return True
    else:
        return False



def genCRCLUT():
    """
    Creates Lookup Table for CRC-16/CCITT-FALSE calculation
    """

    crcTable = []
    poly = 0x1021
    initial = 0xFFFF
    for i in range(256):
        crc = 0
        c = i << 8

        for j in range(8):
            if (crc ^ c) & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc = crc << 1

            c = c << 1
            crc = crc & 0xFFFF

        crcTable.append(crc)
    
    return crcTable
