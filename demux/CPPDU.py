"""
CPPDU.py
https://github.com/sam210723/COMS-1

Parses xRIT CCSDS Path Protocol Data Unit (CP_PDU) header and returns associated chunks of CP_PDU
"""

from tools import get_bits, get_bits_int

class CPPDU:

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset

        self.parse()
    

    def parse(self):
        header = self.data[self.offset : self.offset + 6]

        # Header fields
        self.VER = get_bits(header, 0, 3, 48)                # Version (always b000)
        self.TYPE = get_bits(header, 3, 1, 48)               # Type (always b0)
        self.SHF = get_bits(header, 4, 1, 48)                # Secondary Header Flag
        self.APID = get_bits_int(header, 5, 11, 48)          # Application Process ID
        self.SEQ = get_bits_int(header, 16, 2, 48)           # Sequence Flag
        self.COUNTER = get_bits_int(header, 18, 14, 48)      # Packet Sequence Counter
        self.LENGTH = get_bits_int(header, 32, 16, 48)       # Packet Length

        if self.SEQ == 0:
            self.SEQ = "CONTINUE"
        elif self.SEQ == 1:
            self.SEQ = "FIRST"
        elif self.SEQ == 2:
            self.SEQ = "LAST"
        elif self.SEQ == 3:
            self.SEQ = "SINGLE"
        
        self.PRE_HEADER_DATA = self.data[0 : self.offset]
        self.POST_HEADER_DATA = self.data[self.offset + 6:]
    
    
    def start(self, data):
        """
        Creates full CP_PDU data block for data to be appended to
        """

        self.fullCPPDU = data
    

    def append(self, data):
        """
        Appends data to full CP_PDU data block
        """

        self.fullCPPDU += data


    def getData(self):
        """
        Returns full CP_PDU without trailing CRC bytes (max 8190 bytes)
        """

        return self.fullCPPDU[:-2]


    def checkCRC(self, lut):
        """
        Calculate CRC-16/CCITT-FALSE 
        """

        initial = 0xFFFF
        crc = initial
        data = self.getData()
        txCRC = self.fullCPPDU[-2:]

        # Calculate CRC
        for i in range(len(data)):
            lutPos = ((crc >> 8) ^ data[i]) & 0xFFFF
            crc = ((crc << 8) ^ lut[lutPos]) & 0xFFFF

        # Compare CRC from CP_PDU and calculated CRC
        if int(crc) == int.from_bytes(txCRC, byteorder='big'):
            return True
        else:
            return False


    def genCRCLUT(self):
        """
        Creates Lookup Table for CRC-16/CCITT-FALSE calculation
        """

        crcTable = []
        poly = 0x1021
        
        for i in range(256):
            crc = 0
            c = i << 8

            for j in range(8):
                if (crc ^ c) & 0x8000:
                    crc = (crc << 1) ^ poly
                else:
                    crc = crc << 1

                c = c << 1
                crc = crc & 0xFFFF

            crcTable.append(crc)

        return crcTable
    

    def isEOFMarker(self):
        """
        Checks if CP_PDU is the "EOF marker" CP_PDU of a TP_File.

        After a CP_PDU with the Sequence Flag of LAST, an extra CP_PDU is sent with the following:
            APID: 0
            Counter: 0
            Sequence Flag: CONTINUE (0)
            Length: 0
        This can be used to trigger processing of a completed TP_File, hence "EOF marker".
        """

        if self.COUNTER == 0 and self.APID == 0 and self.LENGTH == 0 and self.SEQ == "CONTINUE":
            return True
        else:
            return False
