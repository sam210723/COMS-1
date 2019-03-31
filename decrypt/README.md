# Decryption
COMS-1 xRIT downlinks are encrypted using single-layer [DES](https://en.wikipedia.org/wiki/Data_Encryption_Standard).
Decryption keys are controlled by [KMA NMSC](http://nmsc.kma.go.kr/html/homepage/en/ver2/main.do) through an application approval process.
However, KMA seems to only approve applications from governments, research institutes, and large organisations.

Valid decryption keys have been discovered in example decryption code provided by KMA themselves.

## Obtaining Decryption Keys
**COMS-1 Encryption Key Message files are no longer hosted in this repository.**

They must be retrieved directly from KMA by downloading the "HRIT/LRIT Data Decrytion samples C code" from the
[COMS Operations](http://nmsc.kma.go.kr/html/homepage/en/ver2/static/selectStaticPage.do?view=satellites.coms.operations.selectIntroduction) page.

## Key Decryption
A user applying for decryption keys from KMA would normally provide them with a MAC address unique to their ground station.
This MAC address is used to encrypt the Key Message file so the keys inside are only accessible to the ground station owner.

The Key Message file provided by KMA in their example code is encrypted in this same way.
The file name of this key file includes the corresponding MAC address needed for key decryption (```EncryptionKeyMessage_AABBCCDDEEFF.bin```).

To decrypt this Key Message file run:
```
python keymsg-decrypt.py EncryptionKeyMessage_AABBCCDDEEFF.bin AABBCCDDEEFF
```
This will create ```EncryptionKeyMessage_AABBCCDDEEFF.bin.dec``` which contains plain-text DES decryption keys for the xRIT downlink.
This file can be used with other tools in this repository to decrypt downlinked images and text.

A detailed explanation of the key decryption process is [available here](https://vksdr.com/lrit-key-dec).
