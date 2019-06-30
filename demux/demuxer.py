"""
demuxer.py
https://github.com/sam210723/COMS-1
"""

import ccsds as CCSDS
from collections import deque
from time import sleep
from threading import Thread
from tools import CCITT_LUT

class Demuxer:
    """
    Coordinates demultiplexing of CCSDS virtual channels into xRIT files.
    """

    def __init__(self, downlink, v, d):
        """
        Initialises demuxer class
        """
        
        # Configure instance globals
        self.rxq = deque()              # Data receive queue
        self.coreReady = False          # Core thread ready state
        self.coreStop = False           # Core thread stop flag
        self.verbose = v                # Verbose output flag
        self.dumpPath = d               # VCDU dump file path
        self.channelHandlers = {}       # List of channel handlers

        if downlink == "LRIT":
            self.coreWait = 54          # Core loop delay in ms for LRIT (108.8ms per packet @ 64 kbps)
        elif downlink == "HRIT":
            self.coreWait = 1           # Core loop delay in ms for HRIT (2.2ms per packet @ 3 Mbps)

        # Start core demuxer thread
        demux_thread = Thread()
        demux_thread.name = "DEMUX CORE"
        demux_thread.run = self.demux_core
        demux_thread.start()

    def demux_core(self):
        """
        Distributes VCDUs to channel handlers.
        """
        
        # Indicate core thread has initialised
        self.coreReady = True

        # Thread globals
        lastVCID = None             # Last VCID seen
        seenVCIDChange = False      # Seen changed in VCID flag
        crclut = CCITT_LUT()        # CP_PDU CRC LUT

        # Open VCDU dump file
        dumpFile = None
        if self.dumpPath != None:
            dumpFile = open(self.dumpPath, 'wb+')

        # Thread loop
        while not self.coreStop:
            # Pull next packet from queue
            packet = self.pull()
            
            # If queue is not empty
            if packet != None:
                # Parse VCDU
                vcdu = CCSDS.VCDU(packet)

                # Dump raw VCDU to file
                if dumpFile != None and vcdu.VCID != 63:
                    dumpFile.write(packet)

                # Check spacecraft is supported
                if vcdu.SC != "COMS-1":
                    if self.verbose: print("SPACECRAFT \"{}\" NOT SUPPORTED".format(vcdu.SCID))
                    continue

                # Check for VCID change
                if lastVCID == None:                # First VCDU (demuxer just started)
                    if self.verbose: print()
                    vcdu.print_info()
                    print("  WAITING FOR VCID TO CHANGE\n")
                    lastVCID = vcdu.VCID
                    continue
                elif lastVCID == vcdu.VCID:         # VCID has not changed
                    if not seenVCIDChange:
                        continue                    # Never seen VCID change, ignore data (avoids partial TP_Files)
                    else:
                        pass
                elif lastVCID != vcdu.VCID:         # VCID has changed
                    if self.verbose: print()
                    vcdu.print_info()
                    seenVCIDChange = True
                    lastVCID = vcdu.VCID
                
                # Discard fill packets
                if vcdu.VCID == 63:
                    continue
                
                # Check channel handler for current VCID exists
                try:
                    self.channelHandlers[vcdu.VCID]
                except KeyError:
                    # Create new channel handler instance
                    self.channelHandlers[vcdu.VCID] = Channel(vcdu.VCID, self.verbose, crclut)
                    if self.verbose: print("  CREATED NEW CHANNEL HANDLER\n")

                # Pass VCDU to appropriate channel handler
                self.channelHandlers[vcdu.VCID].data_in(vcdu)
                
            else:
                # No packet available, sleep thread
                sleep(self.coreWait / 1000)
        
        # Gracefully exit core thread
        if self.coreStop:
            if dumpFile != None:
                dumpFile.close()
            
            return

    def push(self, packet):
        """
        Takes in VCDUs for the demuxer to process
        :param packet: 892 byte Virtual Channel Data Unit (VCDU)
        """

        self.rxq.append(packet)

    def pull(self):
        """
        Pull data from receive queue
        """

        try:
            # Return top item
            return self.rxq.popleft()
        except IndexError:
            # Queue empty
            return None

    def complete(self):
        """
        Checks if receive queue is empty
        """

        if len(self.rxq) == 0:
            return True
        else:
            return False

    def stop(self):
        """
        Stops the demuxer loop by setting thread stop flag
        """

        self.coreStop = True


