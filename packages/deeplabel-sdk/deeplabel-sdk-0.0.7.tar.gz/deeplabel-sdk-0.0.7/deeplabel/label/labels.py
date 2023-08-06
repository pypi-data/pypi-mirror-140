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

class DetectionLabel(DeeplabelBase):
    """Detection Label"""
    color: str  # hashvalue eg. \#efbg17
    name: str
    type: _DetectionLabelType
    category: _DetectionLabelCategory
    label_id: str
    is_deleted:bool = False



    @classmethod
    def from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["DetectionLabel"]:
        resp = client.get("/labels", params=params)
        labels = resp.json()["data"]["labels"]
        return [cls(**label) for label in labels]
