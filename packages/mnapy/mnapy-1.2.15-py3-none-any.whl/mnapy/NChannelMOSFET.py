import math
from typing import List

from mnapy import NChannelMOSFETLimits
from mnapy import Utils
from mnapy import Wire


class NChannelMOSFET:
    def __init__(
            self,
            context,
            W_L_Ratio,
            Vgs,
            Vds,
            gm,
            Io,
            units,
            options_units,
            option_limits,
            VTN,
            K_n,
            gds,
            options,
            Mosfet_Mode,
            Last_Io,
            tag,
            Lambda,
            Last_Vgs,
    ):
        self.W_L_Ratio = W_L_Ratio
        self.Vgs = Vgs
        self.Vds = Vds
        self.gm = gm
        self.Io = Io
        self.units = units
        self.options_units = options_units
        self.option_limits = NChannelMOSFETLimits.NChannelMOSFETLimits(
            **Utils.Utils.FixDictionary(option_limits)
        )
        self.VTN = VTN
        self.K_n = K_n
        self.gds = gds
        self.options = options
        self.Mosfet_Mode = Mosfet_Mode
        self.Last_Io = Last_Io
        self.tag = tag
        self.Lambda = Lambda
        self.Last_Vgs = Last_Vgs
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

    def Set_VTN(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.VTN[0])
                and abs(setter) <= abs(self.option_limits.VTN[1])
        ) or abs(setter) == 0:
            self.VTN = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_VTN(self) -> float:
        None
        return self.VTN

    def Set_K_n(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.K_n[0])
                and abs(setter) <= abs(self.option_limits.K_n[1])
        ) or abs(setter) == 0:
            self.K_n = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_K_n(self) -> float:
        None
        return self.K_n

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
        self.Vgs = 0
        self.Vds = 0
        self.Last_Vgs = 2
        self.Last_Io = self.context.Params.SystemSettings.TOLERANCE * 2
        self.update()

    def update(self) -> None:
        None
        if self.context.Params.SystemFlags.FlagSimulating and self.context.solutions_ready:
            self.Last_Vgs = self.Vgs
            self.Last_Io = self.Io
            self.Vgs = Utils.Utils.log_damping(
                self.context.get_voltage(self.Nodes[2], self.Nodes[1]),
                self.Vgs,
                self.gamma,
                self.kappa,
            )
            self.Vds = Utils.Utils.log_damping(
                self.context.get_voltage(self.Nodes[0], self.Nodes[1]),
                self.Vds,
                self.gamma,
                self.kappa,
            )
            self.gmin = Utils.Utils.gmin_step(
                self.gmin_start, self.get_nmosfet_error(), self.context.iterator, self.context
            )
            kn: float = 0.5 * self.W_L_Ratio * self.K_n
            if self.Vgs <= self.VTN:
                self.Mosfet_Mode = 0
                self.gm = 0
                self.gds = 1.0 / self.context.Params.SystemSettings.R_MAX
                self.Io = 0
            elif self.Vds <= self.Vgs - self.VTN:
                self.Mosfet_Mode = 1
                self.gds = 2.0 * kn * (self.Vgs - self.VTN - self.Vds)
                self.gm = 2.0 * kn * self.Vds
                self.Io = (
                        2.0
                        * kn
                        * ((self.Vgs - self.VTN) * self.Vds - 0.5 * self.Vds * self.Vds)
                        - self.Vgs * self.gm
                        - self.Vds * self.gds
                )
            elif self.Vds >= self.Vgs - self.VTN:
                self.Mosfet_Mode = 2
                self.gds = kn * self.Lambda * math.pow(self.Vgs - self.VTN, 2)
                self.gm = (
                        2.0 * kn * ((self.Vgs - self.VTN) * (1.0 + self.Lambda * self.Vds))
                )
                self.Io = (
                        kn
                        * math.pow(self.Vgs - self.VTN, 2)
                        * (1.0 + self.Lambda * self.Vds)
                        - self.Vgs * self.gm
                        - self.Vds * self.gds
                )

    def stamp(self) -> None:
        None
        if self.Mosfet_Mode != 0:
            self.context.stamp_vccs(
                self.Nodes[2], self.Nodes[1], self.Nodes[0], self.Nodes[1], -self.gm
            )

        self.context.stamp_resistor(self.Nodes[0], self.Nodes[1], 1.0 / self.gmin)
        self.context.stamp_current(self.Nodes[0], self.Nodes[1], -self.Io)
        self.context.stamp_resistor(self.Nodes[0], self.Nodes[1], 1.0 / self.gds)

    def get_nmosfet_error(self) -> float:
        None
        return abs(self.Vgs - self.Last_Vgs)

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
