"""
lrit-demux.py
https://github.com/sam210723/COMS-1

De-multiplexes LRIT downlink VCDUs into LRIT files.
"""

import argparse
from configparser import ConfigParser
import os
import socket

from demuxer import Demuxer
#from statistics import Statistics
from tools import get_bits, new_dir_exists

# Parse CLI arguments
argparser = argparse.ArgumentParser(description="De-multiplexes LRIT downlink VCDUs into LRIT files.")
argparser.add_argument("--config", action="store", help="Configuration file path", default="lrit-demux.ini")
argparser.add_argument("--file", action="store", help="Path to VCDU file", default=None)
args = argparser.parse_args()

# Parse config file
cfgparser = ConfigParser()
cfgparser.read(args.config)

# Set global variables
BUFFER_LEN = 1024
SPACECRAFT = "COMS-1"
DOWNLINK = "LRIT"
OUTPUT_ROOT = cfgparser.get('demuxer', 'output')

if args.file == None:
    INPUT_MODE = cfgparser.get('demuxer', 'input')
else:
    INPUT_MODE = "file"

# Directory structure
DIR_ROOT = os.path.abspath(OUTPUT_ROOT)
DIR_LRIT = DIR_ROOT + "/LRIT"
DIR_LRIT_IMG = DIR_LRIT + "/IMG"
DIR_LRIT_IMG_FD = DIR_LRIT_IMG + "/FD"
DIR_LRIT_IMG_ENH = DIR_LRIT_IMG + "/ENH"
DIR_LRIT_IMG_LSH = DIR_LRIT_IMG + "/LSH"
DIR_LRIT_ADD = DIR_LRIT + "/ADD"
DIR_LRIT_ADD_ANT = DIR_LRIT_ADD + "/ANT"
DIR_LRIT_ADD_GOCI = DIR_LRIT_ADD + "/GOCI"
DIR_LRIT_ADD_NWP = DIR_LRIT_ADD + "/NWP"
DIR_LRIT_ADD_TYP = DIR_LRIT_ADD + "/TYP"
DIRS = [DIR_ROOT, DIR_LRIT, DIR_LRIT_IMG, DIR_LRIT_IMG_FD, DIR_LRIT_IMG_ENH, DIR_LRIT_IMG_LSH, DIR_LRIT_ADD, DIR_LRIT_ADD_ANT, DIR_LRIT_ADD_GOCI, DIR_LRIT_ADD_NWP, DIR_LRIT_ADD_TYP]

# TCP Clients
ospChannelClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#ospStatsClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# File source
vcduFile = None

#demux = Demuxer(DOWNLINK, DIRS)
demux = Demuxer()


def init():
    print("┌───────────────────────────────┐")
    print("│      COMS-1 LRIT Demuxer      │")
    print("│  github.com/sam210723/COMS-1  │")
    print("└───────────────────────────────┘\n")
    
    print_config_info()
    config_dirs()
    config_input()

    if demux.coreReady:
        print("DEMUXER CORE THREAD READY")

    print("──────────────────────────────────────────────────────────────────────────────────\n")
    print("WAITING FOR NEW xRIT DATA...")

    # Main loop
    loop()


def loop():
    """
    Handle data from input source
    """

    while True:
        if INPUT_MODE == "osp":
            channelData = ospChannelClient.recv(BUFFER_LEN)
            #statsData = ospStatsClient.recv(BUFFER_LEN)
        elif INPUT_MODE == "goesrecv":
            return
        elif INPUT_MODE == "file":
            channelData = vcduFile.read(892)

            if channelData == b'':
                print("\n\nREACHED END OF INPUT FILE\nExiting...")
                exit()

        demux.data_in(channelData)
        #stats.data_in(statsData)


def print_config_info():
    """
    Prints configuration information when demuxer starts
    """

    print("SPACECRAFT:     {}".format(SPACECRAFT))
    print("DOWNLINK:       {}".format(DOWNLINK))

    if INPUT_MODE == "osp":
        m = "Open Satellite Project (github.com/opensatelliteproject/xritdemod)"
    elif INPUT_MODE == "goesrecv":
        m = "goesrecv (github.com/pietern/goestools)"
    elif INPUT_MODE == "file":
        m = "File ({})".format(args.file)
    else:
        m = "UNKNOWN"
    
    print("INPUT SOURCE:   {}".format(m))
    print("OUTPUT PATH:    {}".format(DIR_ROOT))
    print()


def config_dirs():
    """
    Create required directory structure
    """
    
    for DIR in DIRS:
        if new_dir_exists(DIR) != True:
            print("Error creating directories")
            print("Exiting...")
            exit()


def config_input():
    """
    Configures input based on config file input mode
    """

    if INPUT_MODE == "osp":
        # Get OSP details from config file
        ospIP = cfgparser.get('osp', 'ip')
        ospChannelPort = int(cfgparser.get('osp', 'vchan'))
        #ospStatsPort = int(cfgparser.get('osp', 'stats'))

        # Start TCP clients for OSP
        print("Connecting to Open Satellite Project ({})...".format(ospIP))
        start_osp_channel_client((ospIP, ospChannelPort))
        #start_osp_stats_client((ospIP, ospStatsPort))

    elif INPUT_MODE == "goesrecv":
        print("Not implemented\nExiting...")
        exit()

    elif INPUT_MODE == "file":
        global vcduFile
        
        fpath = args.file
        vcduFile = open(fpath, 'rb')

    else:
        print("UNKNOWN INPUT MODE: \"{}\"".format(INPUT_MODE))
        print("Exiting...")
        exit()


def start_osp_channel_client(ipport):
    """
    Connect TCP socket to OSP decoder virtual channel port
    """

    try:
        ospChannelClient.connect(ipport)
    except socket.error as e:
        if e.errno == 10061:
            print("  Virtual Channel: CONNECTION REFUSED")
        else:
            print(e)
        
        print("\nExiting...")
        exit()

    print("  Virtual Channel (TCP {}): CONNECTED".format(ipport[1]))

def start_osp_stats_client(ipport):
    """
    Connect TCP socket to OSP decoder virtual channel port
    """

    try:
        ospStatsClient.connect(ipport)
    except socket.error as e:
        if e.errno == 10061:
            print("  Statistics: CONNECTION REFUSED")
        else:
            print(e)
        
        print("\nExiting...")
        exit()

    print("  Statistics (TCP {}): CONNECTED".format(ipport[1]))


# Catch keyboard interrupt
try:
    init()
except KeyboardInterrupt as e:
    print("Exiting...")
    exit()
