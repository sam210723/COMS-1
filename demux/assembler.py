"""
SPDU.py
https://github.com/sam210723/COMS-1

Parses and decrypts S_PDUs and outputs plain xRIT files
"""

import os
from tools import get_bits, get_bits_int

class Assembler:

    def __init__(self, data):
        self.data = data

        self.parse()
        self.decrypt()
        self.save()
    

    def parse(self):
        print("      Parsing xRIT header...")

        #header = self.data[:10]

        # Header fields
        #self.COUNTER = get_bits_int(header, 0, 16, 80)                # File Counter
        #self.LENGTH = get_bits_int(header, 16, 64, 80)                # File Length
    

    def decrypt(self):
        #print("      Decrypting xRIT payload...")
        #print("        KEY: 0x{}".format("--"))
        return
    

    def save(self):
        #print("      Saving xRIT file...")
        return

    def print_info(self):
        #print("        [NEW FILE] ")
        return
