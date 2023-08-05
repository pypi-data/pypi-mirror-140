import math
from typing import List

from mnapy import SawWaveLimits
from mnapy import Utils
from mnapy import Wire


class SawWave:
    def __init__(
            self,
            context,
            Phase,
            Voltage,
            options,
            Frequency,
            tag,
            units,
            options_units,
            option_limits,
            Offset,
    ):
        self.Phase = Phase
        self.Voltage = Voltage
        self.options = options
        self.Frequency = Frequency
        self.tag = tag
        self.units = units
        self.options_units = options_units
        self.option_limits = SawWaveLimits.SawWaveLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.Offset = Offset
        self.Nodes = []
        self.Linkages = []
        self.Designator = ""
        self.Id = -1
        self.SimulationId = -1
        self.ElementType = -1
        self.WireReferences = []
        self.context = context

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

    def Set_Voltage(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Voltage[0])
                and abs(setter) <= abs(self.option_limits.Voltage[1])
        ) or abs(setter) == 0:
            self.Voltage = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Voltage(self) -> float:
        None
        return self.Voltage

    def Set_Frequency(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Frequency[0])
                and abs(setter) <= abs(self.option_limits.Frequency[1])
        ) or abs(setter) == 0:
            self.Frequency = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Frequency(self) -> float:
        None
        return self.Frequency

    def Set_Offset(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Offset[0])
                and abs(setter) <= abs(self.option_limits.Offset[1])
        ) or abs(setter) == 0:
            self.Offset = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Offset(self) -> float:
        None
        return self.Offset

    def reset(self) -> None:
        None

    def update(self) -> None:
        None

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[0],
            self.Nodes[1],
            self.Offset
            - ((2 * self.Voltage) / math.pi)
            * math.atan(
                1.0
                / (
                        math.tan(
                            self.context.simulation_time * math.pi * self.Frequency
                            + math.radians(self.Phase)
                        )
                        + 1e-19
                )
            ),
            self.context.ELEMENT_SAW_OFFSET + self.SimulationId,
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
