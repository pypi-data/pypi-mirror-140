import tensorflow as tf
import numpy as np

from pydantic import Field
from pydantic.typing import Literal
from typing import Optional
from brevettiai.data import FileLoader
from brevettiai.data.image.image_processor import ImageProcessor


class ScalingProcessor(ImageProcessor):
    type: Literal["ScalingProcessor"] = "ScalingProcessor"

    def process(self, image):
        """Process image according to processor"""
        max_ = tf.reduce_max(image)
        min_ = tf.reduce_min(image)
        image = (image - min_) / (max_ - min_)
        return image


class CropResizeProcessor(ImageProcessor):
    type: Literal["CropResizeProcessor"] = "CropResizeProcessor"
    output_height: int = Field(default=0, ge=0, description="Leave at 0 to infer")
    output_width: int = Field(default=0, ge=0, description="Leave at 0 to infer")

    roi_horizontal_offset: int = Field(
        default=0, ge=0, description="Horizontal coordinate of the top-left corner of the bounding box in image.")
    roi_vertical_offset: int = Field(
        default=0, ge=0, description="Vertical coordinate of the top-left corner of the bounding box in image.")
    roi_width: int = Field(default=0, ge=0, description="Width of the bounding box. Zero uses image boundary")
    roi_height: int = Field(default=0, ge=0, description="Height of the bounding box. Zero uses image boundary")

    interpolation: Literal["bilinear", "nearest"] = Field(
        default="bilinear", description="Interpolation mode of cropping and resizing")

    def output_size(self, input_height, input_width):
        """Calculated output size of output after postprocessing, given input image sizes"""
        height = self.roi_height or input_height
        width = self.roi_width or input_width
        return self.output_height or height, self.output_width or width

    def crop_size(self, input_height, input_width):
        height = input_height - self.roi_vertical_offset if self.roi_height == 0 else self.roi_height
        width = input_width - self.roi_horizontal_offset if self.roi_width == 0 else self.roi_width
        return height, width

    def bbox(self, input_height, input_width):
        """
        Calculate bounding box specified in pixel coordinates [y1, x1, y2, x2]
        The points both being included in the region of interest
        """
        height, width = self.crop_size(input_height, input_width)
        return self.roi_vertical_offset, self.roi_horizontal_offset, \
            self.roi_vertical_offset + height - 1, self.roi_horizontal_offset + width - 1

    def affine_transform(self, input_height, input_width):
        crop_height, crop_width = self.crop_size(input_height, input_width)
        output_height, output_width = self.output_size(input_width, input_height)

        return np.array([
            [(crop_width-1) / (output_width-1),  0, self.roi_horizontal_offset],
            [0, (crop_height-1) / (output_height-1), self.roi_vertical_offset],
            [0, 0, 1]
        ])

    def process(self, image):
        shape = tf.shape(image)[:2]
        input_height, input_width = shape[0], shape[1]

        size = self.output_size(input_height, input_width)

        # Normalize bounding box to match crop_and_resize
        # https://www.tensorflow.org/api_docs/python/tf/image/crop_and_resize
        norm = tf.cast([input_height, input_width, input_height, input_width], tf.float32)-1
        bbox = tf.cast(self.bbox(input_height, input_width), tf.float32)
        boxes = [bbox / norm]

        # Crop and resize, attach batch dimension to match tf call
        return tf.image.crop_and_resize(
            image[None], boxes, box_indices=[0], crop_size=size, method=self.interpolation,
            extrapolation_value=0.0
        )[0]


class ImageLoader(FileLoader):
    type: Literal["ImageLoader"] = "ImageLoader"
    output_key: str = Field(default="img", exclude=True)
    postprocessor: Optional[CropResizeProcessor] = Field(default_factory=CropResizeProcessor)
    channels: Literal[0, 1, 3, 4] = Field(default=0, description="Number of channels in images, 0 to autodetect")

    def output_shape(self, image_height=None, image_width=None):
        output_channels = self.channels if self.channels else None
        return (*self.postprocessor.output_size(image_height, image_width), output_channels)

    def load(self, path, postprocess=True):
        data, meta = super().load(path)

        if tf.strings.length(data) > 0:
            image = tf.io.decode_image(data, expand_animations=False, channels=0)

            if postprocess and self.postprocessor is not None:
                image = self.postprocessor.process(image)
        else:
            if postprocess and self.postprocessor is not None:
                image = tf.constant(0, dtype=tf.float32, shape=(1, 1, 1))
            else:
                image = tf.constant(0, dtype=tf.uint8, shape=(1, 1, 1))

        meta["_image_file_shape"] = tf.convert_to_tensor(tf.shape(image))

        return image, meta
