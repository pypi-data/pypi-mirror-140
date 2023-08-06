from typing import Type, Tuple

from wai.annotations.core.component import Component
from wai.annotations.core.domain import DomainSpecifier
from wai.annotations.core.specifier import SinkStageSpecifier


class YOLOODOutputFormatSpecifier(SinkStageSpecifier):
    """
    Specifier of the components for writing the YOLO
    object detection format.
    """
    @classmethod
    def description(cls) -> str:
        return "Writes image object-detection annotations in the YOLO format"

    @classmethod
    def components(cls) -> Tuple[Type[Component], ...]:
        from ..component import ToYOLOOD, YOLOODWriter
        return ToYOLOOD, YOLOODWriter

    @classmethod
    def domain(cls) -> Type[DomainSpecifier]:
        from wai.annotations.domain.image.object_detection import ImageObjectDetectionDomainSpecifier
        return ImageObjectDetectionDomainSpecifier
