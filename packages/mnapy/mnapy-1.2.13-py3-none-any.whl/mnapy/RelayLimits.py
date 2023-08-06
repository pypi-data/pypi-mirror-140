class RelayLimits:
    def __init__(
            self,
            Inductance,
            Closed_Resistance,
            Coil_Resistance,
            Must_Operate_Voltage,
            Must_Release_Voltage,
    ):
        self.Inductance = Inductance
        self.Closed_Resistance = Closed_Resistance
        self.Coil_Resistance = Coil_Resistance
        self.Must_Operate_Voltage = Must_Operate_Voltage
        self.Must_Release_Voltage = Must_Release_Voltage
