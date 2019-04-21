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
        self.crcTable = CPPDU(b'', 0).gen_CRC_LUT()


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
            print("\n\n[VCID] {}: {}".format(currentVCDU.VCID, currentVCDU.VC))

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
            self.handle_CPPDU_header()

        # No CP_PDU header present in current MPDU
        else:
            #TODO: Find cause of AttibuteError
            try:
                self.currentCPPDU
            except AttributeError as e:
                print(e)
                return
            
            # Append MPDU data field to current CP_PDU
            self.currentCPPDU.append(self.currentMPDU.FRAME)
            print(".", end='')

        # Flush output buffer
        sys.stdout.flush()


    def handle_CPPDU_header(self):
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

        # If data precedes CP_PDU header (last or middle CP_PDUs in TP_File)
        else:
            # Detect special EOF marker CP_PDU after last CP_PDU in TP_File
            if CPPDU(self.currentMPDU.FRAME, self.currentMPDU.POINTER).is_EOF_marker():
                # Append final bytes of current CP_PDU from current MPDU before EOF marker CP_PDU header
                self.currentCPPDU.append(self.currentMPDU.FRAME[:self.currentMPDU.POINTER])

                # CP_PDU CRC
                if self.currentCPPDU.check_CRC(self.crcTable):
                    print("\n    CRC:           OK")
                else:
                    print("\n    CRC:           ERROR")
                
                # CP_PDU length check
                if self.currentCPPDU.LENGTH == len(self.currentCPPDU.fullCPPDU):
                    print("    LENGTH:        OK")
                else:
                    ex = self.currentCPPDU.LENGTH
                    ac = len(self.currentCPPDU.fullCPPDU)
                    diff = ac - ex
                    print("    LENGTH:        ERROR (EXPECTED: {}, ACTUAL: {}, DIFF: {})".format(ex, ac, diff))

                #TODO: Close current TP_File

                return
            
            # CP_PDU Sequence Flags CONTINUE and LAST
            else:
                if self.currentCPPDU.SEQ != "LAST":
                    # Parse new CP_PDU header
                    nextCPPDU = CPPDU(self.currentMPDU.FRAME, self.currentMPDU.POINTER)

                # Append data from current CP_PDU before header of next CP_PDU
                self.currentCPPDU.append(nextCPPDU.PRE_HEADER_DATA)

                # CP_PDU CRC
                if self.currentCPPDU.check_CRC(self.crcTable):
                    print("\n    CRC:           OK")
                else:
                    print("\n    CRC:           ERROR")

                # CP_PDU continuity check
                if self.currentCPPDU.COUNTER == (nextCPPDU.COUNTER - 1):
                    print("    CONTINUITY:    OK")
                else:
                    print("    CONTINUITY:    ERROR")
                
                # CP_PDU length check
                if self.currentCPPDU.LENGTH == len(self.currentCPPDU.fullCPPDU):
                    print("    LENGTH:        OK")
                else:
                    ex = self.currentCPPDU.LENGTH
                    ac = len(self.currentCPPDU.fullCPPDU)
                    diff = ac - ex
                    print("    LENGTH:        ERROR (EXPECTED: {}, ACTUAL: {}, DIFF: {})".format(ex, ac, diff))

                if self.currentCPPDU.SEQ != "LAST":
                    # Add data from MPDU to new CP_PDU
                    self.currentCPPDU = nextCPPDU
                    self.currentCPPDU.start(self.currentCPPDU.POST_HEADER_DATA)

        #TODO: In-class print methods
        print("  [CP_PDU] APID: {}, {}, #{}, LEN: {}, PRE: {}, POST: {}".format(self.currentCPPDU.APID, self.currentCPPDU.SEQ, self.currentCPPDU.COUNTER, self.currentCPPDU.LENGTH, len(self.currentCPPDU.PRE_HEADER_DATA), len(self.currentCPPDU.POST_HEADER_DATA)))
        print("    .", end='')
