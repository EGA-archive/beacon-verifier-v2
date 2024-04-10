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
            
class BeaconOrganization(BaseModel):
    address: Optional[str]=None
    contactUrl: Optional[str]=None
    description: Optional[str]=None
    id: str
    info: Optional[dict]=None
    logoUrl: Optional[str]=None
    name: str
    welcomeUrl: Optional[str]=None
    @field_validator('welcomeUrl')
    @classmethod
    def check_welcomeUrl(cls, v: str) -> str:
        if v.startswith('https://'):
            pass
        else:
            raise ValueError('welcomeUrl must be a valid https url')
        return v.title()
    @field_validator('logoUrl')
    @classmethod
    def check_logoUrl(cls, v: str) -> str:
        if v.startswith('https://'):
            pass
        else:
            raise ValueError('logoUrl must be a valid https url')
        return v.title()

class Info(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    alternativeUrl: Optional[str] = None
    apiVersion: Optional[str] = None
    createDateTime: Optional[str] = None
    description: str
    environment: Optional[str] = None
    id: str
    info: Optional[dict] = None
    name: str
    organization: dict
    updateDateTime: Optional[str] = None
    version: Optional[str] = None
    welcomeUrl: Optional[str] = None
    @field_validator('alternativeUrl')
    @classmethod
    def check_alternativeUrl(cls, v: str) -> str:
        if v.startswith('https://'):
            pass
        else:
            raise ValueError('alternativeUrl must be a valid https url')
        return v.title()
    @field_validator('createDateTime')
    @classmethod
    def check_createDateTime(cls, v: str) -> str:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                try: 
                    parse(v)
                except Exception:
                    raise ValueError('ageAtProcedure, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
    @field_validator('environment')
    @classmethod
    def check_environment(cls, v: str) -> str:
        if v in ['prod', 'test', 'dev', 'staging']:
            pass
        else:
            raise ValueError('environment must be one between prod, test, dev, staging')
        return v.title()
    @field_validator('organization')
    @classmethod
    def check_organization(cls, v: dict) -> dict:
        BeaconOrganization(**v)
    @field_validator('updateDateTime')
    @classmethod
    def check_updateDateTime(cls, v: str) -> str:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                try: 
                    parse(v)
                except Exception:
                    raise ValueError('updateDateTime must be a datetime in ISO 8601 format')
            return v.title()
    @field_validator('welcomeUrl')
    @classmethod
    def check_welcomeUrl(cls, v: str) -> str:
        if v.startswith('https://'):
            pass
        else:
            raise ValueError('welcomeUrl must be a valid https url')
        return v.title()

    

