from typing import List

from mnapy import OperationalAmplifierLimits
from mnapy import Utils
from mnapy import Wire


class OperationalAmplifier:
    def __init__(self, context, options, tag, units, options_units, option_limits):
        self.options = options
        self.tag = tag
        self.units = units
        self.options_units = options_units
        self.option_limits = OperationalAmplifierLimits.OperationalAmplifierLimits(
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

    def reset(self) -> None:
        None

    def update(self) -> None:
        None

    def stamp(self) -> None:
        None
        self.context.stamp_ideal_opamp(
            self.Nodes[0],
            self.Nodes[1],
            self.Nodes[2],
            self.context.ELEMENT_OPAMP_OFFSET + self.SimulationId,
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
