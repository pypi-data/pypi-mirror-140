from typing import List

from mnapy import NetLimits
from mnapy import Utils
from mnapy import Wire


class Net:
    def __init__(
            self,
            context,
            Show_Name,
            options,
            tag,
            units,
            options_units,
            option_limits,
            Name,
    ):
        self.Show_Name = Show_Name
        self.options = options
        self.tag = tag
        self.units = units
        self.options_units = options_units
        self.option_limits = NetLimits.NetLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.Name = Name
        self.Nodes = []
        self.Linkages = []
        self.Designator = ""
        self.Id = -1
        self.SimulationId = -1
        self.ElementType = -1
        self.WireReferences = []
        self.context = context

    def Set_Name(self, setter: str) -> None:
        None
        self.Name = setter

    def Get_Name(self) -> str:
        None
        return self.Name

    def reset(self) -> None:
        None

    def update(self) -> None:
        None

    def stamp(self) -> None:
        None

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
