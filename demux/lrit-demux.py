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
TCP_IP = cfgparser.get('network', 'ip')
CHANNEL_PORT = int(cfgparser.get('network', 'vchannel'))
STATS_PORT = int(cfgparser.get('network', 'statistics'))
BUFFER_LEN = 1024
OUTPUT_ROOT = cfgparser.get('demuxer', 'output')
DECODER_MODE = cfgparser.get('demuxer', 'decoder')

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

demux = Demuxer("LRIT", DIRS)


def init():
    print("COMS-1 LRIT Demuxer\n")
    print("Virtual Channel Port: {}".format(CHANNEL_PORT))
    #print("Statistics Port: {}\n".format(STATS_PORT))

    if DECODER_MODE == "osp":
        print("\nStarting in Open Satellite Project mode...")
    elif DECODER_MODE == "goesrecv":
        print("\nStarting in goestools/goesrecv mode...")

    config_dirs()

    # Start TCP clients
    start_channel_client()
    #start_stats_client()

    print("─────────────────────────────────────────────────────────")
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


def config_dirs():
    """
    Create required directory structure
    """
    print("\nCreating directories...")
    print(DIR_ROOT)
    
    for DIR in DIRS:
        if new_dir_exists(DIR) != True:
            print("Error creating directories")
            print("Exiting...")
            exit()
    
    print()


def start_channel_client():
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


def start_stats_client():
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
