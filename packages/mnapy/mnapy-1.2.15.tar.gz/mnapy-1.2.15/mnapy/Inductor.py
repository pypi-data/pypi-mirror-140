from typing import List

from mnapy import InductorLimits
from mnapy import Utils
from mnapy import Wire


class Inductor:
    def __init__(
            self,
            context,
            Transient_Resistance,
            Inductance,
            options,
            Initial_Current,
            tag,
            units,
            Transient_Current,
            Transient_Voltage,
            options_units,
            Equivalent_Current,
            option_limits,
    ):
        self.Transient_Resistance = Transient_Resistance
        self.Inductance = Inductance
        self.options = options
        self.Initial_Current = Initial_Current
        self.tag = tag
        self.units = units
        self.Transient_Current = Transient_Current
        self.Transient_Voltage = Transient_Voltage
        self.options_units = options_units
        self.Equivalent_Current = Equivalent_Current
        self.option_limits = InductorLimits.InductorLimits(
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

    def Set_Inductance(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Inductance[0])
                and abs(setter) <= abs(self.option_limits.Inductance[1])
        ) or abs(setter) == 0:
            self.Inductance = setter
            self.conserve_energy()
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Inductance(self) -> float:
        None
        return self.Inductance

    def Set_Initial_Current(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Initial_Current[0])
                and abs(setter) <= abs(self.option_limits.Initial_Current[1])
        ) or abs(setter) == 0:
            self.Initial_Current = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Initial_Current(self) -> float:
        None
        return self.Initial_Current

    def reset(self) -> None:
        None
        self.Transient_Resistance = (2 * self.Inductance) / self.context.time_step
        self.Transient_Voltage = 0
        self.Transient_Current = self.Initial_Current
        self.Equivalent_Current = (
                self.Transient_Voltage / self.Transient_Resistance + self.Transient_Current
        )

    def update(self) -> None:
        None

    def stamp(self) -> None:
        None
        self.context.stamp_inductor(
            self.Nodes[0],
            self.Nodes[1],
            self.Transient_Resistance,
            self.Equivalent_Current,
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

    def update_inductor(self) -> None:
        None
        if self.context.solutions_ready:
            voltage: float = self.context.get_voltage(self.Nodes[0], self.Nodes[1])
            self.Transient_Voltage = voltage
            self.Transient_Current = (
                    voltage / self.Transient_Resistance + self.Equivalent_Current
            )
            self.Equivalent_Current = (
                    self.Transient_Voltage / self.Transient_Resistance
                    + self.Transient_Current
            )

    def conserve_energy(self) -> None:
        None
        self.Transient_Resistance = (2 * self.Inductance) / self.context.time_step
        self.Equivalent_Current = (
                self.Transient_Voltage / self.Transient_Resistance + self.Transient_Current
        )

    def GetElementType(self) -> int:
        None
        return self.ElementType

    def SetElementType(self, setter: int) -> None:
        None
        self.ElementType = setter
