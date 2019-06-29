"""
ccsds.py
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
        self.VER = get_bits_int(header, 0, 2, 48)           # Virtual Channel Version
        self.SCID = get_bits_int(header, 2, 8, 48)          # Spacecraft ID
        self.VCID = get_bits_int(header, 10, 6, 48)         # Virtual Channel ID
        self.COUNTER = get_bits_int(header, 16, 24, 48)     # VCDU Counter
        self.REPLAY = get_bits_int(header, 40, 1, 48)       # Replay Flag
        self.SPARE = get_bits_int(header, 41, 7, 48)        # Spare (always b0000000)

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

        print("\n[VCID] {} {}: {}".format(self.SC, self.VCID, self.VC))


class M_PDU:
    """
    Parses CCSDS Multiplexing Protocol Data Unit (M_PDU)
    """

    def __init__(self, data):
        self.data = data
        self.parse()
    
    def parse(self):
        """
        Parse M_PDU header fields
        """

        header = self.data[:2]

        # Header fields
        #self.SPARE = get_bits(header, 0, 5, 16)            # Spare Field (always b00000)
        self.POINTER = get_bits_int(header, 5, 11, 16)      # First Pointer Header

        # Detect if M_PDU contains CP_PDU header
        if self.POINTER != 2047:  # 0x07FF
            self.HEADER = True
        else:
            self.HEADER = False
        
        self.PACKET = self.data[2:]
    
    def print_info(self):
        """
        Prints information about the current M_PDU to the console
        """

        if self.HEADER:
            print("    [M_PDU] HEADER: 0x{}".format(hex(self.POINTER)[2:].upper()))
        else:
            print("    [M_PDU]")


class CP_PDU:
    """
    Parses and assembles CCSDS Path Protocol Data Unit (CP_PDU)
    """

    def __init__(self, data):
        self.data = data
        self.PAYLOAD = None
        self.parse()
    
    def parse(self):
        """
        Parse CP_PDU header fields
        """

        header = self.data[:6]

        # Header fields
        self.VER = get_bits(header, 0, 3, 48)                   # Version (always b000)
        self.TYPE = get_bits(header, 3, 1, 48)                  # Type (always b0)
        self.SHF = get_bits(header, 4, 1, 48)                   # Secondary Header Flag
        self.APID = get_bits_int(header, 5, 11, 48)             # Application Process ID
        self.SEQ = get_bits_int(header, 16, 2, 48)              # Sequence Flag
        self.COUNTER = get_bits_int(header, 18, 14, 48)         # Packet Sequence Counter
        self.LENGTH = get_bits_int(header, 32, 16, 48) + 1      # Packet Length

        # Parse sequence flag
        seqn = ["CONTINUE", "FIRST", "LAST", "SINGLE"]
        self.SEQ = seqn[self.SEQ]

        # Add post-header data to payload
        self.PAYLOAD = self.data[6:]
    
    def append(self, data):
        """
        Append data to CP_PDU payload
        """

        self.PAYLOAD += data

    def finish(self, data, crclut):
        """
        Finish CP_PDU by checking length and CRC 
        """

        # Append last chunk of data
        self.append(data)

        # Check payload length against expected length
        plen = len(self.PAYLOAD)
        if plen != self.LENGTH:
            lenok = False
        else:
            lenok = True
        
        # Check payload CRC against expected CRC
        if not self.CRC(crclut):
            crcok = False
        else:
            crcok = True

        return lenok, crcok
    
    def is_EOF(self):
        """
        Checks if CP_PDU is the "EOF marker" CP_PDU of a TP_File.

        After a CP_PDU with the Sequence Flag of LAST, an extra CP_PDU is sent with the following:
            APID: 0
            Counter: 0
            Sequence Flag: CONTINUE (0)
            Length: 1
        """

        if self.COUNTER == 0 and self.APID == 0 and self.LENGTH == 1 and self.SEQ == "CONTINUE":
            return True
        else:
            return False
    
    def CRC(self, lut):
        """
        Calculate CRC-16/CCITT-FALSE 
        """

        initial = 0xFFFF
        crc = initial
        data = self.PAYLOAD[:-2]
        txCRC = self.PAYLOAD[-2:]

        # Calculate CRC
        for i in range(len(data)):
            lutPos = ((crc >> 8) ^ data[i]) & 0xFFFF
            crc = ((crc << 8) ^ lut[lutPos]) & 0xFFFF

        # Compare CRC from CP_PDU and calculated CRC
        if int(crc) == int.from_bytes(txCRC, byteorder='big'):
            return True
        else:
            return False

    def print_info(self):
        """
        Prints information about the current CP_PDU to the console
        """

        print("  [CP_PDU] APID: {}   SEQ: {}   #{}   LEN: {}".format(self.APID, self.SEQ, self.COUNTER, self.LENGTH))


class TP_File:
    """
    Parses and assembles CCSDS Transport Files (TP_File)
    """

    def __init__(self, data):
        self.data = data
        self.PAYLOAD = None
        self.parse()
    
    def parse(self):
        """
        Parse TP_File header fields
        """

        header = self.data[:10]

        # Header fields
        self.COUNTER = get_bits_int(header, 0, 16, 80)                # File Counter
        self.LENGTH = int(get_bits_int(header, 16, 64, 80)/8)         # File Length

        # Add post-header data to payload
        self.PAYLOAD = self.data[10:]
    
    def append(self, data):
        """
        Append data to TP_File payload
        """

        self.PAYLOAD += data

    def finish(self, data):
        """
        Finish CP_PDU by checking length
        """

        # Append last chunk of data
        self.append(data)

        # Check payload length against expected length
        plen = len(self.PAYLOAD)
        if plen != self.LENGTH:
            lenok = False
        else:
            lenok = True
        
        return lenok
    
    def print_info(self):
        """
        Prints information about the current TP_File to the console
        """

        # Get image band based on file counter
        if 1 <= self.COUNTER <= 10:
            band = "VIS"
            num = self.COUNTER
        elif 11 <= self.COUNTER <= 20:
            band = "SWIR"
            num = self.COUNTER - 10
        elif 21 <= self.COUNTER <= 30:
            band = "WV"
            num = self.COUNTER - 20
        elif 31 <= self.COUNTER <= 40:
            band = "IR1"
            num = self.COUNTER - 30
        elif 41 <= self.COUNTER <= 50:
            band = "IR2"
            num = self.COUNTER - 40
        else:
            band = "Other"
            num = "?"
        
        countType = " ({}, SEGMENT: {})".format(band, num)

        print("\n  [TP_File] COUNTER: {}{}   LENGTH: {}".format(self.COUNTER, countType, self.LENGTH))


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
