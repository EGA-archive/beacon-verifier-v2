import json
import re
import pydantic
import inspect
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    field_validator,
    Field,
    PrivateAttr,
    ConfigDict
)

from typing import Optional, Union
import requests

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
            
class DUODataUse(BaseModel, extra='forbid'):
    id: str
    label: Optional[str]=None
    modifiers: Optional[list] = None
    version: str
    @field_validator('id')
    @classmethod
    def id_must_be_CURIE(cls, v: str) -> str:
        if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
            pass
        else:
            raise ValueError('id must be CURIE, e.g. NCIT:C42331')
        return v.title()
    @field_validator('modifiers')
    @classmethod
    def check_modifiers(cls, v: list) -> list:
        for modifier in v:
            OntologyTerm(**modifier)

class DataUseConditions(BaseModel, extra='forbid'):
    duoDataUse: Optional[list] = None
    @field_validator('duoDataUse')
    @classmethod
    def check_dataUseConditions(cls, v: list) -> list:
        for duoData in v:
            DUODataUse(**duoData)

class Datasets(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    createDateTime: Optional[str] = None
    dataUseConditions: DataUseConditions
    description: Optional[str] = None
    externalUrl: Optional[str] = None
    id: str
    info: Optional[dict] = None
    name: str
    updateDateTime: Optional[str]=None
    version: Optional[str] = None
    @field_validator('createDateTime')
    @classmethod
    def check_createDateTime(cls, v: str) -> str:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('createDateTime, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
    @field_validator('updateDateTime')
    @classmethod
    def check_updateDateTime(cls, v: str) -> str:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('updateDateTime, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()

with open("datasets_test.json", "r") as f:
    docs = json.load(f)
    try:
        for doc in docs:
            Datasets(**doc)
    except ValidationError as e:
        print(e)
''' 
f = requests.get('http://localhost:5050/api/datasets')
total_response = json.loads(f.text)
resultsets = total_response["response"]["resultSets"]


for resultset in resultsets:
    results = resultset["results"]
    for result in results:
        try:
            Datasets(**result)
        except ValidationError as e:
            print(e)
            continue
'''
