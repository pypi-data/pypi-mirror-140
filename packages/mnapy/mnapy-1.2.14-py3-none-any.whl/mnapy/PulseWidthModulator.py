import math
from typing import List

from mnapy import PulseWidthModulatorLimits
from mnapy import Utils
from mnapy import Wire


class PulseWidthModulator:
    def __init__(
            self,
            context,
            Max_Frequency,
            A,
            Phase,
            Min_Duty,
            Saw_Wave,
            units,
            High_Voltage,
            options_units,
            Low_Voltage,
            option_limits,
            Min_Frequency,
            Max_Duty,
            Counter,
            Duty,
            Input_Voltage2,
            options,
            Frequency,
            Last_Output_Voltage,
            Input_Voltage1,
            tag,
            Output_Voltage,
            Postscaler,
    ):
        self.Max_Frequency = Max_Frequency
        self.A = A
        self.Phase = Phase
        self.Min_Duty = Min_Duty
        self.Saw_Wave = Saw_Wave
        self.units = units
        self.High_Voltage = High_Voltage
        self.options_units = options_units
        self.Low_Voltage = Low_Voltage
        self.option_limits = PulseWidthModulatorLimits.PulseWidthModulatorLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.Min_Frequency = Min_Frequency
        self.Max_Duty = Max_Duty
        self.Counter = Counter
        self.Duty = Duty
        self.Input_Voltage2 = Input_Voltage2
        self.options = options
        self.Frequency = Frequency
        self.Last_Output_Voltage = Last_Output_Voltage
        self.Input_Voltage1 = Input_Voltage1
        self.tag = tag
        self.Output_Voltage = Output_Voltage
        self.Postscaler = Postscaler
        self.Nodes = []
        self.Linkages = []
        self.Designator = ""
        self.Id = -1
        self.SimulationId = -1
        self.ElementType = -1
        self.WireReferences = []
        self.context = context

    def Set_Max_Frequency(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Max_Frequency[0])
                and abs(setter) <= abs(self.option_limits.Max_Frequency[1])
        ) or abs(setter) == 0:
            self.Max_Frequency = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Max_Frequency(self) -> float:
        None
        return self.Max_Frequency

    def Set_Min_Frequency(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Min_Frequency[0])
                and abs(setter) <= abs(self.option_limits.Min_Frequency[1])
        ) or abs(setter) == 0:
            self.Min_Frequency = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Min_Frequency(self) -> float:
        None
        return self.Min_Frequency

    def Set_Max_Duty(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Max_Duty[0])
                and abs(setter) <= abs(self.option_limits.Max_Duty[1])
        ) or abs(setter) == 0:
            self.Max_Duty = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Max_Duty(self) -> float:
        None
        return self.Max_Duty

    def Set_Phase(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Phase[0])
                and abs(setter) <= abs(self.option_limits.Phase[1])
        ) or abs(setter) == 0:
            self.Phase = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Phase(self) -> float:
        None
        return self.Phase

    def Set_Min_Duty(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Min_Duty[0])
                and abs(setter) <= abs(self.option_limits.Min_Duty[1])
        ) or abs(setter) == 0:
            self.Min_Duty = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Min_Duty(self) -> float:
        None
        return self.Min_Duty

    def Set_Postscaler(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Postscaler[0])
                and abs(setter) <= abs(self.option_limits.Postscaler[1])
        ) or abs(setter) == 0:
            self.Postscaler = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Postscaler(self) -> float:
        None
        return self.Postscaler

    def reset(self) -> None:
        None
        self.A = 0

    def update(self) -> None:
        None
        if (
                self.context.Params.SystemFlags.FlagSimulating
                and self.context.solutions_ready
                and self.context.simulation_step != 0
        ):
            if (
                    self.context.simulation_time < self.context.time_step
                    or self.Counter >= self.Postscaler
            ):
                self.Input_Voltage1 = Utils.Utils.limit(
                    self.context.get_voltage(self.Nodes[0], -1),
                    self.Low_Voltage,
                    self.High_Voltage,
                )
                self.Input_Voltage2 = Utils.Utils.limit(
                    self.context.get_voltage(self.Nodes[1], -1),
                    self.Low_Voltage,
                    self.High_Voltage,
                )
                if self.Counter >= self.Postscaler:
                    self.Counter = 0

            self.Last_Output_Voltage = self.Output_Voltage
            self.Output_Voltage = self.A
            if (
                    abs(self.Last_Output_Voltage - self.Output_Voltage) > 0
                    or self.context.simulation_time < self.context.time_step
            ):
                self.Frequency = Utils.Utils.map_range(
                    self.Input_Voltage1, self.Min_Frequency, self.Max_Frequency
                )
                self.Duty = Utils.Utils.map_range(
                    self.Input_Voltage2, self.Min_Duty, self.Max_Duty
                )
                self.Counter += 1

            self.Saw_Wave = 0.5 - (1 / math.pi) * math.atan(
                1.0
                / (math.tan(
                    self.context.simulation_time * math.pi * self.Frequency
                    + math.radians(self.Phase)
                ) + self.context.Params.SystemConstants.ZERO_BIAS)
            )
            if self.Saw_Wave > 1.0 - self.Duty * 0.01:
                self.A = self.High_Voltage
            else:
                self.A = self.Low_Voltage

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[2],
            -1,
            self.Output_Voltage,
            self.context.ELEMENT_PWM_OFFSET + self.SimulationId,
        )

    def SetId(self, Id: str) -> None:
        None
        self.Id = int(Id)

    def SetNodes(self, Nodes: List[int]) -> None:
        None
        self.Nodes = Nodes

    def SetLinkages(self, Linkages: List[int]) -> None:
        None
        self.Linkages = Linkages

    def SetDesignator(self, Designator: str) -> None:
        None
        self.Designator = Designator

    def GetDesignator(self) -> str:
        None
        return self.Designator

    def SetSimulationId(self, Id: int) -> None:
        None
        self.SimulationId = Id

    def SetWireReferences(self, wires: List[Wire.Wire]) -> None:
        None
        self.WireReferences.clear()
        for i in range(0, len(wires)):
            self.WireReferences.append(wires[i])

    def GetNode(self, i: int) -> int:
        None
        if i < len(self.Nodes):
            return self.Nodes[i]
        else:
            return -1

    def GetElementType(self) -> int:
        None
        return self.ElementType

    def SetElementType(self, setter: int) -> None:
        None
        self.ElementType = setter
