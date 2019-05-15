"""
demuxer.py
https://github.com/sam210723/COMS-1

Coordinates CCSDS demuxing from VCDU layer to xRIT file layer.
"""

import sys
from VCDU import VCDU
from MPDU import MPDU
from CPPDU import CPPDU
from TPFile import TPFile
from assembler import Assembler

class Demuxer:

    def __init__(self, mode, dirs):
        """
        Initialise Demuxer class
        :param mode: Specify LRIT or HRIT mode (currently unused)
        """

        # Set up instance globals
        self.mode = mode
        self.dirs = dirs
        self.lastVCID = None
        self.VCDUCounters = {}
        self.seenVCDUChange = False
        self.currentTPFile = None

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
        
        # Check VCDU counter continuity
        if currentVCDU.VCID in self.VCDUCounters:
            if currentVCDU.COUNT != (self.VCDUCounters[currentVCDU.VCID] + 1):
                diff = currentVCDU.COUNT - self.VCDUCounters[currentVCDU.VCID] - 1
                if diff != -1:
                    print("DROPPED {} FRAMES   (Current: {}   Last: {}   VCID: {})".format(diff, currentVCDU.COUNT, self.VCDUCounters[currentVCDU.VCID], currentVCDU.VCID))
        
        self.VCDUCounters[currentVCDU.VCID] = currentVCDU.COUNT

        # Check spacecraft is supported
        if currentVCDU.SC != "COMS-1":
            print("Spacecraft not supported (SCID: {})".format(currentVCDU.SCID))
            return

        # Wait for VCID change to avoid partial TP_Files (disabled after first change)
        if self.lastVCID == None:
            # First VCDU (demuxer just started)
            self.lastVCID = currentVCDU.VCID
            currentVCDU.print_info()
            return
        elif self.lastVCID == currentVCDU.VCID:
            # VCID has not changed
            if not self.seenVCDUChange:
                # Never seen VCID change, ignore data (avoids starting demux part way through a TP_File)
                return
        else:
            # VCID has changed

            # Trigger TP_File processing on VCID change
            if self.lastVCID != 63:
                try:
                    self.finish_tpfile()
                except AttributeError:
                    pass

            self.seenVCDUChange = True
            self.lastVCID = currentVCDU.VCID

            # Display VCID change
            currentVCDU.print_info()

        if currentVCDU.VCID == 63:
            # Discard fill packets
            return


        """
        M_PDU
        """
        # Parse M_PDU
        self.currentMPDU = MPDU(currentVCDU.MPDU)

        # Current M_PDU contains a CP_PDU header
        if self.currentMPDU.HEADER:
            self.handle_CPPDU_header()

        # No CP_PDU header present in current M_PDU
        else:
            # Append M_PDU data field to current CP_PDU
            self.currentCPPDU.append(self.currentMPDU.FRAME)
            print(".", end='')

        # Flush output buffer
        sys.stdout.flush()


    def handle_CPPDU_header(self):
        """
        Handles CP_PDU headers and triggers TP_File handling
        """

        # If no data precedes CP_PDU header (first CP_PDU in TP_File)
        if self.currentMPDU.POINTER == 0:
            # Parse CP_PDU header
            self.currentCPPDU = CPPDU(self.currentMPDU.FRAME, self.currentMPDU.POINTER)

            # Add data from M_PDU to new CP_PDU
            self.currentCPPDU.start(self.currentCPPDU.POST_HEADER_DATA)


        # If data precedes CP_PDU header (last or middle CP_PDUs in TP_File)
        else:
            # Detect special EOF marker CP_PDU after last CP_PDU in TP_File
            if CPPDU(self.currentMPDU.FRAME, self.currentMPDU.POINTER).is_EOF_marker():
                #self.finish_tpfile()
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
                
                if self.currentTPFile == None:
                    # Start new TP_File and add complete CP_PDU
                    self.currentTPFile = TPFile(self.currentCPPDU.get_data())
                    self.currentTPFile.start(self.currentCPPDU.get_data())
                else:
                    # Append complete CP_PDU to current TP_File
                    self.currentTPFile.append(self.currentCPPDU.get_data())

                # Continue on to new CP_PDU
                if self.currentCPPDU.SEQ != "LAST":
                    # Add data from M_PDU to new CP_PDU
                    self.currentCPPDU = nextCPPDU
                    self.currentCPPDU.start(self.currentCPPDU.POST_HEADER_DATA)

        self.currentCPPDU.print_info()
        print("    .", end='')
    

    def finish_tpfile(self):
        # Append final bytes of current CP_PDU from current M_PDU before EOF marker CP_PDU header
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
        
        # Append complete CP_PDU to current TP_File
        self.currentTPFile.append(self.currentCPPDU.get_data())

        # Assemble completed TP_File into decrypted xRIT file
        self.assemble_file()


    def assemble_file(self):
        # Print TP_File information
        self.currentTPFile.print_info()

        # Assemble xRIT file
        xritFile = Assembler(self.currentTPFile.get_data(), self.dirs)
        xritFile.print_info()

        # Clear current TP_File global
        self.currentTPFile = None
