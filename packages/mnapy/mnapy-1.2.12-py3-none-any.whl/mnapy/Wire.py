from typing import List

from mnapy import Parser


class Wire:
    def __init__(self, Id: str = "", Nodes: str = "") -> None:
        self.Id = Parser.Parser.ParseReferenceId(Id)
        self.Nodes: List[int] = [-1, -1, -1, -1]

        SplitStr = Nodes.split(",")
        for i in range(0, len(SplitStr)):
            self.Nodes[i] = int(SplitStr[i].strip())
        None

    def GetId(self):
        return self.Id

    def GetNodes(self):
        return self.Nodes

    None
