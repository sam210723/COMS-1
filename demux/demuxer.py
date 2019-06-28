"""
demuxer.py
https://github.com/sam210723/COMS-1
"""

import CCSDS
from collections import deque
from time import sleep
from threading import Thread

class Demuxer:
    """
    Coordinates demultiplexing of CCSDS virtual channels into xRIT files.
    """

    def __init__(self, downlink, v):
        """
        Initialises demuxer class
        """
        
        # Configure instance globals
        self.rxq = deque()              # Data receive queue
        self.coreReady = False          # Core thread ready state
        self.coreStop = False           # Core thread stop flag
        self.verbose = v                # Verbose output flag
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

        # Thread loop
        while not self.coreStop:
            # Pull next packet from queue
            packet = self.pull()
            
            # If queue is not empty
            if packet != None:
                # Parse VCDU
                vcdu = CCSDS.VCDU(packet)

                # Check for VCID change
                if lastVCID == None:                # First VCDU (demuxer just started)
                    if self.verbose:
                        vcdu.print_info()
                        print("WAITING FOR VCID TO CHANGE")
                    lastVCID = vcdu.VCID
                    continue
                elif lastVCID == vcdu.VCID:         # VCID has not changed
                    if not seenVCIDChange:
                        continue                    # Never seen VCID change, ignore data (avoids partial TP_Files)
                    else:
                        pass
                elif lastVCID != vcdu.VCID:         # VCID has changed
                    if self.verbose: vcdu.print_info()
                    seenVCIDChange = True
                    lastVCID = vcdu.VCID
                
                # Check channel handler for current VCID exists
                try:
                    self.channelHandlers[vcdu.VCID]
                except KeyError:
                    # Create new channel handler instance
                    self.channelHandlers[vcdu.VCID] = Channel(vcdu.VCID, self.verbose)
                    if self.verbose: print("CREATED NEW CHANNEL HANDLER")

                # Pass VCDU to appropriate channel handler
                self.channelHandlers[vcdu.VCID].data_in(vcdu)
                
            else:
                # No packet available, sleep thread
                sleep(self.coreWait / 1000)
        
        # Gracefully exit core thread
        if self.coreStop:
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

    def __init__(self, vcid, v):
        """
        Initialises virtual channel data handler
        :param vcid: Virtual Channel ID
        """

        self.VCID = vcid            # VCID handler is responsible for
        self.verbose = v            # Verbose output flag
        self.counter = -1           # Last VCDU packet counter
        self.DROPPED = 0            # Dropped packet count
    

    def data_in(self, vcdu):
        """
        Takes in VCDUs for the channel handler to process
        :param packet: Parsed VCDU object
        """

        # Check VCDU continuity
        self.VCDU_C(vcdu)


        # Parse M_PDU
        mpdu = CCSDS.M_PDU(vcdu.MPDU)

        # If M_PDU contains CP_PDU header
        if mpdu.HEADER:
            # Parse CP_PDU header
            pass
        else:
            # Append packet to current CP_PDU
            pass

        if self.verbose: mpdu.print_info()
    

    def VCDU_C(self, vcdu):
        """
        Checks VCDU packet continuity by comparing packet counters
        """
        
        # If at least one VCDU has been received
        if self.counter != -1:
            diff = vcdu.COUNTER - self.counter - 1
            
            if diff != 0:
                self.DROPPED += diff
                print("  DROPPED {} PACKETS  (TOTAL: {})".format(diff, self.DROPPED))
                #print("  DROPPED {} PACKETS    (CURRENT: {}   LAST: {}   VCID: {})".format(diff, vcdu.COUNTER, self.counter, vcdu.VCID))
        
        self.counter = vcdu.COUNTER
