import math
from typing import List

from mnapy import HighPassFilterLimits
from mnapy import Utils
from mnapy import Wire


class HighPassFilter:
    def __init__(
            self,
            context,
            Y_Hat,
            Y_Out,
            X_Hat,
            Cutoff_Frequency,
            Alpha,
            options,
            Input_Voltage,
            tag,
            units,
            Output_Voltage,
            options_units,
            option_limits,
    ):
        self.Y_Hat = Y_Hat
        self.Y_Out = Y_Out
        self.X_Hat = X_Hat
        self.Cutoff_Frequency = Cutoff_Frequency
        self.Alpha = Alpha
        self.options = options
        self.Input_Voltage = Input_Voltage
        self.tag = tag
        self.units = units
        self.Output_Voltage = Output_Voltage
        self.options_units = options_units
        self.option_limits = HighPassFilterLimits.HighPassFilterLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.Nodes = []
        self.Linkages = []
        self.Designator = ""
        self.Id = -1
        self.SimulationId = -1
        self.ElementType = -1
        self.WireReferences = []
        self.context = context

    def Set_Cutoff_Frequency(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Cutoff_Frequency[0])
                and abs(setter) <= abs(self.option_limits.Cutoff_Frequency[1])
        ) or abs(setter) == 0:
            self.Cutoff_Frequency = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Cutoff_Frequency(self) -> float:
        None
        return self.Cutoff_Frequency

    def reset(self) -> None:
        None
        self.Y_Hat = 0
        self.Y_Out = 0
        self.X_Hat = 0
        self.Output_Voltage = 0

    def update(self) -> None:
        None
        if (
                self.context.Params.SystemFlags.FlagSimulating
                and self.context.solutions_ready
                and self.context.simulation_step != 0
        ):
            self.Input_Voltage = self.context.get_voltage(self.Nodes[0], -1)
            self.Output_Voltage = self.highpass_filter(self.Input_Voltage)
        else:
            self.Y_Hat = 0
            self.Y_Out = 0
            self.X_Hat = 0
            self.Output_Voltage = 0

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[1],
            -1,
            self.Output_Voltage,
            self.context.ELEMENT_HPF_OFFSET + self.SimulationId,
        )

    def highpass_filter(self, input: float) -> float:
        None
        self.Alpha = 1.0 / (
                2.0 * math.pi * self.context.time_step * self.Cutoff_Frequency + 1.0
        )
        self.Y_Hat = self.Alpha * self.Y_Out + self.Alpha * (input - self.X_Hat)
        self.Y_Out = self.Y_Hat
        self.X_Hat = input
        return self.Y_Hat

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
