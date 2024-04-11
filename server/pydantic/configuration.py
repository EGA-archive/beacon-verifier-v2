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

class Description(BaseModel):
    description: str

class ReferenceToSchemaDefinition(BaseModel):
    referenceToSchemaDefinition: str
    schemaVersion: Optional[str]=None
    description: Optional[str]=None

class ReferenceToSchemaDefinitionAndBasicElement(BaseModel):
    referenceToSchemaDefinition: str
    schemaVersion: Optional[str]=None
    description: Optional[str]=None
    id: str
    name: str

class BasicElement(BaseModel):
    id: str
    name: str

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
            
class EntryTypeDefinition(BaseModel):
    aCollectionOf: Optional[list]=None
    additionallySupportedSchemas: Optional[list]=None
    defaultSchema: dict
    description: Optional[str]=None
    filteringTerms: Optional[str]=None
    id: str
    name: str
    nonFilteredQueriesAllowed: Optional[bool]=None
    ontologyTermForThisType: OntologyTerm
    partOfSpecification: str
    @field_validator('aCollectionOf')
    @classmethod
    def check_aCollectionOf(cls, v: list) -> list:
        for element in v:
            BasicElement(**element)
    @field_validator('additionallySupportedSchemas')
    @classmethod
    def check_additionallySupportedSchemas(cls, v: list) -> list:
        for element in v:
            ReferenceToSchemaDefinitionAndBasicElement(**element)
    @field_validator('defaultSchema')
    @classmethod
    def check_defaultSchema(cls, v: dict) -> dict:
        ReferenceToSchemaDefinitionAndBasicElement(**v)
    
class MaturityAttributes(BaseModel):
    productionStatus: str
    @field_validator('productionStatus')
    @classmethod
    def check_productionStatus(cls, v: str) -> str:
        if v in ['DEV', 'TEST', 'PROD']:
            pass
        else:
            raise ValueError('productionStatus must be DEV, TEST or PROD')
        return v.title()
    
class SecurityAttributes(BaseModel):
    defaultGranularity: str
    securityLevels: list
    @field_validator('defaultGranularity')
    @classmethod
    def check_defaultGranularity(cls, v: str) -> str:
        if v in ['boolean', 'count', 'aggregated', 'record']:
            pass
        else:
            raise ValueError('defaultGranularity must be boolean, count, aggregated or record')
        return v.title()
    @field_validator('securityLevels')
    @classmethod
    def check_securityLevels(cls, v: str) -> str:
        for securityLevel in v:
            if securityLevel in ['PUBLIC', 'REGISTERED', 'CONTROLLED']:
                pass
            else:
                raise ValueError('securityLevel must be PUBLIC, REGISTERED or CONTROLLED')
        return securityLevel.title()

class Configuration(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    schema_: str=Field(default=None, alias='$schema')
    entryTypes: dict
    maturityAttributes: dict
    securityAttributes: Optional[dict] = None
    @field_validator('entryTypes')
    @classmethod
    def check_entryTypes(cls, v: dict) -> dict:
        for key, value in v.items():
            if key in ['analysis', 'biosample', 'cohort', 'dataset', 'genomicVariant', 'individual', 'run']:
                EntryTypeDefinition(**value)
            else:
                raise ValueError('entryType must be one of analysis, biosample, cohort, dataset, genomicVariant, individual, run')
    @field_validator('maturityAttributes')
    @classmethod
    def check_createDateTime(cls, v: dict) -> dict:
        MaturityAttributes(**v)
    @field_validator('securityAttributes')
    @classmethod
    def check_environment(cls, v: str) -> str:
        SecurityAttributes(**v)

    

