"""
Module to get videos data
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import Field
from deeplabel.basemodel import DeeplabelBase, MixinConfig
from pydantic import validator
import deeplabel.label.videos.frames
import deeplabel.label.videos.detections
import deeplabel.client
import yarl
import os


class _VideoResolution(MixinConfig):
    height: int
    width: int


class _VideoFormat(MixinConfig):
    url: str
    resolution: Optional[_VideoResolution] = None
    extension: Optional[str] = None
    fps: Optional[float] = None
    file_size: Optional[float] = None


class _VideoUrl(MixinConfig):
    source: Optional[_VideoFormat]
    res360: Optional[_VideoFormat] = Field(None, alias="360P")
    res480: Optional[_VideoFormat] = Field(None, alias="480P")
    res720: Optional[_VideoFormat] = Field(None, alias="720P")
    res1080: Optional[_VideoFormat] = Field(None, alias="1080P")
    res1440: Optional[_VideoFormat] = Field(None, alias="1440P")
    res2160: Optional[_VideoFormat] = Field(None, alias="2160P")


class _TaskStatus(Enum):
    TBD = "TBD"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"
    HOLD = 'HOLD' # Not sure where this came from. Not in schema :(


class _BaseStatus(MixinConfig):
    status: _TaskStatus
    start_time: float
    end_time: float
    error: Optional[str] = None


class _InferenceStatus(_BaseStatus):
    dl_model_id: Optional[str]
    progress: float


class _LabelVideoStatus(MixinConfig):
    download: _BaseStatus
    assign_resources: _BaseStatus
    extraction: _BaseStatus
    frames_extraction: _BaseStatus
    inference: _InferenceStatus
    label: _BaseStatus
    review: _BaseStatus
    labelling: _BaseStatus


class _ExtractionPoint(MixinConfig):
    labelling_fps: float
    start_time: float
    end_time: float


class Video(DeeplabelBase):
    video_id: str
    project_id: str
    input_url: str
    video_urls: Optional[_VideoUrl]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    status: _LabelVideoStatus
    extraction_points: List[_ExtractionPoint]
    duration: Optional[float]
    video_fps: Optional[float]
    labelling_fps: int

    @validator('video_url', always=True)
    def validate_url(cls, value, values):
        """
        Validate that either video_url or video_urls.source.url exists
        Refer https://github.com/samuelcolvin/pydantic/issues/832#issuecomment-534896056
        """
        # If video_url key is empty
        if not isinstance(value, str):
            # video_urls.source.url
            source_url = values.get('videoUrls',{}).get('source',{}).get('url','')
            if not source_url:
                # should have either of the two
                raise ValueError(f"Video {values['videoId']} neither has video_url nor video_urls.source.url")
            # set video_url = video_urls.source.url
            return source_url
        # keep video_url as is if it exists
        return value
        

    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["Video"]:
        resp = client.get("/projects/videos", params=params)
        videos = resp.json()["data"]["videos"]
        videos = [cls(**video, client=client) for video in videos]
        return videos # type: ignore
    
    @property
    def ext(self):
        """Extenion of the video, deduced from path/name"""
        return os.path.splitext(yarl.URL(self.video_urls.source.url).name)[-1]


    @property
    def detections(self):
        """Get Detections of the video"""
        return deeplabel.label.videos.detections.Detection.from_video_id(
            self.video_id, self.client
        )

    @property
    def frames(self):
        """Get Detections of the video"""
        return deeplabel.label.videos.frames.Frame.from_video_id(
            self.video_id, self.client
        )
