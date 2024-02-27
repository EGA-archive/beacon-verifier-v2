import json
import re
import inspect
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    field_validator,
    Field,
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

class Age(BaseModel, extra='forbid'):
    iso8601duration: str

class AgeRange(BaseModel, extra='forbid'):
    end: Age
    start: Age

class GestationalAge(BaseModel, extra='forbid'):
    days: Optional[int] = None
    weeks: int

class TimeInterval(BaseModel, extra='forbid'):
    end: str
    start: str

class ReferenceRange(BaseModel, extra='forbid'):
    high: Union[int,float]
    low: Union[int, float]
    unit: OntologyTerm

class Quantity(BaseModel, extra='forbid'):
    referenceRange: Optional[ReferenceRange]
    unit: OntologyTerm
    value: Union[int, float]

class TypedQuantity(BaseModel, extra='forbid'):
    quantity: Quantity
    quantityType: OntologyTerm

class Members(BaseModel, extra='forbid'):
    affected: bool
    memberId: str
    role: OntologyTerm

class Diseases(BaseModel, extra='forbid'):
    ageOfOnset: Optional[Union[str,dict]]=None
    diseaseCode: OntologyTerm
    familyHistory: Optional[bool]=None
    notes: Optional[str]=None
    severity: Optional[OntologyTerm]=None
    stage: Optional[OntologyTerm]=None
    @field_validator('ageOfOnset')
    @classmethod
    def check_ageOfOnset(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('ageOfOnset, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
        elif isinstance(v, dict):
            fits_in_class=False
            try:
                Age(**v)
                fits_in_class=True
            except Exception:
                fits_in_class=False
            if fits_in_class == False:
                try:
                    AgeRange(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    GestationalAge(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    TimeInterval(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    OntologyTerm(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                raise ValueError('ageOfOnset, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')

class Ethnicity(BaseModel, extra='forbid'):
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
    
class Exposures(BaseModel, extra='forbid'):
    ageAtExposure: Age
    date: Optional[str]
    duration: str
    exposureCode: OntologyTerm
    unit: OntologyTerm
    value: Optional[Union[int, float]]

class GeographicOrigin(BaseModel, extra='forbid'):
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

class InterventionsOrProcedures(BaseModel, extra='forbid'):
    ageAtProcedure: Optional[Union[str,dict]]=None
    bodySite: Optional[OntologyTerm]=None
    dateOfProcedure: Optional[str]=None
    procedureCode: OntologyTerm
    @field_validator('ageAtProcedure')
    @classmethod
    def check_ageAtProcedure(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('ageAtProcedure, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
        elif isinstance(v, dict):
            fits_in_class=False
            try:
                Age(**v)
                fits_in_class=True
            except Exception:
                fits_in_class=False
            if fits_in_class == False:
                try:
                    AgeRange(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    GestationalAge(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    TimeInterval(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    OntologyTerm(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                raise ValueError('ageAtProcedure, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
            
class Measurement(BaseModel, extra='forbid'):
    assayCode: OntologyTerm
    date: Optional[str] = None
    measurementValue: Union[Quantity, OntologyTerm, list]
    notes: Optional[str]=None
    observationMoment: Optional[Union[str,dict]]=None
    procedure: Optional[dict] = None
    @field_validator('measurementValue')
    @classmethod
    def check_measurementValue(cls, v: Union[Quantity, OntologyTerm, list]= Field(union_mode='left_to_right')) -> Union[Quantity, OntologyTerm, list]:
        if isinstance(v, list):
            for measurement in v:
                TypedQuantity(**measurement)
    @field_validator('observationMoment')
    @classmethod
    def check_observationMoment(cls, v: Union[str,dict]= Field(union_mode='left_to_right')) -> Union[str,dict]:
        if isinstance(v, str):
            try:
                parse(v)
            except Exception as e:
                raise ValueError('observationMoment, if string, must be Timestamp, getting this error: {}'.format(e))
            return v.title()
        elif isinstance(v, dict):
            fits_in_class=False
            try:
                Age(**v)
                fits_in_class=True
            except Exception:
                fits_in_class=False
            if fits_in_class == False:
                try:
                    AgeRange(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    GestationalAge(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    TimeInterval(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                try:
                    OntologyTerm(**v)
                    fits_in_class=True
                except Exception:
                    fits_in_class=False
            if fits_in_class == False:
                raise ValueError('observationMoment, if object, must be any format possible between age, ageRange, gestationalAge, timeInterval or OntologyTerm')
    @field_validator('procedure')
    @classmethod
    def check_procedure(cls, v: dict) -> dict:
        InterventionsOrProcedures(**v)

class Pedigrees(BaseModel, extra='forbid'):
    disease: Diseases
    id: str
    members: list
    numSubjects: Optional[int]
    @field_validator('members')
    @classmethod
    def check_members(cls, v: dict) -> dict:
        for member in v:
            Members(**member)

class PhenotypicFeatures(BaseModel, extra='forbid'):
    evidence: Diseases
    id: str
    members: list
    numSubjects: Optional[int]
    @field_validator('members')
    @classmethod
    def check_members(cls, v: dict) -> dict:
        for member in v:
            Members(**member)

class Individuals(BaseModel, extra='forbid'):
    _id: Optional[str] = None
    diseases: Optional[list] = None
    ethnicity: Optional[dict] = None
    exposures: Optional[list] = None
    geographicOrigin: Optional[object] = None
    id: str
    info: Optional[object] = None
    interventionsOrProcedures: Optional[list] = None
    karyotypicSex: Optional[str] = None
    measures: Optional[list]=None
    pedigrees: Optional[list] = None
    phenotypicFeatures: Optional[list] = None
    sex: dict
    treatments: Optional[list] = None
    @field_validator('ethnicity')
    @classmethod
    def check_ethnicity(cls, v: dict) -> dict:
        Ethnicity(**v)
    @field_validator('diseases')
    @classmethod
    def check_diseases(cls, v: list) -> list:
        for disease in v:
            Diseases(**disease)
    @field_validator('exposures')
    @classmethod
    def check_exposures(cls, v: list) -> list:
        for exposure in v:
            Exposures(**exposure)
    @field_validator('geographicOrigin')
    @classmethod
    def check_geographicOrigin(cls, v: dict) -> dict:
        GeographicOrigin(**v)
    @field_validator('interventionsOrProcedures')
    @classmethod
    def check_diseases(cls, v: list) -> list:
        for procedure in v:
            InterventionsOrProcedures(**procedure)
    @field_validator('measures')
    @classmethod
    def check_measures(cls, v: list) -> list:
        for measure in v:
            Measurement(**measure)
    @field_validator('pedigrees')
    @classmethod
    def check_pedigrees(cls, v: list) -> list:
        for pedigree in v:
            Measurement(**pedigree)
    @field_validator('phenotypicFeatures')
    @classmethod
    def check_phenotypicFeatures(cls, v: list) -> list:
        for phenotypicFeature in v:
            Measurement(**phenotypicFeature)

with open("test.json", "r") as f:
    docs = json.load(f)
    try:
        for doc in docs:
            Individuals(**doc)
    except ValidationError as e:
        print(e)
''' 
f = requests.get('http://localhost:5050/api/individuals')
total_response = json.loads(f.text)
resultsets = total_response["response"]["resultSets"]


for resultset in resultsets:
    results = resultset["results"]
    for result in results:
        try:
            Individuals(**result)
        except ValidationError as e:
            print(e)
            continue
'''