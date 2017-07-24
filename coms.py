"""
coms.py
https://github.com/sam210723/coms-1

Common functions and variables.
"""

# LRIT header types
headerTypes = {}
headerTypes[0] = "Primary Header"
headerTypes[1] = "Image Structure Header"
headerTypes[2] = "Image Navigation Header"
headerTypes[3] = "Image Data Function Header"
headerTypes[4] = "Annotation Header"
headerTypes[5] = "Time Stamp Header"
headerTypes[6] = "Ancillary Text Header"  # Not used in LRIT, future expansion
headerTypes[7] = "Key Header"
headerTypes[128] = "Image Segment Definition Header"
headerTypes[129] = "Encryption Key Message Header"  # Not used in LRIT

# LRIT file types
fileTypes = {}
fileTypes[0] = "Image data (IMG)"
fileTypes[1] = "Global Telecommunication System (GTS) message"
fileTypes[2] = "Alpha-numeric text (ANT)"
fileTypes[3] = "Encryption key message"  # Not used in LRIT
fileTypes[128] = "COMS Meteorological Data Processing System (CMDPS) analysis data"
fileTypes[129] = "Numerical Weather Prediction (NWP) data"
fileTypes[130] = "Geostationary Ocean Color Imager (GOCI) data"
fileTypes[131] = "KMA typhoon information"

colours = {}
colours['HEADER'] = '\033[95m'
colours['OKBLUE'] = '\033[94m'
colours['OKGREEN'] = '\033[92m'
colours['WARNING'] = '\033[93m'
colours['FAIL'] = '\033[91m'
colours['ENDC'] = '\033[0m'
colours['BOLD'] = '\033[1m'
colours['UNDERLINE'] = '\033[4m'
