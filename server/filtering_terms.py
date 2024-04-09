import json
import re
import argparse
from dateutil.parser import parse
from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    field_validator,
    PrivateAttr,
)

from typing import Optional, Union
import requests

parser = argparse.ArgumentParser()
parser.add_argument("-url", "--url")
args = parser.parse_args()
            
class FilteringTerm(BaseModel, extra='forbid'):
    id: str
    type: str
    label: Optional[str] = None
    scope: Optional[list] = None
    @field_validator('type', 'id')
    @classmethod
    def id_must_be_CURIE(cls, v: Union[str,list], info: ValidationInfo) -> Union[str,list]:
        isontology=False
        if info.field_name == 'type':
            if v == 'ontology':
                isontology=True
        if info.field_name == 'id' and isontology==True:
            if re.match("[A-Za-z0-9]+:[A-Za-z0-9]", v):
                pass
            else:
                raise ValueError('id must be CURIE, e.g. NCIT:C42331')
            return v.title()
    @field_validator('scope')
    @classmethod
    def check_scope(cls, v: list) -> list:
        for scope in v:
            if scope in ["analyse","biosample","cohort","dataset","individual","genomicVariation","run"]:
                pass
            else:
                raise ValueError('scope must be a valid array with items as strings from ["analyses","biosamples","cohorts","datasets","individuals","genomicVariations","runs"]')
            return scope.title()    

class FilteringTerms(BaseModel, extra='forbid'):
    def __init__(self, **data) -> None:
        for private_key in self.__class__.__private_attributes__.keys():
            try:
                value = data.pop(private_key)
            except KeyError:
                pass

        super().__init__(**data)
    _id: Optional[str] = PrivateAttr()
    filteringTerms: Optional[list] = None
    @field_validator('filteringTerms')
    @classmethod
    def check_filteringTerms(cls, v: list) -> list:
        for filteringTerm in v:
            FilteringTerm(**filteringTerm)

url = args.url + '/filtering_terms'

f = requests.get(url)
total_response = json.loads(f.text)

resultsets = total_response["response"]
print("{}".format(url))
try:
    FilteringTerms(**resultsets)
    print("is OK")
except ValidationError as e:
    print("filtering_terms got the next validation errors:")
    print(e)
    

