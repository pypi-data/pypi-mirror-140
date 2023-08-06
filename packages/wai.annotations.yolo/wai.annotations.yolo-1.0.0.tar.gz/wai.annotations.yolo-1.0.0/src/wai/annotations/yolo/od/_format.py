from dataclasses import dataclass
from typing import Tuple

from wai.annotations.domain.image import Image


@dataclass
class YOLOObject:
    """
    Internal representation of a YOLO annotation.
    """
    class_index: int
    centre_x: float
    centre_y: float
    width: float
    height: float

    @classmethod
    def from_string(cls, string: str):
        parts = string.strip().split(" ")
        assert len(parts) == 5, f"{string} didn't split into exactly 5 parts"
        return cls(
            int(parts[0]),
            float(parts[1]),
            float(parts[2]),
            float(parts[3]),
            float(parts[4])
        )

    def __str__(self):
        return f"{self.class_index} {self.centre_x} {self.centre_y} {self.width} {self.height}"


YOLOODFormat = Tuple[Image, Tuple[YOLOObject]]
