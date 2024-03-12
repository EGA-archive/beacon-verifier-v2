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

print("analyses:")
for resultset in resultsets:
    results = resultset["results"]
    dataset = resultset["id"]
    try:
        for result in results:
            Analyses(**result)
        
        print("{} is OK".format(dataset))
    except ValidationError as e:
        print("{} got the next validation errors:".format(dataset))
        print(e)
        continue

