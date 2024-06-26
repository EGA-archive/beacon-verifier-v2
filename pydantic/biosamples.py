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

parser = argparse.ArgumentParser()
parser.add_argument("-url", "--url")
args = parser.parse_args()

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

class Age(BaseModel):
    iso8601duration: str

class AgeRange(BaseModel):
    end: Age
    start: Age

class GestationalAge(BaseModel):
    days: Optional[int] = None
    weeks: int

class TimeInterval(BaseModel):
    end: str
    start: str

class ReferenceRange(BaseModel):
    high: Union[int,float]
    low: Union[int, float]
    unit: OntologyTerm

class Quantity(BaseModel):
    referenceRange: Optional[ReferenceRange] = None
    unit: OntologyTerm
    value: Union[int, float]

class TypedQuantity(BaseModel):
    quantity: Quantity
    quantityType: OntologyTerm

class InterventionsOrProcedures(BaseModel):
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
            
class Measurement(BaseModel):
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

class Handover(BaseModel):
    handoverType: OntologyTerm
    note: Optional[str] = None
    url: str

class SummaryResponseSection(BaseModel):
    exists: bool
    numTotalResults: int

class Biosamples(BaseModel):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    biosampleStatus: OntologyTerm
    collectionDate: Optional[str] = None
    collectionMoment: Optional[str] = None
    diagnosticMarkers: Optional[list] = None
    histologicalDiagnosis: Optional[OntologyTerm] = None
    id: str
    individualId: Optional[str] = None
    info: Optional[dict] = None
    measurements: Optional[list] = None
    notes: Optional[str]=None
    obtentionProcedure: Optional[InterventionsOrProcedures] = None
    pathologicalStage: Optional[OntologyTerm] = None
    pathologicalTnmFinding: Optional[list] = None
    phenotypicFeatures: Optional[list] = None
    sampleOriginDetail: Optional[OntologyTerm] = None
    sampleOriginType: OntologyTerm
    sampleProcessing: Optional[OntologyTerm] = None
    sampleStorage: Optional[OntologyTerm] = None
    tumorGrade: Optional[OntologyTerm] = None
    tumorProgression: Optional[OntologyTerm] = None
    @field_validator('diagnosticMarkers')
    @classmethod
    def check_diagnosticMarkers(cls, v: list) -> list:
        for diagnosticMarker in v:
            OntologyTerm(**diagnosticMarker)
    @field_validator('measurements')
    @classmethod
    def check_measurements(cls, v: list) -> list:
        for measurement in v:
            Measurement(**measurement)

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
    @field_validator('results')
    @classmethod
    def check_results(cls, v: list) -> list:
        if v != []:
            for result in v:
                Biosamples(**result)
                    
class BiosamplesResultsets(BaseModel):
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
    
class BiosamplesResultsetsResponse(BaseModel):
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
    response: BiosamplesResultsets
    responseSummary: SummaryResponseSection
    @field_validator('beaconHandovers')
    @classmethod
    def check_beaconHandovers(cls, v: list) -> list:
        for handover in v:
            if isinstance(handover, dict):
                try:
                    Handover(**handover)
                except Exception as e:
                    print(e)
            else:
                raise ValueError('Handover must be an object')
'''
url = args.url + '/biosamples'

f = requests.get(url)
total_response = json.loads(f.text)
resultsets = total_response["response"]["resultSets"]
meta = total_response["meta"]

print("{}".format(url))
for resultset in resultsets:
    results = resultset["results"]
    dataset = resultset["id"]
    try:
        Meta(**meta)
        for result in results:
            uri_id=result["id"]
            Biosamples(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue

url = args.url + '/biosamples'

a = requests.get(url)
total_response = json.loads(a.text)
resultsets = total_response["response"]["resultSets"]
meta = total_response["meta"]

print("{}".format(url))
for resultset in resultsets:
    results = resultset["results"]
    dataset = resultset["id"]
    try:
        Meta(**meta)
        for result in results:
            Biosamples(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue

url = args.url + '/g_variants'

b = requests.get(url)
total_response = json.loads(b.text)
resultsets = total_response["response"]["resultSets"]
results = resultsets[0]["results"]
uri_id = results[0]["variantInternalId"]

url = args.url + '/g_variants/' + uri_id + '/biosamples'

f = requests.get(url)
total_response = json.loads(f.text)
resultsets = total_response["response"]["resultSets"]
meta = total_response["meta"]

print("{}".format(url))
for resultset in resultsets:
    results = resultset["results"]
    dataset = resultset["id"]
    try:
        Meta(**meta)
        for result in results:
            Biosamples(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue

url = args.url + '/datasets'

c = requests.get(url)

total_response = json.loads(c.text)

resultsets = total_response["response"]["collections"]
uri_id = resultsets[0]["id"]

url = args.url + '/datasets/' + uri_id + '/biosamples'

d = requests.get(url)
total_response = json.loads(d.text)
resultsets = total_response["response"]["resultSets"]
meta = total_response["meta"]

print("{}".format(url))
for resultset in resultsets:
    results = resultset["results"]
    dataset = resultset["id"]
    try:
        Meta(**meta)
        for result in results:
            Biosamples(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue

url = args.url + '/individuals'

e = requests.get(url)
total_response = json.loads(e.text)
resultsets = total_response["response"]["resultSets"]
results = resultsets[0]["results"]
uri_id = results[0]["id"]

url = args.url + '/individuals/' + uri_id + '/biosamples'

f = requests.get(url)
total_response = json.loads(f.text)
resultsets = total_response["response"]["resultSets"]
meta = total_response["meta"]

print("{}".format(url))
for resultset in resultsets:
    results = resultset["results"]
    dataset = resultset["id"]
    try:
        Meta(**meta)
        for result in results:
            Biosamples(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue
'''