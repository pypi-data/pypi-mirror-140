from typing import List

from mnapy import NodeReference


class Node:
    def __init__(self, context, Id: int = -1) -> None:
        self.Id = Id
        self.SimulationId = -1
        self.References: List[NodeReference.NodeReference] = []
        self.context = context

        None

    def ClearReferences(self) -> None:
        self.References.clear()
        self.context.node_manager.remove_node(self.Id)

    def AddReferenceList(
            self, ReferenceList: List[NodeReference.NodeReference]
    ) -> None:
        for i in range(0, len(ReferenceList)):
            self.AddReference(ReferenceList[i].Id, ReferenceList[i].Type)

    def AddReference(self, Id: int, Type: int) -> None:
        IsFound = False

        for i in range(0, len(self.References)):
            if self.References[i].Id == Id and self.References[i].Type == Type:
                IsFound = True
                break
            None
        None

        if not IsFound:
            self.References.append(NodeReference.NodeReference(Id, Type))
            if len(self.References) > 0:
                self.context.node_manager.add_node(self.Id)
                None
            None
        None

    def RemoveReference(self, Id: int, Type: int) -> None:
        if len(self.References) > 0:
            for i in range(0, len(self.References)):
                if self.References[i].Id == Id and self.References[i].Type == Type:
                    del self.References[i]
                    break
            None
        None

        if len(self.References) == 0:
            self.context.node_manager.remove_node(self.Id)
            None
        None

    def ContainsElementType(self, Type: int) -> bool:
        out = False

        for i in range(0, len(self.References)):
            if self.References[i].Type == Type:
                out = True
                break
            None
        None

        return out
