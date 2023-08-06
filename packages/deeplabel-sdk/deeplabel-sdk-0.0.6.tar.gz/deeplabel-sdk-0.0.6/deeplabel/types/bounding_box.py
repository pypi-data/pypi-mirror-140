from pydantic import BaseModel, confloat
from typing import Optional


class BoundingBox(BaseModel):
    xmin:confloat(ge=0,le=1)
    ymin:confloat(ge=0,le=1)
    xmax:confloat(ge=0,le=1)
    ymax:confloat(ge=0,le=1)

    @property
    def area(self) -> float:
        """Area can be negative if xmax < xmin or ymax < ymin"""
        return (self.xmax - self.xmin) * (self.ymax - self.ymin) #type:ignore

    def intersection(self, other: "BoundingBox") -> Optional["BoundingBox"]:
        xmin = max(self.xmin, other.xmin)
        ymin = max(self.ymin, other.ymin)
        xmax = min(self.xmax, other.xmax)
        ymax = min(self.ymax, other.ymax)
        if xmin < xmax and ymin < ymax:
            return BoundingBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)

    def union(self, other: "BoundingBox") -> "BoundingBox":
        return BoundingBox(
            xmin=min(self.xmin, other.xmin),
            ymin=min(self.ymin, other.ymin),
            xmax=max(self.xmax, other.xmax),
            ymax=max(self.ymax, other.ymax),
        )

    def iou(self, other: "BoundingBox") -> float:
        intersection = self.intersection(other)
        if intersection:
            return intersection.area / (self.union(other).area)
        return 0

    def dilate(self, percentage: float) -> "BoundingBox":
        """Dilate the boundingBox by a certain percentage in each direction.

        Dilating by 0% keeps the box unchanged while dilating by 100% doubles the box
        """
        h = self.ymax - self.ymin
        w = self.xmax - self.xmin
        h_delta = h * percentage / 100
        w_delta = w * percentage / 100
        return BoundingBox(
            xmin=max(0, self.xmin - w_delta / 2),
            xmax=min(1, self.xmax + w_delta / 2),
            ymin=max(0, self.ymin - h_delta / 2),
            ymax=min(1, self.ymax + h_delta / 2),
        )


class BoundingBoxWithNumber(BoundingBox):
    """BoundingBox with number attribute for inference boundingBoxes"""
    number: Optional[int] = None
