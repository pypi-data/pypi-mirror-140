"""
Module to get videotasks data
"""
from dataclasses import dataclass
from enum import Enum
from itertools import islice
from typing import List, Tuple, Dict
import deeplabel.infer.graph_nodes
import deeplabel.infer.detections
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
from deeplabel.basemodel import DeeplabelBase, MixinConfig
from pydantic import BaseModel, Field
from loguru import logger


class VideoTaskStatus(Enum):
    TBD = "TBD"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    ABORTED = "ABORTED"
    FAILURE = "FAILURE"


class VideoTaskVideoId(MixinConfig):
    title: str
    video_id: str


class TimePoint(MixinConfig):
    start_time: float
    end_time: float


class VideoTask(DeeplabelBase):
    video_task_id: str
    graph_id: str
    graph_node_id: str
    is_shown: bool
    status: VideoTaskStatus
    progress: int
    init_time_points: List[TimePoint]
    final_time_points: List[TimePoint]
    video_id: VideoTaskVideoId
    name: str

    @classmethod
    def _from_search_params(cls, params: Dict[str, str], client: "deeplabel.client.BaseClient") -> "VideoTask":  # type: ignore Used to ignore using private class BaseClient
        resp = client.get("/videos/tasks", params=params)
        tasks = resp.json()["data"]["videoTasks"]
        # Checkout https://lidatong.github.io/dataclasses-json/#use-my-dataclass-with-json-arrays-or-objects
        tasks = [cls(**task, client=client) for task in tasks]
        return tasks

    @classmethod
    def from_video_task_id(
        cls, video_task_id: str, client: "deeplabel.client.BaseClient"
    ) -> "VideoTask":
        tasks = cls._from_search_params(
            params={"videoTaskId": video_task_id}, client=client
        )
        if not len(tasks):
            raise InvalidIdError(
                f"No VideoTask found for given video_task_id: {video_task_id}"
            )
        # since one videoTaskId corresponds to 1 and only 1 videoTask, return 0th videoTask
        return tasks[0]

    @classmethod
    def from_video_id(
        cls, video_id: str, client: "deeplabel.client.BaseClient"
    ) -> List["VideoTask"]:
        return cls._from_search_params({"videoId": video_id}, client)

    @property
    def graph_node(self) -> "deeplabel.infer.graph_nodes.GraphNode":
        """GraphNode corresponding to this videoTask

        Returns:
            deeplabel.infer.graph_nodes.GraphNode: duh
        """
        if hasattr(self, "_graph_node"):
            return self._graph_node
        self._graph_node = deeplabel.infer.graph_nodes.GraphNode.from_graph_node_id(
            self.graph_node_id, self.client
        )
        return self._graph_node

    @property
    def detections(self) -> List["deeplabel.infer.detections.Detection"]:
        """Get all the detections for the given videoTask

        Returns:
            List[deeplabel.infer.detections.Detection]: duh, isn't that self explanatory?
        """
        if hasattr(self, "_detections"):
            return self._detections
        self._detections = deeplabel.infer.detections.Detection.from_video_task_id(
            self.video_task_id, self.client
        )
        return self._detections

    def insert_detections(
        self, detections: List["deeplabel.infer.detections.Detection"], chunk_size=500
    ):
        self.client: "deeplabel.client.BaseClient"

        def chunk(it, size):  # copied from https://stackoverflow.com/a/22045226/9504749
            it = iter(it)
            return iter(lambda: list(islice(it, size)), [])

        count = 0
        for dets in chunk(detections, chunk_size):
            dets: List[deeplabel.infer.detections.Detection]
            data = [
                det.dict(by_alias=True, exclude_unset=True, exclude_none=True)
                for det in dets
            ]
            logger.debug(f"Pushing ({count} ~ {count+len(data)})/{len(detections)}")
            count += len(data)
            self.client.post("/detections", {"data": data})
        logger.info(
            f"Completed pushing {len(detections)} detections for videoTaskId: {self.video_task_id}"
        )

    # def update(self, data: dict) -> dict:
    #     try:
    #         data["videoTaskId"] = self.video_task_id
    #         data["restriction"] = False
    #         res = requests.put(self.video_task_url, json=data, headers=self.headers)
    #         self.video_task = res.json()["data"]
    #         return self.video_task
    #     except Exception as exc:
    #         print("update videotask failed", exc)
