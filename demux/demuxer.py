"""
demuxer.py
https://github.com/sam210723/COMS-1
"""

from threading import Thread
from queue import Queue

from VCDU import VCDU

class Demuxer:
    """
    Coordinates CCSDS demultiplexing of virtual channels into xRIT files.
    """

    def __init__(self):
        """
        Initialises demuxer class
        """
        
        # Configure instance global
        self.rxbuf = b''               # Data receive queue
        self.coreReady = False         # Core thread ready state

        # Start core demuxer thread
        demux_thread = Thread(name="DEMUXER CORE")
        demux_thread.run = self.demux_core
        demux_thread.start()
    

    def data_in(self, packet):
        """
        Takes in VCDUs for the demuxer to process
        :param packet: 892 byte Virtual Channel Data Unit (VCDU)
        """

        # Add packet to receive buffer
        self.rxbuf += packet
    

    def demux_core(self):
        """
        Demuxer core thread function
        """

        self.coreReady = True
        return
