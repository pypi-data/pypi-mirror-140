from typing import List

from mnapy import NodeNetwork


class NodeManager:
    def __init__(self, context):
        self.context = context
        self.active_nodes: List[int] = []
        self.unique_nodes: List[NodeNetwork.NodeNetwork] = []

    def clear_active_nodes(self) -> None:
        self.active_nodes.clear()

    def add_node(self, Id: int) -> None:
        if Id > -1 and Id < self.context.Params.SystemSettings.MAXNODES:
            if self.find_node(Id) == False:
                self.active_nodes.append(Id)

    def remove_node(self, Id: int) -> None:
        if Id > -1 and Id < self.context.Params.SystemSettings.MAXNODES:
            index = self.find_node_index(Id)
            if index > -1 and index < len(self.active_nodes):
                del self.active_nodes[index]

    def find_node(self, Id: int) -> bool:
        for i in range(0, len(self.active_nodes)):
            if self.active_nodes[i] == Id:
                return True

        return False

    def find_node_index(self, Id: int) -> int:
        for i in range(0, len(self.active_nodes)):
            if self.active_nodes[i] == Id:
                return i

        return -1

    def assign_node_simulation_ids(self) -> None:
        for i in range(0, len(self.active_nodes)):
            self.context.nodes[self.active_nodes[i]].SimulationId = i

    def generate_unique_nodes_list(self) -> None:
        self.unique_nodes.clear()

        for i in range(0, len(self.context.grounds)):
            self.unique_nodes.append(
                NodeNetwork.NodeNetwork(
                    self.context.grounds[i].GetNode(0),
                    self.context.grounds[i].GetNode(0),
                )
            )

        for i in range(0, len(self.context.ccvss)):
            self.unique_nodes.append(
                NodeNetwork.NodeNetwork(
                    self.context.ccvss[i].GetNode(3),
                    self.context.ccvss[i].GetNode(3),
                )
            )

        for i in range(0, len(self.context.vcvss)):
            self.unique_nodes.append(
                NodeNetwork.NodeNetwork(
                    self.context.vcvss[i].GetNode(3),
                    self.context.vcvss[i].GetNode(3),
                )
            )

        for i in range(0, len(self.context.vccss)):
            self.unique_nodes.append(
                NodeNetwork.NodeNetwork(
                    self.context.vccss[i].GetNode(3),
                    self.context.vccss[i].GetNode(3),
                )
            )

        for i in range(0, len(self.context.cccss)):
            self.unique_nodes.append(
                NodeNetwork.NodeNetwork(
                    self.context.cccss[i].GetNode(3),
                    self.context.cccss[i].GetNode(3),
                )
            )
                
        for i in range(0, len(self.unique_nodes)):
            for j in range(0, len(self.unique_nodes)):
                if i != j:
                    self.unique_nodes[i].AddReferences(
                        self.unique_nodes[j].GetReferences()
                    )
                    self.unique_nodes[j].AddReferences(
                        self.unique_nodes[i].GetReferences()
                    )

        net_list: List[int] = []

        for i in range(0, len(self.context.nets)):
            for j in range(0, len(self.context.nets)):
                if i != j:
                    if (
                            self.context.nets[i].Get_Name()
                            == self.context.nets[j].Get_Name()
                    ):
                        if not self.net_redundancy_check(
                                self.context.nets[i].GetNode(0),
                                self.context.nets[j].GetNode(0),
                                net_list,
                        ):
                            net_list.append(
                                [
                                    self.context.nets[i].GetNode(0),
                                    self.context.nets[j].GetNode(0),
                                ]
                            )
                            self.unique_nodes.append(
                                NodeNetwork.NodeNetwork(
                                    self.context.nets[i].GetNode(0),
                                    self.context.nets[j].GetNode(0),
                                )
                            )

        for i in range(0, len(self.context.wires)):
            self.unique_nodes.append(
                NodeNetwork.NodeNetwork(
                    self.context.wires[i].GetNodes()[0],
                    self.context.wires[i].GetNodes()[1],
                )
            )
        
        for i in range(0, len(self.context.bridges)):
            self.unique_nodes.append(
                NodeNetwork.NodeNetwork(
                    self.context.bridges[i].GetNode(0),
                    self.context.bridges[i].GetNode(1),
                )
            )

        for i in range(0, len(self.unique_nodes)):
            for j in range(0, len(self.unique_nodes)):
                if j != i:
                    if self.unique_nodes[i].IsConnected(
                            self.unique_nodes[j].GetReferences()
                    ):
                        self.unique_nodes[i].AddReferences(
                            self.unique_nodes[j].GetReferences()
                        )
                        self.unique_nodes[j].AddReferences(
                            self.unique_nodes[i].GetReferences()
                        )

        for i in range(0, len(self.unique_nodes)):
            for j in range(len(self.active_nodes) - 1, -1, -1):
                if (
                        self.unique_nodes[i].IsRemoved(self.active_nodes[j])
                        and self.active_nodes[j] < self.context.Params.SystemSettings.MAXNODES
                ):
                    del self.active_nodes[j]

    def net_redundancy_check(self, n1: int, n2: int, net_list: List[int]) -> bool:
        output: bool = False

        for i in range(0, len(net_list)):
            if (n1 == net_list[i][0] and n2 == net_list[i][1]) or (
                    n2 == net_list[i][0] and n1 == net_list[i][1]
            ):
                output = True
                break

        return output
