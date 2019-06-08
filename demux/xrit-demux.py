"""
xrit-demux.py
https://github.com/sam210723/COMS-1

Frontend for CCSDS demultiplexer
"""

from argparse import ArgumentParser
from configparser import ConfigParser
from demuxer import Demuxer


def init():
    args = parse_args()
    config = parse_config(args.config)


def parse_args():
    """
    Parses command line arguments
    """

    argp = ArgumentParser()
    argp.description = "Frontend for CCSDS demultiplexer"
    argp.add_argument("--config", action="store", help="Configuration file path (.ini)", default="lrit-demux.ini")
    argp.add_argument("--file", action="store", help="Path to VCDU packet file", default=None)
    
    return argp.parse_args()


def parse_config(path):
    """
    Parses configuration file
    """

    cfgp = ConfigParser()
    cfgp.read(path)

    return cfgp


try:
    init()
except KeyboardInterrupt:
    #demux.stop()
    print("Exiting...")
    exit()
