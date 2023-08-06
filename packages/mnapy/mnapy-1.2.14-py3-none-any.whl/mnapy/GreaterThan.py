from typing import List

from mnapy import GreaterThanLimits
from mnapy import Utils
from mnapy import Wire


class GreaterThan:
    def __init__(
            self,
            context,
            Input_Voltage2,
            options,
            Input_Voltage1,
            tag,
            units,
            Output_Voltage,
            options_units,
            option_limits,
    ):
        self.Input_Voltage2 = Input_Voltage2
        self.options = options
        self.Input_Voltage1 = Input_Voltage1
        self.tag = tag
        self.units = units
        self.Output_Voltage = Output_Voltage
        self.options_units = options_units
        self.option_limits = GreaterThanLimits.GreaterThanLimits(
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
        self.Output_Voltage = 0

    def update(self) -> None:
        None
        if (
                self.context.Params.SystemFlags.FlagSimulating
                and self.context.solutions_ready
                and self.context.simulation_step != 0
        ):
            self.Input_Voltage1 = self.context.get_voltage(self.Nodes[0], -1)
            self.Input_Voltage2 = self.context.get_voltage(self.Nodes[1], -1)
            if self.Input_Voltage1 > self.Input_Voltage2:
                self.Output_Voltage = 1
            else:
                self.Output_Voltage = 0

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[2],
            -1,
            self.Output_Voltage,
            self.context.ELEMENT_GRT_OFFSET + self.SimulationId,
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
