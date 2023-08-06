from typing import List

from mnapy import RelayLimits
from mnapy import Utils
from mnapy import Wire


class Relay:
    def __init__(
            self,
            context,
            Transient_Resistance,
            Transient_Voltage,
            Open_Resistance,
            units,
            Transient_Current,
            options_units,
            option_limits,
            Inductance,
            Coil_Resistance,
            Closed_Resistance,
            Must_Operate_Voltage,
            Must_Release_Voltage,
            Input_Voltage1,
            options,
            Initial_Current,
            Status,
            tag,
            Equivalent_Current,
    ):
        self.Transient_Resistance = Transient_Resistance
        self.Transient_Voltage = Transient_Voltage
        self.Open_Resistance = Open_Resistance
        self.units = units
        self.Transient_Current = Transient_Current
        self.options_units = options_units
        self.option_limits = RelayLimits.RelayLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.Inductance = Inductance
        self.Coil_Resistance = Coil_Resistance
        self.Closed_Resistance = Closed_Resistance
        self.Must_Operate_Voltage = Must_Operate_Voltage
        self.Must_Release_Voltage = Must_Release_Voltage
        self.Input_Voltage1 = Input_Voltage1
        self.options = options
        self.Initial_Current = Initial_Current
        self.Status = Status
        self.tag = tag
        self.Equivalent_Current = Equivalent_Current
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

    def Set_Coil_Resistance(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Coil_Resistance[0])
                and abs(setter) <= abs(self.option_limits.Coil_Resistance[1])
        ) or abs(setter) == 0:
            self.Coil_Resistance = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Coil_Resistance(self) -> float:
        None
        return self.Coil_Resistance

    def Set_Must_Operate_Voltage(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Must_Operate_Voltage[0])
                and abs(setter) <= abs(self.option_limits.Must_Operate_Voltage[1])
        ) or abs(setter) == 0:
            self.Must_Operate_Voltage = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Set_Must_Release_Voltage(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Must_Release_Voltage[0])
                and abs(setter) <= abs(self.option_limits.Must_Release_Voltage[1])
        ) or abs(setter) == 0:
            self.Must_Release_Voltage = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Must_Release_Voltage(self) -> float:
        None
        return self.Must_Operate_Voltage

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
        if self.Input_Voltage1 >= self.Must_Operate_Voltage:
            if (
                    self.context.Params.SystemFlags.FlagSimulating
                    and self.context.solutions_ready
                    and self.context.simulation_time > self.context.time_step
            ):
                self.Status = self.context.Params.SystemConstants.ON

        elif self.Input_Voltage1 <= self.Must_Release_Voltage:
            self.Status = self.context.Params.SystemConstants.OFF

    def stamp(self) -> None:
        None
        self.context.stamp_inductor(
            self.Nodes[0],
            self.Nodes[1],
            self.Transient_Resistance + self.Coil_Resistance,
            self.Equivalent_Current
            / (1 + self.Coil_Resistance / self.Transient_Resistance),
        )
        if self.Status == (self.context.Params.SystemConstants.ON):
            self.context.stamp_resistor(
                self.Nodes[2], self.Nodes[3], self.Closed_Resistance
            )
        else:
            self.context.stamp_node(self.Nodes[2], self.Open_Resistance)
            self.context.stamp_node(self.Nodes[3], self.Open_Resistance)

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

    def update_relay(self) -> None:
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
