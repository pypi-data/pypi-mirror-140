from typing import List
from pydantic import BaseModel


def camel_case_alias_generator(value: str):
    words: List[str] = value.lower().split('_')
    return words[0] + ''.join(word.title() for word in words[1:])


class CamelModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        alias_generator = camel_case_alias_generator
        allow_population_by_field_name = True
        use_enum_values = True

    def dict(self, **kwargs):
        return super().dict(
            **{
                "exclude_none": True,
                **kwargs,
            },
        )
