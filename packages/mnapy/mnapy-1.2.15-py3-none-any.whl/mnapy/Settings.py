import math


class Settings:
    def __init__(self) -> None:
        self.WIRE_RESISTANCE = 1e-6
        self.MAXNODES = 900
        self.SQRT_MAXNODES = math.sqrt(self.MAXNODES)
        self.SQRT_MAXNODES_M1 = self.SQRT_MAXNODES - 1
        self.INV_SQRT_M_1 = 1.0 / (self.SQRT_MAXNODES - 1)
        self.R_MAX = 1e12
        self.INV_R_MAX = 1.0 / self.R_MAX
        self.R_GROUND = 1e-12
        self.R_NODE_TO_GROUND = 1e-15
        self.RELTOL = 1e-3
        self.ABSTOL = 1e-12
        self.VNTOL = 1e-6
        self.TOLERANCE = 1e-3
        self.ITL4 = 96
        self.MAX_VOLTAGE = 500e6
        self.MIN_VOLTAGE = 1e-15
        self.MAX_CURRENT = 500e6
        self.MIN_CURRENT = 1e-15
        self.MAX_CAPACITANCE = 500e6
        self.MIN_CAPACITANCE = 1e-15
        self.MAX_INDUCTANCE = 500e6
        self.MIN_INDUCTANCE = 1e-15
        self.MAX_GAIN = 500e6
        self.MIN_GAIN = 1e-15
        self.MAX_FREQUENCY = 500e6
        self.MIN_FREQUENCY = 1e-15
        self.MAX_WAVELENGTH = 700
        self.MIN_WAVELENGTH = 400
        self.MAX_POTENTIOMETER_WIPER = 99.99
        self.MIN_POTENTIOMETER_WIPER = 0.01
        self.MAX_PHASE = 360.0
        self.MIN_PHASE = 0
        self.MAX_BIT_RESOLUTION = 24
        self.MIN_BIT_RESOLUTION = 1
        self.MAX_DUTY_CYCLE = 98.0
        self.MIN_DUTY_CYCLE = 2
        self.MAX_POSTSCALER = 500e6
        self.MIN_POSTSCALER = 1
        self.THERMAL_VOLTAGE = 25.6e-3
        self.GMIN_DEFAULT = 1e-9
        None
