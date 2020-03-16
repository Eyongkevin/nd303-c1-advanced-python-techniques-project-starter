class Error(Exception):
    """
    Base class exception for this module
    """
    def __init__(self, msg):
            self.msg = msg

    def __str__(self):
        return "{}".format(self.msg)

class UnsupportedFeature(Error):
    """
    Custom exception for an unimplemented feature
    """

    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
    pass


class DataHasIncorrectAttributesError(Error):
    def __init__(self, msg = "DataHasIncorrectAttributesError occured"):
        super().__init__(msg)



class FormatHasINvalidValueError(Error):
    def __init__(self, msg = "FormatHasINvalidValueError occured"):
        super().__init__(msg)

class ArgDatesInputChoiceError(Error):
    def __init__(self, msg = "ArgDatesInputChoiceError occured"):
        super().__init__(msg)


# TODO: See how you can add more information about the exception, like error line number where the exception was raised.