import argparse
import binascii
import pyDes

argparser = argparse.ArgumentParser(description="Decrypts KMA Encryption Key Message files for COMS-1 xRIT decryption")
argparser.add_argument("PATH", action="store", help="Encrypted Key Message file")
argparser.add_argument("MAC", action="store", help="Ground Station MAC address")
args = argparser.parse_args()

headerLen = 8
dataLen = 540
crcLen = 2

print("Loading \"{0}\"...".format(args.PATH))
print("MAC: {0}\n".format(args.MAC))

# Open Encrypted Key Message File
kmFile = open(args.PATH, mode="rb")
kmBytes = kmFile.read()

# Split file into fields
kmHeader = kmBytes[:headerLen]
kmData = kmBytes[headerLen: headerLen + dataLen]
kmCRC = kmBytes[-crcLen:]

# Print field contents
print("Header: {0}".format(kmHeader.hex().upper()))
#print("Data: {0}".format(kmData.hex().upper()))
print("CRC: {0}\n".format(kmCRC.hex().upper()))

# Parse header
kmHeaderHex = kmHeader.hex()
appYear = kmHeaderHex[0:4]
appMonth = kmHeaderHex[4:6]
appDay = kmHeaderHex[6:8]
appHour = kmHeaderHex[8:10]
appMin = kmHeaderHex[10:12]
appSec = str(round(int(kmHeaderHex[12:16])/1000))
print("Application time: {0}/{1}/{2} {3}:{4}:{5}\n".format(appDay, appMonth, appYear, appHour, appMin, appSec.zfill(2)))

# Loop through keys 18 bytes at a time
indexes = []
encKeys = []
print("[Index]: Encrypted Key")
for i in range(30):  # 30 keys total
    offset = i*18
    indexes.append(kmData[offset: offset+2])  # Bytes 0-1: Key index
    encKeys.append(kmData[offset+2:offset+18])  # Bytes 2-17: Encrypted key
    print("[{0}   ]: {1}".format(indexes[i][-1:].hex().upper(), encKeys[i].hex().upper()))

# Decrypt keys
macBin = binascii.unhexlify(args.MAC) + b'\x00\x00' # MAC String to binary + two byte padding
decKeys = []
print("\n[Index]: Decrypted Key")
for i in range(30):
    decKey = pyDes.des(macBin).decrypt(encKeys[i])
    decKeys.append(decKey[:8])
    print("[{0}   ]: {1}".format(indexes[i][-1:].hex().upper(), decKeys[i].hex().upper()))


decKmFileName = "" + args.PATH + ".dec"
print("\nOutput file: {0}".format(decKmFileName))
decKmFile = open(decKmFileName, mode="wb")
decKmFile.write(b'\x00\x1E')  # Number of keys (30/0x1E, 2 bytes)
for i in range(30):
    decKmFile.write(indexes[i])
    decKmFile.write(decKeys[i])
decKmFile.close()
