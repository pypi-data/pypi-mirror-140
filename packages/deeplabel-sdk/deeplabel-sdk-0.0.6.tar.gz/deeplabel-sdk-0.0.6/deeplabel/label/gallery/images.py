from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from deeplabel.basemodel import DeeplabelBase
import deeplabel.client
from deeplabel.exceptions import InvalidIdError
from . import detections

class _ImageResolution(BaseModel):
    height:int
    width:int

class Image(DeeplabelBase):
    image_id: str
    gallery_id:str
    image_url:str
    assignee:Optional[str]
    project_id:str
    resolution:_ImageResolution
    name:str
    displayed:bool
    parentFolderId:Optional[str]
    detections:List[detections.Detection]
    is_deleted:bool
    parent_folder_id:Optional[str]
    project_id: str

    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["Image"]:
        resp = client.get("/projects/gallery/images", params=params)
        images = resp.json()["data"]["images"]
        images = [cls(**image, client=client) for image in images]
        return images
    
    @classmethod
    def from_gallery_id(cls, gallery_id:str, client:"deeplabel.client.BaseClient")->List["Image"]:
        return cls._from_search_params({"galleryId":gallery_id}, client=client)
    
    @classmethod
    def from_image_id(cls, image_id: str, client: "deeplabel.client.BaseClient"):
        images = cls._from_search_params({"imageId": image_id}, client)
        if not len(images):
            raise InvalidIdError(
                f"Failed to fetch image with imageId  : {image_id}"
            )
        # since detectionId should fetch only 1 detection, return that detection instead of a list
        return images[0]
