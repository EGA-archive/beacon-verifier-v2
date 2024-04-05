import json
import argparse
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    ValidationError,
    PrivateAttr
)

from typing import Optional, Union
import requests
from meta import Meta

parser = argparse.ArgumentParser()
parser.add_argument("-url", "--url")
args = parser.parse_args()

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

url = args.url + '/analyses'

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
            Analyses(**result)
        
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

url = args.url + '/g_variants/' + uri_id + '/analyses'

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
            Analyses(**result)
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

url = args.url + '/individuals/' + uri_id + '/analyses'

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
            Analyses(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue

url = args.url + '/biosamples'

e = requests.get(url)
total_response = json.loads(e.text)
resultsets = total_response["response"]["resultSets"]
results = resultsets[0]["results"]
uri_id = results[0]["id"]

url = args.url + '/biosamples/' + uri_id + '/analyses'

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
            Analyses(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue

url = args.url + '/runs'

e = requests.get(url)
total_response = json.loads(e.text)
resultsets = total_response["response"]["resultSets"]
results = resultsets[0]["results"]
uri_id = results[0]["id"]

url = args.url + '/runs/' + uri_id + '/analyses'

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
            Analyses(**result)
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue
