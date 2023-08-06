import math
from typing import List

from mnapy import DFlipFlopLimits
from mnapy import Utils
from mnapy import Wire


class DFlipFlop:
    def __init__(
            self,
            context,
            N_Q,
            Q,
            Last_Clock,
            options,
            Input_Voltage1,
            tag,
            units,
            Clock,
            options_units,
            option_limits,
    ):
        self.N_Q = N_Q
        self.Q = Q
        self.Last_Clock = Last_Clock
        self.options = options
        self.Input_Voltage1 = Input_Voltage1
        self.tag = tag
        self.units = units
        self.Clock = Clock
        self.options_units = options_units
        self.option_limits = DFlipFlopLimits.DFlipFlopLimits(
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
        self.Clock = 0
        self.Last_Clock = 1
        self.Q = 0
        self.N_Q = 1

    def update(self) -> None:
        None
        if self.context.Params.SystemFlags.FlagSimulating and self.context.solutions_ready:
            self.Last_Clock = self.Clock
            self.Input_Voltage1 = math.tanh(
                10 * (self.context.get_voltage(self.Nodes[0], -1) - 0.5)
            )
            self.Clock = math.tanh(
                10 * (self.context.get_voltage(self.Nodes[1], -1) - 0.5)
            )
            if abs(self.Last_Clock - self.Clock) > 0.5 and self.Clock > 0.5:
                q_next: float = 0
                if self.Clock >= 0.5 and self.Input_Voltage1 <= 0.5:
                    q_next = 0
                elif self.Clock >= 0.5 and self.Input_Voltage1 >= 0.5:
                    q_next = 1

                self.Q = q_next
                self.N_Q = 1 - q_next

        else:
            None

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[2],
            -1,
            self.Q,
            self.context.ELEMENT_DFF_OFFSET + (self.SimulationId << 1),
        )
        self.context.stamp_voltage(
            self.Nodes[3],
            -1,
            self.N_Q,
            self.context.ELEMENT_DFF_OFFSET + (self.SimulationId << 1) + 1,
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
