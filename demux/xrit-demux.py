"""
xrit-demux.py
https://github.com/sam210723/COMS-1

Frontend for CCSDS demultiplexer
"""

from argparse import ArgumentParser
from configparser import ConfigParser
from demuxer import Demuxer
from os import mkdir, path
from time import time
from tools import new_dir_exists

# Globals
args = None
config = None
stime = None


def init():
    global args
    global config
    global stime

    # Handle arguments and config file
    args = parse_args()
    config = parse_config(args.config)

    dirs()

    # Get processing start time
    stime = time()


def dirs():
    """
    Configures directories for demuxed files
    """

    global config
    root = config.get('demuxer', 'output')

    paths = [
        root,
        root + "/LRIT",
        root + "/LRIT/IMG",
        root + "/LRIT/IMG/FD",
        root + "/LRIT/IMG/ENH",
        root + "/LRIT/IMG/LSH",
        root + "/LRIT/ADD",
        root + "/LRIT/ADD/ANT",
        root + "/LRIT/ADD/GOCI",
        root + "/LRIT/ADD/NWP",
        root + "/LRIT/ADD/TYP",
    ]

    # Loop through paths in list
    for p in paths:
        absp = path.abspath(p)
        
        # Create new directory if it doesn't exist already
        if not path.isdir(absp):
            try:
                mkdir(absp)
                print("Created: {}".format(p))
            except OSError as e:
                print("Error creating output folders\n{}\n\nExiting...".format(e))
                exit()


def parse_args():
    """
    Parses command line arguments
    """

    argp = ArgumentParser()
    argp.description = "Frontend for CCSDS demultiplexer"
    argp.add_argument("--config", action="store", help="Configuration file path (.ini)", default="xrit-demux.ini")
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
