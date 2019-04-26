"""
assembler.py
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
        print("      Parsing xRIT headers...")

        primaryHeader = self.data[:16]

        # Header fields
        self.HEADER_TYPE = get_bits_int(primaryHeader, 0, 8, 128)               # File Counter (always 0x00)
        self.HEADER_LEN = get_bits_int(primaryHeader, 8, 16, 128)               # Header Length (always 0x10)
        self.FILE_TYPE = get_bits_int(primaryHeader, 24, 8, 128)                # File Type
        self.TOTAL_HEADER_LEN = get_bits_int(primaryHeader, 32, 32, 128)        # Total xRIT Header Length
        self.DATA_LEN = get_bits_int(primaryHeader, 64, 64, 128)                # Data Field Length

        if self.FILE_TYPE == 0:
            self.FILE_TYPE = "Image Data"
        elif self.FILE_TYPE == 1:
            self.FILE_TYPE = "GTS Message"
        elif self.FILE_TYPE == 2:
            self.FILE_TYPE = "Alphanumeric Text"
        elif self.FILE_TYPE == 3:
            self.FILE_TYPE = "Encryption Key Message"
        elif self.FILE_TYPE == 128:
            self.FILE_TYPE = "CMDPS Analysis Data"
        elif self.FILE_TYPE == 129:
            self.FILE_TYPE = "NWP Data"
        elif self.FILE_TYPE == 130:
            self.FILE_TYPE = "GOCI Data"
        elif self.FILE_TYPE == 131:
            self.FILE_TYPE = "Typhoon Info"

        print("        TYPE:      {}".format(self.FILE_TYPE))
        #print("        HEADER LENGTH: {} bits".format(self.TOTAL_HEADER_LEN))
        #print("        DATA LENGTH: {} bits".format(self.DATA_LEN))


        # Loop through headers until Annotation Text header (type 4)
        offset = self.HEADER_LEN
        nextHeader = self.get_next_header(offset)

        while nextHeader != 4:
            offset += self.get_header_len(offset)
            nextHeader = self.get_next_header(offset)
        
        # Parse Annotation Text header (type 4)
        athLen = self.get_header_len(offset)
        self.OUTPUT_FILE_NAME = self.data[offset + 3 : offset + athLen].decode('utf-8')
        print("        FILE NAME: {}".format(self.OUTPUT_FILE_NAME))

        return


    def get_next_header(self, offset):
        return int.from_bytes(self.data[offset : offset + 1], byteorder='big')
    
    
    def get_header_len(self, offset):
        return int.from_bytes(self.data[offset + 1 : offset + 3], byteorder='big')


    def decrypt(self):
        #print("      Decrypting xRIT payload...")
        #print("        KEY: 0x{}".format("--"))
        return
    

    def save(self):
        print("      Saving xRIT file...")

        # Split file name into components
        fnameSplit = self.OUTPUT_FILE_NAME.split("_")
        fType = fnameSplit[0]
        obMode = fnameSplit[1]
        seqNum = fnameSplit[2]
        specCh = fnameSplit[3]
        txDate = fnameSplit[4]
        txTime = fnameSplit[5]
        segNum = fnameSplit[6][:2]
        fExt = self.OUTPUT_FILE_NAME.split(".")[1]

        '''
        print("File Type: " + fType)
        print("Observation Mode: " + obMode)
        print("Sequence Number: " + seqNum)
        print("Spectral Channel: " + specCh)
        print("Transmission Date: " + txDate)
        print("Transmission Time: " + txTime)
        print("Segment Number: " + segNum)
        print("Extension: " + fExt)
        '''
        outPath = self.OUTPUT_FILE_NAME
        print(outPath)
        #outFile = open(outPath, mode="wb")

        return

    def print_info(self):
        #print("        [NEW FILE] ")
        return
