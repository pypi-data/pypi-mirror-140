import tensorflow as tf
from pydantic import BaseModel, Field, PrivateAttr
from pydantic.typing import Literal
from typing import Dict, Optional, List
from brevettiai.data import FileLoader
import json
import numpy as np
from brevettiai.data.image import CropResizeProcessor, annotation_parser


class AnnotationLoader(FileLoader):
    type: Literal["AnnotationLoader"] = "AnnotationLoader"
    path_key: str = Field(default="annotation_path", exclude=True)
    output_key: str = Field(default="annotation", exclude=True)
    mapping: Dict[str, str] = Field(default_factory=dict,
                                    description="mapping from annotation label to class, use '|' to signal multiclass")

    classes: Optional[List[str]] = Field(default=None, exclude=True)
    postprocessor: Optional[CropResizeProcessor] = Field(default_factory=None, exclude=True)

    _label_space = PrivateAttr(default=None)

    @property
    def label_space(self):
        assert self.classes is not None
        if self._label_space is not None:
            return self._label_space

        self._label_space = {}
        targets = dict(zip(self.classes, np.eye(len(self.classes))))
        self._label_space.update(targets)
        for label, class_descriptor in self.mapping.items():
            # Separate multiclass to classes
            classes = class_descriptor.split("|")
            # map classes to
            self._label_space[label] = np.max(tuple(targets[c] for c in classes), 0)
        return self._label_space

    def load(self, path, shape, postprocess=True):
        data, meta = super().load(path)
        label_space = self.label_space

        def _parse_annotation_buffer(buffer, shape):
            try:
                # Decode if bytes
                buffer = buffer.decode()
            except AttributeError:
                # take item if numpy array
                buffer = buffer.item()
            annotation = json.loads(buffer)
            draw_buffer = np.zeros((shape[2], shape[0], shape[1]), dtype=np.float32)
            segmentation = annotation_parser.draw_contours2_CHW(annotation, label_space, bbox=None,
                                                                scale=1, draw_buffer=draw_buffer)
            segmentation = segmentation.transpose(1, 2, 0)
            return segmentation.astype(np.float32)

        annotation = tf.numpy_function(_parse_annotation_buffer, [data, shape],
                                       tf.float32, name="parse_segmentation")
        meta = {}

        if postprocess and self.postprocessor is not None:
            annotation = self.postprocessor.process(annotation)
        return annotation, meta

    def __call__(self, x, *args, **kwargs):
        image_shape = x["_image_file_shape"]
        data, meta = self.load(x[self.path_key], shape=(image_shape[0], image_shape[1], len(self.classes)))
        x[self.output_key] = data
        x.update(meta)
        return x