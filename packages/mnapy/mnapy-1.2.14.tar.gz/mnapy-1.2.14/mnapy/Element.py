from typing import List

from mnapy import KeyPair
from mnapy import Limit
from mnapy import Parser
from mnapy import Type
from mnapy import Utils


class Element:
    def __init__(self, Id: str, Property: str, Wires: str, context) -> None:
        self.Id = Parser.Parser.ParseReferenceId(Id)
        self.Property = Property.strip()
        self.Wires = Wires.strip()
        self.Tag = Parser.Parser.ParseTag(self.Property)
        self.Designator = self.Tag + self.Id
        self.Options = Parser.Parser.ParseOptions(self.Property).split(",")
        self.ElementType = Utils.Utils.GetElementType(self.Tag)
        self.context = context
        self.WireReferences: List[str] = Parser.Parser.ParseWires(self.Wires)
        self.Nodes = [-1, -1, -1, -1]
        self.Linkages = [-1, -1, -1, -1]
        self.OptionLimits = [
            Limit.Limit("", -1, -1),
            Limit.Limit("", -1, -1),
            Limit.Limit("", -1, -1),
            Limit.Limit("", -1, -1),
            Limit.Limit("", -1, -1),
            Limit.Limit("", -1, -1)
        ]

        self.OptionData = [
            KeyPair.KeyPair("", ""),
            KeyPair.KeyPair("", ""),
            KeyPair.KeyPair("", ""),
            KeyPair.KeyPair("", ""),
            KeyPair.KeyPair("", ""),
            KeyPair.KeyPair("", "")
        ]

        temp = -1

        for i in range(0, len(self.WireReferences)):
            temp = Parser.Parser.ParseWireAnchorPoint(self.WireReferences[i])
            if (temp > -1 and temp < len(self.Nodes)):
                self.Nodes[temp] = Parser.Parser.ParseWireId(self.WireReferences[i])
                self.Linkages[temp] = Parser.Parser.ParseWireLinkage(self.WireReferences[i])
            None

        for i in range(0, min(len(self.Options), len(self.OptionLimits))):
            self.OptionLimits[i] = Parser.Parser.ParseOptionLimits(self.Property, self.Options[i])
        None

        for i in range(0, min(len(self.Options), len(self.OptionData))):
            self.OptionData[i] = Parser.Parser.ParseOptionData(self.Property, self.Options[i])
        None

    def SetProperty(self, Option: str, Setter: str) -> None:
        index = -1

        for i in range(0, len(self.OptionData)):
            if (self.OptionData[i].key == Option):
                index = i
                break
            None
        None

        if (index != -1):
            var_type = Utils.Utils.GetDataType(Setter)
            if (var_type == self.OptionData[index].type):
                self.OptionData[index].data = Setter
            None
        None

    def GetProperty(self, Option: str) -> str:
        for i in range(0, len(self.OptionData)):
            if (self.OptionData[i].key.strip() == Option.strip()):
                return self.OptionData[i].data
            None
        None

        return Type.Type.TYPE_UNDEFINED

    def GetDesignator(self) -> str:
        return self.Designator

    def GetKeys(self):
        return self.Options

    def GetId(self):
        return self.Id

    def GetJsonProperty(self):
        return self.Property

    def GetJsonWire(self):
        return self.Wires

    def GetTag(self):
        return self.Tag

    def GetNodes(self):
        return self.Nodes

    def GetLinkages(self):
        return self.Linkages

    def GetElementType(self):
        return self.ElementType

    def ToString(self) -> str:
        return (str(self.Property) + ", " + str(self.Tag) + ", " + str(self.Designator) + ", " +
                str(self.Options) + ", " + str(self.ElementType))

    def Anchor(self) -> None:
        for i in range(0, len(self.Nodes)):
            for j in range(0, len(self.context.wires)):
                if (self.context.wires[j].GetId() == str(self.Nodes[i])):
                    self.Nodes[i] = self.context.wires[j].GetNodes()[self.Linkages[i]]
                    self.context.nodes[self.Nodes[i]].AddReference(Utils.Utils.ParseInt(self.Id),
                                                                   Utils.Utils.GetElementType(self.Tag))
                    break
                None
            None
        None

    None
