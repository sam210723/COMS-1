"""
lrit-demux.py
https://github.com/sam210723/COMS-1

De-multiplexes LRIT downlink into LRIT files.
"""

import argparse
import os
import socket

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

def init():
    print("COMS-1 LRIT Demuxer\n")
    print("Virtual Channel Port: {}".format(CHANNEL_PORT))
    print("Statistics Port: {}\n".format(STATS_PORT))

    config_dirs()

    # Start TCP clients
    start_channel_client()
    start_stats_client()

    # Main loop
    loop()


def loop():
    """
    Handle incoming data from OSP decoder
    """

    while True:
        channelData = channelClient.recv(BUFFER_LEN)
        #statsData = statsClient.recv(BUFFER_LEN)


def config_dirs():
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
