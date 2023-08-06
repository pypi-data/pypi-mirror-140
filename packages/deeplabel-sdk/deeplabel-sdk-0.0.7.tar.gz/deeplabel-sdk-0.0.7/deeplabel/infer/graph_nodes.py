from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List
from dataclasses_json import dataclass_json, LetterCase, Undefined, CatchAll
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
from deeplabel.infer import video_tasks
from deeplabel.basemodel import DeeplabelBase
import deeplabel.infer.graphs


class GraphNodeTypes(Enum):
    DLMODEL = "DLMODEL"  # deprecated
    SCRIPT = "SCRIPT"  # deprecated
    NOTEBOOK = "NOTEBOOK"
    VIDEOWRITE = "VIDEOWRITE"
    VIDEO_CONVERSION = "VIDEO_CONVERSION"
    # TODO: Support more datadypes


class GraphNode(DeeplabelBase):
    graph_node_id: str
    name: str
    notebook_id: str
    type: GraphNodeTypes
    is_head: bool
    is_shown: bool
    graph_id: str

    @classmethod
    def _from_search_params(cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient") -> List["GraphNode"]:  # type: ignore Used to ignore using private class BaseClient
        resp = client.get("/graphs/nodes", params=params)
        nodes = resp.json()["data"]["graphNodes"]
        nodes = [cls(**node, client=client) for node in nodes]
        return nodes

    @classmethod
    def from_graph_node_id(cls, graph_node_id: str, client: "deeplabel.client.BaseClient") -> "GraphNode":  # type: ignore Used to ignore using private class BaseClient
        nodes = cls._from_search_params({"graphNodeId": graph_node_id}, client)
        if not len(nodes):
            raise InvalidIdError(f"No Graph Node found for graphNodeId {graph_node_id}")
        # Since node_id will always yield 1 graphNode, return that instead of a list
        return nodes[0]

    @property
    def graph(self) -> "deeplabel.infer.graphs.Graph":
        if hasattr(self, "_graph"):
            return self._graph
        self._graph = deeplabel.infer.graphs.Graph.from_graph_id(
            self.graph_id, self.client
        )
        return self._graph

    @property
    def prev_nodes(self):
        if hasattr(self, "_prev_nodes"):
            return self._prev_nodes
        # mapping between graph_node_id and the corresponding node objects
        memo = {node.graph_node_id: node for node in self.graph.nodes}
        self._prev_nodes = [
            memo[edge.src_graph_node_id]
            for edge in self.graph.edges
            if edge.target_graph_node_id == self.graph_node_id
        ]
        return self._prev_nodes

    @property
    def next_nodes(self):
        if hasattr(self, "_next_nodes"):
            return self._next_nodes
        # mapping between graph_node_id and the corresponding node objects
        memo = {node.graph_node_id: node for node in self.graph.nodes}
        self._next_nodes = [
            memo[edge.target_graph_node_id]
            for edge in self.graph.edges
            if edge.src_graph_node_id == self.graph_node_id
        ]
        return self._next_nodes

    # def update(self, graph_node_id: str, data: dict) -> dict:
    #     try:
    #         data["graphNodeId"] = graph_node_id
    #         data["restriction"] = False
    #         res = requests.put(self.graph_node_url,
    #                            json=data, headers=self.headers)
    #         graph_node = res.json()["data"]
    #         return graph_node
    #     except Exception as exc:
    #         print("update graphnode failed", exc)
