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
args = argparser.parse_args()

# Parse config file
cfgparser = ConfigParser()
cfgparser.read(args.config)

# Set global variables
BUFFER_LEN = 1024
SPACECRAFT = "COMS-1"
DOWNLINK = "LRIT"
INPUT_MODE = cfgparser.get('demuxer', 'input')
OUTPUT_ROOT = cfgparser.get('demuxer', 'output')

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
channelClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#statsClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

demux = Demuxer(DOWNLINK, DIRS)


def init():
    print("┌───────────────────────────────┐")
    print("│      COMS-1 LRIT Demuxer      │")
    print("│  github.com/sam210723/COMS-1  │")
    print("└───────────────────────────────┘\n")
    
    print_info()
    config_dirs()
    config_input()
        

    print("──────────────────────────────────────────────────────────────────────────────────\n")
    print("Waiting for Virtual Channel to change...")

    # Main loop
    loop()


def loop():
    """
    Handle incoming data from OSP decoder
    """

    while True:
        channelData = channelClient.recv(BUFFER_LEN)
        #statsData = statsClient.recv(BUFFER_LEN)

        demux.data_in(channelData)
        #stats.data_in(statsData)


def print_info():
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
        m = "File"
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
        ospIP = cfgparser.get('osp', 'ip')
        ospChannelPort = int(cfgparser.get('osp', 'vchan'))
        ospStatsPort = int(cfgparser.get('osp', 'stats'))

        # Start TCP clients for OSP
        print("Connecting to Open Satellite Project ({})...".format(ospIP))
        start_osp_channel_client((ospIP, ospChannelPort))
        #start_osp_stats_client((ospIP, ospStatsPort))

    elif INPUT_MODE == "goesrecv":
        print("goesrecv input is \nExiting...")
        exit()

    elif INPUT_MODE == "file":
        print("File input is WIP\nExiting...")
        exit()

    else:
        print("UNKNOWN INPUT MODE: \"{}\"".format(INPUT_MODE))
        print("Exiting...")
        exit()


def start_osp_channel_client(ipport):
    """
    Connect TCP socket to OSP decoder virtual channel port
    """

    try:
        channelClient.connect(ipport)
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
        statsClient.connect(ipport)
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
