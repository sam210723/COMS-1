"""
VCDU.py
https://github.com/sam210723/COMS-1

Parses xRIT Virtual Channel Data Unit (VCDU) and returns the enclosed Multiplexing Protocol Data Unit (M_PDU)
"""

from tools import get_bits, get_bits_int

class VCDU:

    def __init__(self, data):
        self.data = data

        self.parse()


    def parse(self):
        header = self.data[:6]

        # Header fields
        self.VER = get_bits_int(header, 0, 2, 48)
        self.SCID = get_bits_int(header, 2, 8, 48)
        self.VCID = get_bits_int(header, 10, 6, 48)
        self.COUNT = get_bits_int(header, 16, 24, 48)
        self.REPLAY = get_bits_int(header, 40, 1, 48)
        self.SPARE = get_bits_int(header, 41, 7, 48)

        self.get_SC_name()
        self.get_VC_name()

        self.MPDU = self.data[6:]


    def get_SC_name(self):
        """
        Get name of Spacecraft by ID
        """

        if self.SCID == 195:
            self.SC = "COMS-1"
        else:
            self.SC = None
    

    def get_VC_name(self):
        """
        Get name of Virtual Channel by ID
        """

        if self.VCID == 0:
            self.VC = "VIS"
        elif self.VCID == 1:
            self.VC = "SWIR"
        elif self.VCID == 2:
            self.VC = "WV"
        elif self.VCID == 3:
            self.VC = "IR1"
        elif self.VCID == 4:
            self.VC = "IR2"
        elif self.VCID == 5:
            self.VC = "ANT"
        elif self.VCID == 6:
            self.VC = "ENC"
        elif self.VCID == 7:
            self.VC = "CMDPS"
        elif self.VCID == 8:
            self.VC = "NWP"
        elif self.VCID == 9:
            self.VC = "GOCI"
        elif self.VCID == 10:
            self.VC = "BINARY"
        elif self.VCID == 11:
            self.VC = "TYPHOON"
        elif self.VCID == 63:
            self.VC = "Fill"
        else:
            self.VC = None
