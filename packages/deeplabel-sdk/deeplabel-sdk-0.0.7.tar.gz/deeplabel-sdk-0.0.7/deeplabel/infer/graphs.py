from dataclasses import dataclass
from typing import List
from dataclasses_json import dataclass_json, LetterCase, Undefined, CatchAll
import deeplabel.client
import deeplabel
from deeplabel.exceptions import InvalidIdError
from deeplabel.infer import graph_nodes
from deeplabel.infer import graph_edges
from deeplabel.basemodel import DeeplabelBase


class Graph(DeeplabelBase):
    graph_id: str
    name: str
    project_id: str
    metadata: CatchAll  # type: ignore

    @classmethod
    def from_graph_id(cls, graph_id: str, client: "deeplabel.client.BaseClient") -> "Graph":  # type: ignore Used to ignore using private class BaseClient
        resp = client.get("/graphs", params={"graphId": graph_id})
        graphs = resp.json()["data"]["graphs"]
        if not len(graphs):
            raise InvalidIdError(f"No Graph found for graphEdgeId {graph_id}")
        graph: Graph = cls( **graphs[0], client = client)
        return graph

    @property
    def nodes(self) -> List["graph_nodes.GraphNode"]:
        if hasattr(self, "_nodes"):
            return self._nodes  # type: ignore
        assert hasattr(self, "client"), (
            f"Nodes property can only be accessed for fetched "
            "Graph objects that have graph.client access."
        )
        self._nodes = graph_nodes.GraphNode._from_search_params(
            {"graphId": self.graph_id, "limit": "-1", "project_id": self.project_id},
            client=self.client,
        )
        for node in self._nodes:
            node._graph = self
        return self._nodes

    @property
    def edges(self) -> List["graph_edges.GraphEdge"]:
        if hasattr(self, "_edges"):
            return self._edges  # type: ignore
        assert hasattr(self, "client"), (
            "edges property can only be accessed for fetched "
            "Graph objects that have graph.client access."
        )
        self._edges = graph_edges.GraphEdge._from_search_params(
            {"graphId": self.graph_id, "limit": "-1", "project_id": self.project_id},
            client=self.client,
        )
        for edge in self._edges:
            edge._graph = self
        return self._edges

    # def update(self, graph_id: str, data: dict) -> dict:
    #     try:
    #         data["graphId"] = graph_id
    #         data["restriction"] = False
    #         res = requests.put(self.graph_url,
    #                            json=data, headers=self.headers)
    #         graph = res.json()["data"]
    #         return graph
    #     except Exception as exc:
    #         print("update graph failed", exc)
