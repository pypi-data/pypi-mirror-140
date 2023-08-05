import math
from typing import List

from mnapy import Utils
from mnapy import VoltageControlledSwitchLimits
from mnapy import Wire


class VoltageControlledSwitch:
    def __init__(
            self,
            context,
            Closed_Resistance,
            options,
            Input_Voltage,
            tag,
            units,
            High_Voltage,
            Output_Voltage,
            options_units,
            option_limits,
    ):
        self.Closed_Resistance = Closed_Resistance
        self.options = options
        self.Input_Voltage = Input_Voltage
        self.tag = tag
        self.units = units
        self.High_Voltage = High_Voltage
        self.Output_Voltage = Output_Voltage
        self.options_units = options_units
        self.option_limits = (
            VoltageControlledSwitchLimits.VoltageControlledSwitchLimits(
                **Utils.Utils.FixDictionary(option_limits)
            )
        )
        self.Nodes = []
        self.Linkages = []
        self.Designator = ""
        self.Id = -1
        self.SimulationId = -1
        self.ElementType = -1
        self.WireReferences = []
        self.context = context

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

    def Set_High_Voltage(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.High_Voltage[0])
                and abs(setter) <= abs(self.option_limits.High_Voltage[1])
        ) or abs(setter) == 0:
            self.High_Voltage = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_High_Voltage(self) -> float:
        None
        return self.High_Voltage

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
            self.Input_Voltage = math.tanh(
                10
                * (
                        self.context.get_voltage(self.Nodes[1], -1) / self.High_Voltage
                        - 0.5
                )
            )
            self.Output_Voltage = self.High_Voltage * 0.5 * (1 - self.Input_Voltage)

    def stamp(self) -> None:
        None
        if self.Output_Voltage < self.High_Voltage * 0.5:
            self.context.stamp_resistor(
                self.Nodes[0], self.Nodes[2], self.Closed_Resistance
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
