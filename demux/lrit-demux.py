"""
lrit-demux.py
https://github.com/sam210723/COMS-1

De-multiplexes LRIT downlink into LRIT files.
"""

import argparse
import socket

argparser = argparse.ArgumentParser(description="De-multiplexes LRIT downlink into LRIT files.")
args = argparser.parse_args()

TCP_IP = "127.0.0.1"
CHANNEL_PORT = 5001
STATS_PORT = 5002

channelClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
statsClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


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
    
    while True:
        pass


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


init()
