from datetime import datetime, timedelta
from jdcal import jd2gcal

class COMS:
    """
    coms.py
    https://github.com/sam210723/coms-1

    Variables and methods for COMS-1 xRIT parsing.
    """

    # xRIT header types
    headerTypes = {}
    headerTypes[0] = "Primary Header"
    headerTypes[1] = "Image Structure Header"
    headerTypes[2] = "Image Navigation Header"
    headerTypes[3] = "Image Data Function Header"
    headerTypes[4] = "Annotation Header"
    headerTypes[5] = "Time Stamp Header"
    headerTypes[6] = "Ancillary Text Header"  # Not used in xRIT, future expansion
    headerTypes[7] = "Key Header"
    headerTypes[128] = "Image Segmentation Information Header"
    headerTypes[129] = "Encryption Key Message Header"  # Not used in xRIT
    headerTypes[130] = "Image Compensation Information Header"  # HRIT only
    headerTypes[131] = "Image Observation Time Header"  # HRIT only
    headerTypes[132] = "Image Quality Information Header"  # HRIT only

    # LRIT file types
    fileTypes = {}
    fileTypes[0] = "Image data (IMG)"
    fileTypes[1] = "Global Telecommunication System (GTS) message"  # LRIT only
    fileTypes[2] = "Alpha-numeric text (ANT)"
    fileTypes[3] = "Encryption key message"  # Not used in xRIT
    fileTypes[128] = "COMS Meteorological Data Processing System (CMDPS) analysis data"  # LRIT only
    fileTypes[129] = "Numerical Weather Prediction (NWP) data"  # LRIT only
    fileTypes[130] = "Geostationary Ocean Color Imager (GOCI) data"  # LRIT only
    fileTypes[131] = "KMA typhoon information"  # LRIT only
    fileTypes[132] = fileTypes[130]

    # LRIT image types
    imageTypes = {}
    imageTypes[0] = "Full Disk (FD)"
    imageTypes[1] = "Extended Northern Hemisphere (ENH)"
    imageTypes[2] = "Limited Southern Hemisphere (LSH)"
    imageTypes[3] = "Asia and Pacific in Northern Hemisphere (APNH)"

    # LRIT image compression types
    compressionTypes = {}
    compressionTypes[0] = "None"
    compressionTypes[1] = "Lossless"
    compressionTypes[2] = "Lossy"

    # Console colour characters
    colours = {}
    colours['HEADER'] = '\033[95m'
    colours['OKBLUE'] = '\033[94m'
    colours['OKGREEN'] = '\033[92m'
    colours['WARNING'] = '\033[93m'
    colours['FAIL'] = '\033[91m'
    colours['ENDC'] = '\033[0m'
    colours['BOLD'] = '\033[1m'
    colours['UNDERLINE'] = '\033[4m'

    primaryHeader = {}
    imageStructureHeader = {}
    imageNavigationHeader = {}
    imageDataFunctionHeader = {}
    annotationTextHeader = {}
    timestampHeader = {}
    ancillaryTextHeader = {}
    keyHeader = {}
    imageSegmentationInformationHeader = {}
    imageCompensationInformationHeader = {}
    imageObservationTimeHeader = {}
    imageQualityInformationHeader = {}

    # Byte counter for tracking progress through file
    byteOffset = 0


    def __init__(self, path):
        self.path = path  # LRIT file path

        # Load xRIT file
        xritFile = open(self.path, mode="rb")
        self.xritString = xritFile.read()


    # Tool methods
    def readbytes(self, offset, length=1):
        """
        Reads n bytes at x offset
        :param offset: Start position offset 
        :param length: Number of bytes to return
        :return: Bytes  
        """
        return self.xritString[self.byteOffset+offset:self.byteOffset+offset+length]

    def intToHexStr(self, int, fill=0):
        """
        Converts integer into hex string representation
        :param: int: Integer to convert
        :param: fill: Zero padding amount
        :return: Hex string
        """
        return "0x{0}".format(hex(int).upper()[2:].zfill(fill))

    def setConsoleColour(self, colour="ENDC"):
        """
        Sets console colour. Defaults to no colour.
        :param colour: Colour to set
        """
        print(self.colours[colour], end='')


    # Header parsing methods
    def parsePrimaryHeader(self, printInfo=False):
        """
        Parses xRIT Primary header (type 0, required)
        :param printInfo: Print info after parsing
        """

        if self.readbytes(0, 3) == b'\x00\x00\x10':
            self.primaryHeader['valid'] = True
            self.primaryHeader['header_type'] = 0
            self.primaryHeader['header_len'] = 16
            self.primaryHeader['header_offset'] = self.byteOffset
            self.primaryHeader['file_type'] = int.from_bytes(self.readbytes(3), byteorder='big')
            self.primaryHeader['total_header_len'] = int.from_bytes(self.readbytes(4, 4), byteorder='big')
            self.primaryHeader['data_field_len'] = int.from_bytes(self.readbytes(8, 8), byteorder='big')

            self.byteOffset += self.primaryHeader['header_len']
            if printInfo:
                self.printPrimaryHeader()
        else:
            self.primaryHeader['valid'] = False

    def parseImageStructureHeader(self, printInfo=False):
        """
        Parses xRIT Image Structure header (type 1)
        :param printInfo: Print info after parsing
        """

        if self.readbytes(0, 3) == b'\x01\x00\x09':
            self.imageStructureHeader['valid'] = True
            self.imageStructureHeader['header_type'] = 1
            self.imageStructureHeader['header_len'] = 9
            self.imageStructureHeader['header_offset'] = self.byteOffset

            self.imageStructureHeader['bits_per_pixel'] = self.readbytes(3)  # LRIT = 8 bits, HRIT = 16 bits

            # Detect LRIT/HRIT using bpp
            if int.from_bytes(self.imageStructureHeader['bits_per_pixel'], byteorder='big') == 8:
                self.imageStructureHeader['is_lrit'] = 1
            else:
                self.imageStructureHeader['is_lrit'] = 0

            self.imageStructureHeader['num_cols'] = int.from_bytes(self.readbytes(4, 2), byteorder='big')
            self.imageStructureHeader['num_lines'] = int.from_bytes(self.readbytes(6, 2), byteorder='big')

            # Image type based on column and line count
            if self.imageStructureHeader['num_cols'] == 2200 and self.imageStructureHeader['num_lines'] == 220:  # LRIT FD
                self.imageStructureHeader['image_type'] = 0
            elif self.imageStructureHeader['num_cols'] == 1547 and (self.imageStructureHeader['num_lines'] == 308 or self.imageStructureHeader['num_lines'] == 309):  # LRIT ENH
                self.imageStructureHeader['image_type'] = 1
            elif self.imageStructureHeader['num_cols'] == 1547 and self.imageStructureHeader['num_lines'] == 318:  # LRIT LSH
                self.imageStructureHeader['image_type'] = 2
            elif self.imageStructureHeader['num_cols'] == 810 and self.imageStructureHeader['num_lines'] == 611:  # LRIT APNH
                self.imageStructureHeader['image_type'] = 3
            elif self.imageStructureHeader['num_cols'] == 11000 and self.imageStructureHeader['num_lines'] == 1100:  # HRIT FD VIS
                self.imageStructureHeader['image_type'] = 0
            elif self.imageStructureHeader['num_cols'] == 2750 and self.imageStructureHeader['num_lines'] == 275:  # HRIT FD IR
                self.imageStructureHeader['image_type'] = 0
            elif self.imageStructureHeader['num_cols'] == 7736 and self.imageStructureHeader['num_lines'] == 1544:  # HRIT ENH VIS
                self.imageStructureHeader['image_type'] = 1
            elif self.imageStructureHeader['num_cols'] == 1934 and self.imageStructureHeader['num_lines'] == 386:  # HRIT ENH IR
                self.imageStructureHeader['image_type'] = 1
            elif self.imageStructureHeader['num_cols'] == 7736 and self.imageStructureHeader['num_lines'] == 1592:  # HRIT LSH VIS
                self.imageStructureHeader['image_type'] = 2
            elif self.imageStructureHeader['num_cols'] == 1934 and self.imageStructureHeader['num_lines'] == 398:  # HRIT LSH IR
                self.imageStructureHeader['image_type'] = 2
            elif self.imageStructureHeader['num_cols'] == 4056 and self.imageStructureHeader['num_lines'] == 3060:  # HRIT APNH VIS
                self.imageStructureHeader['image_type'] = 3
            elif self.imageStructureHeader['num_cols'] == 1014 and self.imageStructureHeader['num_lines'] == 765:  # HRIT APNH IR
                self.imageStructureHeader['image_type'] = 3

            self.imageStructureHeader['image_compression'] = int.from_bytes(self.readbytes(8), byteorder='big')

            self.byteOffset += self.imageStructureHeader['header_len']
            if printInfo:
                self.printImageStructureHeader()
        else:
            self.imageStructureHeader['valid'] = False

    def parseImageNavigationHeader(self, printInfo=False):
        """
        Parses xRIT Image Navigation header (type 2)
        :param printInfo: Print info after parsing
        """

        if self.readbytes(0, 3) == b'\x02\x00\x33':
            self.imageNavigationHeader['valid'] = True
            self.imageNavigationHeader['header_type'] = 2
            self.imageNavigationHeader['header_len'] = 51
            self.imageNavigationHeader['header_offset'] = self.byteOffset

            # Projection and longitude
            projectionString = self.readbytes(3, 32).decode()
            if projectionString.__contains__("GEOS"):
                self.imageNavigationHeader['projection'] = "Normalized Geostationary Projection (GEOS)"
            self.imageNavigationHeader['longitude'] = projectionString[projectionString.index("(") + 1:projectionString.index(")")]

            # Scaling factors
            self.imageNavigationHeader['col_scaling'] = int.from_bytes(self.readbytes(35, 4), byteorder='big')
            self.imageNavigationHeader['line_scaling'] = int.from_bytes(self.readbytes(39, 4), byteorder='big')

            # Offsets
            self.imageNavigationHeader['col_offset'] = int.from_bytes(self.readbytes(43, 4), byteorder='big')
            self.imageNavigationHeader['line_offset'] = int.from_bytes(self.readbytes(47, 4), byteorder='big')

            self.byteOffset += self.imageNavigationHeader['header_len']
            if printInfo:
                self.printImageNavigationHeader()
        else:
            self.imageNavigationHeader['valid'] = False

    def parseImageDataFunctionHeader(self, printInfo=False):
        """
        Parses xRIT Image Data Function header (type 3)
        :param printInfo: Print info after parsing
        """

        if self.readbytes(0) == b'\x03':
            self.imageDataFunctionHeader['valid'] = True
            self.imageDataFunctionHeader['header_type'] = 3
            self.imageDataFunctionHeader['header_len'] = int.from_bytes(self.readbytes(1, 2), byteorder='big')
            self.imageDataFunctionHeader['header_offset'] = self.byteOffset

            self.imageDataFunctionHeader['data_definition_block'] = self.readbytes(3, self.imageDataFunctionHeader['header_len'] - 3).decode()
            self.imageDataFunctionHeader['data_definition_block_filename'] = self.path[:-5] + "_IDF-DDB.txt"

            ddbFile = open(self.imageDataFunctionHeader['data_definition_block_filename'], 'w')
            ddbFile.write(self.imageDataFunctionHeader['data_definition_block'])
            ddbFile.close()

            self.byteOffset += self.imageDataFunctionHeader['header_len']
            if printInfo:
                self.printImageDataFunctionHeader()

    def parseAnnotationTextHeader(self, printInfo=False):
        """
        Parses xRIT Annotation Text header (type 4)
        :param printInfo: Print info after parsing
        """

        if self.readbytes(0) == b'\x04':
            self.annotationTextHeader['valid'] = True
            self.annotationTextHeader['header_type'] = 4
            self.annotationTextHeader['header_len'] = int.from_bytes(self.readbytes(1, 2), byteorder='big')
            self.annotationTextHeader['header_offset'] = self.byteOffset

            self.annotationTextHeader['text_data'] = self.readbytes(3, self.annotationTextHeader['header_len'] - 3).decode()

            self.byteOffset += self.annotationTextHeader['header_len']
            if printInfo:
                self.printAnnotationTextHeader()
        else:
            self.imageNavigationHeader['valid'] = False

    def parseTimestampHeader(self, printInfo=False):
        """
        Parses xRIT CCSDS Timestamp header (type 5)
        :param printInfo: Print info after parsing 
        """

        if self.readbytes(0, 3) == b'\x05\x00\x0A':
            self.timestampHeader['valid'] = True
            self.timestampHeader['header_type'] = 5
            self.timestampHeader['header_len'] = 10
            self.timestampHeader['header_offset'] = self.byteOffset

            # CDS P Field
            pFieldInt = int.from_bytes(self.readbytes(3), byteorder='big')
            self.timestampHeader['p_field'] = bin(pFieldInt)[2:].zfill(8)

            # Bit 0 - Extension flag, Bits 1-3 - Time code ID, Bits 4-7 - Detail bits
            pField = [self.timestampHeader['p_field'][0], self.timestampHeader['p_field'][1:4], self.timestampHeader['p_field'][4:8]]

            # Extension flag
            if pField[0] == "0":
                self.timestampHeader['p_field_ext_flag'] = "0 (No extension)"
            else:
                self.timestampHeader['p_field_ext_flag'] = pField[0] + " (Extended field)"

            # Time code ID
            if pField[1] == "100":
                self.timestampHeader['p_field_time_code'] = "100 (1958 January 1 epoch - Level 1 Time Code)"
            elif pField[1] == "010":
                self.timestampHeader['p_field_time_code'] = "010 (Agency-defined epoch - Level 2 Time Code)"

            # Detail bits
            self.timestampHeader['p_field_detail_bits'] = pField[2]


            # CDS T Field
            tFieldInt = int.from_bytes(self.readbytes(4, 6), byteorder='big')
            self.timestampHeader['t_field'] = bin(tFieldInt)[2:].zfill(48)

            # Bits 0-16 - Days since epoch, Bits 16-48 - Milliseconds of day
            tField = [int(self.timestampHeader['t_field'][0:16], 2), int(self.timestampHeader['t_field'][16:48], 2)]

            epoch = datetime.strptime("01/01/1958", '%d/%m/%Y')
            currentDate = epoch + timedelta(days=tField[0])
            self.timestampHeader['t_field_day_count'] = tField[0]
            self.timestampHeader['t_field_current_date'] = currentDate.strftime('%d/%m/%Y')
            self.timestampHeader['t_field_millis'] = tField[1]
            currentDate += timedelta(milliseconds=self.timestampHeader['t_field_millis'])
            self.timestampHeader['t_field_current_time'] = currentDate.strftime('%H:%M:%S')

            self.byteOffset += self.timestampHeader['header_len']
            if printInfo:
                self.printTimestampHeader()
        else:
            self.timestampHeader['valid'] = False

    def parseAncillaryTextHeader(self, printInfo=False):
        """
        Parses xRIT Ancillary Text header (type 6)
        Header type unused. Allows for future xRIT expansion.
        :param printInfo: Print info after parsing 
        """

        if self.readbytes == b'\x06':
            self.ancillaryTextHeader['valid'] = True
            self.ancillaryTextHeader['header_type'] = 6
            self.ancillaryTextHeader['header_len'] = int.from_bytes(self.readbytes(1, 2), byteorder='big')
            self.ancillaryTextHeader['header_offset'] = self.byteOffset

            self.byteOffset += self.ancillaryTextHeader['header_len']
            # if printInfo:  # Not implemented
                # self.printAncillaryTextHeader()
        else:
            self.ancillaryTextHeader['valid'] = False

    def parseKeyHeader(self, printInfo=False):
        """
        Parses xRIT Key header (type 7)
        Provides number of encryption key used.
        :param printInfo: Print info after parsing.
        """
        if self.readbytes(0, 3) == b'\x07\x00\x07':
            self.keyHeader['valid'] = True
            self.keyHeader['header_type'] = 7
            self.keyHeader['header_len'] = 7
            self.keyHeader['header_offset'] = self.byteOffset

            self.keyHeader['key'] = int.from_bytes(self.readbytes(3, 4), byteorder='big')

            self.byteOffset += self.keyHeader['header_len']
            if printInfo:
                self.printKeyHeader()
        else:
            self.keyHeader['valid'] = False

    def parseImageSegmentationInformationHeader(self, printInfo=False):
        """
        Parses xRIT Image Segmentation Information header (type 128)
        :param printInfo: Print info after parsing.
        """
        if self.readbytes(0, 3) == b'\x80\x00\x07':
            self.imageSegmentationInformationHeader['valid'] = True
            self.imageSegmentationInformationHeader['header_type'] = 128
            self.imageSegmentationInformationHeader['header_len'] = 7
            self.imageSegmentationInformationHeader['header_offset'] = self.byteOffset

            self.imageSegmentationInformationHeader['segment_num'] = int.from_bytes(self.readbytes(3), byteorder='big')
            self.imageSegmentationInformationHeader['segment_total'] = int.from_bytes(self.readbytes(4), byteorder='big')
            self.imageSegmentationInformationHeader['line_num_of_segment'] = int.from_bytes(self.readbytes(5, 2), byteorder='big')

            self.byteOffset += self.imageSegmentationInformationHeader['header_len']
            if printInfo:
                self.printImageSegmentationInformationHeader()
        else:
            self.imageSegmentationInformationHeader['valid'] = False

    def parseImageCompensationInformationHeader(self, printInfo=False):
        """
        Parses HRIT Image Compensation Information header (type 130)
        :param printInfo: Print info after parsing.
        """
        if self.readbytes(0) == b'\x82':
            self.imageCompensationInformationHeader['valid'] = True
            self.imageCompensationInformationHeader['header_type'] = 130
            self.imageCompensationInformationHeader['header_len'] = int.from_bytes(self.readbytes(1, 2), byteorder='big')
            self.imageCompensationInformationHeader['header_offset'] = self.byteOffset
            self.imageCompensationInformationHeader['data'] = self.readbytes(3, self.imageCompensationInformationHeader['header_len']-3).decode().replace('\n', '\n\t')

            self.byteOffset += self.imageCompensationInformationHeader['header_len']
            if printInfo:
                self.printImageCompensationInformationHeader()
        else:
            self.imageCompensationInformationHeader['valid'] = False

    def parseImageObservationTimeHeader(self, printInfo=False):
        """
        Parses HRIT Image Observation Time header (type 131)
        :param printInfo: Print info after parsing.
        """

        if self.readbytes(0) == b'\x83':
            self.imageObservationTimeHeader['valid'] = True
            self.imageObservationTimeHeader['header_type'] = 131
            self.imageObservationTimeHeader['header_len'] = int.from_bytes(self.readbytes(1, 2), byteorder='big')
            self.imageObservationTimeHeader['header_offset'] = self.byteOffset
            self.imageObservationTimeHeader['mjd'] = self.readbytes(3, self.imageObservationTimeHeader['header_len']-3).decode()
            self.imageObservationTimeHeader['date'] = jd2gcal(2400000.5, float(self.imageObservationTimeHeader['mjd']))

            self.byteOffset += self.imageObservationTimeHeader['header_len']
            if printInfo:
                self.printImageObservationTimeHeader()
        else:
            self.imageObservationTimeHeader['valid'] = False

    def parseImageQualityInformationHeader(self, printInfo=False):
        """
        Parses HRIT Image Quality Information header (type 132)
        :param printInfo: Print info after parsing.
        """

        if self.readbytes(0) == b'\x84':
            self.imageQualityInformationHeader['valid'] = True
            self.imageQualityInformationHeader['header_type'] = 132
            self.imageQualityInformationHeader['header_len'] = int.from_bytes(self.readbytes(1, 2), byteorder='big')
            self.imageQualityInformationHeader['header_offset'] = self.byteOffset
            self.imageQualityInformationHeader['quality'] = self.readbytes(3, self.imageQualityInformationHeader['header_len']-3).decode()

            self.byteOffset += self.imageQualityInformationHeader['header_len']
            if printInfo:
                self.printImageQualityInformationHeader()
        else:
            self.imageQualityInformationHeader['valid'] = False


    # Header output methods
    def printPrimaryHeader(self):
        """
        Output Primary header details to the console
        """

        if self.primaryHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.primaryHeader['header_type']).zfill(3), self.intToHexStr(self.primaryHeader['header_offset'], 4), self.headerTypes[0]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.primaryHeader['header_len'], self.intToHexStr(self.primaryHeader['header_len'])))

            print("\tFile type:             {0}, {1}".format(self.primaryHeader['file_type'], self.fileTypes[self.primaryHeader['file_type']]))
            print("\tTotal header length:   {0} ({1})".format(self.primaryHeader['total_header_len'], self.intToHexStr(self.primaryHeader['total_header_len'])))
            print("\tData length:           {0} ({1})".format(self.primaryHeader['data_field_len'], self.intToHexStr(self.primaryHeader['data_field_len'])))
            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[0]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printImageStructureHeader(self):
        """
        Output Image Structure header details to the console
        """

        if self.imageStructureHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.imageStructureHeader['header_type']).zfill(3), self.intToHexStr(self.imageStructureHeader['header_offset'], 4), self.headerTypes[1]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.imageStructureHeader['header_len'], self.intToHexStr(self.imageStructureHeader['header_len'])))

            print("\tBits per pixel:        {0} ({1})".format(int.from_bytes(self.imageStructureHeader['bits_per_pixel'], byteorder='big'), self.intToHexStr(int.from_bytes(self.imageStructureHeader['bits_per_pixel'], byteorder='big'))))

            print("\tImage:                 {0}".format(self.imageTypes[self.imageStructureHeader['image_type']]))
            print("\t  - Columns: {0}".format(self.imageStructureHeader['num_cols']))
            print("\t  - Lines:   {0}".format(self.imageStructureHeader['num_lines']))

            print("\tCompression:           {0}, {1}".format(self.imageStructureHeader['image_compression'], self.compressionTypes[self.imageStructureHeader['image_compression']]))
            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[1]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printImageNavigationHeader(self):
        """
        Output Image Navigation header details to the console
        """
        if self.imageNavigationHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.imageNavigationHeader['header_type']).zfill(3), self.intToHexStr(self.imageNavigationHeader['header_offset'], 4), self.headerTypes[2]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.imageNavigationHeader['header_len'], self.intToHexStr(self.imageNavigationHeader['header_len'])))

            # Projection and longitude
            print("\tProjection:            {0}".format(self.imageNavigationHeader['projection']))
            print("\tLongitude:             {0}° E".format(self.imageNavigationHeader['longitude']))

            # Scaling factors
            print("\tColumn scaling factor: {0}".format(self.imageNavigationHeader['col_scaling']))
            print("\tLine scaling factor:   {0}".format(self.imageNavigationHeader['line_scaling']))

            # Offsets
            print("\tColumn offset:         {0}".format(self.imageNavigationHeader['col_offset']))
            print("\tLine offset:           {0}".format(self.imageNavigationHeader['line_offset']))
            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[2]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printImageDataFunctionHeader(self):
        """
        Output Image Data Function header details to the console
        """
        if self.imageDataFunctionHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.imageDataFunctionHeader['header_type']).zfill(3), self.intToHexStr(self.imageDataFunctionHeader['header_offset'], 4), self.headerTypes[3]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.imageDataFunctionHeader['header_len'], self.intToHexStr( self.imageDataFunctionHeader['header_len'])))

            print("\tData Definition Block:")
            print("\t  - dumped to \"{0}\"".format(self.imageDataFunctionHeader['data_definition_block_filename']))
            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[3]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printAnnotationTextHeader(self):
        """
        Output Annotation Text header details to the console
        """
        if self.annotationTextHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.annotationTextHeader['header_type']).zfill(3), self.intToHexStr(self.annotationTextHeader['header_offset'], 4), self.headerTypes[4]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.annotationTextHeader['header_len'], self.intToHexStr(self.annotationTextHeader['header_len'])))

            print("\tText data:             \"{0}\"".format(self.annotationTextHeader['text_data']))
            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[4]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printTimestampHeader(self):
        """
        Output Timestamp header details to the console
        """
        if self.timestampHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.timestampHeader['header_type']).zfill(3), self.intToHexStr(self.timestampHeader['header_offset'], 4), self.headerTypes[5]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.timestampHeader['header_len'], self.intToHexStr( self.timestampHeader['header_len'])))

            # CDS P Field
            print("\tP Field:               {0}".format(self.timestampHeader['p_field']))
            print("\t  - Extension flag:    {0}".format(self.timestampHeader['p_field_ext_flag']))
            print("\t  - Time code ID:      {0}".format(self.timestampHeader['p_field_time_code']))
            print("\t  - Detail bits:       {0}".format(self.timestampHeader['p_field_detail_bits']))


            # CDS T Field
            print("\tT Field:               {0}".format(self.timestampHeader['t_field']))
            print("\t  - Day counter:       {0} ({1} - DD/MM/YYYY)".format(self.timestampHeader['t_field_day_count'], self.timestampHeader['t_field_current_date']))
            print("\t  - Milliseconds:      {0} ({1} - HH:MM:SS)".format(self.timestampHeader['t_field_millis'], self.timestampHeader['t_field_current_time']))

            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[5]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printKeyHeader(self):
        """
        Output Key header details to the console
        """

        if self.keyHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.keyHeader['header_type']).zfill(3), self.intToHexStr(self.keyHeader['header_offset'], 4), self.headerTypes[7]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.keyHeader['header_len'], self.intToHexStr(self.keyHeader['header_len'])))

            if self.keyHeader['key'] == 0:
                encryptionState = " (disabled)"
            else:
                encryptionState = ""
            print("\tEncryption key:        {0}{1}".format(self.intToHexStr(self.keyHeader['key']), encryptionState))
            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[7]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printImageSegmentationInformationHeader(self):
        """
        Output Image Segmentation Information header details to the console
        """

        if self.imageSegmentationInformationHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.imageSegmentationInformationHeader['header_type']).zfill(3), self.intToHexStr(self.imageSegmentationInformationHeader['header_offset'], 4), self.headerTypes[128]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.imageSegmentationInformationHeader['header_len'], self.intToHexStr(self.imageSegmentationInformationHeader['header_len'])))

            print("\tSegment number:        {0} of {1}".format(self.imageSegmentationInformationHeader['segment_num'], self.imageSegmentationInformationHeader['segment_total']))
            print("\tLine num of image:     {0}".format(self.imageSegmentationInformationHeader['line_num_of_segment']))
            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[128]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printImageCompensationInformationHeader(self):
        """
        Output Image Compensation Information header details to the console
        """

        if self.imageCompensationInformationHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.imageCompensationInformationHeader['header_type']).zfill(3), self.intToHexStr(self.imageCompensationInformationHeader['header_offset'], 4), self.headerTypes[130]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.imageCompensationInformationHeader['header_len'], self.intToHexStr(self.imageCompensationInformationHeader['header_len'])))
            print("\t{0}".format(self.imageCompensationInformationHeader['data']))

            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[130]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printImageObservationTimeHeader(self):
        """
        Output Image Observation Time header details to the console
        """

        if self.imageObservationTimeHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.imageObservationTimeHeader['header_type']).zfill(3), self.intToHexStr(self.imageObservationTimeHeader['header_offset'], 4), self.headerTypes[131]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.imageObservationTimeHeader['header_len'], self.intToHexStr(self.imageObservationTimeHeader['header_len'])))
            print("\tMJD:                   {0}".format(self.imageObservationTimeHeader['mjd']))
            print("\tDate:                  {0}/{1}/{2}".format(str(self.imageObservationTimeHeader['date'][2]).zfill(2), str(self.imageObservationTimeHeader['date'][1]).zfill(2), self.imageObservationTimeHeader['date'][0]))
            print("\tTime:                  {0}".format(str(self.imageObservationTimeHeader['date'][3])))

            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[131]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)

    def printImageQualityInformationHeader(self):
        """
        Output Image Quality Information header details to the console
        """

        if self.imageQualityInformationHeader['valid']:
            self.setConsoleColour("OKGREEN")
            print("[Type {0} : Offset {1}] {2}:".format(str(self.imageQualityInformationHeader['header_type']).zfill(3), self.intToHexStr(self.imageQualityInformationHeader['header_offset'], 4), self.headerTypes[132]))
            self.setConsoleColour()
            print("\tHeader length:         {0} ({1})".format(self.imageQualityInformationHeader['header_len'], self.intToHexStr(self.imageQualityInformationHeader['header_len'])))
            print("\tQuality:               {0}".format(self.imageQualityInformationHeader['quality']))

            print()
        else:
            self.setConsoleColour("FAIL")
            print("ERROR: {0} invalid\n".format(self.headerTypes[132]))
            self.setConsoleColour()
            print("Exiting...")
            exit(1)