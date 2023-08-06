import os
from typing import List, Optional

from wai.annotations.core.component.util import AnnotationFileProcessor
from wai.annotations.core.stream import ThenFunction
from wai.annotations.domain.image import Image
from wai.annotations.domain.image.util import get_associated_image

from wai.common.cli.options import TypedOption

from .._format import YOLOODFormat, YOLOObject


class YOLOODReader(AnnotationFileProcessor[YOLOODFormat]):
    """
    Reader of YOLO object-detection files.
    """
    # The relative path to the data image files from the annotation images
    relative_path_to_data_images: Optional[str] = TypedOption(
        "--image-path-rel",
        type=str,
        metavar="PATH",
        help="Relative path to image files from annotations"
    )

    def read_annotation_file(
            self,
            filename: str,
            then: ThenFunction[YOLOODFormat]
    ):

        # Split the filename into path, basename, ext
        path, basename = os.path.split(filename)
        basename, extension = os.path.splitext(basename)

        # Use the provided relative path if given, otherwise default to the same
        # sub-structure from a "labels" directory down in an "images" directory
        relative_path = self.relative_path_to_data_images
        if relative_path is None:
            relative_path = os.path.join("..", "images")
            abs_path = os.path.abspath(path)
            path_parts = os.path.split(abs_path)
            relevant_path_parts = []
            while abs_path:
                abs_path, path_part = os.path.split(abs_path)
                if path_part == "labels":
                    break
                relevant_path_parts.append(path_part)
            if len(relevant_path_parts) == len(path_parts):
                raise Exception(f"No 'labels' directory found in path of {abs_path}")
            for path_part in reversed(relevant_path_parts):
                relative_path = os.path.join("..", relative_path, path_part)

        # Join the path with the relative path to the data-image
        image_path = os.path.join(path, relative_path)

        # Find the image
        image_filename = get_associated_image(
            os.path.join(image_path, basename)
        )

        # Read the YOLO annotations
        objects = []
        with open(filename, "r") as file:
            for line in file.readlines():
                objects.append(YOLOObject.from_string(line))

        # Read the image
        image = Image.from_file(image_filename)

        then((image, tuple(objects)))

    def read_negative_file(
            self,
            filename: str,
            then: ThenFunction[YOLOODFormat]
    ):
        image_info = Image.from_file(filename)

        then((image_info, None))
