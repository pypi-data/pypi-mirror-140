from enum import Enum
from typing import Any, Dict, List
from deeplabel.basemodel import MixinConfig, DeeplabelBase
import deeplabel.client


class _DetectionLabelType(Enum):
    OBJECT = "OBJECT"
    ACTION = "ACTION"


class _DetectionLabelCategory(Enum):
    DETECTION = "DETECTION"
    CLASSIFICATION = "CLASSIFICATION"


class Label(MixinConfig):
    id: str
    color: str  # hashvalue eg. \#efbg17
    name: str
    type: _DetectionLabelType
    category: _DetectionLabelCategory
    is_deleted:bool = False


class LabelMap(DeeplabelBase):
    """Detection Label"""
    label_id:str
    label:Label
    name_lower:str
    project_id:str

    @classmethod
    def from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["LabelMap"]:
        resp = client.get("/labels/projectmaps", params=params)
        labels = resp.json()["data"]["labelProjectMaps"]
        return [cls(**label) for label in labels]
