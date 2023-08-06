from mnapy import Constants
from mnapy import Flags
from mnapy import Settings
from mnapy import Variable


class Global:
    def __init__(self):
        self.SystemVariables = Variable.Variable()
        self.SystemSettings = Settings.Settings()
        self.SystemFlags = Flags.Flags()
        self.SystemConstants = Constants.Constants()
        None