class Channel:
    """
    Virtual channel data handler
    """

    def __init__(self, vcid, v, crclut):
        """
        Initialises virtual channel data handler
        :param vcid: Virtual Channel ID
        :param crclut: CP_PDU CRC LUT
        :param v: Verbose output flag
        """

        self.VCID = vcid            # VCID for this handler
        self.crclut = crclut        # CP_PDU CRC LUT
        self.verbose = v            # Verbose output flag
        self.counter = -1           # Last VCDU packet counter
        self.cCPPDU = None          # Current CP_PDU object
        self.cTPFile = None         # Current TP_File object


    def data_in(self, vcdu):
        """
        Takes in VCDUs for the channel handler to process
        :param packet: Parsed VCDU object
        """

        # Check VCDU continuity
        self.VCDU_continuity(vcdu)

        # Parse M_PDU
        mpdu = CCSDS.M_PDU(vcdu.MPDU)

        # If M_PDU contains CP_PDU header
        if mpdu.HEADER:
            # If data preceeds header
            if mpdu.POINTER != 0:
                # Finish previous CP_PDU
                preptr = mpdu.PACKET[:mpdu.POINTER]
                lenok, crcok = self.cCPPDU.finish(preptr, self.crclut)
                if self.verbose: self.check_CPPDU(lenok, crcok)

                # Handle finished CP_PDU
                self.handle_CPPDU(self.cCPPDU)

                #TODO: Check CP_PDU continuity
                
                # Create new CP_PDU
                postptr = mpdu.PACKET[mpdu.POINTER:]
                self.cCPPDU = CCSDS.CP_PDU(postptr)

            else:
                # First CP_PDU in TP_File
                # Create new CP_PDU
                self.cCPPDU = CCSDS.CP_PDU(mpdu.PACKET)
            
            #TODO: Finish SEQ LAST CP_PDU before going to FILL

            # Handle special EOF CP_PDU
            if self.cCPPDU.is_EOF():
                self.cCPPDU = None
            else:
                if self.verbose:
                    self.cCPPDU.print_info()
                    print("    HEADER:     0x{}".format(hex(mpdu.POINTER)[2:].upper()))
        else:
            # Append packet to current CP_PDU
            try:
                self.cCPPDU.append(mpdu.PACKET)
            except AttributeError:
                if self.verbose: print("NO CP_PDU TO APPEND M_PDU TO")
    

    def VCDU_continuity(self, vcdu):
        """
        Checks VCDU packet continuity by comparing packet counters
        """
        #TODO: Check counter globally?
        #TODO: Case for counter restart

        # If at least one VCDU has been received
        if self.counter != -1:
            diff = vcdu.COUNTER - self.counter - 1
            
            if diff != 0:
                print("  DROPPED {} PACKETS".format(diff))
                #print("  DROPPED {} PACKETS    (CURRENT: {}   LAST: {}   VCID: {})".format(diff, vcdu.COUNTER, self.counter, vcdu.VCID))
        
        self.counter = vcdu.COUNTER

    
    def check_CPPDU(self, lenok, crcok):
        """
        Checks length and CRC of finished CP_PDU
        """

        # Show length error
        if lenok:
            print("    LENGTH:     OK")
        else:
            ex = self.cCPPDU.LENGTH
            ac = len(self.cCPPDU.PAYLOAD)
            diff = ac - ex
            print("    LENGTH:     ERROR (EXPECTED: {}, ACTUAL: {}, DIFF: {})".format(ex, ac, diff))

        # Show CRC error
        if crcok:
            print("    CRC:        OK")
        else:
            print("    CRC:        ERROR")
        print()


    def handle_CPPDU(self, cppdu):
        """
        Processes complete CP_PDUs to build a TP_File
        """

        if cppdu.SEQ == "FIRST":
            # Create new TP_File
            self.cTPFile = CCSDS.TP_File(cppdu.PAYLOAD[:-2])

        elif cppdu.SEQ == "CONTINUE":
            # Add data to TP_File
            self.cTPFile.append(cppdu.PAYLOAD[:-2])

        elif cppdu.SEQ == "LAST":
            # Close current TP_File
            lenok = self.cTPFile.finish(cppdu.PAYLOAD[:-2])

            if self.verbose: self.cTPFile.print_info()
            if lenok:
                if self.verbose: print("    LENGTH:     OK")
                
                #TODO: Process S_PDU

            elif not lenok:
                ex = self.cTPFile.LENGTH
                ac = len(self.cTPFile.PAYLOAD)
                diff = ac - ex

                if self.verbose: print("    LENGTH:     ERROR (EXPECTED: {}, ACTUAL: {}, DIFF: {})".format(ex, ac, diff))
                print("  SKIPPING FILE (DROPPED PACKETS?)")
