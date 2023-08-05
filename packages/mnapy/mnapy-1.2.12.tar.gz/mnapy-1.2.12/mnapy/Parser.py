import re
from typing import List

from mnapy import KeyPair
from mnapy import Limit


class Parser:
    def __init__(self) -> None:
        None

    @staticmethod
    def ParseReferenceId(ReferenceID: str) -> str:
        return Parser.FindFirstMatch(ReferenceID, '"ref_id":(\d*)').strip()

    @staticmethod
    def ParseTag(Property: str) -> str:
        return Parser.FindFirstMatch(Property, '"tag":"(\w*)"').strip()

    @staticmethod
    def ParseOptionData(Property: str, Option: str) -> KeyPair.KeyPair:
        return KeyPair.KeyPair(
            Option, Parser.FindFirstMatch(Property, '"' + Option + '":(\d*)').strip()
        )

    @staticmethod
    def ParseOptions(Property: str) -> str:
        return Parser.FindFirstMatch(Property, '"options":\["(\w*|\d*)"\]').strip()

    @staticmethod
    def ParseOptionLimits(Property: str, Option: str) -> Limit.Limit:
        Output: Limit.Limit = Limit.Limit(Option, -1, -1)
        Match: str = Parser.FindFirstMatch(
            Property, '"' + Option + r"\":\[(.*)\]"
        ).strip()

        MinMax: List[str] = Match.split(",")
        Min: float = -1
        Max: float = -1

        if len(MinMax) > 1:
            Min = float(MinMax[0])
            Max = float(MinMax[1])

        Output.Min = Min
        Output.Max = Max

        return Output

    @staticmethod
    def ParseWireId(Property: str) -> int:
        if len(Property) > -1:
            return int(Property[0])
        else:
            return -1

    @staticmethod
    def ParseWireAnchorPoint(Property: str) -> int:
        if len(Property) > 1:
            return int(Property[1])
        else:
            return -1

    @staticmethod
    def ParseWireLinkage(Property: str) -> int:
        if len(Property) > 2:
            return int(Property[2])
        else:
            return -1

    @staticmethod
    def ParseWires(Wires: str) -> List[str]:
        return Parser.FindAllMatches(
            Wires, '"wire_id":(\d*),"anchor_point":(\d*),"linkage":(\d*)'
        )

    @staticmethod
    def FindFirstMatch(Text: str, Regex: str) -> str:
        out = re.findall(Regex, Text)

        if len(out) > 0:
            return out[0]
        else:
            return ""
        None

    @staticmethod
    def FindAllMatches(Text: str, Regex: str) -> List[str]:
        Data = re.findall(Regex, Text)

        if len(Data) > 0:
            return Data
        else:
            return [""]
