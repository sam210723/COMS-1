"""
lrit-additional.py
https://github.com/sam210723/coms-1

Extracts data from LRIT Additional Data (ADD) files.
Data includes Alpha-numeric text (ANT), CMDPS (CT/CTT/CTH), and GOCI.
"""

import argparse
from coms import COMS as comsClass

argparser = argparse.ArgumentParser(description="Extracts data from LRIT Additional Data (ADD) files. Data includes Alpha-numeric text (ANT), CMDPS (CT/CTT/CTH), and GOCI.")
argparser.add_argument("PATH", action="store", help="Input LRIT file")
args = argparser.parse_args()

# Create COMS class instance and load LRIT file
COMS = comsClass(args.PATH)

# Primary Header (type 0, required)
COMS.parsePrimaryHeader(True)

# START OPTIONAL HEADERS
COMS.parseAnnotationTextHeader(True)

COMS.parseTimestampHeader(True)

COMS.parseKeyHeader(True)

# BEGIN DATA DUMPING
data = COMS.readbytes(0, COMS.primaryHeader['data_field_len'])

if COMS.primaryHeader['file_type'] == 2:  # Alphanumeric Text (ANT)
    dumpExtension = "txt"
elif COMS.primaryHeader['file_type'] == 128:  # CMDPS Data (CT, CTT, CTH)
    dumpExtension = "png"
elif COMS.primaryHeader['file_type'] == 132 or COMS.primaryHeader['file_type'] == 130:  # GOCI (seems to have 2 file type codes)
    dumpExtension = "jpg"

dumpFileName = COMS.path[:-5] + "_DATA.{0}".format(dumpExtension)
dumpFile = open(dumpFileName, 'wb')
dumpFile.write(data)
dumpFile.close()
print("\nAdditional Data dumped to \"{0}\"".format(dumpFileName))
