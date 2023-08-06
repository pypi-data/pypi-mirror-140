from typing import List

from mnapy import Utils
from mnapy import VoltageSaturationLimits
from mnapy import Wire


class VoltageSaturation:
    def __init__(
            self,
            context,
            options,
            Input_Voltage,
            tag,
            units,
            High_Voltage,
            Output_Voltage,
            options_units,
            Low_Voltage,
            option_limits,
    ):
        self.options = options
        self.Input_Voltage = Input_Voltage
        self.tag = tag
        self.units = units
        self.High_Voltage = High_Voltage
        self.Output_Voltage = Output_Voltage
        self.options_units = options_units
        self.Low_Voltage = Low_Voltage
        self.option_limits = VoltageSaturationLimits.VoltageSaturationLimits(
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

    def Set_Low_Voltage(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Low_Voltage[0])
                and abs(setter) <= abs(self.option_limits.Low_Voltage[1])
        ) or abs(setter) == 0:
            self.Low_Voltage = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Low_Voltage(self) -> float:
        None
        return self.Low_Voltage

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
            self.Input_Voltage = self.context.get_voltage(self.Nodes[0], -1)
            self.Output_Voltage = Utils.Utils.limit(
                self.Input_Voltage, self.Low_Voltage, self.High_Voltage
            )

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[1],
            -1,
            self.Output_Voltage,
            self.context.ELEMENT_VSAT_OFFSET + self.SimulationId,
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
