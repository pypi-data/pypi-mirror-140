from typing import List

from mnapy import FuseLimits
from mnapy import Utils
from mnapy import Wire


class Fuse:
    def __init__(
            self,
            context,
            Resistance,
            Voltage,
            Current_Rating,
            options,
            tag,
            units,
            options_units,
            option_limits,
            Broken,
    ):
        self.Resistance = Resistance
        self.Voltage = Voltage
        self.Current_Rating = Current_Rating
        self.options = options
        self.tag = tag
        self.units = units
        self.options_units = options_units
        self.option_limits = FuseLimits.FuseLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.Broken = Broken
        self.Nodes = []
        self.Linkages = []
        self.Designator = ""
        self.Id = -1
        self.SimulationId = -1
        self.ElementType = -1
        self.WireReferences = []
        self.context = context

    def Set_Resistance(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Resistance[0])
                and abs(setter) <= abs(self.option_limits.Resistance[1])
        ) or abs(setter) == 0:
            self.Resistance = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Resistance(self) -> float:
        None
        return self.Resistance

    def Set_Current_Rating(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Current_Rating[0])
                and abs(setter) <= abs(self.option_limits.Current_Rating[1])
        ) or abs(setter) == 0:
            self.Current_Rating = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Current_Rating(self) -> float:
        None
        return self.Current_Rating

    def reset(self) -> None:
        None
        self.Broken = False

    def update(self) -> None:
        None
        if (
                self.context.Params.SystemFlags.FlagSimulating
                and self.context.solutions_ready
                and self.context.simulation_step != 0
        ):
            self.Voltage = abs(self.context.get_voltage(self.Nodes[0], self.Nodes[1]))
            if self.Voltage / self.Resistance >= self.Current_Rating:
                self.Broken = True

        else:
            self.Broken = False

    def stamp(self) -> None:
        None
        if not self.Broken:
            self.context.stamp_resistor(self.Nodes[0], self.Nodes[1], self.Resistance)

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
