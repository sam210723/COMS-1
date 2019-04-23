"""
TPFile.py
https://github.com/sam210723/COMS-1

Assembles and parses xRIT Transport Files (TP_File) from multiple CP_PDUs
"""

import os
from tools import get_bits, get_bits_int

class TPFile:

    def __init__(self, data):
        self.data = data

        self.parse()
    

    def parse(self):
        header = self.data[:10]

        # Header fields
        self.COUNTER = get_bits_int(header, 0, 16, 80)                # File Counter
        self.LENGTH = get_bits_int(header, 16, 64, 80)                # File Length
    

    def start(self, data):
        """
        Creates full TP_File data block for data to be appended to
        """

        self.fullTPFile = data
    

    def append(self, data):
        """
        Appends data to full TP_File data block
        """

        self.fullTPFile += data
    

    def get_data(self):
        """
        Returns full S_PDU contained in complete TP_File without leading header bytes
        """

        return self.fullTPFile[10:]
    
    
    def close(self, path):
        """
        Writes encrypted S_PDU contained in complete TP_File to temp directory
        """

        #TODO: Check length against length header

        fpath = path + "\\spdu.bin"

        file = open(fpath, mode='wb')
        file.write(self.get_data())
        file.close()

        return
    

    def print_info(self):
        """
        Prints information about the current TP_File to the console
        """

        # Get image band based on file counter
        if 0 <= self.COUNTER <= 9:
            band = "VIS"
            num = self.COUNTER
        elif 10 <= self.COUNTER <= 19:
            band = "SWIR"
            num = self.COUNTER - 10
        elif 20 <= self.COUNTER <= 29:
            band = "WV"
            num = self.COUNTER - 20
        elif 30 <= self.COUNTER <= 39:
            band = "IR1"
            num = self.COUNTER - 30
        elif 40 <= self.COUNTER <= 49:
            band = "IR2"
            num = self.COUNTER - 40
        else:
            band = "Other"
            num = "?"
        
        countType = " ({}, SEGMENT: {})".format(band, num)

        print("\n    [TP_File] COUNTER: {}{}   LENGTH: {}".format(self.COUNTER, countType, int(self.LENGTH/8)))
