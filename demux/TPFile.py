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

        print("\n    [TP_File] COUNTER: {}   LENGTH: {}".format(self.COUNTER, int(self.LENGTH/8)))
