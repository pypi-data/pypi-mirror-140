import os
from functools import partial

from wai.annotations.core.component.util import (
    SeparateFileWriter,
    SplitSink,
    SplitState,
    ExpectsDirectory,
    RequiresNoSplitFinalisation
)

from .._format import YOLOODFormat


class YOLOODWriter(
    ExpectsDirectory,
    RequiresNoSplitFinalisation,
    SeparateFileWriter[YOLOODFormat],
    SplitSink[YOLOODFormat]
):
    """
    Writer of YOLO files.
    """
    labels_split_path: str = SplitState(lambda self: self.split_path("labels"))
    images_split_path: str = SplitState(lambda self: self.split_path("images"))

    def consume_element_for_split(
            self,
            element: YOLOODFormat
    ):
        # Unpack the instance
        image_info, yolo_objects = element

        # Write the image
        self.write_data_file(image_info, self.images_split_path)

        # If the image is a negative, skip writing the annotations
        if len(yolo_objects) == 0:
            return

        # Format the filename
        labels_filename = f"{os.path.splitext(image_info.filename)[0]}.txt"

        # Write the annotations file
        with open(os.path.join(self.labels_split_path, labels_filename), "w") as labels_file:
            labels_file.write("\n".join(map(str, yolo_objects)))

    @classmethod
    def get_help_text_for_output_option(cls) -> str:
        return "output directory to write images and annotations to"

    def split_path(self, path: str) -> str:
        """
        Helper function which both formats and makes a split directory.

        :param path:
                    The sub-directory in which to make the split directories.
        :return:
                    The split directory.
        """
        split_base_path = os.path.join(self.output_path, path)
        self.create_split_directories(split_base_path)
        return self.get_split_path(self.split_label, split_base_path)
