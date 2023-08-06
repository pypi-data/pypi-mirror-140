from functools import partial
from typing import List, Optional

from wai.annotations.core.component import ProcessorComponent
from wai.annotations.core.stream import ThenFunction, DoneFunction
from wai.annotations.core.stream.util import ProcessState, RequiresNoFinalisation
from wai.annotations.domain.image.object_detection import ImageObjectDetectionInstance
from wai.annotations.domain.image.object_detection.util import set_object_label

from wai.common.adams.imaging.locateobjects import LocatedObjects, LocatedObject
from wai.common.cli.options import TypedOption

from .._format import YOLOODFormat, YOLOObject


class FromYOLOOD(
    RequiresNoFinalisation,
    ProcessorComponent[YOLOODFormat, ImageObjectDetectionInstance]
):
    """
    Converter from YOLO annotations to internal format.
    """
    # Path to the labels file
    labels_file: Optional[str] = TypedOption(
        "-l", "--labels",
        type=str,
        metavar="PATH",
        help="Path to the labels file"
    )

    # Mapping from class index to label
    labels: List[str] = ProcessState(lambda self: self.read_labels_file())

    def process_element(
            self,
            element: YOLOODFormat,
            then: ThenFunction[ImageObjectDetectionInstance],
            done: DoneFunction
    ):
        # Unpack the external format
        image_info, yolo_objects = element

        # Convert YOLO objects to located objects
        located_objects = None
        if len(yolo_objects) > 0:
            to_located_object = partial(self.to_located_object, image_width=image_info.width, image_height=image_info.height)
            located_objects = LocatedObjects(map(to_located_object, yolo_objects))

        then(
            ImageObjectDetectionInstance(
                image_info,
                located_objects
            )
        )

    def read_labels_file(self) -> List[str]:
        """
        Parses the labels file if one is given.

        :return:
                    The label mapping.
        """
        # If no label file is given, return an empty mapping
        if self.labels_file is None:
            return []

        # Read and parse the labels file
        with open(self.labels_file, "r") as labels_file:
            return labels_file.read().split(",")

    def to_located_object(self, object: YOLOObject, *, image_width: int, image_height: int) -> LocatedObject:
        """
        Converts the YOLO object to a located object.

        :param object:
                    The YOLO object.
        :return:
                    The located object.
        """
        # Get the object label (just uses the class index if no mapping is provided)
        label: str = self.labels[object.class_index] if len(self.labels) > 0 else str(object.class_index)

        # Get the boundary co-ordinates
        width = round(object.width * image_width)
        height = round(object.height * image_height)
        x_min = round(object.centre_x * image_width - width / 2)
        y_min = round(object.centre_y * image_height - height / 2)

        # Create the located object
        located_object = LocatedObject(x_min, y_min, width, height)
        set_object_label(located_object, label)

        return located_object
