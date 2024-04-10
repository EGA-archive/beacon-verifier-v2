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


class OntologyTerm(BaseModel):
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

class Handover(BaseModel):
    handoverType: OntologyTerm
    note: Optional[str] = None
    url: str


class SummaryResponseSection(BaseModel):
    exists: bool
    numTotalResults: int

class ResultsetInstance(BaseModel):
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
    
class Resultsets(BaseModel):
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
    
class ResultsetsResponse(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    beaconHandovers: Optional[list]=None
    info: list
    meta: Meta
    response: Resultsets
    responseSummary: SummaryResponseSection
    @field_validator('beaconHandovers')
    @classmethod
    def check_beaconHandovers(cls, v: list) -> list:
        for handover in v:
            try:
                Handover(**handover)
            except Exception as e:
                print(e)