"""
xrit-header.py
https://github.com/sam210723/COMS-1

Parses xRIT file and displays header information in a human-readable format.
"""

import argparse
from coms import COMS as comsClass

argparser = argparse.ArgumentParser(description="Parses xRIT file and displays header information in a human-readable format.")
argparser.add_argument("PATH", action="store", help="Input xRIT file")
args = argparser.parse_args()

# Create COMS class instance and load xRIT file
COMS = comsClass(args.PATH)

# Primary Header (type 0, required)
COMS.parsePrimaryHeader(True)

# START OPTIONAL HEADERS
COMS.parseImageStructureHeader(True)

COMS.parseImageNavigationHeader(True)

COMS.parseImageDataFunctionHeader(True)

COMS.parseAnnotationTextHeader(True)

COMS.parseTimestampHeader(True)

COMS.parseAncillaryTextHeader(True)

COMS.parseKeyHeader(True)

COMS.parseImageSegmentationInformationHeader(True)

COMS.parseImageCompensationInformationHeader(True)

COMS.parseImageObservationTimeHeader(True)

COMS.parseImageQualityInformationHeader(True)
