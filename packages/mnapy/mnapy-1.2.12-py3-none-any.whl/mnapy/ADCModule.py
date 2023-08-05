import math
from typing import List

from mnapy import ADCModuleLimits
from mnapy import Utils
from mnapy import Wire


class ADCModule:
    def __init__(
            self,
            context,
            Reference_Voltage,
            options,
            LSB,
            Input_Voltage,
            Bit_Resolution,
            tag,
            units,
            Max_Bits,
            Output_Voltage,
            options_units,
            option_limits,
    ):
        self.Reference_Voltage = Reference_Voltage
        self.options = options
        self.LSB = LSB
        self.Input_Voltage = Input_Voltage
        self.Bit_Resolution = Bit_Resolution
        self.tag = tag
        self.units = units
        self.Max_Bits = Max_Bits
        self.Output_Voltage = Output_Voltage
        self.options_units = options_units
        self.option_limits = ADCModuleLimits.ADCModuleLimits(
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

    def Set_Reference_Voltage(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Reference_Voltage[0])
                and abs(setter) <= abs(self.option_limits.Reference_Voltage[1])
        ) or abs(setter) == 0:
            self.Reference_Voltage = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Reference_Voltage(self) -> float:
        None
        return self.Reference_Voltage

    def Set_Bit_Resolution(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Bit_Resolution[0])
                and abs(setter) <= abs(self.option_limits.Bit_Resolution[1])
        ) or abs(setter) == 0:
            self.Bit_Resolution = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Bit_Resolution(self) -> float:
        None
        return self.Bit_Resolution

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
            self.Max_Bits = math.pow(2, self.Bit_Resolution)
            self.LSB = self.Reference_Voltage / self.Max_Bits
            self.Output_Voltage = Utils.Utils.limit(
                Utils.Utils.cast_int(self.Input_Voltage / self.LSB), 0, self.Max_Bits - 1
            )

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[1],
            -1,
            self.Output_Voltage,
            self.context.ELEMENT_ADC_OFFSET + self.SimulationId,
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
