"""
MPDU.py
https://github.com/sam210723/COMS-1

Parses xRIT Multiplexing Protocol Data Unit (M_PDU) and returns part of a CCSDS Path Protocol Data Unit (CP_PDU)
"""

from tools import get_bits, get_bits_int

class MPDU:

    def __init__(self, data):
        self.data = data

        self.parse()
    

    def parse(self):
        header = self.data[:2]

        # Header fields
        self.SPARE = get_bits(header, 0, 5, 16)             # Spare Field (always b00000)
        self.POINTER = get_bits_int(header, 5, 11, 16)      # First Pointer Header

        # Detect if M_PDU contains CP_PDU header
        if self.POINTER != 2047:  # 0x07FF
            self.HEADER = True
        else:
            self.HEADER = False
        
        self.FRAME = self.data[2:]
