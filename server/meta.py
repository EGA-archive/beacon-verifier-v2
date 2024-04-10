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

parser = argparse.ArgumentParser()
parser.add_argument("-url", "--url")
args = parser.parse_args()

class RequestedSchema(BaseModel):
    entityType: Optional[str] = None
    schema_: Optional[str]=Field(default=None, alias='schema')

class Pagination(BaseModel):
    currentPage: Optional[str] = None
    limit: Optional[int] = None
    nextPage: Optional[str] = None
    previousPage: Optional[str] = None
    skip: Optional[int] = None

class ReceivedRequestSummary(BaseModel):
    apiVersion: str
    filters: Optional[list] = None
    includeResultsetResponses: Optional[str] = None
    pagination: dict
    requestParameters: Optional[dict] = None
    requestedGranularity: str
    requestedSchemas: list
    testMode: Optional[bool] = None
    @field_validator('filters')
    @classmethod
    def check_filters(cls, v: list) -> list:
        for filter in v:
            if isinstance(filter, str):
                pass
            else:
                raise ValueError('filter in receivedRequestSummary must be a string')
    @field_validator('includeResultsetResponses')
    @classmethod
    def check_includeResultsetResponses(cls, v: str) -> str:
        if v in ['HIT', 'MISS', 'ALL', 'NONE']:
            pass
        else:
            raise ValueError('includeResultsetResponses must be one between HIT, MISS, ALL, NONE')
        return v.title()
    @field_validator('pagination')
    @classmethod
    def check_pagination(cls, v: dict) -> dict:
        Pagination(**v)
    @field_validator('requestedGranularity')
    @classmethod
    def check_requestedGranularity(cls, v: str) -> str:
        if v in ['boolean', 'count', 'aggregated', 'record']:
            pass
        else:
            raise ValueError('requestedGranularity must be one between boolean, count, aggregated or record')
        return v.title()
    @field_validator('requestedSchemas')
    @classmethod
    def check_requestedSchemas(cls, v: list) -> list:
        for requestedSchema in v:
            RequestedSchema(**requestedSchema)

class Meta(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    apiVersion: str
    beaconId: str
    receivedRequestSummary: dict
    returnedGranularity: Optional[str] = None
    returnedSchemas: list
    testMode: Optional[dict] = None
    @field_validator('receivedRequestSummary')
    @classmethod
    def check_receivedRequestSummary(cls, v: dict) -> dict:
        ReceivedRequestSummary(**v)
    @field_validator('returnedSchemas')
    @classmethod
    def check_returnedSchemas(cls, v: list) -> list:
        for returnedSchema in v:
            RequestedSchema(**returnedSchema)
    @field_validator('returnedGranularity')
    @classmethod
    def check_returnedGranularity(cls, v: str) -> str:
        if v in ['boolean', 'count', 'aggregated', 'record']:
            pass
        else:
            raise ValueError('returnedGranularity must be one between boolean, count, aggregated or record')
        return v.title()