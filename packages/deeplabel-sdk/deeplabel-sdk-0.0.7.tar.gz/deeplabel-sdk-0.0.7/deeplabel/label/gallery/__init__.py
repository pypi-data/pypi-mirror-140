from enum import Enum
from typing import List, Optional, Dict, Any
from deeplabel.basemodel import DeeplabelBase, MixinConfig
import deeplabel.label.gallery.images
import deeplabel.client


class _TaskStatus(Enum):
    TBD = "TBD"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"


class _BaseStatus(MixinConfig):
    status: _TaskStatus
    start_time: float
    end_time: float
    error: Optional[str] = None


class _InferenceStatus(_BaseStatus):
    dl_model_id: Optional[str]
    progress: float


class _LabelGalleryStatus(MixinConfig):
    submit: _BaseStatus
    assign_resources: _BaseStatus
    inference: _InferenceStatus
    label: _BaseStatus
    review: _BaseStatus
    labelling: _BaseStatus


class Gallery(DeeplabelBase):
    gallery_id: str
    title:str
    description:str
    is_deleted:bool
    parent_folder_id:Optional[str]
    project_id: str
    status: _LabelGalleryStatus

    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["Gallery"]:
        resp = client.get("/projects/gallery", params=params)
        galleries = resp.json()["data"]["gallery"]
        galleries = [cls(**gallery, client=client) for gallery in galleries]
        return galleries

    @property
    def images(self)->List["deeplabel.label.gallery.images.Image"]:
        """Get Images of the Gallery"""
        return deeplabel.label.gallery.images.Image.from_gallery_id(
            self.gallery_id, self.client
        )
