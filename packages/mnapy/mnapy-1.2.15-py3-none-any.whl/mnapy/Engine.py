import math
from typing import List

import numpy as np

from mnapy import AbsoluteValue
from mnapy import ACCurrent
from mnapy import ACSource
from mnapy import ADCModule
from mnapy import Adder
from mnapy import ANDGate
from mnapy import AmMeter
from mnapy import Bridge
from mnapy import Capacitor
from mnapy import Constant
from mnapy import CurrentControlledCurrentSource
from mnapy import CurrentControlledVoltageSource
from mnapy import DACModule
from mnapy import DCCurrent
from mnapy import DCSource
from mnapy import DFlipFlop
from mnapy import DifferentiatorModule
from mnapy import Diode
from mnapy import Divider
from mnapy import Fuse
from mnapy import GainBlock
from mnapy import GreaterThan
from mnapy import Ground
from mnapy import HighPassFilter
from mnapy import Inductor
from mnapy import IntegratorModule
from mnapy import LightEmittingDiode
from mnapy import LookUpTable
from mnapy import LowPassFilter
from mnapy import Multiplier
from mnapy import NANDGate
from mnapy import NChannelMOSFET
from mnapy import NORGate
from mnapy import NOTGate
from mnapy import NPNBipolarJunctionTransistor
from mnapy import Net
from mnapy import Note
from mnapy import ORGate
from mnapy import OhmMeter
from mnapy import OperationalAmplifier
from mnapy import PChannelMOSFET
from mnapy import PIDModule
from mnapy import PNPBipolarJunctionTransistor
from mnapy import Potentiometer
from mnapy import PulseWidthModulator
from mnapy import Rail
from mnapy import Relay
from mnapy import Resistor
from mnapy import SampleAndHold
from mnapy import SawWave
from mnapy import SinglePoleDoubleThrow
from mnapy import SinglePoleSingleThrow
from mnapy import SquareWave
from mnapy import Subtractor
from mnapy import TPTZModule
from mnapy import Transformer
from mnapy import TriangleWave
from mnapy import VoltMeter
from mnapy import VoltageControlledCapacitor
from mnapy import VoltageControlledCurrentSource
from mnapy import VoltageControlledInductor
from mnapy import VoltageControlledResistor
from mnapy import VoltageControlledSwitch
from mnapy import VoltageControlledVoltageSource
from mnapy import VoltageSaturation
from mnapy import WattMeter
from mnapy import Wire
from mnapy import XNORGate
from mnapy import XORGate
from mnapy import ZenerDiode
from mnapy import Element
from mnapy import Global
from mnapy import KeyPair
from mnapy import Node
from mnapy import NodeManager
from mnapy import Type
from mnapy import Utils
import copy

