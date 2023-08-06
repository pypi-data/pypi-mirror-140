from pydantic import BaseModel, Field, parse_obj_as
from typing import Optional, Type
from brevettiai import Module

from brevettiai.io.h5_metadata import get_metadata as h5_metadata


class ModelMetadata(BaseModel):
    id: str = Field(description="unique id of model")
    run_id: str = Field(description="Specifier of which training run created the model")
    name: str = Field(description="Name of model")
    producer: str = Field(description="Name of producing code")
    host_name: Optional[str] = Field(default=None, description="URI to host where more information may be found")

    class Config:
        json_encoders = {
            Module: lambda x: x.get_config()
        }


def get_metadata(file: str, metadata_type: Type[ModelMetadata] = ModelMetadata):
    if file.endswith(".h5"):
        return parse_obj_as(metadata_type, h5_metadata(file))
    else:
        raise NotImplementedError(f"Getting metadata from '{file}' not implemented")
