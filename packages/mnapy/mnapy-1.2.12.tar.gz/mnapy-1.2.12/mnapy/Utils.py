import json
import math
from typing import List

from mnapy import Parser
from mnapy import Tags
from mnapy import Type


class Utils:
    FLOATING_POINT_REGEX = "[+-]?[0-9]+(\.[0-9]+)?([Ee][+-]?[0-9]+)?"

    def __init__(self) -> None:
        None

    @staticmethod
    def GetDataType(Input: str) -> str:
        if (len(Parser.Parser.FindAllMatches(Input, Utils.FLOATING_POINT_REGEX)) > 0):
            return Type.Type.TYPE_NUMBER

        return Type.Type.TYPE_STRING

    None

    @staticmethod
    def MapElement(Designator: str, Elements) -> str:
        for i in range(0, len(Elements)):
            if (Designator == Elements[i].GetDesignator()):
                return str(i)
            None
        None

        return Type.Type.TYPE_UNDEFINED

    None

    @staticmethod
    def gmin_step(step: int, error: float, iterator: int, context):
        gmin: float = context.Params.SystemSettings.GMIN_DEFAULT
        if (iterator > step and error > context.Params.SystemSettings.TOLERANCE):
            gmin = math.exp(-24.723 * (1.0 - 0.99 * (iterator / context.Params.SystemSettings.ITL4)))
        None
        return gmin

    None

    @staticmethod
    def map_range(inp: float, lower_bound: float, upper_bound: float):
        return lower_bound + inp * (upper_bound - lower_bound)

    None

    @staticmethod
    def log_damping(next: float, now: float, gamma: float, kappa: float):
        return now + (gamma / kappa) * Utils.signum(next - now) * Utils.logbx(math.e, 1 + abs(next - now) * kappa)

    None

    @staticmethod
    def signum(inp: float):
        if (inp < 0):
            return -1
        else:
            return 1
        None

    None

    @staticmethod
    def logbx(b: float, x: float):
        return math.log(x) / math.log(b)

    None

    @staticmethod
    def linterp(x_arr: List[float], y_arr: List[float], inp: float):
        k: int = Utils.linsearch(x_arr, inp, len(y_arr))
        x0: float = x_arr[k]
        x1: float = x_arr[k + 1]
        y0: float = y_arr[k]
        y1: float = y_arr[k + 1]

        if (inp > x_arr[len(x_arr) - 1]):
            return y_arr[len(y_arr) - 1]
        elif (inp < x_arr[0]):
            return y_arr[0]
        None
        return y0 + ((y1 - y0) / (x1 - x0)) * (inp - x0)

    None

    @staticmethod
    def linsearch(x_arr: List[float], inp: float, size: int):
        i: int = 0
        out: int = 0
        for i in range(0, size - 1):
            if (inp >= x_arr[i] and inp <= x_arr[i + 1]):
                out = i
                break
            None
        None
        return out

    None

    @staticmethod
    def ParseInt(Input: str):
        return int(round(float(Input)))

    None

    @staticmethod
    def ParseDouble(Input: str):
        return float(Input)

    None

    @staticmethod
    def ParseBoolean(Input: str):
        return bool(Input)

    None

    @staticmethod
    def PrintMatrix(Data):
        string: str = ""

        if (len(Data) > 0):
            for i in range(0, len(Data)):
                string = ""

                for j in range(0, len(Data[0])):
                    string += Data[i][j] + " "
                None

                print(string)
            None
        None

    None

    @staticmethod
    def to_radians(degrees: float):
        return degrees * Utils.PI_DIV_180

    None

    @staticmethod
    def calculate_vcrit(Emission_Coefficient: float, Saturation_Current: float, context):
        return (Emission_Coefficient * context.Params.SystemSettings.THERMAL_VOLTAGE
                * math.log((Emission_Coefficient * context.Params.SystemSettings.THERMAL_VOLTAGE) / (
                            1.41421 * Saturation_Current)))

    None

    @staticmethod
    def cast_int(Input: float):
        return int(round(Input))

    None

    @staticmethod
    def limit(inp: float, low: float, high: float):
        if (inp < low):
            return low
        elif (inp > high):
            return high
        else:
            return inp
        None

    None

    @staticmethod
    def wrap(inp: float, max: float):
        return inp - max * math.floor(inp / max)

    None

    @staticmethod
    def meter_max(context):
        meter_max_array = [len(context.voltmeters), len(context.ohmmeters), len(context.ammeters),
                           len(context.wattmeters)]
        max_general_number: int = 0
        for i in range(0, len(meter_max_array)):
            if (meter_max_array[i] > max_general_number):
                max_general_number = meter_max_array[i]
            None
        None
        return max_general_number

    None

    @staticmethod
    def element_max(context) -> int:
        element_max_array: List[int] = [len(context.resistors), len(context.capacitors), len(context.inductors),
                                        len(context.grounds), len(context.dcsources), len(context.dccurrents),
                                        len(context.acsources),
                                        len(context.accurrents), len(context.squarewaves), len(context.sawwaves),
                                        len(context.trianglewaves), len(context.constants), len(context.wires),
                                        len(context.nets),
                                        len(context.notes), len(context.rails), len(context.voltmeters),
                                        len(context.ohmmeters),
                                        len(context.ammeters), len(context.wattmeters), len(context.fuses),
                                        len(context.spsts),
                                        len(context.spdts), len(context.nots), len(context.diodes), len(context.leds),
                                        len(context.zeners),
                                        len(context.potentiometers), len(context.ands), len(context.ors),
                                        len(context.nands),
                                        len(context.nors), len(context.xors), len(context.xnors), len(context.dffs),
                                        len(context.vsats),
                                        len(context.adders), len(context.subtractors), len(context.multipliers),
                                        len(context.dividers),
                                        len(context.gains), len(context.absvals), len(context.vcsws),
                                        len(context.vcvss),
                                        len(context.vccss), len(context.cccss), len(context.ccvss), len(context.opamps),
                                        len(context.nmosfets), len(context.pmosfets), len(context.npns),
                                        len(context.pnps),
                                        len(context.adcs), len(context.dacs), len(context.sandhs), len(context.pwms),
                                        len(context.integrators), len(context.differentiators), len(context.lowpasses),
                                        len(context.highpasses), len(context.relays), len(context.pids),
                                        len(context.luts),
                                        len(context.vcrs), len(context.vccas), len(context.vcls), len(context.grts),
                                        len(context.tptzs),
                                        len(context.transformers), len(context.bridges)]
        max_general_number: int = 0
        for i in range(0, len(element_max_array)):
            if (element_max_array[i] > max_general_number):
                max_general_number = element_max_array[i]
            None
        None
        return max_general_number

    None

    @staticmethod
    def FixProperties(JsonData):
        Properties = [json.loads(JsonData)]
        ModifiedProperties = \
        [{k.replace(' ', '_').replace("'", "_").replace("/", "_").replace("!", "N_"): v for k, v in d.items()} for d in
         Properties][0]
        return ModifiedProperties

    @staticmethod
    def FixDictionary(Dictionary):
        Properties = [Dictionary]
        ModifiedProperties = \
        [{k.replace(' ', '_').replace("'", "_").replace("/", "_").replace("!", "N_"): v for k, v in d.items()} for d in
         Properties][0]
        return ModifiedProperties

    @staticmethod
    def GetElementType(Tag: str) -> int:
        if (Tag == Tags.Tags.TAG_RESISTOR):
            return Type.Type.TYPE_RESISTOR
        elif (Tag == Tags.Tags.TAG_CAPACITOR):
            return Type.Type.TYPE_CAPACITOR
        elif (Tag == Tags.Tags.TAG_INDUCTOR):
            return Type.Type.TYPE_INDUCTOR
        elif (Tag == Tags.Tags.TAG_GROUND):
            return Type.Type.TYPE_GROUND
        elif (Tag == Tags.Tags.TAG_DCSOURCE):
            return Type.Type.TYPE_DCSOURCE
        elif (Tag == Tags.Tags.TAG_DCCURRENT):
            return Type.Type.TYPE_DCCURRENT
        elif (Tag == Tags.Tags.TAG_ACSOURCE):
            return Type.Type.TYPE_ACSOURCE
        elif (Tag == Tags.Tags.TAG_ACCURRENT):
            return Type.Type.TYPE_ACCURRENT
        elif (Tag == Tags.Tags.TAG_SQUAREWAVE):
            return Type.Type.TYPE_SQUAREWAVE
        elif (Tag == Tags.Tags.TAG_SAW):
            return Type.Type.TYPE_SAW
        elif (Tag == Tags.Tags.TAG_TRI):
            return Type.Type.TYPE_TRI
        elif (Tag == Tags.Tags.TAG_CONSTANT):
            return Type.Type.TYPE_CONSTANT
        elif (Tag == Tags.Tags.TAG_BRIDGE):
            return Type.Type.TYPE_BRIDGE
        elif (Tag == Tags.Tags.TAG_WIRE):
            return Type.Type.TYPE_WIRE
        elif (Tag == Tags.Tags.TAG_NET):
            return Type.Type.TYPE_NET
        elif (Tag == Tags.Tags.TAG_NOTE):
            return Type.Type.TYPE_NOTE
        elif (Tag == Tags.Tags.TAG_RAIL):
            return Type.Type.TYPE_RAIL
        elif (Tag == Tags.Tags.TAG_VOLTMETER):
            return Type.Type.TYPE_VOLTMETER
        elif (Tag == Tags.Tags.TAG_OHMMETER):
            return Type.Type.TYPE_OHMMETER
        elif (Tag == Tags.Tags.TAG_AMMETER):
            return Type.Type.TYPE_AMMETER
        elif (Tag == Tags.Tags.TAG_WATTMETER):
            return Type.Type.TYPE_WATTMETER
        elif (Tag == Tags.Tags.TAG_FUSE):
            return Type.Type.TYPE_FUSE
        elif (Tag == Tags.Tags.TAG_SPST):
            return Type.Type.TYPE_SPST
        elif (Tag == Tags.Tags.TAG_SPDT):
            return Type.Type.TYPE_SPDT
        elif (Tag == Tags.Tags.TAG_NOT):
            return Type.Type.TYPE_NOT
        elif (Tag == Tags.Tags.TAG_DIODE):
            return Type.Type.TYPE_DIODE
        elif (Tag == Tags.Tags.TAG_LED):
            return Type.Type.TYPE_LED
        elif (Tag == Tags.Tags.TAG_ZENER):
            return Type.Type.TYPE_ZENER
        elif (Tag == Tags.Tags.TAG_POTENTIOMETER):
            return Type.Type.TYPE_POTENTIOMETER
        elif (Tag == Tags.Tags.TAG_AND):
            return Type.Type.TYPE_AND
        elif (Tag == Tags.Tags.TAG_OR):
            return Type.Type.TYPE_OR
        elif (Tag == Tags.Tags.TAG_NAND):
            return Type.Type.TYPE_NAND
        elif (Tag == Tags.Tags.TAG_NOR):
            return Type.Type.TYPE_NOR
        elif (Tag == Tags.Tags.TAG_XOR):
            return Type.Type.TYPE_XOR
        elif (Tag == Tags.Tags.TAG_XNOR):
            return Type.Type.TYPE_XNOR
        elif (Tag == Tags.Tags.TAG_DFF):
            return Type.Type.TYPE_DFF
        elif (Tag == Tags.Tags.TAG_VSAT):
            return Type.Type.TYPE_VSAT
        elif (Tag == Tags.Tags.TAG_ADD):
            return Type.Type.TYPE_ADD
        elif (Tag == Tags.Tags.TAG_SUB):
            return Type.Type.TYPE_SUB
        elif (Tag == Tags.Tags.TAG_MUL):
            return Type.Type.TYPE_MUL
        elif (Tag == Tags.Tags.TAG_DIV):
            return Type.Type.TYPE_DIV
        elif (Tag == Tags.Tags.TAG_GAIN):
            return Type.Type.TYPE_GAIN
        elif (Tag == Tags.Tags.TAG_ABS):
            return Type.Type.TYPE_ABS
        elif (Tag == Tags.Tags.TAG_VCSW):
            return Type.Type.TYPE_VCSW
        elif (Tag == Tags.Tags.TAG_VCVS):
            return Type.Type.TYPE_VCVS
        elif (Tag == Tags.Tags.TAG_VCCS):
            return Type.Type.TYPE_VCCS
        elif (Tag == Tags.Tags.TAG_CCCS):
            return Type.Type.TYPE_CCCS
        elif (Tag == Tags.Tags.TAG_CCVS):
            return Type.Type.TYPE_CCVS
        elif (Tag == Tags.Tags.TAG_OPAMP):
            return Type.Type.TYPE_OPAMP
        elif (Tag == Tags.Tags.TAG_NMOS):
            return Type.Type.TYPE_NMOS
        elif (Tag == Tags.Tags.TAG_PMOS):
            return Type.Type.TYPE_PMOS
        elif (Tag == Tags.Tags.TAG_NPN):
            return Type.Type.TYPE_NPN
        elif (Tag == Tags.Tags.TAG_PNP):
            return Type.Type.TYPE_PNP
        elif (Tag == Tags.Tags.TAG_ADC):
            return Type.Type.TYPE_ADC
        elif (Tag == Tags.Tags.TAG_DAC):
            return Type.Type.TYPE_DAC
        elif (Tag == Tags.Tags.TAG_SAH):
            return Type.Type.TYPE_SAH
        elif (Tag == Tags.Tags.TAG_PWM):
            return Type.Type.TYPE_PWM
        elif (Tag == Tags.Tags.TAG_INTEGRATOR):
            return Type.Type.TYPE_INTEGRATOR
        elif (Tag == Tags.Tags.TAG_DIFFERENTIATOR):
            return Type.Type.TYPE_DIFFERENTIATOR
        elif (Tag == Tags.Tags.TAG_LPF):
            return Type.Type.TYPE_LPF
        elif (Tag == Tags.Tags.TAG_HPF):
            return Type.Type.TYPE_HPF
        elif (Tag == Tags.Tags.TAG_REL):
            return Type.Type.TYPE_REL
        elif (Tag == Tags.Tags.TAG_PID):
            return Type.Type.TYPE_PID
        elif (Tag == Tags.Tags.TAG_LUT):
            return Type.Type.TYPE_LUT
        elif (Tag == Tags.Tags.TAG_VCR):
            return Type.Type.TYPE_VCR
        elif (Tag == Tags.Tags.TAG_VCCA):
            return Type.Type.TYPE_VCCA
        elif (Tag == Tags.Tags.TAG_VCL):
            return Type.Type.TYPE_VCL
        elif (Tag == Tags.Tags.TAG_GRT):
            return Type.Type.TYPE_GRT
        elif (Tag == Tags.Tags.TAG_TPTZ):
            return Type.Type.TYPE_TPTZ
        elif (Tag == Tags.Tags.TAG_TRAN):
            return Type.Type.TYPE_TRAN
        None

        return -1

    None
