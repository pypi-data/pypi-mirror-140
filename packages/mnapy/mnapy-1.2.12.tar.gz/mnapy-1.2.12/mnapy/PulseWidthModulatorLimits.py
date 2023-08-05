class PulseWidthModulatorLimits:
    def __init__(
            self, Max_Frequency, Min_Frequency, Max_Duty, Phase, Min_Duty, Postscaler
    ):
        self.Max_Frequency = Max_Frequency
        self.Min_Frequency = Min_Frequency
        self.Max_Duty = Max_Duty
        self.Phase = Phase
        self.Min_Duty = Min_Duty
        self.Postscaler = Postscaler
