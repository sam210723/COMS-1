"""
lrit-demux.py
https://github.com/sam210723/COMS-1

De-multiplexes LRIT downlink into LRIT files.
"""

import argparse
import os
import socket
import sys

from VCDU import parseVCDU, getVCName
from MPDU import parseMPDU
from CPPDU import parseCPPDU, genCRCLUT, checkCRC
from tools import getBits, newDirExists

argparser = argparse.ArgumentParser(description="De-multiplexes LRIT downlink into LRIT files.")
argparser.add_argument("ROOT", action="store", help="LRIT file directory")
args = argparser.parse_args()

TCP_IP = "127.0.0.1"
CHANNEL_PORT = 5001
STATS_PORT = 5002
BUFFER_LEN = 892

# Directory structure
DIR_ROOT = os.path.abspath(args.ROOT)
DIR_TEMP = DIR_ROOT + "/temp"
DIR_LRIT = DIR_ROOT + "/LRIT"
DIR_FD = DIR_LRIT + "/FD"
DIR_ENH = DIR_LRIT + "/ENH"
DIR_LSH = DIR_LRIT + "/LSH"
DIR_ADD = DIR_LRIT + "/ADD"
DIRS = [DIR_ROOT, DIR_TEMP, DIR_LRIT, DIR_FD, DIR_ENH, DIR_LSH, DIR_ADD]

# TCP Clients
channelClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
statsClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Globals
lastVCID = None
lastVCIDCount = None
currentCPPDU = None
lastCPPDUCount = None
crcLUT = None

def init():
    print("COMS-1 LRIT Demuxer\n")
    print("Virtual Channel Port: {}".format(CHANNEL_PORT))
    print("Statistics Port: {}\n".format(STATS_PORT))

    configDirs()

    # Start TCP clients
    startChannelClient()
    startStatsClient()

    # Generate CP_PDU CRC LUT
    global crcLUT
    crcLUT = genCRCLUT()

    # Main loop
    loop()


def loop():
    """
    Handle incoming data from OSP decoder
    """
    
    global lastVCID
    global lastVCIDCount
    global currentCPPDU
    global lastCPPDUCount
    global crcLUT
    print(crcLUT)

    while True:
        channelData = channelClient.recv(BUFFER_LEN)
        statsData = statsClient.recv(BUFFER_LEN)

        ###--- VCDU ---###
        # Parse VCDU header and return enclosed M_PDU
        SCID, VCID, COUNT, MPDU = parseVCDU(channelData)
        
        if VCID == 63:
            # Discard fill packets
            pass
        else:
            # Detect change in VCID
            if VCID != lastVCID:
                print("\n\n[VCDU]  {}  VCID: {}".format(getVCName(VCID), VCID))
            else:
                # Check VCDU counter continuity
                if COUNT != (lastVCIDCount + 1):
                    print("PACKET LOSS DETECTED")

            lastVCID = VCID
            lastVCIDCount = COUNT


            ###--- M_PDU ---###
            HEADER, POINTER, FRAME = parseMPDU(MPDU)

            # If M_PDU contains new CP_PDU header
            if HEADER:
                # Parse CP_PDU header and return CP_PDU chunks before and after header
                APID, SEQ, COUNT, PRECHUNK, POSTCHUNK = parseCPPDU(FRAME, POINTER)

                #TODO: Check CP_PDU counter continuity
                #if SEQ == "START":
                    #lastCPPDUCount = COUNT
                #else:
                    #if lastCPPDUCount != None:
                        #if COUNT != (lastCPPDUCount + 1):
                            #print("PACKET LOSS DETECTED")
                #lastCPPDUCount = COUNT

                # Handle completed CP_PDU
                if POINTER != 0 and currentCPPDU != None:
                    # Append data from previous CP_PDU before header of next CP_PDU
                    currentCPPDU += PRECHUNK

                    print(len(currentCPPDU))
                    
                    # Trim CRC from end of CP_PDU
                    currentCRC = currentCPPDU[-2:]
                    currentCPPDU = currentCPPDU[:-2]

                    ###--- CP_PDU ---###
                    if not checkCRC(currentCPPDU, currentCRC, crcLUT):
                        print("CP_PDU CRC ERROR!")


                    #TODO: Append CP_PDU to TP_File
                    #TODO: Extract S_PDU from TP_File
                    #TODO: Decrypt S_PDU into xRIT File

                # Start new CP_PDU
                currentCPPDU = POSTCHUNK
            else:
                # If no CP_PDU header present, append bytes to current CP_PDU
                if currentCPPDU != None:
                    currentCPPDU += FRAME


def configDirs():
    """
    Create required directory structure
    """
    print("Creating directories...")
    print(DIR_ROOT)
    
    for DIR in DIRS:
        if newDirExists(DIR) != True:
            print("Error creating directories")
            print("Exiting...")
            exit()
    
    print()


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
