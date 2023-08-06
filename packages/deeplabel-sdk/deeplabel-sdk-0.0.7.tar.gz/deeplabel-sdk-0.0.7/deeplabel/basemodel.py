from pydantic import BaseModel, Field, root_validator
from caseconverter import camelcase
from typing import Any
import typing

# import deeplabel.client

class MixinConfig(BaseModel):
    class Config:
        allow_population_by_field_name = True
        alias_generator = camelcase
        arbitrary_types_allowed = True


class DeeplabelBase(MixinConfig):
    """Base Model for all models that don't need client"""
    extra: typing.Dict[str, Any] = Field(exclude=True)
    client: Any = Field(exclude=True)

    @root_validator(pre=True)
    def build_extra(cls, values: typing.Dict[str, Any]) -> typing.Dict[str, Any]:
        all_required_field_names = {field.alias for field in cls.__fields__.values() if field.alias != 'extra'}  # to support alias

        extra: typing.Dict[str, Any] = {}
        for field_name in list(values):
            if field_name not in all_required_field_names:
                extra[field_name] = values.pop(field_name)
        values['extra'] = extra
        return values

        

