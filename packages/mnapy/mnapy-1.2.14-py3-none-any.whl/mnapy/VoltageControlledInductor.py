from typing import List

from mnapy import Utils
from mnapy import VoltageControlledInductorLimits
from mnapy import Wire


class VoltageControlledInductor:
    def __init__(
            self,
            context,
            Transient_Resistance,
            Elm1,
            Input_Voltage,
            Elm0,
            units,
            High_Voltage,
            Elm3,
            Transient_Current,
            Elm2,
            options_units,
            Low_Voltage,
            option_limits,
            Interpolate,
            options,
            Initial_Current,
            tag,
            Output_Inductance,
            Transient_Voltage,
            Equivalent_Current,
    ):
        self.Transient_Resistance = Transient_Resistance
        self.Elm1 = Elm1
        self.Input_Voltage = Input_Voltage
        self.Elm0 = Elm0
        self.units = units
        self.High_Voltage = High_Voltage
        self.Elm3 = Elm3
        self.Transient_Current = Transient_Current
        self.Elm2 = Elm2
        self.options_units = options_units
        self.Low_Voltage = Low_Voltage
        self.option_limits = (
            VoltageControlledInductorLimits.VoltageControlledInductorLimits(
                **Utils.Utils.FixDictionary(option_limits)
            )
        )
        self.Interpolate = Interpolate
        self.options = options
        self.Initial_Current = Initial_Current
        self.tag = tag
        self.Output_Inductance = Output_Inductance
        self.Transient_Voltage = Transient_Voltage
        self.Equivalent_Current = Equivalent_Current
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

    def reset(self) -> None:
        None
        self.Transient_Resistance = (
                                            2 * self.Output_Inductance
                                    ) / self.context.time_step
        self.Transient_Voltage = 0
        self.Transient_Current = self.Initial_Current
        self.Equivalent_Current = (
                self.Transient_Voltage / self.Transient_Resistance + self.Transient_Current
        )

    def update(self) -> None:
        None
        if (
                self.context.Params.SystemFlags.FlagSimulating
                and self.context.solutions_ready
                and self.context.simulation_step != 0
        ):
            self.Input_Voltage = Utils.Utils.limit(
                self.context.get_voltage(self.Nodes[1], -1),
                self.Low_Voltage,
                self.High_Voltage,
            )
            if self.Interpolate == (self.context.Params.SystemConstants.ON):
                self.Output_Inductance = Utils.Utils.linterp(
                    [
                        self.High_Voltage * 0,
                        self.High_Voltage * 0.33,
                        self.High_Voltage * 0.66,
                        self.High_Voltage * 1.0,
                    ],
                    [self.Elm0, self.Elm1, self.Elm2, self.Elm3],
                    self.Input_Voltage,
                )
            elif self.Interpolate == (self.context.Params.SystemConstants.OFF):
                index: int = 0
                if (
                        self.Input_Voltage >= self.High_Voltage * 0
                        and self.Input_Voltage <= self.High_Voltage * 0.25
                ):
                    index = 0
                elif (
                        self.Input_Voltage >= self.High_Voltage * 0.25
                        and self.Input_Voltage <= self.High_Voltage * 0.5
                ):
                    index = 1
                elif (
                        self.Input_Voltage >= self.High_Voltage * 0.5
                        and self.Input_Voltage <= self.High_Voltage * 0.75
                ):
                    index = 2
                elif (
                        self.Input_Voltage >= self.High_Voltage * 0.75
                        and self.Input_Voltage <= self.High_Voltage * 1.0
                ):
                    index = 3

                self.Output_Inductance = [self.Elm0, self.Elm1, self.Elm2, self.Elm3][
                    index
                ]

    def stamp(self) -> None:
        None
        self.context.stamp_inductor(
            self.Nodes[0],
            self.Nodes[2],
            self.Transient_Resistance,
            self.Equivalent_Current,
        )
        self.context.stamp_node(self.Nodes[1], self.context.Params.SystemSettings.R_MAX)

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

    def update_vcl(self) -> None:
        None
        if self.context.solutions_ready:
            self.conserve_energy()
            voltage: float = self.context.get_voltage(self.Nodes[0], self.Nodes[2])
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
        self.Transient_Resistance = (
                                            2 * self.Output_Inductance
                                    ) / self.context.time_step
        self.Equivalent_Current = (
                self.Transient_Voltage / self.Transient_Resistance + self.Transient_Current
        )

    def GetElementType(self) -> int:
        None
        return self.ElementType

    def SetElementType(self, setter: int) -> None:
        None
        self.ElementType = setter
