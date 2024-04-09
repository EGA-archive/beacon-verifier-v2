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

parser = argparse.ArgumentParser()
parser.add_argument("-url", "--url")
args = parser.parse_args()

class Endpoints(BaseModel, extra='forbid'):
    url: str
    returnedEntryType: str
    @field_validator('url')
    @classmethod
    def check_url(cls, v: str) -> str:
        if v.startswith('https://'):
            pass
        else:
            raise ValueError('url must be a valid https url')
        return v.title()
            
class Endpoint2(BaseModel, extra='forbid'):
    entryType: str
    openAPIEndpointsDefinition: Optional[str]=None
    rootUrl: str
    singleEntryUrl: Optional[str]=None
    filteringTermsUrl: Optional[str]=None
    endpoints: Optional[dict]=None
    @field_validator('rootUrl')
    @classmethod
    def check_rootUrl(cls, v: str) -> str:
        if v.startswith('https://'):
            pass
        else:
            raise ValueError('rootUrl must be a valid https url')
        return v.title()
    @field_validator('singleEntryUrl')
    @classmethod
    def check_singleEntryUrl(cls, v: str) -> str:
        if v.startswith('https://'):
            pass
        else:
            raise ValueError('singleEntryUrl must be a valid https url')
        return v.title()
    @field_validator('filteringTermsUrl')
    @classmethod
    def check_filteringTermsUrl(cls, v: str) -> str:
        if v.startswith('https://'):
            pass
        else:
            raise ValueError('filteringTermsUrl must be a valid https url')
        return v.title()
    @field_validator('endpoints')
    @classmethod
    def check_endpoints(cls, v: dict) -> dict:
        Endpoints(**v)

class Endpoint(BaseModel):
    @field_validator('*')
    @classmethod
    def check_all(cls, v: dict) -> dict:
        Endpoint2(**v)

class Map(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    schema_: str=Field(default=None, alias='$schema')
    endpointSets: dict
    @field_validator('endpointSets')
    @classmethod
    def check_endpointSets(cls, v: dict) -> dict:
        Endpoint(**v)



url = args.url + '/map'

f = requests.get(url)
total_response = json.loads(f.text)
resultsets = total_response["response"]
endpoints = resultsets["endpointSets"]
list_of_endpoints=[]
def list_endpoints(list_of_endpoints, endpoints):
    for k, v in endpoints.items():
        for k2, v2 in v.items():
            if k2 == 'rootUrl':
                list_of_endpoints.append(v2)
            elif k2 == 'endpoints':
                for k3, v3 in v2.items():
                    for k4, v4 in v3.items():
                        if k4 == 'url':
                            list_of_endpoints.append(v4)
    return list_of_endpoints

endpoints_to_verify = list_endpoints(list_of_endpoints, endpoints)

    

