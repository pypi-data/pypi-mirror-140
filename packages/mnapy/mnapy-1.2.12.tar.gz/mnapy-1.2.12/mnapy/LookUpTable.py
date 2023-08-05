from typing import List

from mnapy import LookUpTableLimits
from mnapy import Utils
from mnapy import Wire


class LookUpTable:
    def __init__(
            self,
            context,
            Elm1,
            Elm0,
            units,
            Elm3,
            High_Voltage,
            Elm2,
            options_units,
            Low_Voltage,
            option_limits,
            Elm4,
            Interpolate,
            options,
            Input_Voltage1,
            tag,
            Output_Voltage,
    ):
        self.Elm1 = Elm1
        self.Elm0 = Elm0
        self.units = units
        self.Elm3 = Elm3
        self.High_Voltage = High_Voltage
        self.Elm2 = Elm2
        self.options_units = options_units
        self.Low_Voltage = Low_Voltage
        self.option_limits = LookUpTableLimits.LookUpTableLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.Elm4 = Elm4
        self.Interpolate = Interpolate
        self.options = options
        self.Input_Voltage1 = Input_Voltage1
        self.tag = tag
        self.Output_Voltage = Output_Voltage
        self.Nodes = []
        self.Linkages = []
        self.Designator = ""
        self.Id = -1
        self.SimulationId = -1
        self.ElementType = -1
        self.WireReferences = []
        self.context = context

    def Set_Interpolate(self, setter: str) -> None:
        None
        if setter == (self.context.Params.SystemConstants.ON) or setter == (
                self.context.Params.SystemConstants.OFF
        ):
            self.Interpolate = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Interpolate(self) -> str:
        None
        return self.Interpolate

    def Set_Elm1(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Elm1[0])
                and abs(setter) <= abs(self.option_limits.Elm1[1])
        ) or abs(setter) == 0:
            self.Elm1 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Elm1(self) -> float:
        None
        return self.Elm1

    def Set_Elm0(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Elm0[0])
                and abs(setter) <= abs(self.option_limits.Elm0[1])
        ) or abs(setter) == 0:
            self.Elm0 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Elm0(self) -> float:
        None
        return self.Elm0

    def Set_Elm3(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Elm3[0])
                and abs(setter) <= abs(self.option_limits.Elm3[1])
        ) or abs(setter) == 0:
            self.Elm3 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Elm3(self) -> float:
        None
        return self.Elm3

    def Set_Elm2(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Elm2[0])
                and abs(setter) <= abs(self.option_limits.Elm2[1])
        ) or abs(setter) == 0:
            self.Elm2 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Elm2(self) -> float:
        None
        return self.Elm2

    def Set_Elm4(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Elm4[0])
                and abs(setter) <= abs(self.option_limits.Elm4[1])
        ) or abs(setter) == 0:
            self.Elm4 = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Elm4(self) -> float:
        None
        return self.Elm4

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
            self.Input_Voltage1 = Utils.Utils.limit(
                self.context.get_voltage(self.Nodes[0], -1),
                self.Low_Voltage,
                self.High_Voltage,
            )
            if self.Interpolate == (self.context.Params.SystemConstants.ON):
                self.Output_Voltage = Utils.Utils.linterp(
                    [
                        self.High_Voltage * 0,
                        self.High_Voltage * 0.25,
                        self.High_Voltage * 0.5,
                        self.High_Voltage * 0.75,
                        self.High_Voltage,
                    ],
                    [
                        self.Elm0, self.Elm1, self.Elm2, self.Elm3, self.Elm4
                    ],
                    self.Input_Voltage1,
                )
            elif self.Interpolate == (self.context.Params.SystemConstants.OFF):
                index: int = 0
                if (
                        self.Input_Voltage1 >= self.High_Voltage * 0
                        and self.Input_Voltage1 <= self.High_Voltage * 0.2
                ):
                    index = 0
                elif (
                        self.Input_Voltage1 >= self.High_Voltage * 0.2
                        and self.Input_Voltage1 <= self.High_Voltage * 0.4
                ):
                    index = 1
                elif (
                        self.Input_Voltage1 >= self.High_Voltage * 0.4
                        and self.Input_Voltage1 <= self.High_Voltage * 0.6
                ):
                    index = 2
                elif (
                        self.Input_Voltage1 >= self.High_Voltage * 0.6
                        and self.Input_Voltage1 <= self.High_Voltage * 0.8
                ):
                    index = 3
                elif (
                        self.Input_Voltage1 >= self.High_Voltage * 0.8
                        and self.Input_Voltage1 <= self.High_Voltage * 1.0
                ):
                    index = 4

                self.Output_Voltage = [
                    self.Elm0, self.Elm1, self.Elm2, self.Elm3, self.Elm4
                ][index]

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[1],
            -1,
            self.Output_Voltage,
            self.context.ELEMENT_LUT_OFFSET + self.SimulationId,
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