class Engine:
    def __init__(self) -> None:
        '''The Engine class is how to interact with a circuit dynamically. It loads all the data from the
        generated netlist and creates objects that can be modified during the execution of the code. NOTE: None
        of the modifications are actually written to file. '''

        self.__version__ = "1.2.15"
        # Version control variables.
        self.ELEMENT_DIVIDER = "#DIVIDER#"
        self.WIRE_DIVIDER = "#WIRE#"
        self.ID_DIVIDER = "#ID#"
        self.VERSION_NUMBER = "#VERSION#"
        self.WIRE_ELEMENT = "<WIRE>"

        self.MINIMUM_MAJOR = 1
        self.MINIMUM_MINOR = 1
        self.MINIMUM_PATCH = 9

        self.MAJOR_SHIFT = 16
        self.MINOR_SHIFT = 8
        self.PATCH_SHIFT = 0

        self.MAJOR_MASK = (0xFF) << self.MAJOR_SHIFT
        self.MINOR_MASK = (0xFF) << self.MINOR_SHIFT
        self.PATCH_MASK = (0xFF) << self.PATCH_SHIFT

        self.MINIMUM_VERSION = (
                ((self.MINIMUM_MAJOR << self.MAJOR_SHIFT) & self.MAJOR_MASK)
                | ((self.MINIMUM_MINOR << self.MINOR_SHIFT) & self.MINOR_MASK)
                | ((self.MINIMUM_PATCH << self.PATCH_SHIFT) & self.PATCH_MASK)
        )

        # Contains system File Data (Loaded from user file).
        self.FileData = ""

        # Portions of the Net List File.
        self.Parts = []
        self.Elements = []
        self.Id_Properties = []
        self.CircuitElements: List[Element.Element] = []

        self.Map: List[KeyPair.KeyPair] = []

        self.SIMULATION_MAX_TIME: float = 1e18

        # Used for generating offsets for determining matrix size.
        self.MATRIX_OFFSET: int = 0
        self.matrix_a: np.ndarray = np.zeros((1, 1), dtype=np.float64)
        self.matrix_z: np.ndarray = np.zeros((1, 1), dtype=np.float64)
        self.matrix_x: np.ndarray = np.zeros((1, 1), dtype=np.float64)
        self.matrix_x_copy: np.ndarray = np.zeros((1, 1), dtype=np.float64)

        # Circuit Elements
        self.bridges = []
        self.nodes = []
        self.wires = []
        self.resistors = []
        self.capacitors = []
        self.inductors = []
        self.grounds = []
        self.dcsources = []
        self.dccurrents = []
        self.acsources = []
        self.accurrents = []
        self.squarewaves = []
        self.sawwaves = []
        self.trianglewaves = []
        self.constants = []
        self.nets = []
        self.notes = []
        self.rails = []
        self.voltmeters = []
        self.ohmmeters = []
        self.ammeters = []
        self.wattmeters = []
        self.fuses = []
        self.spsts = []
        self.spdts = []
        self.nots = []
        self.diodes = []
        self.leds = []
        self.zeners = []
        self.potentiometers = []
        self.ands = []
        self.ors = []
        self.nands = []
        self.nors = []
        self.xors = []
        self.xnors = []
        self.dffs = []
        self.vsats = []
        self.adders = []
        self.subtractors = []
        self.multipliers = []
        self.dividers = []
        self.gains = []
        self.absvals = []
        self.vcsws = []
        self.vcvss = []
        self.vccss = []
        self.cccss = []
        self.ccvss = []
        self.opamps = []
        self.nmosfets = []
        self.pmosfets = []
        self.npns = []
        self.pnps = []
        self.adcs = []
        self.dacs = []
        self.sandhs = []
        self.pwms = []
        self.integrators = []
        self.differentiators = []
        self.lowpasses = []
        self.highpasses = []
        self.relays = []
        self.pids = []
        self.luts = []
        self.vcrs = []
        self.vccas = []
        self.vcls = []
        self.grts = []
        self.tptzs = []
        self.transformers = []

        # Element Offsets.
        self.ELEMENT_DCSOURCE_OFFSET = 0
        self.ELEMENT_ACSOURCE_OFFSET = 0
        self.ELEMENT_SQUAREWAVE_OFFSET = 0
        self.ELEMENT_SAW_OFFSET = 0
        self.ELEMENT_TRI_OFFSET = 0
        self.ELEMENT_CONSTANT_OFFSET = 0
        self.ELEMENT_RAIL_OFFSET = 0
        self.ELEMENT_OHMMETER_OFFSET = 0
        self.ELEMENT_AMMETER_OFFSET = 0
        self.ELEMENT_WATTMETER_OFFSET = 0
        self.ELEMENT_NOT_OFFSET = 0
        self.ELEMENT_AND_OFFSET = 0
        self.ELEMENT_OR_OFFSET = 0
        self.ELEMENT_NAND_OFFSET = 0
        self.ELEMENT_NOR_OFFSET = 0
        self.ELEMENT_XOR_OFFSET = 0
        self.ELEMENT_XNOR_OFFSET = 0
        self.ELEMENT_DFF_OFFSET = 0
        self.ELEMENT_VSAT_OFFSET = 0
        self.ELEMENT_ADD_OFFSET = 0
        self.ELEMENT_SUB_OFFSET = 0
        self.ELEMENT_MUL_OFFSET = 0
        self.ELEMENT_DIV_OFFSET = 0
        self.ELEMENT_GAIN_OFFSET = 0
        self.ELEMENT_ABS_OFFSET = 0
        self.ELEMENT_VCVS_OFFSET = 0
        self.ELEMENT_CCCS_OFFSET = 0
        self.ELEMENT_CCVS_OFFSET = 0
        self.ELEMENT_OPAMP_OFFSET = 0
        self.ELEMENT_ADC_OFFSET = 0
        self.ELEMENT_DAC_OFFSET = 0
        self.ELEMENT_SAH_OFFSET = 0
        self.ELEMENT_PWM_OFFSET = 0
        self.ELEMENT_INTEGRATOR_OFFSET = 0
        self.ELEMENT_DIFFERENTIATOR_OFFSET = 0
        self.ELEMENT_LPF_OFFSET = 0
        self.ELEMENT_HPF_OFFSET = 0
        self.ELEMENT_PID_OFFSET = 0
        self.ELEMENT_LUT_OFFSET = 0
        self.ELEMENT_GRT_OFFSET = 0
        self.ELEMENT_TPTZ_OFFSET = 0
        self.ELEMENT_TRAN_OFFSET = 0

        self.node_manager: NodeManager.NodeManager = NodeManager.NodeManager(self)
        self.node_size: int = 0
        self.node_1: int = -1
        self.node_2: int = -1
        self.node_3: int = -1
        self.node_4: int = -1
        self.v_node_1: float = 0
        self.v_node_2: float = 0
        self.node_offset: int = 0
        self.time_step: float = 1e-5
        self.simulation_time: float = 0
        self.simulation_step: float = 0
        self.solutions_ready: bool = False
        self.iterator: int = 0
        self.continue_solving: bool = True
        self.first_matrix_build: bool = True
        self.first_x_matrix_copy: bool = True
        self.first_x_matrix_solution: bool = True
        self.first_error_check: bool = True
        self.max_voltage_error: np.ndarray = np.zeros((1, 1), dtype=np.float64)
        self.max_current_error: np.ndarray = np.zeros((1, 1), dtype=np.float64)
        self.voltage_error_locked: bool = False
        self.current_error_locked: bool = False
        self.voltage_converged: bool = False
        self.current_converged: bool = False
        self.system_ready: bool = False
        self.Params = Global.Global()
        None
        
    def save_state(self):
        State = {
            "simulation_time" : (self.simulation_time),
            "time_step" : (self.time_step),
            "matrix_x" : (self.matrix_x),
            "matrix_x_copy" : (self.matrix_x_copy),
            "matrix_a" : (self.matrix_a),
            "matrix_z" : (self.matrix_z),
            "elements" : [
                (self.bridges),
                (self.nodes),
                (self.wires),
                (self.resistors),
                (self.capacitors),
                (self.inductors),
                (self.grounds),
                (self.dcsources),
                (self.dccurrents),
                (self.acsources),
                (self.accurrents),
                (self.squarewaves),
                (self.sawwaves),
                (self.trianglewaves),
                (self.constants),
                (self.nets),
                (self.notes),
                (self.rails),
                (self.voltmeters),
                (self.ohmmeters),
                (self.ammeters),
                (self.wattmeters),
                (self.fuses),
                (self.spsts),
                (self.spdts),
                (self.nots),
                (self.diodes),
                (self.leds),
                (self.zeners),
                (self.potentiometers),
                (self.ands),
                (self.ors),
                (self.nands),
                (self.nors),
                (self.xors),
                (self.xnors),
                (self.dffs),
                (self.vsats),
                (self.adders),
                (self.subtractors),
                (self.multipliers),
                (self.dividers),
                (self.gains),
                (self.absvals),
                (self.vcsws),
                (self.vcvss),
                (self.vccss),
                (self.cccss),
                (self.ccvss),
                (self.opamps),
                (self.nmosfets),
                (self.pmosfets),
                (self.npns),
                (self.pnps),
                (self.adcs),
                (self.dacs),
                (self.sandhs),
                (self.pwms),
                (self.integrators),
                (self.differentiators),
                (self.lowpasses),
                (self.highpasses),
                (self.relays),
                (self.pids),
                (self.luts),
                (self.vcrs),
                (self.vccas),
                (self.vcls),
                (self.grts),
                (self.tptzs),
                (self.transformers)
            ]
        }
        
        return State
    
    def apply_state(self, State):
        self.simulation_time = (State["simulation_time"])
        self.time_step = (State["time_step"])
        self.matrix_x = (State["matrix_x"])
        self.matrix_x_copy = (State["matrix_x_copy"])
        self.matrix_a = (State["matrix_a"])
        self.matrix_z = (State["matrix_z"])
        
        [
            self.bridges,
            self.nodes,
            self.wires,
            self.resistors,
            self.capacitors,
            self.inductors,
            self.grounds,
            self.dcsources,
            self.dccurrents,
            self.acsources,
            self.accurrents,
            self.squarewaves,
            self.sawwaves,
            self.trianglewaves,
            self.constants,
            self.nets,
            self.notes,
            self.rails,
            self.voltmeters,
            self.ohmmeters,
            self.ammeters,
            self.wattmeters,
            self.fuses,
            self.spsts,
            self.spdts,
            self.nots,
            self.diodes,
            self.leds,
            self.zeners,
            self.potentiometers,
            self.ands,
            self.ors,
            self.nands,
            self.nors,
            self.xors,
            self.xnors,
            self.dffs,
            self.vsats,
            self.adders,
            self.subtractors,
            self.multipliers,
            self.dividers,
            self.gains,
            self.absvals,
            self.vcsws,
            self.vcvss,
            self.vccss,
            self.cccss,
            self.ccvss,
            self.opamps,
            self.nmosfets,
            self.pmosfets,
            self.npns,
            self.pnps,
            self.adcs,
            self.dacs,
            self.sandhs,
            self.pwms,
            self.integrators,
            self.differentiators,
            self.lowpasses,
            self.highpasses,
            self.relays,
            self.pids,
            self.luts,
            self.vcrs,
            self.vccas,
            self.vcls,
            self.grts,
            self.tptzs,
            self.transformers
        ] = (State["elements"])
                
    def setup(self):
        for i in range(0, len(self.capacitors)):
            self.capacitors[i].conserve_energy()
		
        for i in range(0, len(self.inductors)):
            self.inductors[i].conserve_energy()
		
        for i in range(0, len(self.relays)):
            self.relays[i].conserve_energy()
		
        for i in range(0, len(self.vccas)):
            self.vccas[i].conserve_energy()
		
        for i in range(0, len(self.vcls)):
            self.vcls[i].conserve_energy()
		
    def InstanceOfResistor(self, index: int):
        return self.resistors[index]

    None

    def InstanceOfCapacitor(self, index: int):
        return self.capacitors[index]

    None

    def InstanceOfInductor(self, index: int):
        return self.inductors[index]

    None

    def InstanceOfGround(self, index: int):
        return self.grounds[index]

    None

    def InstanceOfDCSource(self, index: int):
        return self.dcsources[index]

    None

    def InstanceOfDCCurrent(self, index: int):
        return self.dccurrents[index]

    None

    def InstanceOfACSource(self, index: int):
        return self.acsources[index]

    None

    def InstanceOfACCurrent(self, index: int):
        return self.accurrents[index]

    None
    
    def InstanceOfBridge(self, index: int):
        return self.bridges[index]

    None

    def InstanceOfSquareWave(self, index: int):
        return self.squarewaves[index]

    None

    def InstanceOfSawWave(self, index: int):
        return self.sawwaves[index]

    None

    def InstanceOfTriangleWave(self, index: int):
        return self.trianglewaves[index]

    None

    def InstanceOfConstant(self, index: int):
        return self.constants[index]

    None

    def InstanceOfWire(self, index: int):
        return self.wires[index]

    None

    def InstanceOfNet(self, index: int):
        return self.nets[index]

    None

    def InstanceOfNote(self, index: int):
        return self.notes[index]

    None

    def InstanceOfRail(self, index: int):
        return self.rails[index]

    None

    def InstanceOfVoltMeter(self, index: int):
        return self.voltmeters[index]

    None

    def InstanceOfOhmMeter(self, index: int):
        return self.ohmmeters[index]

    None

    def InstanceOfAmMeter(self, index: int):
        return self.ammeters[index]

    None

    def InstanceOfWattMeter(self, index: int):
        return self.wattmeters[index]

    None

    def InstanceOfFuse(self, index: int):
        return self.fuses[index]

    None

    def InstanceOfSinglePoleSingleThrow(self, index: int):
        return self.spsts[index]

    None

    def InstanceOfSinglePoleDoubleThrow(self, index: int):
        return self.spdts[index]

    None

    def InstanceOfNOTGate(self, index: int):
        return self.nots[index]

    None

    def InstanceOfDiode(self, index: int):
        return self.diodes[index]

    None

    def InstanceOfLightEmittingDiode(self, index: int):
        return self.leds[index]

    None

    def InstanceOfZenerDiode(self, index: int):
        return self.zeners[index]

    None

    def InstanceOfPotentiometer(self, index: int):
        return self.potentiometers[index]

    None

    def InstanceOfANDGate(self, index: int):
        return self.ands[index]

    None

    def InstanceOfORGate(self, index: int):
        return self.ors[index]

    None

    def InstanceOfNANDGate(self, index: int):
        return self.nands[index]

    None

    def InstanceOfNORGate(self, index: int):
        return self.nors[index]

    None

    def InstanceOfXORGate(self, index: int):
        return self.xors[index]

    None

    def InstanceOfXNORGate(self, index: int):
        return self.xnors[index]

    None

    def InstanceOfDFlipFlop(self, index: int):
        return self.dffs[index]

    None

    def InstanceOfVoltageSaturation(self, index: int):
        return self.vsats[index]

    None

    def InstanceOfAdder(self, index: int):
        return self.adders[index]

    None

    def InstanceOfSubtractor(self, index: int):
        return self.subtractors[index]

    None

    def InstanceOfMultiplier(self, index: int):
        return self.multipliers[index]

    None

    def InstanceOfDivider(self, index: int):
        return self.dividers[index]

    None

    def InstanceOfGainBlock(self, index: int):
        return self.gains[index]

    None

    def InstanceOfAbsoluteValue(self, index: int):
        return self.absvals[index]

    None

    def InstanceOfVoltageControlledSwitch(self, index: int):
        return self.vcsws[index]

    None

    def InstanceOfVoltageControlledVoltageSource(self, index: int):
        return self.vcvss[index]

    None

    def InstanceOfVoltageControlledCurrentSource(self, index: int):
        return self.vccss[index]

    None

    def InstanceOfCurrentControlledCurrentSource(self, index: int):
        return self.cccss[index]

    None

    def InstanceOfCurrentControlledVoltageSource(self, index: int):
        return self.ccvss[index]

    None

    def InstanceOfOperationalAmplifier(self, index: int):
        return self.opamps[index]

    None

    def InstanceOfNChannelMOSFET(self, index: int):
        return self.nmosfets[index]

    None

    def InstanceOfPChannelMOSFET(self, index: int):
        return self.pmosfets[index]

    None

    def InstanceOfNPNBipolarJunctionTransistor(self, index: int):
        return self.npns[index]

    None

    def InstanceOfPNPBipolarJunctionTransistor(self, index: int):
        return self.pnps[index]

    None

    def InstanceOfADCModule(self, index: int):
        return self.adcs[index]

    None

    def InstanceOfDACModule(self, index: int):
        return self.dacs[index]

    None

    def InstanceOfSampleAndHold(self, index: int):
        return self.sandhs[index]

    None

    def InstanceOfPulseWidthModulator(self, index: int):
        return self.pwms[index]

    None

    def InstanceOfIntegratorModule(self, index: int):
        return self.integrators[index]

    None

    def InstanceOfDifferentiatorModule(self, index: int):
        return self.differentiators[index]

    None

    def InstanceOfLowPassFilter(self, index: int):
        return self.lowpasses[index]

    None

    def InstanceOfHighPassFilter(self, index: int):
        return self.highpasses[index]

    None

    def InstanceOfRelay(self, index: int):
        return self.relays[index]

    None

    def InstanceOfPIDModule(self, index: int):
        return self.pids[index]

    None

    def InstanceOfLookUpTable(self, index: int):
        return self.luts[index]

    None

    def InstanceOfVoltageControlledResistor(self, index: int):
        return self.vcrs[index]

    None

    def InstanceOfVoltageControlledCapacitor(self, index: int):
        return self.vccas[index]

    None

    def InstanceOfVoltageControlledInductor(self, index: int):
        return self.vcls[index]

    None

    def InstanceOfGreaterThan(self, index: int):
        return self.grts[index]

    None

    def InstanceOfTPTZModule(self, index: int):
        return self.tptzs[index]

    None

    def InstanceOfTransformer(self, index: int):
        return self.transformers[index]

    None

    def assign_element_simulation_ids(self, context):
        elm_max: int = Utils.Utils.element_max(context)
        for i in range(0, elm_max):
            if i > -1 and i < len(self.resistors):
                self.resistors[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.capacitors):
                self.capacitors[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.inductors):
                self.inductors[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.bridges):
                self.bridges[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.grounds):
                self.grounds[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.dcsources):
                self.dcsources[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.dccurrents):
                self.dccurrents[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.acsources):
                self.acsources[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.accurrents):
                self.accurrents[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.squarewaves):
                self.squarewaves[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.sawwaves):
                self.sawwaves[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.trianglewaves):
                self.trianglewaves[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.constants):
                self.constants[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.nets):
                self.nets[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.notes):
                self.notes[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.rails):
                self.rails[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.voltmeters):
                self.voltmeters[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.ohmmeters):
                self.ohmmeters[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.ammeters):
                self.ammeters[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.wattmeters):
                self.wattmeters[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.fuses):
                self.fuses[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.spsts):
                self.spsts[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.spdts):
                self.spdts[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.nots):
                self.nots[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.diodes):
                self.diodes[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.leds):
                self.leds[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.zeners):
                self.zeners[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.potentiometers):
                self.potentiometers[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.ands):
                self.ands[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.ors):
                self.ors[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.nands):
                self.nands[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.nors):
                self.nors[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.xors):
                self.xors[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.xnors):
                self.xnors[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.dffs):
                self.dffs[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.vsats):
                self.vsats[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.adders):
                self.adders[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.subtractors):
                self.subtractors[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.multipliers):
                self.multipliers[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.dividers):
                self.dividers[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.gains):
                self.gains[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.absvals):
                self.absvals[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.vcsws):
                self.vcsws[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.vcvss):
                self.vcvss[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.vccss):
                self.vccss[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.cccss):
                self.cccss[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.ccvss):
                self.ccvss[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.opamps):
                self.opamps[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.nmosfets):
                self.nmosfets[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.pmosfets):
                self.pmosfets[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.npns):
                self.npns[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.pnps):
                self.pnps[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.adcs):
                self.adcs[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.dacs):
                self.dacs[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.sandhs):
                self.sandhs[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.pwms):
                self.pwms[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.integrators):
                self.integrators[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.differentiators):
                self.differentiators[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.lowpasses):
                self.lowpasses[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.highpasses):
                self.highpasses[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.relays):
                self.relays[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.pids):
                self.pids[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.luts):
                self.luts[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.vcrs):
                self.vcrs[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.vccas):
                self.vccas[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.vcls):
                self.vcls[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.grts):
                self.grts[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.tptzs):
                self.tptzs[i].SetSimulationId(i)
            None

            if i > -1 and i < len(self.transformers):
                self.transformers[i].SetSimulationId(i)
            None
        None

    None

    def load_file(self, FilePath: str) -> None:
        with open(FilePath, "r") as UserFile:
            self.FileData = UserFile.readlines()
            self.FileData = "".join(self.FileData)

    def contains(self, Phrase: str, Text: str) -> bool:
        return Phrase in Text

    None

    def reset_elements(self):
        for i in range(0, len(self.resistors)):
            self.resistors[i].reset()
        None

        for i in range(0, len(self.capacitors)):
            self.capacitors[i].reset()
        None

        for i in range(0, len(self.inductors)):
            self.inductors[i].reset()
        None

        for i in range(0, len(self.grounds)):
            self.grounds[i].reset()
        None
        
        for i in range(0, len(self.bridges)):
            self.bridges[i].reset()
        None

        for i in range(0, len(self.dcsources)):
            self.dcsources[i].reset()
        None

        for i in range(0, len(self.dccurrents)):
            self.dccurrents[i].reset()
        None

        for i in range(0, len(self.acsources)):
            self.acsources[i].reset()
        None

        for i in range(0, len(self.accurrents)):
            self.accurrents[i].reset()
        None

        for i in range(0, len(self.squarewaves)):
            self.squarewaves[i].reset()
        None

        for i in range(0, len(self.sawwaves)):
            self.sawwaves[i].reset()
        None

        for i in range(0, len(self.trianglewaves)):
            self.trianglewaves[i].reset()
        None

        for i in range(0, len(self.constants)):
            self.constants[i].reset()
        None

        for i in range(0, len(self.nets)):
            self.nets[i].reset()
        None

        for i in range(0, len(self.notes)):
            self.notes[i].reset()
        None

        for i in range(0, len(self.rails)):
            self.rails[i].reset()
        None

        for i in range(0, len(self.voltmeters)):
            self.voltmeters[i].reset()
        None

        for i in range(0, len(self.ohmmeters)):
            self.ohmmeters[i].reset()
        None

        for i in range(0, len(self.ammeters)):
            self.ammeters[i].reset()
        None

        for i in range(0, len(self.wattmeters)):
            self.wattmeters[i].reset()
        None

        for i in range(0, len(self.fuses)):
            self.fuses[i].reset()
        None

        for i in range(0, len(self.spsts)):
            self.spsts[i].reset()
        None

        for i in range(0, len(self.spdts)):
            self.spdts[i].reset()
        None

        for i in range(0, len(self.nots)):
            self.nots[i].reset()
        None

        for i in range(0, len(self.diodes)):
            self.diodes[i].reset()
        None

        for i in range(0, len(self.leds)):
            self.leds[i].reset()
        None

        for i in range(0, len(self.zeners)):
            self.zeners[i].reset()
        None

        for i in range(0, len(self.potentiometers)):
            self.potentiometers[i].reset()
        None

        for i in range(0, len(self.ands)):
            self.ands[i].reset()
        None

        for i in range(0, len(self.ors)):
            self.ors[i].reset()
        None

        for i in range(0, len(self.nands)):
            self.nands[i].reset()
        None

        for i in range(0, len(self.nors)):
            self.nors[i].reset()
        None

        for i in range(0, len(self.xors)):
            self.xors[i].reset()
        None

        for i in range(0, len(self.xnors)):
            self.xnors[i].reset()
        None

        for i in range(0, len(self.dffs)):
            self.dffs[i].reset()
        None

        for i in range(0, len(self.vsats)):
            self.vsats[i].reset()
        None

        for i in range(0, len(self.adders)):
            self.adders[i].reset()
        None

        for i in range(0, len(self.subtractors)):
            self.subtractors[i].reset()
        None

        for i in range(0, len(self.multipliers)):
            self.multipliers[i].reset()
        None

        for i in range(0, len(self.dividers)):
            self.dividers[i].reset()
        None

        for i in range(0, len(self.gains)):
            self.gains[i].reset()
        None

        for i in range(0, len(self.absvals)):
            self.absvals[i].reset()
        None

        for i in range(0, len(self.vcsws)):
            self.vcsws[i].reset()
        None

        for i in range(0, len(self.vcvss)):
            self.vcvss[i].reset()
        None

        for i in range(0, len(self.vccss)):
            self.vccss[i].reset()
        None

        for i in range(0, len(self.cccss)):
            self.cccss[i].reset()
        None

        for i in range(0, len(self.ccvss)):
            self.ccvss[i].reset()
        None

        for i in range(0, len(self.opamps)):
            self.opamps[i].reset()
        None

        for i in range(0, len(self.nmosfets)):
            self.nmosfets[i].reset()
        None

        for i in range(0, len(self.pmosfets)):
            self.pmosfets[i].reset()
        None

        for i in range(0, len(self.npns)):
            self.npns[i].reset()
        None

        for i in range(0, len(self.pnps)):
            self.pnps[i].reset()
        None

        for i in range(0, len(self.adcs)):
            self.adcs[i].reset()
        None

        for i in range(0, len(self.dacs)):
            self.dacs[i].reset()
        None

        for i in range(0, len(self.sandhs)):
            self.sandhs[i].reset()
        None

        for i in range(0, len(self.pwms)):
            self.pwms[i].reset()
        None

        for i in range(0, len(self.integrators)):
            self.integrators[i].reset()
        None

        for i in range(0, len(self.differentiators)):
            self.differentiators[i].reset()
        None

        for i in range(0, len(self.lowpasses)):
            self.lowpasses[i].reset()
        None

        for i in range(0, len(self.highpasses)):
            self.highpasses[i].reset()
        None

        for i in range(0, len(self.relays)):
            self.relays[i].reset()
        None

        for i in range(0, len(self.pids)):
            self.pids[i].reset()
        None

        for i in range(0, len(self.luts)):
            self.luts[i].reset()
        None

        for i in range(0, len(self.vcrs)):
            self.vcrs[i].reset()
        None

        for i in range(0, len(self.vccas)):
            self.vccas[i].reset()
        None

        for i in range(0, len(self.vcls)):
            self.vcls[i].reset()
        None

        for i in range(0, len(self.grts)):
            self.grts[i].reset()
        None

        for i in range(0, len(self.tptzs)):
            self.tptzs[i].reset()
        None

        for i in range(0, len(self.transformers)):
            self.transformers[i].reset()
        None

    None

    def update_elements(self):
        for i in range(0, len(self.resistors)):
            self.resistors[i].update()
        None

        for i in range(0, len(self.capacitors)):
            self.capacitors[i].update()
        None

        for i in range(0, len(self.inductors)):
            self.inductors[i].update()
        None

        for i in range(0, len(self.bridges)):
            self.bridges[i].update()
        None

        for i in range(0, len(self.grounds)):
            self.grounds[i].update()
        None

        for i in range(0, len(self.dcsources)):
            self.dcsources[i].update()
        None

        for i in range(0, len(self.dccurrents)):
            self.dccurrents[i].update()
        None

        for i in range(0, len(self.acsources)):
            self.acsources[i].update()
        None

        for i in range(0, len(self.accurrents)):
            self.accurrents[i].update()
        None

        for i in range(0, len(self.squarewaves)):
            self.squarewaves[i].update()
        None

        for i in range(0, len(self.sawwaves)):
            self.sawwaves[i].update()
        None

        for i in range(0, len(self.trianglewaves)):
            self.trianglewaves[i].update()
        None

        for i in range(0, len(self.constants)):
            self.constants[i].update()
        None

        for i in range(0, len(self.nets)):
            self.nets[i].update()
        None

        for i in range(0, len(self.notes)):
            self.notes[i].update()
        None

        for i in range(0, len(self.rails)):
            self.rails[i].update()
        None

        for i in range(0, len(self.voltmeters)):
            self.voltmeters[i].update()
        None

        for i in range(0, len(self.ohmmeters)):
            self.ohmmeters[i].update()
        None

        for i in range(0, len(self.ammeters)):
            self.ammeters[i].update()
        None

        for i in range(0, len(self.wattmeters)):
            self.wattmeters[i].update()
        None

        for i in range(0, len(self.fuses)):
            self.fuses[i].update()
        None

        for i in range(0, len(self.spsts)):
            self.spsts[i].update()
        None

        for i in range(0, len(self.spdts)):
            self.spdts[i].update()
        None

        for i in range(0, len(self.potentiometers)):
            self.potentiometers[i].update()
        None

        for i in range(0, len(self.dffs)):
            self.dffs[i].update()
        None

        for i in range(0, len(self.vsats)):
            self.vsats[i].update()
        None

        for i in range(0, len(self.adders)):
            self.adders[i].update()
        None

        for i in range(0, len(self.subtractors)):
            self.subtractors[i].update()
        None

        for i in range(0, len(self.multipliers)):
            self.multipliers[i].update()
        None

        for i in range(0, len(self.dividers)):
            self.dividers[i].update()
        None

        for i in range(0, len(self.gains)):
            self.gains[i].update()
        None

        for i in range(0, len(self.absvals)):
            self.absvals[i].update()
        None

        for i in range(0, len(self.vcsws)):
            self.vcsws[i].update()
        None

        for i in range(0, len(self.vcvss)):
            self.vcvss[i].update()
        None

        for i in range(0, len(self.vccss)):
            self.vccss[i].update()
        None

        for i in range(0, len(self.cccss)):
            self.cccss[i].update()
        None

        for i in range(0, len(self.ccvss)):
            self.ccvss[i].update()
        None

        for i in range(0, len(self.opamps)):
            self.opamps[i].update()
        None

        for i in range(0, len(self.adcs)):
            self.adcs[i].update()
        None

        for i in range(0, len(self.dacs)):
            self.dacs[i].update()
        None

        for i in range(0, len(self.sandhs)):
            self.sandhs[i].update()
        None

        for i in range(0, len(self.pwms)):
            self.pwms[i].update()
        None

        for i in range(0, len(self.integrators)):
            self.integrators[i].update()
        None

        for i in range(0, len(self.differentiators)):
            self.differentiators[i].update()
        None

        for i in range(0, len(self.lowpasses)):
            self.lowpasses[i].update()
        None

        for i in range(0, len(self.highpasses)):
            self.highpasses[i].update()
        None

        for i in range(0, len(self.relays)):
            self.relays[i].update()
        None

        for i in range(0, len(self.pids)):
            self.pids[i].update()
        None

        for i in range(0, len(self.luts)):
            self.luts[i].update()
        None

        for i in range(0, len(self.vcrs)):
            self.vcrs[i].update()
        None

        for i in range(0, len(self.vccas)):
            self.vccas[i].update()
        None

        for i in range(0, len(self.vcls)):
            self.vcls[i].update()
        None

        for i in range(0, len(self.grts)):
            self.grts[i].update()
        None

        for i in range(0, len(self.tptzs)):
            self.tptzs[i].update()
        None

        for i in range(0, len(self.transformers)):
            self.transformers[i].update()
        None

    None

    def stamp_elements(self):
        for i in range(0, len(self.resistors)):
            self.resistors[i].stamp()
        None

        for i in range(0, len(self.capacitors)):
            self.capacitors[i].stamp()
        None

        for i in range(0, len(self.inductors)):
            self.inductors[i].stamp()
        None

        for i in range(0, len(self.grounds)):
            self.grounds[i].stamp()
        None

        for i in range(0, len(self.bridges)):
            self.bridges[i].stamp()
        None
        
        for i in range(0, len(self.dcsources)):
            self.dcsources[i].stamp()
        None

        for i in range(0, len(self.dccurrents)):
            self.dccurrents[i].stamp()
        None

        for i in range(0, len(self.acsources)):
            self.acsources[i].stamp()
        None

        for i in range(0, len(self.accurrents)):
            self.accurrents[i].stamp()
        None

        for i in range(0, len(self.squarewaves)):
            self.squarewaves[i].stamp()
        None

        for i in range(0, len(self.sawwaves)):
            self.sawwaves[i].stamp()
        None

        for i in range(0, len(self.trianglewaves)):
            self.trianglewaves[i].stamp()
        None

        for i in range(0, len(self.constants)):
            self.constants[i].stamp()
        None

        for i in range(0, len(self.nets)):
            self.nets[i].stamp()
        None

        for i in range(0, len(self.notes)):
            self.notes[i].stamp()
        None

        for i in range(0, len(self.rails)):
            self.rails[i].stamp()
        None

        for i in range(0, len(self.voltmeters)):
            self.voltmeters[i].stamp()
        None

        for i in range(0, len(self.ohmmeters)):
            self.ohmmeters[i].stamp()
        None

        for i in range(0, len(self.ammeters)):
            self.ammeters[i].stamp()
        None

        for i in range(0, len(self.wattmeters)):
            self.wattmeters[i].stamp()
        None

        for i in range(0, len(self.fuses)):
            self.fuses[i].stamp()
        None

        for i in range(0, len(self.spsts)):
            self.spsts[i].stamp()
        None

        for i in range(0, len(self.spdts)):
            self.spdts[i].stamp()
        None

        for i in range(0, len(self.nots)):
            self.nots[i].stamp()
        None

        for i in range(0, len(self.diodes)):
            self.diodes[i].stamp()
        None

        for i in range(0, len(self.leds)):
            self.leds[i].stamp()
        None

        for i in range(0, len(self.zeners)):
            self.zeners[i].stamp()
        None

        for i in range(0, len(self.potentiometers)):
            self.potentiometers[i].stamp()
        None

        for i in range(0, len(self.ands)):
            self.ands[i].stamp()
        None

        for i in range(0, len(self.ors)):
            self.ors[i].stamp()
        None

        for i in range(0, len(self.nands)):
            self.nands[i].stamp()
        None

        for i in range(0, len(self.nors)):
            self.nors[i].stamp()
        None

        for i in range(0, len(self.xors)):
            self.xors[i].stamp()
        None

        for i in range(0, len(self.xnors)):
            self.xnors[i].stamp()
        None

        for i in range(0, len(self.dffs)):
            self.dffs[i].stamp()
        None

        for i in range(0, len(self.vsats)):
            self.vsats[i].stamp()
        None

        for i in range(0, len(self.adders)):
            self.adders[i].stamp()
        None

        for i in range(0, len(self.subtractors)):
            self.subtractors[i].stamp()
        None

        for i in range(0, len(self.multipliers)):
            self.multipliers[i].stamp()
        None

        for i in range(0, len(self.dividers)):
            self.dividers[i].stamp()
        None

        for i in range(0, len(self.gains)):
            self.gains[i].stamp()
        None

        for i in range(0, len(self.absvals)):
            self.absvals[i].stamp()
        None

        for i in range(0, len(self.vcsws)):
            self.vcsws[i].stamp()
        None

        for i in range(0, len(self.vcvss)):
            self.vcvss[i].stamp()
        None

        for i in range(0, len(self.vccss)):
            self.vccss[i].stamp()
        None

        for i in range(0, len(self.cccss)):
            self.cccss[i].stamp()
        None

        for i in range(0, len(self.ccvss)):
            self.ccvss[i].stamp()
        None

        for i in range(0, len(self.opamps)):
            self.opamps[i].stamp()
        None

        for i in range(0, len(self.nmosfets)):
            self.nmosfets[i].stamp()
        None

        for i in range(0, len(self.pmosfets)):
            self.pmosfets[i].stamp()
        None

        for i in range(0, len(self.npns)):
            self.npns[i].stamp()
        None

        for i in range(0, len(self.pnps)):
            self.pnps[i].stamp()
        None

        for i in range(0, len(self.adcs)):
            self.adcs[i].stamp()
        None

        for i in range(0, len(self.dacs)):
            self.dacs[i].stamp()
        None

        for i in range(0, len(self.sandhs)):
            self.sandhs[i].stamp()
        None

        for i in range(0, len(self.pwms)):
            self.pwms[i].stamp()
        None

        for i in range(0, len(self.integrators)):
            self.integrators[i].stamp()
        None

        for i in range(0, len(self.differentiators)):
            self.differentiators[i].stamp()
        None

        for i in range(0, len(self.lowpasses)):
            self.lowpasses[i].stamp()
        None

        for i in range(0, len(self.highpasses)):
            self.highpasses[i].stamp()
        None

        for i in range(0, len(self.relays)):
            self.relays[i].stamp()
        None

        for i in range(0, len(self.pids)):
            self.pids[i].stamp()
        None

        for i in range(0, len(self.luts)):
            self.luts[i].stamp()
        None

        for i in range(0, len(self.vcrs)):
            self.vcrs[i].stamp()
        None

        for i in range(0, len(self.vccas)):
            self.vccas[i].stamp()
        None

        for i in range(0, len(self.vcls)):
            self.vcls[i].stamp()
        None

        for i in range(0, len(self.grts)):
            self.grts[i].stamp()
        None

        for i in range(0, len(self.tptzs)):
            self.tptzs[i].stamp()
        None

        for i in range(0, len(self.transformers)):
            self.transformers[i].stamp()
        None

    None

    def initialize(self) -> None:
        self.Parts.clear()
        self.Elements.clear()
        self.Id_Properties.clear()
        self.CircuitElements.clear()
        
        self.Parts = self.FileData.split(self.VERSION_NUMBER)
        
        if len(self.Parts) > 1:
            Version = self.Parts[0]
            print("File Version: %s" % Version)

            MajorMinorPatch = self.Parts[0].split(".")
            if len(MajorMinorPatch) >= 3:
                Major = int(MajorMinorPatch[0].replace("[^\d]", ""))
                Minor = int(MajorMinorPatch[1].replace("[^\d]", ""))
                Patch = int(MajorMinorPatch[2].replace("[^\d]", ""))

                VersionNumber = (
                        ((Major << self.MAJOR_SHIFT) & self.MAJOR_MASK)
                        | ((Minor << self.MINOR_SHIFT) & self.MINOR_MASK)
                        | ((Patch << self.PATCH_SHIFT) & self.PATCH_MASK)
                )

                if VersionNumber < self.MINIMUM_VERSION:
                    raise RuntimeError("Invalid file version: %d.%d.%d. The minimum file version number is: %d.%d.%d."
                                       % (
                                           Major,
                                           Minor,
                                           Patch,
                                           self.MINIMUM_MAJOR,
                                           self.MINIMUM_MINOR,
                                           self.MINIMUM_PATCH,
                                       ))
                None
            None
        else:
            raise RuntimeError("Invalid file type.")
        None

        self.Elements = self.Parts[1].split(self.ELEMENT_DIVIDER)

        for i in range(0, len(self.Elements)):
            self.Wires = self.Elements[i].split(self.WIRE_DIVIDER)
            if len(self.Wires) > 1:
                self.Id_Properties = self.Wires[0].split(self.ID_DIVIDER)
                if self.contains(self.WIRE_ELEMENT, self.Wires[1]):
                    self.wires.append(
                        Wire.Wire(self.Id_Properties[0], self.Id_Properties[1])
                    )
                else:
                    self.CircuitElements.append(
                        Element.Element(
                            self.Id_Properties[0],
                            self.Id_Properties[1],
                            self.Wires[1],
                            self,
                        )
                    )
                None
            None
        None

        for i in range(0, len(self.CircuitElements)):
            ModifiedProperties = Utils.Utils.FixProperties(
                self.CircuitElements[i].GetJsonProperty()
            )

            if self.CircuitElements[i].GetElementType() == Type.Type.TYPE_RESISTOR:
                self.resistors.append(Resistor.Resistor(self, **ModifiedProperties))
                self.resistors[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.resistors[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.resistors[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.resistors[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_BRIDGE:
                self.bridges.append(Bridge.Bridge(self, **ModifiedProperties))
                self.bridges[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.bridges[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.bridges[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.bridges[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_CAPACITOR:
                self.capacitors.append(Capacitor.Capacitor(self, **ModifiedProperties))
                self.capacitors[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.capacitors[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.capacitors[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.capacitors[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_INDUCTOR:
                self.inductors.append(Inductor.Inductor(self, **ModifiedProperties))
                self.inductors[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.inductors[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.inductors[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.inductors[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_GROUND:
                self.grounds.append(Ground.Ground(self, **ModifiedProperties))
                self.grounds[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.grounds[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.grounds[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.grounds[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_DCSOURCE:
                self.dcsources.append(DCSource.DCSource(self, **ModifiedProperties))
                self.dcsources[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.dcsources[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.dcsources[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.dcsources[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_DCCURRENT:
                self.dccurrents.append(DCCurrent.DCCurrent(self, **ModifiedProperties))
                self.dccurrents[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.dccurrents[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.dccurrents[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.dccurrents[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_ACSOURCE:
                self.acsources.append(ACSource.ACSource(self, **ModifiedProperties))
                self.acsources[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.acsources[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.acsources[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.acsources[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_ACCURRENT:
                self.accurrents.append(ACCurrent.ACCurrent(self, **ModifiedProperties))
                self.accurrents[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.accurrents[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.accurrents[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.accurrents[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_SQUAREWAVE:
                self.squarewaves.append(
                    SquareWave.SquareWave(self, **ModifiedProperties)
                )
                self.squarewaves[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.squarewaves[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.squarewaves[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.squarewaves[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_SAW:
                self.sawwaves.append(SawWave.SawWave(self, **ModifiedProperties))
                self.sawwaves[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.sawwaves[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.sawwaves[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.sawwaves[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_TRI:
                self.trianglewaves.append(
                    TriangleWave.TriangleWave(self, **ModifiedProperties)
                )
                self.trianglewaves[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.trianglewaves[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.trianglewaves[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.trianglewaves[-1].SetLinkages(
                    self.CircuitElements[i].GetLinkages()
                )
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_CONSTANT:
                self.constants.append(Constant.Constant(self, **ModifiedProperties))
                self.constants[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.constants[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.constants[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.constants[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_WIRE:
                self.wires.append(Wire.Wire(self, **ModifiedProperties))
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_NET:
                self.nets.append(Net.Net(self, **ModifiedProperties))
                self.nets[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.nets[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.nets[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.nets[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_NOTE:
                self.notes.append(Note.Note(self, **ModifiedProperties))
                self.notes[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.notes[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.notes[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.notes[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_RAIL:
                self.rails.append(Rail.Rail(self, **ModifiedProperties))
                self.rails[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.rails[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.rails[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.rails[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_VOLTMETER:
                self.voltmeters.append(VoltMeter.VoltMeter(self, **ModifiedProperties))
                self.voltmeters[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.voltmeters[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.voltmeters[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.voltmeters[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_OHMMETER:
                self.ohmmeters.append(OhmMeter.OhmMeter(self, **ModifiedProperties))
                self.ohmmeters[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.ohmmeters[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.ohmmeters[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.ohmmeters[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_AMMETER:
                self.ammeters.append(AmMeter.AmMeter(self, **ModifiedProperties))
                self.ammeters[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.ammeters[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.ammeters[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.ammeters[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_WATTMETER:
                self.wattmeters.append(WattMeter.WattMeter(self, **ModifiedProperties))
                self.wattmeters[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.wattmeters[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.wattmeters[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.wattmeters[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_FUSE:
                self.fuses.append(Fuse.Fuse(self, **ModifiedProperties))
                self.fuses[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.fuses[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.fuses[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.fuses[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_SPST:
                self.spsts.append(
                    SinglePoleSingleThrow.SinglePoleSingleThrow(
                        self, **ModifiedProperties
                    )
                )
                self.spsts[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.spsts[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.spsts[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.spsts[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_SPDT:
                self.spdts.append(
                    SinglePoleDoubleThrow.SinglePoleDoubleThrow(
                        self, **ModifiedProperties
                    )
                )
                self.spdts[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.spdts[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.spdts[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.spdts[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_NOT:
                self.nots.append(NOTGate.NOTGate(self, **ModifiedProperties))
                self.nots[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.nots[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.nots[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.nots[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_DIODE:
                self.diodes.append(Diode.Diode(self, **ModifiedProperties))
                self.diodes[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.diodes[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.diodes[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.diodes[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_LED:
                self.leds.append(
                    LightEmittingDiode.LightEmittingDiode(self, **ModifiedProperties)
                )
                self.leds[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.leds[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.leds[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.leds[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_ZENER:
                self.zeners.append(ZenerDiode.ZenerDiode(self, **ModifiedProperties))
                self.zeners[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.zeners[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.zeners[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.zeners[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif (
                    self.CircuitElements[i].GetElementType() == Type.Type.TYPE_POTENTIOMETER
            ):
                self.potentiometers.append(
                    Potentiometer.Potentiometer(self, **ModifiedProperties)
                )
                self.potentiometers[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.potentiometers[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.potentiometers[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.potentiometers[-1].SetLinkages(
                    self.CircuitElements[i].GetLinkages()
                )
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_AND:
                self.ands.append(ANDGate.ANDGate(self, **ModifiedProperties))
                self.ands[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.ands[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.ands[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.ands[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_OR:
                self.ors.append(ORGate.ORGate(self, **ModifiedProperties))
                self.ors[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.ors[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.ors[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.ors[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_NAND:
                self.nands.append(NANDGate.NANDGate(self, **ModifiedProperties))
                self.nands[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.nands[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.nands[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.nands[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_NOR:
                self.nors.append(NORGate.NORGate(self, **ModifiedProperties))
                self.nors[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.nors[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.nors[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.nors[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_XOR:
                self.xors.append(XORGate.XORGate(self, **ModifiedProperties))
                self.xors[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.xors[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.xors[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.xors[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_XNOR:
                self.xnors.append(XNORGate.XNORGate(self, **ModifiedProperties))
                self.xnors[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.xnors[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.xnors[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.xnors[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_DFF:
                self.dffs.append(DFlipFlop.DFlipFlop(self, **ModifiedProperties))
                self.dffs[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.dffs[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.dffs[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.dffs[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_VSAT:
                self.vsats.append(
                    VoltageSaturation.VoltageSaturation(self, **ModifiedProperties)
                )
                self.vsats[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.vsats[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.vsats[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.vsats[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_ADD:
                self.adders.append(Adder.Adder(self, **ModifiedProperties))
                self.adders[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.adders[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.adders[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.adders[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_SUB:
                self.subtractors.append(
                    Subtractor.Subtractor(self, **ModifiedProperties)
                )
                self.subtractors[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.subtractors[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.subtractors[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.subtractors[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_MUL:
                self.multipliers.append(
                    Multiplier.Multiplier(self, **ModifiedProperties)
                )
                self.multipliers[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.multipliers[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.multipliers[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.multipliers[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_DIV:
                self.dividers.append(Divider.Divider(self, **ModifiedProperties))
                self.dividers[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.dividers[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.dividers[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.dividers[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_GAIN:
                self.gains.append(GainBlock.GainBlock(self, **ModifiedProperties))
                self.gains[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.gains[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.gains[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.gains[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_ABS:
                self.absvals.append(
                    AbsoluteValue.AbsoluteValue(self, **ModifiedProperties)
                )
                self.absvals[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.absvals[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.absvals[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.absvals[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_VCSW:
                self.vcsws.append(
                    VoltageControlledSwitch.VoltageControlledSwitch(
                        self, **ModifiedProperties
                    )
                )
                self.vcsws[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.vcsws[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.vcsws[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.vcsws[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_VCVS:
                self.vcvss.append(
                    VoltageControlledVoltageSource.VoltageControlledVoltageSource(
                        self, **ModifiedProperties
                    )
                )
                self.vcvss[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.vcvss[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.vcvss[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.vcvss[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_VCCS:
                self.vccss.append(
                    VoltageControlledCurrentSource.VoltageControlledCurrentSource(
                        self, **ModifiedProperties
                    )
                )
                self.vccss[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.vccss[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.vccss[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.vccss[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_CCCS:
                self.cccss.append(
                    CurrentControlledCurrentSource.CurrentControlledCurrentSource(
                        self, **ModifiedProperties
                    )
                )
                self.cccss[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.cccss[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.cccss[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.cccss[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_CCVS:
                self.ccvss.append(
                    CurrentControlledVoltageSource.CurrentControlledVoltageSource(
                        self, **ModifiedProperties
                    )
                )
                self.ccvss[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.ccvss[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.ccvss[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.ccvss[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_OPAMP:
                self.opamps.append(
                    OperationalAmplifier.OperationalAmplifier(
                        self, **ModifiedProperties
                    )
                )
                self.opamps[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.opamps[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.opamps[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.opamps[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_NMOS:
                self.nmosfets.append(
                    NChannelMOSFET.NChannelMOSFET(self, **ModifiedProperties)
                )
                self.nmosfets[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.nmosfets[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.nmosfets[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.nmosfets[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_PMOS:
                self.pmosfets.append(
                    PChannelMOSFET.PChannelMOSFET(self, **ModifiedProperties)
                )
                self.pmosfets[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.pmosfets[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.pmosfets[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.pmosfets[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_NPN:
                self.npns.append(
                    NPNBipolarJunctionTransistor.NPNBipolarJunctionTransistor(
                        self, **ModifiedProperties
                    )
                )
                self.npns[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.npns[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.npns[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.npns[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_PNP:
                self.pnps.append(
                    PNPBipolarJunctionTransistor.PNPBipolarJunctionTransistor(
                        self, **ModifiedProperties
                    )
                )
                self.pnps[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.pnps[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.pnps[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.pnps[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_ADC:
                self.adcs.append(ADCModule.ADCModule(self, **ModifiedProperties))
                self.adcs[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.adcs[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.adcs[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.adcs[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_DAC:
                self.dacs.append(DACModule.DACModule(self, **ModifiedProperties))
                self.dacs[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.dacs[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.dacs[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.dacs[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_SAH:
                self.sandhs.append(
                    SampleAndHold.SampleAndHold(self, **ModifiedProperties)
                )
                self.sandhs[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.sandhs[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.sandhs[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.sandhs[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_PWM:
                self.pwms.append(
                    PulseWidthModulator.PulseWidthModulator(self, **ModifiedProperties)
                )
                self.pwms[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.pwms[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.pwms[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.pwms[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_INTEGRATOR:
                self.integrators.append(
                    IntegratorModule.IntegratorModule(self, **ModifiedProperties)
                )
                self.integrators[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.integrators[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.integrators[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.integrators[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif (
                    self.CircuitElements[i].GetElementType()
                    == Type.Type.TYPE_DIFFERENTIATOR
            ):
                self.differentiators.append(
                    DifferentiatorModule.DifferentiatorModule(
                        self, **ModifiedProperties
                    )
                )
                self.differentiators[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.differentiators[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.differentiators[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.differentiators[-1].SetLinkages(
                    self.CircuitElements[i].GetLinkages()
                )
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_LPF:
                self.lowpasses.append(
                    LowPassFilter.LowPassFilter(self, **ModifiedProperties)
                )
                self.lowpasses[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.lowpasses[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.lowpasses[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.lowpasses[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_HPF:
                self.highpasses.append(
                    HighPassFilter.HighPassFilter(self, **ModifiedProperties)
                )
                self.highpasses[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.highpasses[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.highpasses[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.highpasses[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_REL:
                self.relays.append(Relay.Relay(self, **ModifiedProperties))
                self.relays[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.relays[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.relays[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.relays[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_PID:
                self.pids.append(PIDModule.PIDModule(self, **ModifiedProperties))
                self.pids[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.pids[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.pids[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.pids[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_LUT:
                self.luts.append(LookUpTable.LookUpTable(self, **ModifiedProperties))
                self.luts[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.luts[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.luts[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.luts[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_VCR:
                self.vcrs.append(
                    VoltageControlledResistor.VoltageControlledResistor(
                        self, **ModifiedProperties
                    )
                )
                self.vcrs[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.vcrs[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.vcrs[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.vcrs[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_VCCA:
                self.vccas.append(
                    VoltageControlledCapacitor.VoltageControlledCapacitor(
                        self, **ModifiedProperties
                    )
                )
                self.vccas[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.vccas[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.vccas[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.vccas[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_VCL:
                self.vcls.append(
                    VoltageControlledInductor.VoltageControlledInductor(
                        self, **ModifiedProperties
                    )
                )
                self.vcls[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.vcls[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.vcls[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.vcls[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_GRT:
                self.grts.append(GreaterThan.GreaterThan(self, **ModifiedProperties))
                self.grts[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.grts[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.grts[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.grts[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_TPTZ:
                self.tptzs.append(TPTZModule.TPTZModule(self, **ModifiedProperties))
                self.tptzs[-1].SetDesignator(self.CircuitElements[i].GetDesignator())
                self.tptzs[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.tptzs[-1].SetElementType(self.CircuitElements[i].GetElementType())
                self.tptzs[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            elif self.CircuitElements[i].GetElementType() == Type.Type.TYPE_TRAN:
                self.transformers.append(
                    Transformer.Transformer(self, **ModifiedProperties)
                )
                self.transformers[-1].SetDesignator(
                    self.CircuitElements[i].GetDesignator()
                )
                self.transformers[-1].SetNodes(self.CircuitElements[i].GetNodes())
                self.transformers[-1].SetElementType(
                    self.CircuitElements[i].GetElementType()
                )
                self.transformers[-1].SetLinkages(self.CircuitElements[i].GetLinkages())
            None
        None

        for i in range(0, self.Params.SystemSettings.MAXNODES):
            self.nodes.append(Node.Node(self, i))
        None

        TempIndex: str = ""
        for i in range(0, len(self.CircuitElements)):
            self.CircuitElements[i].Anchor()
            TempIndex = Utils.Utils.MapElement(
                self.CircuitElements[i].GetDesignator(), self.CircuitElements
            )
            if not (TempIndex == Type.Type.TYPE_UNDEFINED):
                self.Map.append(
                    KeyPair.KeyPair(self.CircuitElements[i].GetDesignator(), TempIndex)
                )
            None
        None

        self.Params.SystemVariables.IsSingular = False
        self.first_matrix_build = True
        self.simulation_time = 0
        self.continue_solving = True
        self.solutions_ready = False
        self.iterator = 0
        self.simulation_step = 0
        self.first_error_check = True
        self.first_x_matrix_copy = True
        self.first_x_matrix_solution = False
        self.system_ready = False
        self.reset_elements()

        self.node_manager.generate_unique_nodes_list()
        self.node_manager.assign_node_simulation_ids()
        self.assign_element_simulation_ids(self)
        self.node_size = len(self.node_manager.active_nodes)

        # Element Offsets.
        self.ELEMENT_DCSOURCE_OFFSET = 0
        self.ELEMENT_ACSOURCE_OFFSET = self.ELEMENT_DCSOURCE_OFFSET + len(
            self.dcsources
        )
        self.ELEMENT_SQUAREWAVE_OFFSET = self.ELEMENT_ACSOURCE_OFFSET + len(
            self.acsources
        )
        self.ELEMENT_SAW_OFFSET = self.ELEMENT_SQUAREWAVE_OFFSET + len(self.squarewaves)
        self.ELEMENT_TRI_OFFSET = self.ELEMENT_SAW_OFFSET + len(self.sawwaves)
        self.ELEMENT_CONSTANT_OFFSET = self.ELEMENT_TRI_OFFSET + len(self.trianglewaves)
        self.ELEMENT_RAIL_OFFSET = self.ELEMENT_CONSTANT_OFFSET + len(self.constants)
        self.ELEMENT_OHMMETER_OFFSET = self.ELEMENT_RAIL_OFFSET + len(self.rails)
        self.ELEMENT_AMMETER_OFFSET = self.ELEMENT_OHMMETER_OFFSET + len(self.ohmmeters)
        self.ELEMENT_WATTMETER_OFFSET = self.ELEMENT_AMMETER_OFFSET + len(self.ammeters)
        self.ELEMENT_NOT_OFFSET = self.ELEMENT_WATTMETER_OFFSET + len(self.wattmeters)
        self.ELEMENT_AND_OFFSET = self.ELEMENT_NOT_OFFSET + len(self.nots)
        self.ELEMENT_OR_OFFSET = self.ELEMENT_AND_OFFSET + len(self.ands)
        self.ELEMENT_NAND_OFFSET = self.ELEMENT_OR_OFFSET + len(self.ors)
        self.ELEMENT_NOR_OFFSET = self.ELEMENT_NAND_OFFSET + len(self.nands)
        self.ELEMENT_XOR_OFFSET = self.ELEMENT_NOR_OFFSET + len(self.nors)
        self.ELEMENT_XNOR_OFFSET = self.ELEMENT_XOR_OFFSET + len(self.xors)
        self.ELEMENT_DFF_OFFSET = self.ELEMENT_XNOR_OFFSET + len(self.xnors)
        self.ELEMENT_VSAT_OFFSET = self.ELEMENT_DFF_OFFSET + 2 * len(self.dffs)
        self.ELEMENT_ADD_OFFSET = self.ELEMENT_VSAT_OFFSET + len(self.vsats)
        self.ELEMENT_SUB_OFFSET = self.ELEMENT_ADD_OFFSET + len(self.adders)
        self.ELEMENT_MUL_OFFSET = self.ELEMENT_SUB_OFFSET + len(self.subtractors)
        self.ELEMENT_DIV_OFFSET = self.ELEMENT_MUL_OFFSET + len(self.multipliers)
        self.ELEMENT_GAIN_OFFSET = self.ELEMENT_DIV_OFFSET + len(self.dividers)
        self.ELEMENT_ABS_OFFSET = self.ELEMENT_GAIN_OFFSET + len(self.gains)
        self.ELEMENT_VCVS_OFFSET = self.ELEMENT_ABS_OFFSET + len(self.absvals)
        self.ELEMENT_CCCS_OFFSET = self.ELEMENT_VCVS_OFFSET + len(self.vcvss)
        self.ELEMENT_CCVS_OFFSET = self.ELEMENT_CCCS_OFFSET + len(self.cccss)
        self.ELEMENT_OPAMP_OFFSET = self.ELEMENT_CCVS_OFFSET + 2 * len(self.ccvss)
        self.ELEMENT_ADC_OFFSET = self.ELEMENT_OPAMP_OFFSET + len(self.opamps)
        self.ELEMENT_DAC_OFFSET = self.ELEMENT_ADC_OFFSET + len(self.adcs)
        self.ELEMENT_SAH_OFFSET = self.ELEMENT_DAC_OFFSET + len(self.dacs)
        self.ELEMENT_PWM_OFFSET = self.ELEMENT_SAH_OFFSET + len(self.sandhs)
        self.ELEMENT_INTEGRATOR_OFFSET = self.ELEMENT_PWM_OFFSET + len(self.pwms)
        self.ELEMENT_DIFFERENTIATOR_OFFSET = self.ELEMENT_INTEGRATOR_OFFSET + len(
            self.integrators
        )
        self.ELEMENT_LPF_OFFSET = self.ELEMENT_DIFFERENTIATOR_OFFSET + len(
            self.differentiators
        )
        self.ELEMENT_HPF_OFFSET = self.ELEMENT_LPF_OFFSET + len(self.lowpasses)
        self.ELEMENT_PID_OFFSET = self.ELEMENT_HPF_OFFSET + len(self.highpasses)
        self.ELEMENT_LUT_OFFSET = self.ELEMENT_PID_OFFSET + len(self.pids)
        self.ELEMENT_GRT_OFFSET = self.ELEMENT_LUT_OFFSET + len(self.luts)
        self.ELEMENT_TPTZ_OFFSET = self.ELEMENT_GRT_OFFSET + len(self.grts)
        self.ELEMENT_TRAN_OFFSET = self.ELEMENT_TPTZ_OFFSET + len(self.tptzs)

        self.MATRIX_OFFSET = (
                len(self.dcsources)
                + len(self.acsources)
                + len(self.squarewaves)
                + len(self.sawwaves)
                + len(self.trianglewaves)
                + len(self.constants)
                + len(self.rails)
                + len(self.ohmmeters)
                + len(self.ammeters)
                + len(self.wattmeters)
                + len(self.nots)
                + len(self.ands)
                + len(self.ors)
                + len(self.nands)
                + len(self.nors)
                + len(self.xors)
                + len(self.xnors)
                + (2 * len(self.dffs))
                + len(self.vsats)
                + len(self.adders)
                + len(self.subtractors)
                + len(self.multipliers)
                + len(self.dividers)
                + len(self.gains)
                + len(self.absvals)
                + len(self.vcvss)
                + len(self.cccss)
                + (2 * len(self.ccvss))
                + len(self.opamps)
                + len(self.adcs)
                + len(self.dacs)
                + len(self.sandhs)
                + len(self.pwms)
                + len(self.integrators)
                + len(self.differentiators)
                + len(self.lowpasses)
                + len(self.highpasses)
                + len(self.pids)
                + len(self.luts)
                + len(self.grts)
                + len(self.tptzs)
                + len(self.transformers)
        )

        self.Params.SystemFlags.FlagSimulating = True

    def map_node(self, node_id: int) -> int:
        temp: int = -1
        output: int = -1

        for i in range(0, len(self.node_manager.active_nodes)):
            if node_id == self.node_manager.active_nodes[i]:
                temp = self.nodes[self.node_manager.active_nodes[i]].SimulationId
                if temp > -1 and temp < len(self.node_manager.active_nodes):
                    output = temp
                    break
                None
            None
        None

        if len(self.node_manager.active_nodes) > 0 and node_id != -1:
            for i in range(0, len(self.node_manager.unique_nodes)):
                if self.node_manager.unique_nodes[i].IsFound(node_id):
                    temp = self.check_node(
                        self.node_manager.unique_nodes[i].GetLowestId(node_id)
                    )
                    if temp != -1:
                        output = temp
                        break
                    None
                None
            None
        None

        return output

    None

    def check_node(self, node_id: int) -> int:
        modified_keys: int = -1
        for i in range(0, len(self.node_manager.active_nodes)):
            if self.node_manager.active_nodes[i] == node_id:
                modified_keys = i
                break
            None
        None
        return modified_keys

    None

    def stamp_resistor(self, n1: int, n2: int, resistance: float) -> None:
        node_1: int = self.map_node(n1)
        node_2: int = self.map_node(n2)
        if node_1 != -1:
            self.matrix_a[node_1][node_1] += 1.0 / resistance
        None
        if node_2 != -1:
            self.matrix_a[node_2][node_2] += 1.0 / resistance
        None
        if node_1 != -1 and node_2 != -1:
            self.matrix_a[node_1][node_2] += -1.0 / resistance
            self.matrix_a[node_2][node_1] += -1.0 / resistance
        None

    None

    def stamp_node(self, n1: int, resistance: float) -> None:
        node_1 = self.map_node(n1)
        if node_1 != -1:
            self.matrix_a[node_1][node_1] += 1.0 / resistance
        None

    None

    def stamp_across_nodes(self, n1: int, n2: int, resistance: float) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        if node_1 != -1 and node_2 != -1:
            self.matrix_a[node_1][node_2] += 1.0 / resistance
        None

    None

    def stamp_voltage(self, n1: int, n2: int, voltage: float, id: int) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        node_offset: int = self.node_size
        if node_1 != -1:
            self.matrix_a[node_1][node_offset + id] = 1
            self.matrix_a[node_offset + id][node_1] = 1
            self.matrix_a[node_1][node_1] += 1.0 / self.Params.SystemSettings.R_MAX
        None
        if node_2 != -1:
            self.matrix_a[node_2][node_offset + id] = -1
            self.matrix_a[node_offset + id][node_2] = -1
            self.matrix_a[node_2][node_2] += 1.0 / self.Params.SystemSettings.R_MAX
        None
        if node_1 != -1 and node_2 != -1:
            self.matrix_a[node_1][node_2] += -1.0 / self.Params.SystemSettings.R_MAX
            self.matrix_a[node_2][node_1] += -1.0 / self.Params.SystemSettings.R_MAX
        None
        self.matrix_z[node_offset + id][0] += voltage

    None
    
    def stamp_gate1(self, n1: int, par_vout_par_vin1: float, v_eq: float, id: int) -> None:
    	node_1 = self.map_node(n1)
    	node_offset = self.node_size
    	if node_1 != -1:
    		self.matrix_a[node_1][node_offset + id] = 1
    		self.matrix_a[node_offset + id][node_1] = -1
    		self.matrix_a[node_offset + id][node_1 + 1] = par_vout_par_vin1
    		self.matrix_a[node_1][node_1] += 1.0 / self.Params.SystemSettings.R_MAX
    	None
    	self.matrix_z[node_offset + id][0] += v_eq
    None
    
    def stamp_gate2(self, n1: int, par_vout_par_vin1: float, par_vout_par_vin2: float, v_eq: float, id: int) -> None:
    	node_1 = self.map_node(n1)
    	node_offset = self.node_size
    	if node_1 != -1:
    		self.matrix_a[node_1][node_offset+ id] = 1
    		self.matrix_a[node_offset + id][node_1] = -1
    		self.matrix_a[node_offset + id][node_1 + 1] = par_vout_par_vin1
    		self.matrix_a[node_offset + id][node_1 + 2] = par_vout_par_vin2
    		self.matrix_a[node_1][node_1] += 1.0 / self.Params.SystemSettings.R_MAX
    	None
    	self.matrix_z[node_offset + id][0] += v_eq
    None

    def stamp_current(self, n1: int, n2: int, current: float) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        if node_1 != -1:
            self.matrix_z[node_1][0] += current
        None
        if node_2 != -1:
            self.matrix_z[node_2][0] += -current
        None

    None

    def stamp_capacitor(
            self, n1: int, n2: int, transient_resistance: float, transient_ieq: float
    ) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        if node_1 != -1:
            self.matrix_a[node_1][node_1] += 1.0 / transient_resistance
            self.matrix_z[node_1][0] += -transient_ieq
        None
        if node_2 != -1:
            self.matrix_a[node_2][node_2] += 1.0 / transient_resistance
            self.matrix_z[node_2][0] += transient_ieq
        None
        if node_1 != -1 and node_2 != -1:
            self.matrix_a[node_1][node_2] += -1.0 / transient_resistance
            self.matrix_a[node_2][node_1] += -1.0 / transient_resistance
        None

    None

    def stamp_inductor(
            self, n1: int, n2: int, transient_resistance: float, transient_ieq: float
    ) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        if node_1 != -1:
            self.matrix_a[node_1][node_1] += 1.0 / transient_resistance
            self.matrix_z[node_1][0] += -transient_ieq
        None
        if node_2 != -1:
            self.matrix_a[node_2][node_2] += 1.0 / transient_resistance
            self.matrix_z[node_2][0] += transient_ieq
        None
        if node_1 != -1 and node_2 != -1:
            self.matrix_a[node_1][node_2] += -1.0 / transient_resistance
            self.matrix_a[node_2][node_1] += -1.0 / transient_resistance
        None

    None
    
    def stamp_ccvs(
            self, n1: int, n2: int, n3: int, n4: int, gain: float, id: int
    ) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        node_3 = self.map_node(n3)
        node_4 = self.map_node(n4)
        node_offset: int = self.node_size
        if node_1 != -1:
            self.matrix_a[node_offset + id][node_1] = 1
            self.matrix_a[node_1][node_offset + id] = 1
        None
        if node_2 != -1:
            self.matrix_a[node_offset + id + 1][node_2] = 1
            self.matrix_a[node_2][node_offset + id + 1] = 1
        None
        if node_3 != -1:
            self.matrix_a[node_offset + id + 1][node_3] = -1
            self.matrix_a[node_3][node_offset + id + 1] = -1
        None
        if node_4 != -1:
            self.matrix_a[node_offset + id][node_4] = -1
            self.matrix_a[node_4][node_offset + id] = -1
        None
        self.matrix_a[node_offset + id + 1][node_offset + id] = -gain

    None

    def stamp_vccs(self, n1: int, n2: int, n3: int, n4: int, gain: float) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        node_3 = self.map_node(n3)
        node_4 = self.map_node(n4)
        if node_1 != -1 and node_2 != -1:
            self.matrix_a[node_2][node_1] += gain
        None
        if node_2 != -1 and node_4 != -1:
            self.matrix_a[node_2][node_4] += -gain
        None
        if node_1 != -1 and node_3 != -1:
            self.matrix_a[node_3][node_1] += -gain
        None
        if node_3 != -1 and node_4 != -1:
            self.matrix_a[node_3][node_4] += gain
        None

    None

    def stamp_cccs(
            self, n1: int, n2: int, n3: int, n4: int, gain: float, id: int
    ) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        node_3 = self.map_node(n3)
        node_4 = self.map_node(n4)
        node_offset: int = self.node_size
        if node_1 != -1:
            self.matrix_a[node_offset + id][node_1] = 1
            self.matrix_a[node_1][node_offset + id] = 1
        None
        if node_2 != -1:
            self.matrix_a[node_2][node_offset + id] = gain
        None
        if node_3 != -1:
            self.matrix_a[node_3][node_offset + id] = -gain
        None
        if node_4 != -1:
            self.matrix_a[node_offset + id][node_4] = -1
            self.matrix_a[node_4][node_offset + id] = -1
        None

    None

    def stamp_vcvs(
            self, n1: int, n2: int, n3: int, n4: int, gain: float, id: int
    ) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        node_3 = self.map_node(n3)
        node_4 = self.map_node(n4)
        node_offset: int = self.node_size
        if node_1 != -1:
            self.matrix_a[node_offset + id][node_1] = -gain
        None
        if node_2 != -1:
            self.matrix_a[node_offset + id][node_2] = 1
            self.matrix_a[node_2][node_offset + id] = 1
        None
        if node_3 != -1:
            self.matrix_a[node_offset + id][node_3] = -1
            self.matrix_a[node_3][node_offset + id] = -1
        None
        if node_4 != -1:
            self.matrix_a[node_offset + id][node_4] = gain
        None

    None

    def stamp_ideal_opamp(self, n1: int, n2: int, n3: int, id: int) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        node_3 = self.map_node(n3)
        node_offset: int = self.node_size
        if node_1 != -1:
            self.matrix_a[node_offset + id][node_1] = 1
        None
        if node_2 != -1:
            self.matrix_a[node_offset + id][node_2] = -1
        None
        if node_3 != -1:
            self.matrix_a[node_3][node_offset + id] = 1
        None
        self.matrix_a[node_offset + id][node_offset + id] += 1e-9

    None

    def stamp_transformer(
            self, n1: int, n2: int, n3: int, n4: int, gain: float, id: int
    ) -> None:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        node_3 = self.map_node(n3)
        node_4 = self.map_node(n4)
        node_offset: int = self.node_size
        if node_1 != -1:
            self.matrix_a[node_offset + id][node_1] = -1
            self.matrix_a[node_1][node_offset + id] = 1
        None
        if node_2 != -1:
            self.matrix_a[node_offset + id][node_2] = 1
            self.matrix_a[node_2][node_offset + id] = -1
        None
        if node_3 != -1:
            self.matrix_a[node_offset + id][node_3] = gain
            self.matrix_a[node_3][node_offset + id] = -gain
        None
        if node_4 != -1:
            self.matrix_a[node_offset + id][node_4] = -gain
            self.matrix_a[node_4][node_offset + id] = gain
        None

    None

    def get_voltage(self, n1: int, n2: int) -> float:
        node_1 = self.map_node(n1)
        node_2 = self.map_node(n2)
        node_3 = 0
        v_node_1 = 0
        v_node_2 = 0
        v_node_ground = 0
        if node_1 != -1 and node_1 < len(self.matrix_x):
            v_node_1 = self.matrix_x[node_1][0]
        None
        if node_2 != -1 and node_2 < len(self.matrix_x):
            v_node_2 = self.matrix_x[node_2][0]
        None
        
        if len(self.grounds) > 0:
            node_3 = self.map_node(self.grounds[0].GetNode(0))   
            if node_3 != -1 and node_3 < len(self.matrix_x):
                v_node_ground = self.matrix_x[node_3][0]
            None
        None
        return v_node_1 - v_node_2 - v_node_ground

    None        
        
    def simulate(self):
        if self.Params.SystemFlags.FlagSimulating:
            if self.simulation_step == 0:
                self.solve()
                if self.continue_solving:
                    self.solve()
                None
            else:
                if (not self.continue_solving):
                    self.update_reactive_elements()
    
                    if (self.iterator >= self.Params.SystemSettings.ITL4
                            or self.Params.SystemVariables.IsSingular
                            or self.simulation_time >= self.SIMULATION_MAX_TIME
                    ):
                        if self.iterator >= self.Params.SystemSettings.ITL4:
                            self.Params.SystemFlags.FlagSimulating = False
                            print("Error: Convergence Error")
                        elif self.Params.SystemVariables.IsSingular:
                            self.Params.SystemFlags.FlagSimulating = False
                            print("Error: Singular Matrix")
                        elif self.simulation_time >= self.SIMULATION_MAX_TIME:
                            self.Params.SystemFlags.FlagSimulating = False
                            print("Error: End Of Time")
                        None
                    else:
                        self.continue_solving = True
                        self.iterator = 0
                        self.update_vir()
                        self.led_check()
                
                        self.system_ready = True
                        self.simulation_time += self.time_step
                        self.simulation_step = 0

            self.update_elements()
        None
    
    def solve(self):
        if self.continue_solving and self.iterator < self.Params.SystemSettings.ITL4:
            self.continue_solving = False
            if self.first_matrix_build:
                self.matrix_a = self.matrix(
                    self.node_size + self.MATRIX_OFFSET,
                    self.node_size + self.MATRIX_OFFSET,
                )
                self.matrix_z = self.matrix(self.node_size + self.MATRIX_OFFSET, 1)
                self.first_matrix_build = False
            else:
                for i in range(0, len(self.matrix_z)):
                    self.matrix_z[i][0] = 0
                None

                for i in range(0, len(self.matrix_a)):
                    for j in range(0, len(self.matrix_a[0])):
                        self.matrix_a[i][j] = 0
                    None
                None
            None
            self.matrix_a = self.set_matrix_diagonal(
                self.matrix_a, self.Params.SystemSettings.R_NODE_TO_GROUND, self.node_size
            )
            self.stamp_elements()
            if self.first_x_matrix_copy:
                if not self.first_x_matrix_solution:
                    self.matrix_x_copy = self.matrix(
                        self.node_size + self.MATRIX_OFFSET, 1
                    )
                else:
                    self.matrix_x_copy = self.clone(self.matrix_x)
                    self.first_x_matrix_copy = False
                None
            else:
                for i in range(0, len(self.matrix_x)):
                    self.matrix_x_copy[i][0] = self.matrix_x[i][0]
                None
            None

            if np.linalg.det(self.matrix_a) == 0:
                self.matrix_x = np.linalg.pinv(self.matrix_a).dot(self.matrix_z)
            else:
                self.matrix_x = np.linalg.solve(self.matrix_a, self.matrix_z)
            
            for i in range(0, len(self.matrix_x)):
                if math.isnan(self.matrix_x[i][0]):
                    self.continue_solving = False
                    self.iterator = self.Params.SystemSettings.ITL4
                    self.matrix_x[i][0] = 0
                None
            None

            if not self.first_x_matrix_solution:
                self.first_x_matrix_solution = True
            None

            if self.Params.SystemVariables.IsSingular:
                self.iterator = 0
                self.continue_solving = False
                self.iterator = self.Params.SystemSettings.ITL4
                self.simulation_step += 1
            None

            self.solutions_ready = True
            self.non_linear_update()
            self.convergence_check()
            self.iterator += 1

            if not self.continue_solving:
                self.simulation_step += 1
            None

        else:
            self.simulation_step += 1
        None

    None

    def update_vir(self):
        self.update_scopes()

    None

    def update_scopes(self):
        met_max: int = Utils.Utils.meter_max(self)
        iteration_size: int = met_max
        v_side_1: float = 0
        v_side_2: float = 0
        for i in range(0, iteration_size):
            if i < len(self.voltmeters):
                self.voltmeters[i].push_voltage(
                    self.get_voltage(
                        self.voltmeters[i].GetNode(0), self.voltmeters[i].GetNode(1)
                    )
                )
            None
            if i < len(self.ammeters):
                if self.ammeters[i].get_simulation_index() < len(self.matrix_x):
                    self.ammeters[i].push_current(
                        self.matrix_x[self.ammeters[i].get_simulation_index()][0]
                    )
                None
            None
            if i < len(self.ohmmeters):
                if self.ohmmeters[i].get_simulation_index() < len(self.matrix_x):
                    self.ohmmeters[i].push_voltage_current(
                        self.get_voltage(
                            self.ohmmeters[i].GetNode(0), self.ohmmeters[i].GetNode(1)
                        ),
                        self.matrix_x[self.ohmmeters[i].get_simulation_index()][0],
                    )
                None
            None
            if i < len(self.wattmeters):
                if self.wattmeters[i].get_simulation_index() < len(self.matrix_x):
                    v_side_1 = abs(self.get_voltage(self.wattmeters[i].GetNode(0), -1))
                    v_side_2 = abs(self.get_voltage(self.wattmeters[i].GetNode(1), -1))
                    self.wattmeters[i].push_voltage(v_side_1, v_side_2)
                None
            None
        None

    None

    def led_check(self):
        for i in range(0, len(self.leds)):
            self.leds[i].turn_on_check()
        None

    None

    def non_linear_update(self):
        for i in range(0, len(self.diodes)):
            self.diodes[i].update()
        None
        for i in range(0, len(self.leds)):
            self.leds[i].update()
        None
        for i in range(0, len(self.zeners)):
            self.zeners[i].update()
        None
        for i in range(0, len(self.nmosfets)):
            self.nmosfets[i].update()
        None
        for i in range(0, len(self.pmosfets)):
            self.pmosfets[i].update()
        None
        for i in range(0, len(self.npns)):
            self.npns[i].update()
        None
        for i in range(0, len(self.pnps)):
            self.pnps[i].update()
        None
        for i in range(0, len(self.nots)):
            self.nots[i].update()
        None
        for i in range(0, len(self.ands)):
            self.ands[i].update()
        None
        for i in range(0, len(self.ors)):
            self.ors[i].update()
        None
        for i in range(0, len(self.nands)):
            self.nands[i].update()
        None
        for i in range(0, len(self.nors)):
            self.nors[i].update()
        None
        for i in range(0, len(self.xors)):
            self.xors[i].update()
        None
        for i in range(0, len(self.xnors)):
            self.xnors[i].update()
        None
    None

    def update_reactive_elements(self):
        for i in range(0, len(self.capacitors)):
            self.capacitors[i].update_capacitor()
        None
        for i in range(0, len(self.inductors)):
            self.inductors[i].update_inductor()
        None
        for i in range(0, len(self.relays)):
            self.relays[i].update_relay()
        None
        for i in range(0, len(self.vccas)):
            self.vccas[i].update_vcca()
        None
        for i in range(0, len(self.vcls)):
            self.vcls[i].update_vcl()
        None

    None

    def convergence_check(self):
        if self.node_size > 0 and len(self.matrix_x) == len(self.matrix_x_copy):
            if self.first_error_check:
                self.max_voltage_error = self.matrix(
                    len(self.matrix_x), len(self.matrix_x[0])
                )
                self.max_current_error = self.matrix(
                    len(self.matrix_x), len(self.matrix_x[0])
                )
                self.first_error_check = False
            else:
                for i in range(0, len(self.max_voltage_error)):
                    for j in range(0, len(self.max_voltage_error[0])):
                        self.max_voltage_error[i][j] = 0
                        self.max_current_error[i][j] = 0
                    None
                None
            None

            self.voltage_error_locked = False
            self.current_error_locked = False
            self.voltage_converged = False
            self.current_converged = False

            for i in range(0, len(self.matrix_x)):
                if i < self.node_size:
                    self.max_voltage_error[i][0] = max(
                        max(abs(self.matrix_x[i][0]), abs(self.matrix_x_copy[i][0])),
                        self.Params.SystemSettings.VNTOL,
                    )
                else:
                    self.max_current_error[i][0] = max(
                        max(abs(self.matrix_x[i][0]), abs(self.matrix_x_copy[i][0])),
                        self.Params.SystemSettings.ABSTOL,
                    )
                None
            None

            for i in range(0, len(self.matrix_x)):
                if i < self.node_size:
                    if (
                            abs(self.matrix_x[i][0] - self.matrix_x_copy[i][0])
                            < self.Params.SystemSettings.RELTOL * self.max_voltage_error[i][0]
                            + self.Params.SystemSettings.VNTOL
                    ):
                        if not self.voltage_error_locked:
                            self.voltage_converged = True
                        None
                    else:
                        self.voltage_error_locked = True
                        self.voltage_converged = False
                    None
                else:
                    if (
                            abs(self.matrix_x[i][0] - self.matrix_x_copy[i][0])
                            < self.Params.SystemSettings.RELTOL * self.max_current_error[i][0]
                            + self.Params.SystemSettings.ABSTOL
                    ):
                        if not self.current_error_locked:
                            self.current_converged = True
                        None
                    else:
                        self.current_error_locked = True
                        self.current_converged = False
                    None
                None
            None

            if len(self.matrix_x) - self.node_size <= 0:
                self.current_converged = True
            None

            if not self.voltage_converged or not self.current_converged:
                self.continue_solving = True
            None

        None

    None

    def ready(self):
        return not self.continue_solving

    None

    def set_matrix_diagonal(self, matrix, value, n):
        None
        for i in range(0, n):
            matrix[i][i] = value
        None

        return matrix

    def matrix(self, rows: int, cols: int):
        None
        return np.zeros((rows, cols), dtype=np.float64)

    def vector(self, size: int):
        None
        output = np.zeros(size, dtype=int)
        for i in range(0, size):
            output[i] = i
        None

        return output

    def clone(self, inp):
        None
        if (np.shape(inp)[0] > 0 and np.shape(inp)[1] > 0):
            output = np.zeros((len(inp), len(inp[0])), dtype=np.float64)
            for i in range(0, len(output)):
                for j in range(0, len(output[0])):
                    output[i][j] = inp[i][j]
                None
            None

            return output
        else:
            return np.zeros((1, 1), dtype=np.float64)

    def IndexOfResistor(self, Designator: str):
        for i in range(0, len(self.resistors)):
            if self.resistors[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfCapacitor(self, Designator: str):
        for i in range(0, len(self.capacitors)):
            if self.capacitors[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfInductor(self, Designator: str):
        for i in range(0, len(self.inductors)):
            if self.inductors[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfGround(self, Designator: str):
        for i in range(0, len(self.grounds)):
            if self.grounds[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None
    
    def IndexOfBridge(self, Designator: str):
        for i in range(0, len(self.bridges)):
            if self.bridges[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfDCSource(self, Designator: str):
        for i in range(0, len(self.dcsources)):
            if self.dcsources[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfDCCurrent(self, Designator: str):
        for i in range(0, len(self.dccurrents)):
            if self.dccurrents[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfACSource(self, Designator: str):
        for i in range(0, len(self.acsources)):
            if self.acsources[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfACCurrent(self, Designator: str):
        for i in range(0, len(self.accurrents)):
            if self.accurrents[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfSquareWave(self, Designator: str):
        for i in range(0, len(self.squarewaves)):
            if self.squarewaves[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfSawWave(self, Designator: str):
        for i in range(0, len(self.sawwaves)):
            if self.sawwaves[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfTriangleWave(self, Designator: str):
        for i in range(0, len(self.trianglewaves)):
            if self.trianglewaves[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfConstant(self, Designator: str):
        for i in range(0, len(self.constants)):
            if self.constants[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfNet(self, Designator: str):
        for i in range(0, len(self.nets)):
            if self.nets[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfNote(self, Designator: str):
        for i in range(0, len(self.notes)):
            if self.notes[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfRail(self, Designator: str):
        for i in range(0, len(self.rails)):
            if self.rails[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfVoltMeter(self, Designator: str):
        for i in range(0, len(self.voltmeters)):
            if self.voltmeters[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfOhmMeter(self, Designator: str):
        for i in range(0, len(self.ohmmeters)):
            if self.ohmmeters[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfAmMeter(self, Designator: str):
        for i in range(0, len(self.ammeters)):
            if self.ammeters[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfWattMeter(self, Designator: str):
        for i in range(0, len(self.wattmeters)):
            if self.wattmeters[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfFuse(self, Designator: str):
        for i in range(0, len(self.fuses)):
            if self.fuses[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfSinglePoleSingleThrow(self, Designator: str):
        for i in range(0, len(self.spsts)):
            if self.spsts[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfSinglePoleDoubleThrow(self, Designator: str):
        for i in range(0, len(self.spdts)):
            if self.spdts[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfNOTGate(self, Designator: str):
        for i in range(0, len(self.nots)):
            if self.nots[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfDiode(self, Designator: str):
        for i in range(0, len(self.diodes)):
            if self.diodes[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfLightEmittingDiode(self, Designator: str):
        for i in range(0, len(self.leds)):
            if self.leds[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfZenerDiode(self, Designator: str):
        for i in range(0, len(self.zeners)):
            if self.zeners[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfPotentiometer(self, Designator: str):
        for i in range(0, len(self.potentiometers)):
            if self.potentiometers[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfANDGate(self, Designator: str):
        for i in range(0, len(self.ands)):
            if self.ands[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfORGate(self, Designator: str):
        for i in range(0, len(self.ors)):
            if self.ors[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfNANDGate(self, Designator: str):
        for i in range(0, len(self.nands)):
            if self.nands[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfNORGate(self, Designator: str):
        for i in range(0, len(self.nors)):
            if self.nors[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfXORGate(self, Designator: str):
        for i in range(0, len(self.xors)):
            if self.xors[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfXNORGate(self, Designator: str):
        for i in range(0, len(self.xnors)):
            if self.xnors[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfDFlipFlop(self, Designator: str):
        for i in range(0, len(self.dffs)):
            if self.dffs[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfVoltageSaturation(self, Designator: str):
        for i in range(0, len(self.vsats)):
            if self.vsats[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfAdder(self, Designator: str):
        for i in range(0, len(self.adders)):
            if self.adders[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfSubtractor(self, Designator: str):
        for i in range(0, len(self.subtractors)):
            if self.subtractors[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfMultiplier(self, Designator: str):
        for i in range(0, len(self.multipliers)):
            if self.multipliers[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfDivider(self, Designator: str):
        for i in range(0, len(self.dividers)):
            if self.dividers[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfGainBlock(self, Designator: str):
        for i in range(0, len(self.gains)):
            if self.gains[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfAbsoluteValue(self, Designator: str):
        for i in range(0, len(self.absvals)):
            if self.absvals[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfVoltageControlledSwitch(self, Designator: str):
        for i in range(0, len(self.vcsws)):
            if self.vcsws[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfVoltageControlledVoltageSource(self, Designator: str):
        for i in range(0, len(self.vcvss)):
            if self.vcvss[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfVoltageControlledCurrentSource(self, Designator: str):
        for i in range(0, len(self.vccss)):
            if self.vccss[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfCurrentControlledCurrentSource(self, Designator: str):
        for i in range(0, len(self.cccss)):
            if self.cccss[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfCurrentControlledVoltageSource(self, Designator: str):
        for i in range(0, len(self.ccvss)):
            if self.ccvss[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfOperationalAmplifier(self, Designator: str):
        for i in range(0, len(self.opamps)):
            if self.opamps[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfNChannelMOSFET(self, Designator: str):
        for i in range(0, len(self.nmosfets)):
            if self.nmosfets[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfPChannelMOSFET(self, Designator: str):
        for i in range(0, len(self.pmosfets)):
            if self.pmosfets[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfNPNBipolarJunctionTransistor(self, Designator: str):
        for i in range(0, len(self.npns)):
            if self.npns[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfPNPBipolarJunctionTransistor(self, Designator: str):
        for i in range(0, len(self.pnps)):
            if self.pnps[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfADCModule(self, Designator: str):
        for i in range(0, len(self.adcs)):
            if self.adcs[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfDACModule(self, Designator: str):
        for i in range(0, len(self.dacs)):
            if self.dacs[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfSampleAndHold(self, Designator: str):
        for i in range(0, len(self.sandhs)):
            if self.sandhs[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfPulseWidthModulator(self, Designator: str):
        for i in range(0, len(self.pwms)):
            if self.pwms[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfIntegratorModule(self, Designator: str):
        for i in range(0, len(self.integrators)):
            if self.integrators[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfDifferentiatorModule(self, Designator: str):
        for i in range(0, len(self.differentiators)):
            if self.differentiators[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfLowPassFilter(self, Designator: str):
        for i in range(0, len(self.lowpasses)):
            if self.lowpasses[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfHighPassFilter(self, Designator: str):
        for i in range(0, len(self.highpasses)):
            if self.highpasses[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfRelay(self, Designator: str):
        for i in range(0, len(self.relays)):
            if self.relays[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfPIDModule(self, Designator: str):
        for i in range(0, len(self.pids)):
            if self.pids[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfLookUpTable(self, Designator: str):
        for i in range(0, len(self.luts)):
            if self.luts[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfVoltageControlledResistor(self, Designator: str):
        for i in range(0, len(self.vcrs)):
            if self.vcrs[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfVoltageControlledCapacitor(self, Designator: str):
        for i in range(0, len(self.vccas)):
            if self.vccas[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfVoltageControlledInductor(self, Designator: str):
        for i in range(0, len(self.vcls)):
            if self.vcls[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfGreaterThan(self, Designator: str):
        for i in range(0, len(self.grts)):
            if self.grts[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfTPTZModule(self, Designator: str):
        for i in range(0, len(self.tptzs)):
            if self.tptzs[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None

    def IndexOfTransformer(self, Designator: str):
        for i in range(0, len(self.transformers)):
            if self.transformers[i].GetDesignator().strip() == Designator.strip():
                return i
            None
        None
        raise RuntimeError("Element not found.")

    None