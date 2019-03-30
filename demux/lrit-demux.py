"""
lrit-demux.py
https://github.com/sam210723/COMS-1

De-multiplexes LRIT downlink into LRIT files.
"""

import argparse
import socket
import sys

from VCDU import *
from MPDU import parseMPDU

argparser = argparse.ArgumentParser(description="De-multiplexes LRIT downlink into LRIT files.")
args = argparser.parse_args()

TCP_IP = "127.0.0.1"
CHANNEL_PORT = 5001
STATS_PORT = 5002
BUFFER_LEN = 892

channelClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
statsClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Globals
lastVCID = None

def init():
    print("COMS-1 LRIT Demuxer\n")
    print("Virtual Channel Port: {}".format(CHANNEL_PORT))
    print("Statistics Port: {}\n".format(STATS_PORT))

    startChannelClient()
    startStatsClient()

    socketLoop()


def socketLoop():
    """
    Handle incoming data from OSP decoder
    """
    
    global lastVCID

    while True:
        channelData = channelClient.recv(BUFFER_LEN)
        statsData = statsClient.recv(BUFFER_LEN)

        # Unwrap VCDU into M_PDU
        SCID, VCID, COUNT, MPDU = parseVCDU(channelData)
        
        # Parse M_PDU of non-fill VCID
        if VCID != 63:
            # Detect change in VCID
            if lastVCID != VCID:
                print("\n\n[VCDU] VCID: {} ({})".format(getVCName(VCID), VCID))
            lastVCID = VCID
            
            NEW, POINTER, FRAME = parseMPDU(MPDU)

            # MPDU progress indicator
            if NEW:
                sys.stdout.write("|")
            else:
                sys.stdout.write(".")
            sys.stdout.flush()

            # Temporary dump to file
            channelDump = open('demux/CPPDU.bin', 'wb')
            channelDump.write(FRAME)
            channelDump.close()


def startChannelClient():
    """
    Connect TCP socket to OSP decoder virtual channel port
    """
    
    print("Starting CHANNEL client...")

    try:
        channelClient.connect((TCP_IP, CHANNEL_PORT))
    except socket.error as e:
        if e.errno == 10061:
            print("TCP CONNECTION REFUSED".format())
        else:
            print(e)
        
        print("Exiting...\n")
        exit()    

    print("CHANNEL OK\n")


def startStatsClient():
    """
    Connect TCP socket to OSP decoder statistics port
    """

    print("Starting STATISTICS client...")

    try:
        statsClient.connect((TCP_IP, STATS_PORT))
    except socket.error as e:
        if e.errno == 10061:
            print("TCP CONNECTION REFUSED".format())
        else:
            print(e)
        
        print("Exiting...\n")
        exit()

    print("STATISTICS OK\n")

# Catch keyboard interrupt
try:
    init()
except KeyboardInterrupt as e:
    print("Exiting...")
    exit()
