import subprocess
import argparse
import requests
from biosamples import BiosamplesResultsetsResponse
from individuals import IndividualsResultsetsResponse
from genomicVariations import GenomicVariationsResultsetsResponse
from filtering_terms import FilteringTerms
from meta import Meta
from map import Map
from info import Info
from get_map import list_endpoints
from configuration import Configuration
from counts import CountResponse
from boolean import BooleanResponse
from resultsets import ResultsetsResponse
from pydantic import (
    BaseModel,
    ValidationError,
    field_validator,
    Field,
    PrivateAttr
)
import json

parser = argparse.ArgumentParser()
parser.add_argument("-url", "--url")
args = parser.parse_args()

url = args.url + '/map'
print("{}".format(url))
f = requests.get(url)
total_response = json.loads(f.text)
resultsets = total_response["response"]
endpoints = resultsets["endpointSets"]
list_of_endpoints=[]
endpoints_to_verify = list_endpoints(list_of_endpoints, endpoints)
meta = total_response["meta"]
try:
    Map(**resultsets)
    print("map is OK")
except ValidationError as e:
    print("map got the next validation errors:")
    print(e)

'''
try:
    Meta(**meta)
    print("metadata from map is OK")
except ValidationError as e:
    print("metadata from map got the next validation errors:")
    print(e)
'''

url = args.url + '/info'
print("{}".format(url))
f = requests.get(url)
total_response = json.loads(f.text)
resultsets = total_response["response"]
meta = total_response["meta"]
try:
    Info(**resultsets)
    print("info is OK")
except ValidationError as e:
    print("info got the next validation errors:")
    print(e)
'''
try:
    Meta(**meta)
    print("metadata from info is OK")
except ValidationError as e:
    print("metadata from info got the next validation errors:")
    print(e)
'''

url = args.url + '/configuration'
print("{}".format(url))
f = requests.get(url)
total_response = json.loads(f.text)
resultsets = total_response["response"]
meta = total_response["meta"]
try:
    Configuration(**resultsets)
    print("configuration is OK")
except ValidationError as e:
    print("configuration got the next validation errors:")
    print(e)
'''
try:
    Meta(**meta)
    print("metadata from configuration is OK")
except ValidationError as e:
    print("metadata from configuration got the next validation errors:")
    print(e)
'''


for endpoint in endpoints_to_verify:
    if endpoint.endswith('biosamples') and 'g_variants' in endpoint:
        pass
    elif endpoint.endswith('biosamples') and 'd}' not in endpoint:
        url = args.url + '/biosamples'
        f = requests.get(url)
        total_response = json.loads(f.text)
        response = total_response["response"]
        dataset = response["resultSets"][0]["id"]
        meta = total_response["meta"]
        try:
            granularity = meta["returnedGranularity"]
        except Exception:
            granularity = meta["receivedRequestSummary"]["requestedGranularity"]

        print("{}".format(url))
        try:
            Meta(**meta)
            print("metadata from biosamples is OK")
        except ValidationError as e:
            print("metadata from biosamples got the next validation errors:")
            print(e)
        try:
            if granularity == 'record':
                BiosamplesResultsetsResponse(**total_response)
            elif granularity == 'count':
                CountResponse(**total_response)
            elif granularity == 'boolean':
                BooleanResponse(**total_response)
            print("{} is OK".format(dataset))
        except ValidationError as e:
            print("{} got the next validation errors:".format(dataset))
            print(e)

    elif endpoint.endswith('g_variants') and 'd}' not in endpoint:
        url = args.url + '/g_variants'
        f = requests.get(url)
        total_response = json.loads(f.text)
        response = total_response["response"]
        dataset = response["resultSets"][0]["id"]

        meta = total_response["meta"]
        try:
            granularity = meta["returnedGranularity"]
        except Exception:
            granularity = meta["receivedRequestSummary"]["requestedGranularity"]

        print("{}".format(url))
        try:
            Meta(**meta)
            print("metadata from g_variants is OK")
        except ValidationError as e:
            print("metadata from g_variants got the next validation errors:")
            print(e)
        try:
            if granularity == 'record':
                GenomicVariationsResultsetsResponse(**total_response)
            elif granularity == 'count':
                CountResponse(**total_response)
            elif granularity == 'boolean':
                BooleanResponse(**total_response)
            print("{} is OK".format(dataset))
        except ValidationError as e:
            print("{} got the next validation errors:".format(dataset))
            print(e)
    elif endpoint.endswith('individuals') and 'd}' not in endpoint:
        url = args.url + '/individuals'
        f = requests.get(url)
        total_response = json.loads(f.text)
        dataset = response["resultSets"][0]["id"]

        meta = total_response["meta"]
        try:
            granularity = meta["returnedGranularity"]
        except Exception:
            granularity = meta["receivedRequestSummary"]["requestedGranularity"]

        print("{}".format(url))
        try:
            Meta(**meta)
            print("metadata from g_variants is OK")
        except ValidationError as e:
            print("metadata from g_variants got the next validation errors:")
            print(e)
        try:
            if granularity == 'record':
                IndividualsResultsetsResponse(**total_response)
            elif granularity == 'count':
                print(total_response)
                CountResponse(**total_response)
            elif granularity == 'boolean':
                BooleanResponse(**total_response)
            print("{} is OK".format(dataset))
        except ValidationError as e:
            print("{} got the next validation errors:".format(dataset))
            print(e)

    elif endpoint.endswith('filtering_terms'):
        url = args.url + '/filtering_terms'
        f = requests.get(url)
        total_response = json.loads(f.text)
        response = total_response["response"]

        meta = total_response["meta"]

        print("{}".format(url))
        try:
            FilteringTerms(**response)
            print("filtering_terms is OK".format(dataset))
        except ValidationError as e:
            print("filtering_terms got the next validation errors:")
            print(e)

'''

string='python3 analyses.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)

string='python3 cohorts.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 datasets.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 filtering_terms.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 genomicVariations.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 individuals.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
string='python3 runs.py' + ' -url ' + args.url
bash_string = (string)
try:
    bash = subprocess.check_output([bash_string], shell=True)
    stringed_bash = bash.decode("utf-8") 
    replaced_stringed_bash=stringed_bash.replace("'","")
    print(replaced_stringed_bash)
except subprocess.CalledProcessError as e:
    output = e.output
    print(output)
    '''