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

class OntologyTerm(BaseModel, extra='forbid'):
    id: str
    label: Optional[str]=None
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v.title()

class Handover(BaseModel, extra='forbid'):
    handoverType: OntologyTerm
    note: Optional[str] = None
    url: str

class BooleanResponseSection(BaseModel, extra='forbid'):
    exists: bool
    
class BooleanResponse(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    beaconHandovers: Optional[list]=None
    info: Optional[dict] = None
    meta: Meta
    responseSummary: BooleanResponseSection
    @field_validator('beaconHandovers')
    @classmethod
    def check_beaconHandovers(cls, v: list) -> list:
        for handover in v:
            Handover(**handover)
        return v.title()