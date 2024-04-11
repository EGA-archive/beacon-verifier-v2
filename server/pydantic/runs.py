import json
import re
import argparse
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

class Runs(BaseModel):
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

url = args.url + '/runs'

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
            Runs(**result)
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

url = args.url + '/datasets/' + uri_id + '/runs'

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
            Runs(**result)
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

url = args.url + '/g_variants/' + uri_id + '/runs'

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
            Runs(**result)
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

url = args.url + '/individuals/' + uri_id + '/runs'

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
            Runs(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue