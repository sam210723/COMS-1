"""
VCDU.py
https://github.com/sam210723/COMS-1

Parses xRIT Virtual Channel Data Unit (VCDU) and returns the enclosed Multiplexing Protocol Data Unit (M_PDU)
"""

from tools import getBits

def parseVCDU(data):
    headerBytes = data[0:6]
    
    # Header Fields
    #VERS = int(getBits(headerBytes, 0, 2, 48), 2)          # VCID Version (always 0x01)
    SCID = int(getBits(headerBytes, 2, 8, 48), 2)           # Spacecraft ID
    VCID = int(getBits(headerBytes, 10, 6, 48), 2)          # Virtual Channel ID
    COUNT = int(getBits(headerBytes, 16, 24, 48), 2)        # VCID Counter (0-16,777,215)
    #SIG = getBits(headerBytes, 40, 8, 48)                  # Signaling Field (always 0x00)

    SC = getSCName(SCID)
    VC = getVCName(VCID)

    print("[VCDU] {}\n SCID: {} ({})\n VCID: {} ({})\n".format(COUNT, SC, SCID, VC, VCID))

    MPDU = data[6:]
    return SCID, VCID, COUNT, MPDU


def getSCName(SCID):
    """
    Get name of Spacecraft by ID
    """

    if SCID == 195:
        SC = "COMS-1"
    else:
        SC = None
    
    return SC

def getVCName(VCID):
    """
    Get name of Virtual Channel by ID
    """

    if VCID == 0:
        VC = "VIS"
    elif VCID == 1:
        VC = "SWIR"
    elif VCID == 2:
        VC = "WV"
    elif VCID == 3:
        VC = "IR1"
    elif VCID == 4:
        VC = "IR2"
    elif VCID == 5:
        VC = "ANT"
    elif VCID == 6:
        VC = "ENC"
    elif VCID == 7:
        VC = "CMDPS"
    elif VCID == 8:
        VC = "NWP"
    elif VCID == 9:
        VC = "GOCI"
    elif VCID == 10:
        VC = "BINARY"
    elif VCID == 11:
        VC = "TYPHOON"
    elif VCID == 63:
        VC = "Fill"
    else:
        VC = None
    
    return VC