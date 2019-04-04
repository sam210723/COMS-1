class Demuxer:
    """
    Coordinates CCSDS demuxing from VCDU layer to xRIT file layer.
    """

    def __init__(self, mode):
        """
        Initialise Demuxer class
        :param mode: Specify LRIT specify or HRIT mode
        """

        self.mode = mode


    def data_in(self, data):
        
