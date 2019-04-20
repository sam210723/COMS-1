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

        # Set up instance globals
        self.mode = mode
        self.lastVCID = None
        self.seenVCDUChange = False

        # Generate CP_PDU CRC table once rather than on every CRC check
        self.crcTable = CPPDU(b'', 0).genCRCLUT()


    def data_in(self, data):
        """
        Handle data block from from OSP decoder
        :param data: 892 byte UDP data block (one VCDU)
        """

        """
        VCDU
        """
        # Parse VCDU
        currentVCDU = VCDU(data)
        
        # Check spacecraft is supported
        if currentVCDU.SC != "COMS-1":
            print("Spacecraft not supported (SCID: {})".format(currentVCDU.SCID))
            return

        # Wait for VCID change to avoid partial TP_Files (disabled after first change)
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
            #TODO: In-class print methods
            print("\n[VCID] {}: {}".format(currentVCDU.VCID, currentVCDU.VC))

        if currentVCDU.VCID == 63:
            # Discard fill packets
            return


        """
        MPDU
        """
        # Parse MPDU
        self.currentMPDU = MPDU(currentVCDU.MPDU)

        # Current MPDU contains a CP_PDU header
        if self.currentMPDU.HEADER:
            self.handleCPPDUHeader()

        # No CP_PDU header present in current MPDU
        else:
            #try:
                #self.currentCPPDU
            #except AttributeError:
                #return
            
            # Append MPDU data field to current CP_PDU
            self.currentCPPDU.append(self.currentMPDU.FRAME)
        
        # Flush output buffer
        sys.stdout.flush()


    def handleCPPDUHeader(self):
        """
        Handles CP_PDU headers
        """

        # If no data precedes CP_PDU header (first CP_PDU in TP_File)
        if self.currentMPDU.POINTER == 0:
            # Parse CP_PDU header
            self.currentCPPDU = CPPDU(self.currentMPDU.FRAME, self.currentMPDU.POINTER)

            # Add data from MPDU to new CP_PDU
            self.currentCPPDU.start(self.currentCPPDU.POST_HEADER_DATA)

            #TODO: Open new TP_File

            #TODO: In-class print methods
            print("  [CP_PDU] APID: {}, {}, #{}, LEN: {}, PRE: {}, POST {}".format(self.currentCPPDU.APID, self.currentCPPDU.SEQ, self.currentCPPDU.COUNTER, self.currentCPPDU.LENGTH + 1, len(self.currentCPPDU.PRE_HEADER_DATA), len(self.currentCPPDU.POST_HEADER_DATA)))

        # If data precedes CP_PDU header (last or middle CP_PDUs in TP_File)
        else:
            # Detect special EOF marker CP_PDU after last CP_PDU in TP_File
            if CPPDU(self.currentMPDU.FRAME, self.currentMPDU.POINTER).isEOFMarker():

                # CP_PDU CRC
                if self.currentCPPDU.checkCRC(self.crcTable):
                    print("    CRC OK")
                else:
                    print("    CRC ERROR")
                    return

                #TODO: Close current TP_File
            
            # CP_PDU Sequence Flags CONTINUE and LAST
            else:
                # Parse new CP_PDU header
                nextCPPDU = CPPDU(self.currentMPDU.FRAME, self.currentMPDU.POINTER)

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

            # Add data from MPDU to new CP_PDU
            self.currentCPPDU = nextCPPDU
            self.currentCPPDU.start(self.currentCPPDU.POST_HEADER_DATA)

            #TODO: In-class print methods
            print("  [CP_PDU] APID: {}, {}, #{}, LEN: {}, PRE: {}, POST: {}".format(self.currentCPPDU.APID, self.currentCPPDU.SEQ, self.currentCPPDU.COUNTER, self.currentCPPDU.LENGTH + 1, len(self.currentCPPDU.PRE_HEADER_DATA), len(self.currentCPPDU.POST_HEADER_DATA)))
