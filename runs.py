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

class Runs(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    biosampleId: str
    id: str
    individualId: Optional[str] = None
    info: Optional[dict] = None
    libraryLayout: Optional[str]=None
    librarySelection: Optional[str]=None
    librarySource: Optional[OntologyTerm] = None
    libraryStrategy: Optional[str] = None
    platform: Optional[str] = None
    platformModel: Optional[OntologyTerm] = None
    runDate: Optional[str] = None

'''
with open("test/runs_test.json", "r") as f:
    docs = json.load(f)
    try:
        for doc in docs:
            Runs(**doc)
        print("runs is OK")
    except ValidationError as e:
        print(e)
''' 
f = requests.get('http://localhost:5050/api/runs')
total_response = json.loads(f.text)
resultsets = total_response["response"]["resultSets"]


for resultset in resultsets:
    results = resultset["results"]
    dataset = resultset["id"]
    try:
        for result in results:
            Runs(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue

