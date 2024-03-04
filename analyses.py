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

class Analyses(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    aligner: Optional[str] = None
    analysisDate: str
    biosampleId: Optional[str] = None
    id: str
    individualId: Optional[str] = None
    info: Optional[dict] = None
    pipelineName: str
    pipelineRef: Optional[str]=None
    runId: Optional[str]=None
    variantCaller: Optional[str]=None


with open("analyses_test.json", "r") as f:
    docs = json.load(f)
    try:
        for doc in docs:
            Analyses(**doc)
    except ValidationError as e:
        print(e)
''' 
f = requests.get('http://localhost:5050/api/analyses')
total_response = json.loads(f.text)
resultsets = total_response["response"]["resultSets"]


for resultset in resultsets:
    results = resultset["results"]
    for result in results:
        try:
            Analyses(**result)
        except ValidationError as e:
            print(e)
            continue
'''
