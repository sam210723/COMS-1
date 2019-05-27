"""
demuxer.py
https://github.com/sam210723/COMS-1
"""

from threading import Thread
from collections import deque

from VCDU import VCDU

class Demuxer:
    """
    Coordinates CCSDS demultiplexing of virtual channels into xRIT files.
    """

    def __init__(self):
        """
        Initialises demuxer class
        """
        
        # Configure instance globals
        self.rxq = deque()             # Data receive queue
    

    def new_packet(self):
        """
        Called from rx_push() when new packet is added to queue
        """

        return


    def rx_push(self, packet):
        """
        Takes in VCDUs for the demuxer to process
        :param packet: 892 byte Virtual Channel Data Unit (VCDU)
        """

        self.rxq.append(packet)


    def rx_pull(self):
        """
        Pull data from receive queue
        """

        try:
            # Return top item
            return self.rxq.popleft()
        except IndexError:
            # Queue empty
            return None
