import math
from typing import List

from mnapy import PNPBipolarJunctionTransistorLimits
from mnapy import Utils
from mnapy import Wire


class PNPBipolarJunctionTransistor:
    def __init__(
            self,
            context,
            Saturation_Current,
            g_ec,
            Reverse_Beta,
            g_ee,
            g_cc,
            g_ce,
            Forward_Beta,
            Emission_Coefficient,
            units,
            i_c,
            I_c,
            Last_Veb,
            options_units,
            i_e,
            I_e,
            option_limits,
            Veb,
            Vcb,
            options,
            Last_Io,
            tag,
    ):
        self.Saturation_Current = Saturation_Current
        self.g_ec = g_ec
        self.Reverse_Beta = Reverse_Beta
        self.g_ee = g_ee
        self.g_cc = g_cc
        self.g_ce = g_ce
        self.Forward_Beta = Forward_Beta
        self.Emission_Coefficient = Emission_Coefficient
        self.units = units
        self.i_c = i_c
        self.I_c = I_c
        self.Last_Veb = Last_Veb
        self.options_units = options_units
        self.i_e = i_e
        self.I_e = I_e
        self.option_limits = (
            PNPBipolarJunctionTransistorLimits.PNPBipolarJunctionTransistorLimits(
                **Utils.Utils.FixDictionary(option_limits)
            )
        )
        self.Veb = Veb
        self.Vcb = Vcb
        self.options = options
        self.Last_Io = Last_Io
        self.tag = tag
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

    def Set_Reverse_Beta(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Reverse_Beta[0])
                and abs(setter) <= abs(self.option_limits.Reverse_Beta[1])
        ) or abs(setter) == 0:
            self.Reverse_Beta = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Reverse_Beta(self) -> float:
        None
        return self.Reverse_Beta

    def Set_Forward_Beta(self, setter: float) -> None:
        None
        if (
                abs(setter) >= abs(self.option_limits.Forward_Beta[0])
                and abs(setter) <= abs(self.option_limits.Forward_Beta[1])
        ) or abs(setter) == 0:
            self.Forward_Beta = setter
        else:
            print(self.Designator + " -> Value is outside of limits.")

    def Get_Forward_Beta(self) -> float:
        None
        return self.Forward_Beta

    def reset(self) -> None:
        None
        self.Veb = 0
        self.Vcb = 0
        self.Last_Veb = Utils.Utils.calculate_vcrit(
            self.Emission_Coefficient, self.Saturation_Current, self.context
        )
        self.Last_Io = self.context.Params.SystemSettings.TOLERANCE * 2
        self.update()

    def update(self) -> None:
        None
        if self.context.Params.SystemFlags.FlagSimulating and self.context.solutions_ready:
            self.Last_Veb = self.Veb
            self.Last_Io = self.I_e - self.I_c
            next_veb: float = self.context.get_voltage(self.Nodes[0], self.Nodes[2])
            vcrit: float = Utils.Utils.calculate_vcrit(
                self.Emission_Coefficient, self.Saturation_Current, self.context
            )
            veb: float = 0
            if next_veb > self.damping_safety_factor * vcrit:
                veb = Utils.Utils.log_damping(
                    next_veb, self.Veb, self.gamma, self.kappa
                )
            elif next_veb < -self.damping_safety_factor * vcrit:
                veb = Utils.Utils.log_damping(
                    next_veb, self.Veb, self.gamma, self.kappa
                )
            else:
                veb = next_veb

            veb = Utils.Utils.limit(veb, -vcrit, vcrit)
            self.Veb = veb
            next_vcb: float = self.context.get_voltage(self.Nodes[1], self.Nodes[2])
            vcb: float = 0
            if next_vcb > self.damping_safety_factor * vcrit:
                vcb = Utils.Utils.log_damping(
                    next_vcb, self.Vcb, self.gamma, self.kappa
                )
            elif next_vcb < -self.damping_safety_factor * vcrit:
                vcb = Utils.Utils.log_damping(
                    next_vcb, self.Vcb, self.gamma, self.kappa
                )
            else:
                vcb = next_vcb

            vcb = Utils.Utils.limit(vcb, -vcrit, vcrit)
            self.Vcb = vcb
            self.gmin = Utils.Utils.gmin_step(
                self.gmin_start, self.get_pnpbjt_error(), self.context.iterator, self.context
            )
            forward_alpha: float = self.Forward_Beta / (1 + self.Forward_Beta)
            reverse_alpha: float = self.Reverse_Beta / (1 + self.Reverse_Beta)
            self.g_ee = (
                                self.Saturation_Current / self.context.Params.SystemSettings.THERMAL_VOLTAGE
                        ) * math.exp(self.Veb / self.context.Params.SystemSettings.THERMAL_VOLTAGE)
            self.g_ec = -(
                    reverse_alpha
                    * (self.Saturation_Current / self.context.Params.SystemSettings.THERMAL_VOLTAGE)
            ) * math.exp(self.Vcb / self.context.Params.SystemSettings.THERMAL_VOLTAGE)
            self.g_ce = -(
                    forward_alpha
                    * (self.Saturation_Current / self.context.Params.SystemSettings.THERMAL_VOLTAGE)
            ) * math.exp(self.Veb / self.context.Params.SystemSettings.THERMAL_VOLTAGE)
            self.g_cc = (
                                self.Saturation_Current / self.context.Params.SystemSettings.THERMAL_VOLTAGE
                        ) * math.exp(self.Vcb / self.context.Params.SystemSettings.THERMAL_VOLTAGE)
            self.i_e = self.Saturation_Current * (
                    math.exp(self.Veb / self.context.Params.SystemSettings.THERMAL_VOLTAGE) - 1
            ) - reverse_alpha * self.Saturation_Current * (
                               math.exp(self.Vcb / self.context.Params.SystemSettings.THERMAL_VOLTAGE) - 1
                       )
            self.i_c = self.Saturation_Current * (
                    math.exp(self.Vcb / self.context.Params.SystemSettings.THERMAL_VOLTAGE) - 1
            ) - forward_alpha * self.Saturation_Current * (
                               math.exp(self.Veb / self.context.Params.SystemSettings.THERMAL_VOLTAGE) - 1
                       )
            self.I_e = self.i_e - self.g_ee * self.Veb - self.g_ec * self.Vcb
            self.I_c = self.i_c - self.g_ce * self.Veb - self.g_cc * self.Vcb

    def stamp(self) -> None:
        None
        b: int = self.Nodes[2]
        c: int = self.Nodes[1]
        e: int = self.Nodes[0]
        self.context.stamp_across_nodes(c, b, -1.0 / self.g_ce)
        self.context.stamp_across_nodes(b, e, -1.0 / self.g_ce)
        self.context.stamp_across_nodes(c, e, 1.0 / self.g_ce)
        self.context.stamp_node(b, 1.0 / self.g_ce)
        self.context.stamp_across_nodes(e, b, -1.0 / self.g_ec)
        self.context.stamp_across_nodes(b, c, -1.0 / self.g_ec)
        self.context.stamp_across_nodes(e, c, 1.0 / self.g_ec)
        self.context.stamp_node(b, 1.0 / self.g_ec)
        self.context.stamp_resistor(c, b, 1.0 / self.g_cc)
        self.context.stamp_resistor(e, b, 1.0 / self.g_ee)
        self.context.stamp_current(b, c, self.I_c)
        self.context.stamp_current(b, e, self.I_e)

    def get_pnpbjt_error(self) -> float:
        None
        return abs(self.Veb - self.Last_Veb)

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
