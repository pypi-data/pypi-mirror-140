import numpy as np

from pydantic import BaseModel


class ImageProcessor(BaseModel):
    """
    Baseclass for implementing interface for image proccessors
    """
    type: str

    def process(self, image):
        """Process image according to processor"""
        raise NotImplementedError("process(image)-> image should be implemented")
        # noinspection PyUnreachableCode
        return image

    @staticmethod
    def affine_transform(input_height, input_width):
        return np.eye(3)
