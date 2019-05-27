# Wait for VCID change to avoid partial TP_Files (disabled after first change)
        if self.lastVCID == None:
            # First VCDU (demuxer just started)
            self.lastVCID = currentVCDU.VCID
            currentVCDU.print_info()
            return
        elif self.lastVCID == currentVCDU.VCID:
            # VCID has not changed
            if not self.seenVCDUChange:
                # Never seen VCID change, ignore data (avoids starting demux part way through a TP_File)
                return
        else:
            # VCID has changed

            # Trigger TP_File processing on VCID change
            if self.lastVCID != 63:
                try:
                    self.finish_tpfile()
                except AttributeError:
                    pass

            self.seenVCDUChange = True
            self.lastVCID = currentVCDU.VCID

            # Display VCID change
            currentVCDU.print_info()

        if currentVCDU.VCID == 63:
            # Discard fill packets
            return