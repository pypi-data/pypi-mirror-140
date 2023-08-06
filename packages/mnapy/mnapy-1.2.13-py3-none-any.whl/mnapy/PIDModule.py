from typing import List

from mnapy import PIDController
from mnapy import PIDModuleLimits
from mnapy import Utils
from mnapy import Wire


class PIDModule:
    def __init__(
            self,
            context,
            Kp,
            Min_Output,
            Setpoint,
            units,
            High_Voltage,
            options_units,
            Low_Voltage,
            option_limits,
            Max_Output,
            Input_Voltage2,
            options,
            Kd,
            Input_Voltage1,
            tag,
            Output_Voltage,
            Ki,
    ):
        self.Kp = Kp
        self.Min_Output = Min_Output
        self.Setpoint = Setpoint
        self.units = units
        self.High_Voltage = High_Voltage
        self.options_units = options_units
        self.Low_Voltage = Low_Voltage
        self.option_limits = PIDModuleLimits.PIDModuleLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.Max_Output = Max_Output
        self.Input_Voltage2 = Input_Voltage2
        self.options = options
        self.Kd = Kd
        self.Input_Voltage1 = Input_Voltage1
        self.tag = tag
        self.Output_Voltage = Output_Voltage
        self.Ki = Ki
        self.Nodes = []
        self.Linkages = []
        self.Designator = ""
        self.Id = -1
        self.SimulationId = -1
        self.ElementType = -1
        self.WireReferences = []
        self.context = context
        self.pid_controller = PIDController.PIDController(Setpoint, Kp, Ki, Kd, context)
        self.pid_controller.set_output_limits(Min_Output, Max_Output)

    def Set_Max_Output(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Max_Output[0])
                and abs(setter) <= abs(self.option_limits.Max_Output[1])
        ) or abs(setter) == 0:
            self.Max_Output = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Max_Output(self) -> float:
        None
        return self.Max_Output

    def Set_Kp(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Kp[0])
                and abs(setter) <= abs(self.option_limits.Kp[1])
        ) or abs(setter) == 0:
            self.Kp = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Kp(self) -> float:
        None
        return self.Kp

    def Set_Min_Output(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Min_Output[0])
                and abs(setter) <= abs(self.option_limits.Min_Output[1])
        ) or abs(setter) == 0:
            self.Min_Output = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Min_Output(self) -> float:
        None
        return self.Min_Output

    def Set_Setpoint(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Setpoint[0])
                and abs(setter) <= abs(self.option_limits.Setpoint[1])
        ) or abs(setter) == 0:
            self.Setpoint = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Setpoint(self) -> float:
        None
        return self.Setpoint

    def Set_Kd(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Kd[0])
                and abs(setter) <= abs(self.option_limits.Kd[1])
        ) or abs(setter) == 0:
            self.Kd = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Kd(self) -> float:
        None
        return self.Kd

    def Set_Ki(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Ki[0])
                and abs(setter) <= abs(self.option_limits.Ki[1])
        ) or abs(setter) == 0:
            self.Ki = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Ki(self) -> float:
        None
        return self.Ki

    def reset(self) -> None:
        None
        self.pid_controller.reset()
        self.Output_Voltage = 0

    def update(self) -> None:
        None
        if (
                self.context.Params.SystemFlags.FlagSimulating
                and self.context.solutions_ready
                and self.context.simulation_step != 0
        ):
            self.pid_controller.set_setpoint(self.Setpoint)
            self.pid_controller.set_kp(self.Kp)
            self.pid_controller.set_ki(self.Ki)
            self.pid_controller.set_kd(self.Kd)
            self.pid_controller.set_output_limits(self.Min_Output, self.Max_Output)
            self.Input_Voltage1 = self.context.get_voltage(self.Nodes[0], -1)
            self.Input_Voltage2 = Utils.Utils.limit(
                self.context.get_voltage(self.Nodes[1], -1),
                self.Low_Voltage,
                self.High_Voltage,
            )
            if self.Input_Voltage2 > 0.5 * self.High_Voltage:
                self.pid_controller.reset()

            self.Output_Voltage = self.pid_controller.get_output(
                self.context.simulation_time, self.Input_Voltage1
            )
        else:
            None

    def stamp(self) -> None:
        None
        self.context.stamp_voltage(
            self.Nodes[2],
            -1,
            self.Output_Voltage,
            self.context.ELEMENT_PID_OFFSET + self.SimulationId,
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
