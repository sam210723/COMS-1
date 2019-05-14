"""
overlay.py
https://github.com/sam210723/COMS-1

Adds overlays and text to COMS-1 Meteorological Imager images.
"""

import argparse

argparser = argparse.ArgumentParser(description="Adds overlays and text to COMS-1 Meteorological Imager images.")
argparser.add_argument("INPUT", action="store", help="LRIT file to process")
argparser.add_argument("-c", action="store_true", help="Enable coastline overlay", default=False)
argparser.add_argument("-tl", action="store", help="Left text value", default=None)
argparser.add_argument("-tr", action="store", help="Right text value", default=None)
argparser.add_argument("-tc", action="store", help="Text colour", default="white")
args = argparser.parse_args()

def init():
    return


try:
    init()
except KeyboardInterrupt:
    print("Exiting...")
    exit(0)
