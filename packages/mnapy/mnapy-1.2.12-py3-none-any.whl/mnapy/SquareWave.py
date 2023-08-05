from typing import List

from mnapy import SquareWaveLimits
from mnapy import Utils
from mnapy import Wire


class SquareWave:
    def __init__(
            self,
            context,
            Duty,
            Voltage,
            options,
            Frequency,
            tag,
            units,
            options_units,
            option_limits,
            Offset,
    ):
        self.Duty = Duty
        self.Voltage = Voltage
        self.options = options
        self.Frequency = Frequency
        self.tag = tag
        self.units = units
        self.options_units = options_units
        self.option_limits = SquareWaveLimits.SquareWaveLimits(
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

    def Set_Duty(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Duty[0])
                and abs(setter) <= abs(self.option_limits.Duty[1])
        ) or abs(setter) == 0:
            self.Duty = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")
        None

    def Get_Duty(self) -> float:
        None
        return self.Duty

    def Set_Voltage(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Voltage[0])
                and abs(setter) <= abs(self.option_limits.Voltage[1])
        ) or abs(setter) == 0:
            self.Voltage = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")
        None

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
        None

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
        None

    def Get_Offset(self) -> float:
        None
        return self.Offset

    def reset(self) -> None:
        None

    def update(self) -> None:
        None

    def stamp(self) -> None:
        None
        mod = 0
        if Utils.Utils.wrap(
                self.context.simulation_time, 1.0 / self.Frequency
        ) < self.Duty * 0.01 * (1.0 / self.Frequency):
            mod = 1
        else:
            mod = 0

        self.context.stamp_voltage(
            self.Nodes[0],
            self.Nodes[1],
            self.Offset + self.Voltage * mod,
            self.context.ELEMENT_SQUAREWAVE_OFFSET + self.SimulationId,
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
        None

    def GetNode(self, i: int) -> int:
        None
        if i < len(self.Nodes):
            return self.Nodes[i]
        else:
            return -1
        None

    def GetElementType(self) -> int:
        None
        return self.ElementType

    def SetElementType(self, setter: int) -> None:
        None
        self.ElementType = setter
