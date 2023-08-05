from typing import List

from mnapy import OhmMeterLimits
from mnapy import Utils
from mnapy import Wire


class OhmMeter:
    def __init__(
            self,
            context,
            Test_Voltage,
            options,
            tag,
            units,
            Sensed_Resistance,
            options_units,
            option_limits,
    ):
        self.Test_Voltage = Test_Voltage
        self.options = options
        self.tag = tag
        self.units = units
        self.Sensed_Resistance = Sensed_Resistance
        self.options_units = options_units
        self.option_limits = OhmMeterLimits.OhmMeterLimits(
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
        self.Sensed_Resistance = self.context.Params.SystemSettings.INV_R_MAX

    def update(self) -> None:
        None

    def stamp(self) -> None:
        None
        self.context.stamp_resistor(
            self.Nodes[0], self.Nodes[1], self.context.Params.SystemSettings.R_MAX
        )
        self.context.stamp_voltage(
            self.Nodes[0],
            self.Nodes[1],
            self.Test_Voltage,
            self.context.ELEMENT_OHMMETER_OFFSET + self.SimulationId,
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

    def GetSimulationId(self) -> int:
        None
        return self.SimulationId

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

    def push_voltage_current(self, voltage: float, current: float) -> None:
        None
        if (
                self.context.Params.SystemFlags.FlagSimulating
                and self.context.simulation_time >= self.context.time_step
                and self.context.solutions_ready
        ):
            self.Sensed_Resistance = abs(voltage / current)

    def get_simulation_index(self) -> int:
        None
        return (
                self.context.node_size
                + self.context.ELEMENT_OHMMETER_OFFSET
                + self.SimulationId
        )

    def Get_Resistance(self) -> float:
        None
        return self.Sensed_Resistance

    def GetElementType(self) -> int:
        None
        return self.ElementType

    def SetElementType(self, setter: int) -> None:
        None
        self.ElementType = setter
