"""
lrit-img.py
https://github.com/sam210723/coms-1

Extracts image data from LRIT IMG file.
"""

import argparse
from coms import COMS as comsClass

argparser = argparse.ArgumentParser(description="Extracts Meteorological Imager data from LRIT Image (IMG) files.")
argparser.add_argument("INPUT", action="store", help="Input LRIT file")
argparser.add_argument('OUTPUT', action="store", help="Output path of BIN file")
args = argparser.parse_args()

# Create COMS class instance and load LRIT file
COMS = comsClass(args.INPUT)

# Primary Header (type 0, required)
COMS.parsePrimaryHeader(True)

# START OPTIONAL HEADERS
COMS.parseImageStructureHeader(True)

COMS.parseImageNavigationHeader(True)

COMS.parseImageDataFunctionHeader(True)

COMS.parseAnnotationTextHeader(True)

COMS.parseTimestampHeader(True)

COMS.parseKeyHeader(True)

COMS.parseImageSegmentationInformationHeader(True)

# BEGIN DATA DUMPING
datFile = open(args.OUTPUT, "ab")
datFile.write(COMS.readbytes(0+21, COMS.primaryHeader['data_field_len']))
print("Image data dumped to \"{0}\"".format(args.OUTPUT))
