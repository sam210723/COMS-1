"""
demuxer.py
https://github.com/sam210723/COMS-1

Coordinates CCSDS demuxing from VCDU layer to xRIT file layer.
"""

from VCDU import VCDU
from MPDU import MPDU

class Demuxer:
    
    def __init__(self, mode):
        """
        Initialise Demuxer class
        :param mode: Specify LRIT or HRIT mode
        """

        self.mode = mode


    def data_in(self, data):
        # Parse VCDU
        currentVCDU = VCDU(data)

        currentMPDU = MPDU(currentVCDU.MPDU)
