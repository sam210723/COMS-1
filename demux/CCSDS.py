"""
CCSDS.py
https://github.com/sam210723/COMS-1

Parsing and assembly functions for all CCSDS protocol layers
"""

from tools import get_bits, get_bits_int


class VCDU:
    """
    Parses CCSDS Virtual Channel Data Unit (VCDU)
    """

    def __init__(self, data):
        self.data = data
        self.parse()
    
    def parse(self):
        """
        Parse VCDU header fields
        """

        header = self.data[:6]

        # Header fields
        self.VER = get_bits_int(header, 0, 2, 48)          # Virtual Channel Version
        self.SCID = get_bits_int(header, 2, 8, 48)         # Spacecraft ID
        self.VCID = get_bits_int(header, 10, 6, 48)        # Virtual Channel ID
        self.COUNT = get_bits_int(header, 16, 24, 48)      # VCDU Counter
        self.REPLAY = get_bits_int(header, 40, 1, 48)      # Replay Flag
        self.SPARE = get_bits_int(header, 41, 7, 48)       # Spare (always b0000000)

        # Spacecraft and virtual channel names
        self.SC = self.get_SC(self.SCID)
        self.VC = self.get_VC(self.VCID)

        # M_PDU contained in VCDU
        self.MPDU = self.data[6:]
    
    def get_SC(self, scid):
        """
        Get name of spacecraft by ID
        """

        scname = {}
        scname[195] = "COMS-1"

        try:
            return scname[scid]
        except KeyError:
            return None
    
    def get_VC(self, vcid):
        """
        Get name of Virtual Channel by ID
        """
        vcname = {}
        vcname[0] = "VIS"
        vcname[1] = "SWIR"
        vcname[2] = "WV"
        vcname[3] = "IR1"
        vcname[4] = "IR2"
        vcname[5] = "ANT"
        vcname[6] = "ENC"
        vcname[7] = "CMDPS"
        vcname[8] = "NWP"
        vcname[9] = "GOCI"
        vcname[10] = "BINARY"
        vcname[11] = "TYPHOON"
        vcname[63] = "FILL"

        try:
            return vcname[vcid]
        except KeyError:
            return None

    def print_info(self):
        """
        Prints information about the current VCDU to the console
        """

        print("\n\n[VCID] {} {}: {}".format(self.SC, self.VCID, self.VC))


class M_PDU:
    """
    Parses CCSDS Multiplexing Protocol Data Unit (M_PDU)
    """

    def __init__(self):
        return


class CP_PDU:
    """
    Parses and assembles CCSDS Path Protocol Data Unit (CP_PDU)
    """

    def __init__(self):
        return


class TP_File:
    """
    Parses and assembles CCSDS Transport Files (TP_File)
    """

    def __init__(self):
        return


class S_PDU:
    """
    Parses CCSDS Session Protocol Data Unit (S_PDU)
    """

    def __init__(self):
        return


class xRIT:
    """
    Parses and assembles CCSDS xRIT Files (xRIT_Data)
    """

    def __init__(self):
        return
