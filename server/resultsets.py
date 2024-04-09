import json
import re
import argparse
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    Field,
    PrivateAttr
)

from typing import Optional, Union
import requests
from meta import Meta
from datetime import date

class ResultsetInstance(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    exists: bool
    id: str
    info: Optional[dict] = None
    results: list
    resultsCount: int
    resultsHandovers: Optional[list] = None
    setType: str
    
class Resultsets(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    schema_: Optional[str]=Field(default=None, alias='$schema')
    resultSets: list
    @field_validator('resultSets')
    @classmethod
    def check_resultSets(cls, v: list) -> list:
        for resultset in v:
            ResultsetInstance(**resultset)
        return v.title()