"""
demuxer.py
https://github.com/sam210723/COMS-1

Coordinates CCSDS demuxing from VCDU layer to xRIT file layer.
"""

import sys
from VCDU import VCDU
from MPDU import MPDU
from CPPDU import CPPDU

class Demuxer:

    def __init__(self, mode):
        """
        Initialise Demuxer class
        :param mode: Specify LRIT or HRIT mode (currently unused)
        """

        self.mode = mode

        self.lastVCID = None
        self.seenVCDUChange = False
        self.crcTable = CPPDU(b'', 0).genCRCLUT()


    def data_in(self, data):
        # Parse VCDU
        currentVCDU = VCDU(data)
        
        # Stop demuxing if spacecraft not supported
        if currentVCDU.SC != "COMS-1":
            print("Spacecraft not supported (SCID: {})".format(currentVCDU.SCID))
            return

        # Wait for VCID to change before begining to parse (avoids partial TP_Files)
        # Check disabled after first VCID change
        if self.lastVCID == None:
            # First VCDU (demuxer just started)
            self.lastVCID = currentVCDU.VCID
            return
        elif self.lastVCID == currentVCDU.VCID:
            # VCID has not changed
            if not self.seenVCDUChange:
                # Never seen VCID change, ignore data
                return
        else:
            # VCID has changed
            self.seenVCDUChange = True      
            self.lastVCID = currentVCDU.VCID

            # Show VCID change
            print("\n[VCID] {}: {}".format(currentVCDU.VCID, currentVCDU.VC))

        if currentVCDU.VCID == 63:
            # Discard fill packets
            return

        # Parse MPDU
        currentMPDU = MPDU(currentVCDU.MPDU)

        # Current MPDU contains a CP_PDU header
        if currentMPDU.HEADER:
            if currentMPDU.POINTER == 0:
                # Parse CP_PDU header
                self.currentCPPDU = CPPDU(currentMPDU.FRAME, currentMPDU.POINTER)
                print("  [CP_PDU] APID: {}, {}, #{}, LEN: {}, PRE: {}, POST {}".format(self.currentCPPDU.APID, self.currentCPPDU.SEQ, self.currentCPPDU.COUNTER, self.currentCPPDU.LENGTH + 1, len(self.currentCPPDU.PRE_HEADER_DATA), len(self.currentCPPDU.POST_HEADER_DATA)))

                # Add data from MPDU to new CP_PDU
                self.currentCPPDU.start(self.currentCPPDU.POST_HEADER_DATA)
            else:
                # Detect extra CP_PDU after last CP_PDU in TP_File
                tempCPPDU = CPPDU(currentMPDU.FRAME, currentMPDU.POINTER)
                if tempCPPDU.COUNTER == 0 and tempCPPDU.APID == 0 and tempCPPDU.LENGTH == 0 and tempCPPDU.SEQ == "CONTINUE":
                     # CP_PDU CRC
                    if self.currentCPPDU.checkCRC(self.crcTable):
                        print("    CRC OK")
                    else:
                        print("    CRC ERROR")
                    return
                else:
                    # Parse new CP_PDU header
                    nextCPPDU = CPPDU(currentMPDU.FRAME, currentMPDU.POINTER)

                    # Append data from current CP_PDU before header of next CP_PDU
                    self.currentCPPDU.append(nextCPPDU.PRE_HEADER_DATA)

                    # CP_PDU CRC
                    if self.currentCPPDU.checkCRC(self.crcTable):
                        print("    CRC OK")
                    else:
                        print("    CRC ERROR")

                    if self.currentCPPDU.COUNTER == (nextCPPDU.COUNTER - 1):
                        print("    CONTINUITY OK")
                    else:
                        print("    CONTINUITY ERROR")

                #TODO: Append to current TP_File

                # Add data from MPDU to new CP_PDU
                self.currentCPPDU = nextCPPDU
                print("  [CP_PDU] APID: {}, {}, #{}, LEN: {}, PRE: {}, POST: {}".format(self.currentCPPDU.APID, self.currentCPPDU.SEQ, self.currentCPPDU.COUNTER, self.currentCPPDU.LENGTH + 1, len(self.currentCPPDU.PRE_HEADER_DATA), len(self.currentCPPDU.POST_HEADER_DATA)))
                self.currentCPPDU.start(self.currentCPPDU.POST_HEADER_DATA)
        else:
            #try:
                #self.currentCPPDU
            #except AttributeError:
                #return
            
            # Append data from MPDU to current CP_PDU if no header is present
            self.currentCPPDU.append(currentMPDU.FRAME)
        
        sys.stdout.flush()
