import math
from typing import List

from mnapy import PChannelMOSFETLimits
from mnapy import Utils
from mnapy import Wire


class PChannelMOSFET:
    def __init__(
            self,
            context,
            W_L_Ratio,
            Last_Vsg,
            Vsd,
            gm,
            Io,
            Vsg,
            units,
            options_units,
            option_limits,
            VTP,
            K_p,
            options,
            gsd,
            Mosfet_Mode,
            Last_Io,
            tag,
            Lambda,
    ):
        self.W_L_Ratio = W_L_Ratio
        self.Last_Vsg = Last_Vsg
        self.Vsd = Vsd
        self.gm = gm
        self.Io = Io
        self.Vsg = Vsg
        self.units = units
        self.options_units = options_units
        self.option_limits = PChannelMOSFETLimits.PChannelMOSFETLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.VTP = VTP
        self.K_p = K_p
        self.options = options
        self.gsd = gsd
        self.Mosfet_Mode = Mosfet_Mode
        self.Last_Io = Last_Io
        self.tag = tag
        self.Lambda = Lambda
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

    def Set_W_L_Ratio(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.W_L_Ratio[0])
                and abs(setter) <= abs(self.option_limits.W_L_Ratio[1])
        ) or abs(setter) == 0:
            self.W_L_Ratio = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_W_L_Ratio(self) -> float:
        None
        return self.W_L_Ratio

    def Set_VTP(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.VTP[0])
                and abs(setter) <= abs(self.option_limits.VTP[1])
        ) or abs(setter) == 0:
            self.VTP = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_VTP(self) -> float:
        None
        return self.VTP

    def Set_K_p(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.K_p[0])
                and abs(setter) <= abs(self.option_limits.K_p[1])
        ) or abs(setter) == 0:
            self.K_p = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_K_p(self) -> float:
        None
        return self.K_p

    def Set_Lambda(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Lambda[0])
                and abs(setter) <= abs(self.option_limits.Lambda[1])
        ) or abs(setter) == 0:
            self.Lambda = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Lambda(self) -> float:
        None
        return self.Lambda

    def reset(self) -> None:
        None
        self.Mosfet_Mode = 0
        self.Vsg = 0
        self.Vsd = 0
        self.Last_Vsg = 2
        self.Last_Io = self.context.Params.SystemSettings.TOLERANCE * 2
        self.update()

    def update(self) -> None:
        None
        if self.context.Params.SystemFlags.FlagSimulating and self.context.solutions_ready:
            self.Last_Vsg = self.Vsg
            self.Last_Io = self.Io
            self.Vsg = Utils.Utils.log_damping(
                self.context.get_voltage(self.Nodes[0], self.Nodes[2]),
                self.Vsg,
                self.gamma,
                self.kappa,
            )
            self.Vsd = Utils.Utils.log_damping(
                self.context.get_voltage(self.Nodes[0], self.Nodes[1]),
                self.Vsd,
                self.gamma,
                self.kappa,
            )
            self.gmin = Utils.Utils.gmin_step(
                self.gmin_start, self.get_pmosfet_error(), self.context.iterator, self.context
            )
            kp: float = 0.5 * self.W_L_Ratio * -self.K_p
            if self.Vsg <= -self.VTP:
                self.Mosfet_Mode = 0
                self.gm = 0
                self.gsd = 1.0 / self.context.Params.SystemSettings.R_MAX
                self.Io = 0
            elif self.Vsd <= self.Vsg + self.VTP:
                self.Mosfet_Mode = 1
                self.gsd = 2.0 * kp * (self.Vsg + self.VTP - self.Vsd)
                self.gm = 2.0 * kp * self.Vsd
                self.Io = (
                        2.0
                        * kp
                        * ((self.Vsg + self.VTP) * self.Vsd - 0.5 * self.Vsd * self.Vsd)
                        - self.Vsg * self.gm
                        - self.Vsd * self.gsd
                )
            elif self.Vsd >= self.Vsg + self.VTP:
                self.Mosfet_Mode = 2
                self.gsd = kp * self.Lambda * math.pow(self.Vsg + self.VTP, 2)
                self.gm = (
                        2.0 * kp * ((self.Vsg + self.VTP) * (1.0 + self.Lambda * self.Vsd))
                )
                self.Io = (
                        kp * math.pow(self.Vsg + self.VTP, 2) * (1.0 + self.Lambda * self.Vsd)
                        - self.Vsg * self.gm
                        - self.Vsd * self.gsd
                )

    def stamp(self) -> None:
        None
        if self.Mosfet_Mode != 0:
            self.context.stamp_vccs(
                self.Nodes[0], self.Nodes[2], self.Nodes[1], self.Nodes[0], self.gm
            )

        self.context.stamp_resistor(self.Nodes[0], self.Nodes[1], 1.0 / self.gmin)
        self.context.stamp_current(self.Nodes[0], self.Nodes[1], self.Io)
        self.context.stamp_resistor(self.Nodes[0], self.Nodes[1], 1.0 / self.gsd)

    def get_pmosfet_error(self) -> float:
        None
        return abs(self.Vsg - self.Last_Vsg)

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
