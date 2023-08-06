from typing import List

from mnapy import SinglePoleSingleThrowLimits
from mnapy import Utils
from mnapy import Wire


class SinglePoleSingleThrow:
    def __init__(
            self,
            context,
            Closed_Resistance,
            options,
            Open_Resistance,
            tag,
            units,
            Switch_State,
            options_units,
            option_limits,
    ):
        self.Closed_Resistance = Closed_Resistance
        self.options = options
        self.Open_Resistance = Open_Resistance
        self.tag = tag
        self.units = units
        self.Switch_State = Switch_State
        self.options_units = options_units
        self.option_limits = SinglePoleSingleThrowLimits.SinglePoleSingleThrowLimits(
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

    def Set_Switch_State(self, setter: str) -> None:
        None
        if setter == (self.context.Params.SystemConstants.OFF) or setter == (
                self.context.Params.SystemConstants.ON
        ):
            self.Switch_State = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Switch_State(self) -> str:
        None
        return self.Switch_State

    def Set_Closed_Resistance(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Closed_Resistance[0])
                and abs(setter) <= abs(self.option_limits.Closed_Resistance[1])
        ) or abs(setter) == 0:
            self.Closed_Resistance = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Closed_Resistance(self) -> float:
        None
        return self.Closed_Resistance

    def reset(self) -> None:
        None

    def update(self) -> None:
        None

    def stamp(self) -> None:
        None
        if self.Switch_State == (self.context.Params.SystemConstants.ON):
            self.context.stamp_resistor(
                self.Nodes[0], self.Nodes[1], self.Closed_Resistance
            )
        else:
            self.context.stamp_node(self.Nodes[0], self.Open_Resistance)
            self.context.stamp_node(self.Nodes[1], self.Open_Resistance)

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
