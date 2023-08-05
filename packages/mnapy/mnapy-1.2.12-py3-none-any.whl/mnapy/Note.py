from typing import List

from mnapy import NoteLimits
from mnapy import Utils
from mnapy import Wire


class Note:
    def __init__(
            self,
            context,
            Show_Marker,
            Text_Style,
            Note,
            options,
            tag,
            units,
            options_units,
            option_limits,
    ):
        self.Show_Marker = Show_Marker
        self.Text_Style = Text_Style
        self.Note = Note
        self.options = options
        self.tag = tag
        self.units = units
        self.options_units = options_units
        self.option_limits = NoteLimits.NoteLimits(
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

    def Set_Note(self, setter: str) -> None:
        None
        self.Note = setter

    def Get_Note(self) -> str:
        None
        return self.Note

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
