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
    
    def get_SC(self, id):
        """
        Get name of spacecraft by ID
        """

        if self.SCID == 195:
            return "COMS-1"
        else:
            return None
    
    def get_VC(self, vcid):
        """
        Get name of Virtual Channel by ID
        """

        if self.VCID == 0:
            return "VIS"
        elif self.VCID == 1:
            return "SWIR"
        elif self.VCID == 2:
            return "WV"
        elif self.VCID == 3:
            return "IR1"
        elif self.VCID == 4:
            return "IR2"
        elif self.VCID == 5:
            return "ANT"
        elif self.VCID == 6:
            return "ENC"
        elif self.VCID == 7:
            return "CMDPS"
        elif self.VCID == 8:
            return "NWP"
        elif self.VCID == 9:
            return "GOCI"
        elif self.VCID == 10:
            return "BINARY"
        elif self.VCID == 11:
            return "TYPHOON"
        elif self.VCID == 63:
            return "FILL"
        else:
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
