import math
from typing import List

from mnapy import DiodeLimits
from mnapy import Utils
from mnapy import Wire


class Diode:
    def __init__(
            self,
            context,
            Last_Voltage,
            Resistance,
            Last_Current,
            Saturation_Current,
            Voltage,
            options,
            Emission_Coefficient,
            tag,
            units,
            options_units,
            Equivalent_Current,
            option_limits,
    ):
        self.Last_Voltage = Last_Voltage
        self.Resistance = Resistance
        self.Last_Current = Last_Current
        self.Saturation_Current = Saturation_Current
        self.Voltage = Voltage
        self.options = options
        self.Emission_Coefficient = Emission_Coefficient
        self.tag = tag
        self.units = units
        self.options_units = options_units
        self.Equivalent_Current = Equivalent_Current
        self.option_limits = DiodeLimits.DiodeLimits(
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
        self.gamma = 0.12
        self.kappa = 0.414
        self.gmin = 1e-9
        self.gmin_start = 12
        self.damping_safety_factor = 0.97

    def Set_Saturation_Current(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Saturation_Current[0])
                and abs(setter) <= abs(self.option_limits.Saturation_Current[1])
        ) or abs(setter) == 0:
            self.Saturation_Current = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Saturation_Current(self) -> float:
        None
        return self.Saturation_Current

    def Set_Emission_Coefficient(self, setter: float) -> None:
        None
        if (
                setter > self.option_limits.Emission_Coefficient[0]
                and setter < self.option_limits.Emission_Coefficient[1]
        ):
            self.Emission_Coefficient = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Emission_Coefficient(self) -> float:
        None
        return self.Emission_Coefficient

    def reset(self) -> None:
        None
        self.Voltage = 0
        self.Last_Voltage = Utils.Utils.calculate_vcrit(
            self.Emission_Coefficient, self.Saturation_Current, self.context
        )
        self.Last_Current = self.context.Params.SystemSettings.TOLERANCE * 2
        self.Resistance = self.context.Params.SystemSettings.R_MAX
        self.Equivalent_Current = 0
        self.update()

    def update(self) -> None:
        None
        if self.context.Params.SystemFlags.FlagSimulating and self.context.solutions_ready:
            self.Last_Voltage = self.Voltage
            self.Last_Current = self.Equivalent_Current
            next_voltage: float = self.context.get_voltage(self.Nodes[0], self.Nodes[1])
            vcrit: float = Utils.Utils.calculate_vcrit(
                self.Emission_Coefficient, self.Saturation_Current, self.context
            )
            diode_voltage: float = 0
            if next_voltage > self.damping_safety_factor * vcrit:
                diode_voltage = Utils.Utils.log_damping(
                    next_voltage, self.Voltage, self.gamma, self.kappa
                )
            elif next_voltage < -self.damping_safety_factor * vcrit:
                diode_voltage = Utils.Utils.log_damping(
                    next_voltage, self.Voltage, self.gamma, self.kappa
                )
            else:
                diode_voltage = next_voltage

            diode_voltage = Utils.Utils.limit(diode_voltage, -vcrit, vcrit)
            self.gmin = Utils.Utils.gmin_step(
                self.gmin_start, self.get_diode_error(), self.context.iterator, self.context
            )
            self.Voltage = diode_voltage
            self.Resistance = 1.0 / (
                    (
                            self.Saturation_Current
                            / (
                                    self.Emission_Coefficient
                                    * self.context.Params.SystemSettings.THERMAL_VOLTAGE
                            )
                    )
                    * math.exp(
                self.Voltage
                / (
                        self.Emission_Coefficient
                        * self.context.Params.SystemSettings.THERMAL_VOLTAGE
                )
            )
            )
            self.Equivalent_Current = -(
                    self.Saturation_Current
                    * (
                            math.exp(
                                self.Voltage
                                / (
                                        self.Emission_Coefficient
                                        * self.context.Params.SystemSettings.THERMAL_VOLTAGE
                                )
                            )
                            - 1
                    )
                    - self.Voltage / self.Resistance
            )

    def stamp(self) -> None:
        None
        self.context.stamp_resistor(self.Nodes[0], self.Nodes[1], 1.0 / self.gmin)
        self.context.stamp_current(
            self.Nodes[0], self.Nodes[1], self.Equivalent_Current
        )
        self.context.stamp_resistor(self.Nodes[0], self.Nodes[1], self.Resistance)

    def get_diode_error(self) -> float:
        None
        return abs(self.Voltage - self.Last_Voltage)

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
