from typing import List

from mnapy import TPTZController
from mnapy import TPTZModuleLimits
from mnapy import Utils
from mnapy import Wire


class TPTZModule:
    def __init__(
            self,
            context,
            A1,
            B2,
            A2,
            options,
            Input_Voltage,
            tag,
            units,
            Output_Voltage,
            options_units,
            B0,
            option_limits,
            B1,
    ):
        self.A1 = A1
        self.B2 = B2
        self.A2 = A2
        self.options = options
        self.Input_Voltage = Input_Voltage
        self.tag = tag
        self.units = units
        self.Output_Voltage = Output_Voltage
        self.options_units = options_units
        self.B0 = B0
        self.option_limits = TPTZModuleLimits.TPTZModuleLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.B1 = B1
        self.Nodes = []
        self.Linkages = []
        self.Designator = ""
        self.Id = -1
        self.SimulationId = -1
        self.ElementType = -1
        self.WireReferences = []
        self.context = context
        self.tptz_controller = TPTZController.TPTZController([A1, A2, B0, B1, B2])
        self.tptz_controller.set_initial(0)

    def Set_A1(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.A1[0])
                and abs(setter) <= abs(self.option_limits.A1[1])
        ) or abs(setter) == 0:
            self.A1 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_A1(self) -> float:
        None
        return self.A1

    def Set_B2(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.B2[0])
                and abs(setter) <= abs(self.option_limits.B2[1])
        ) or abs(setter) == 0:
            self.B2 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_B2(self) -> float:
        None
        return self.B2

    def Set_A2(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.A2[0])
                and abs(setter) <= abs(self.option_limits.A2[1])
        ) or abs(setter) == 0:
            self.A2 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_A2(self) -> float:
        None
        return self.A2

    def Set_B0(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.B0[0])
                and abs(setter) <= abs(self.option_limits.B0[1])
        ) or abs(setter) == 0:
            self.B0 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_B0(self) -> float:
        None
        return self.B0

    def Set_B1(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.B1[0])
                and abs(setter) <= abs(self.option_limits.B1[1])
        ) or abs(setter) == 0:
            self.B1 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_B1(self) -> float:
        None
        return self.B1

    def reset(self) -> None:
        None
        self.tptz_controller.set_initial(0)
        self.Output_Voltage = 0

    def update(self) -> None:
        None
        if (
                self.context.Params.SystemFlags.FlagSimulating
                and self.context.solutions_ready
                and self.context.simulation_step != 0
        ):
            self.Input_Voltage = self.context.get_voltage(self.Nodes[0], -1)
            self.tptz_controller.set_tptz_coefficients(
                [self.A1, self.A2, self.B0, self.B1, self.B2]
            )
            self.Output_Voltage = self.tptz_controller.get_output(self.Input_Voltage)

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[1],
            -1,
            self.Output_Voltage,
            self.context.ELEMENT_TPTZ_OFFSET + self.SimulationId,
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
