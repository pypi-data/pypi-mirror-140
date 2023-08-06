class PIDModuleLimits:
    def __init__(self, Max_Output, Kp, Min_Output, Setpoint, Kd, Ki):
        self.Max_Output = Max_Output
        self.Kp = Kp
        self.Min_Output = Min_Output
        self.Setpoint = Setpoint
        self.Kd = Kd
        self.Ki = Ki
