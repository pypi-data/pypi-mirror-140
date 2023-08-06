from functools import partial
from typing import Dict, Optional

from wai.annotations.core.component import ProcessorComponent
from wai.annotations.core.stream import OutputElementType, ThenFunction, DoneFunction
from wai.annotations.core.stream.util import ProcessState
from wai.annotations.domain.image.object_detection import ImageObjectDetectionInstance
from wai.annotations.domain.image.object_detection.util import get_object_label

from wai.common.adams.imaging.locateobjects import LocatedObject
from wai.common.cli.options import TypedOption

from .._format import YOLOODFormat, YOLOObject


class ToYOLOOD(
    ProcessorComponent[ImageObjectDetectionInstance, YOLOODFormat]
):
    """
    Converter from internal format to YOLO annotations.
    """
    # Path to the labels file to write
    labels_file: Optional[str] = TypedOption(
        "-l", "--labels",
        type=str,
        metavar="PATH",
        help="Path to the labels file to write"
    )

    # Path to the labels CSV file to write
    labels_csv_file: Optional[str] = TypedOption(
        "-c", "--labels-csv",
        type=str,
        metavar="PATH",
        help="Path to the labels CSV file to write"
    )

    # Label-index mapping accumulator
    labels: Dict[str, int] = ProcessState(lambda self: {})

    def process_element(
            self,
            element: ImageObjectDetectionInstance,
            then: ThenFunction[YOLOODFormat],
            done: DoneFunction
    ):
        image_info, located_objects = element

        if located_objects is None or len(located_objects) == 0:
            return then((image_info, tuple()))

        to_yolo_object = partial(self.to_yolo_object, image_width=image_info.width, image_height=image_info.height)
        yolo_objects = tuple(map(to_yolo_object, located_objects))

        then((image_info, yolo_objects))

    def finish(self, then: ThenFunction[OutputElementType], done: DoneFunction):
        # Write the labels file
        if self.labels_file is not None:
            with open(self.labels_file, "w") as labels_file:
                labels_file.write(",".join(self.labels.keys()))

        # Write the labels CSV file
        if self.labels_csv_file is not None:
            with open(self.labels_csv_file, "w") as labels_csv_file:
                labels_csv_file.write("Index,Label")
                for label, index in self.labels.items():
                    labels_csv_file.write(f"\n{index},{label}")

        done()

    def to_yolo_object(self, located_object: LocatedObject, *, image_width: int, image_height: int) -> YOLOObject:
        """
        Converts a single located object into a YOLO object.

        :param located_object:
                    The located object to convert.
        :param image_width:
                    The image width (for normalisation).
        :param image_height:
                    The image height (for normalisation).
        :return:
                    The YOLO object.
        """
        # Update the label mapping
        label = get_object_label(located_object)
        if label not in self.labels:
            self.labels[label] = len(self.labels)
        class_index = self.labels[label]

        return YOLOObject(
            class_index,
            (located_object.x + located_object.width / 2) / image_width,
            (located_object.y + located_object.height / 2) / image_height,
            located_object.width / image_width,
            located_object.height / image_height
        )
