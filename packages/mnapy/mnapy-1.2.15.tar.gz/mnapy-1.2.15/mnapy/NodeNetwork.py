from typing import List


class NodeNetwork:
    def __init__(self, NodeA: int, NodeB: int) -> None:
        self.References = []
        self.Lowest = -1
        self.GeneralBooolean = False

        if NodeA != NodeB:
            self.References.append(NodeA)
            self.References.append(NodeB)
        else:
            self.References.append(NodeA)
        None

    def GetLowestId(self, Node: int) -> int:
        self.Lowest = self.FindLowestId()
        if self.IsFound(Node) and self.Lowest != -1:
            return self.Lowest
        else:
            return Node
        None

    def IsFound(self, Node: int) -> bool:
        self.GeneralBooolean = False

        for i in range(0, len(self.References)):
            if self.References[i] == Node:
                self.GeneralBooolean = True
                break
            None
        None

        return self.GeneralBooolean

    def GetReferences(self) -> List[int]:
        return self.References

    def AddReferences(self, Refs: List[int]) -> None:
        for i in range(0, len(Refs)):
            if not self.IsFound(Refs[i]):
                self.References.append(Refs[i])
            None
        None

    def IsConnected(self, Inp: List[int]):
        IsFound = False
        for i in range(0, len(Inp)):
            if self.IsFound(Inp[i]):
                IsFound = True
                break
            None
        None

        return IsFound

    def IsRemoved(self, Node: int) -> bool:
        return (
                (self.IsFound(Node) and Node != self.FindLowestId())
                or self.FindLowestId() == -1
                or Node == -1
        )

    def FindLowestId(self) -> int:
        Lowest = -1
        if len(self.References) > 0:
            Lowest = self.References[0]
        else:
            Lowest = -1
        None

        for i in range(1, len(self.References)):
            if self.References[i] < Lowest:
                Lowest = self.References[i]
            None
        None

        return Lowest
