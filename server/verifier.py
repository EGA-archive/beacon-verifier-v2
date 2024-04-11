from classes import JSONSchemaValidator
import argparse
import requests
import json
from jsonschema import validate, RefResolver, Draft202012Validator
import os
from get_map import list_endpoints

parser = argparse.ArgumentParser()
parser.add_argument("-url", "--url")
args = parser.parse_args()

def endpoint_check(endpoint:str, id_parameter: bool):
    if endpoint != 'genomicVariations' and id_parameter == False:
        url = args.url + '/' + endpoint
        f = requests.get(url)
        total_response = json.loads(f.text)
    elif id_parameter == False:
        url = args.url + '/' + 'g_variants'
        f = requests.get(url)
        total_response = json.loads(f.text)
    else:
        last_part = endpoint.split('/')
        url = args.url + '/' + last_part[-3]
        f = requests.get(url)
        total_response = json.loads(f.text)
        if last_part[-3] == 'g_variants':
            id = total_response["response"]["resultSets"][0]["results"][0]["variantInternalId"]
            url = endpoint.replace('{variantInternalId}', id)
        elif last_part[-3] == 'cohorts':
            id = total_response["response"]["collections"][0]["id"]
            url = endpoint.replace('{id}', id)
        elif last_part[-3] == 'datasets':
            id = total_response["response"]["collections"][0]["id"]
            url = endpoint.replace('{id}', id)
        else:
            id = total_response["response"]["resultSets"][0]["results"][0]["id"]
            url = endpoint.replace('{id}', id)
       
        f = requests.get(url)
        total_response = json.loads(f.text)
        endpoint = last_part[-1]
        if endpoint == 'g_variants':
            endpoint = 'genomicVariations'
        
        
    if endpoint in ['cohorts', 'datasets']:
        resultsets = total_response["response"]["collections"]
    else:
        try:
            resultsets=total_response["response"]["resultSets"][0]["results"]
        except Exception:
            return('empty response for {}'.format(url))
    meta = total_response["meta"]
    print("{}".format(url))
    try:
        granularity = meta["returnedGranularity"]
    except Exception:
        granularity = meta["receivedRequestSummary"]["requestedGranularity"]
    if granularity == 'record':
        if endpoint in ['cohorts', 'datasets']:
            with open('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconCollectionsResponse.json', 'r') as f:
                response = json.load(f)
            schema_path = 'file:///{0}/'.format(
                    os.path.dirname('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconCollectionsResponse.json').replace("\\", "/"))
        else:
            with open('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconResultsetsResponse.json', 'r') as f:
                response = json.load(f)
            schema_path = 'file:///{0}/'.format(
                    os.path.dirname('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconResultsetsResponse.json').replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        JSONSchemaValidator.validate(total_response, response, resolver)
        with open('beacon-verifier-v2/server/ref_schemas/models/json/beacon-v2-default-model/' +endpoint+'/defaultSchema.json', 'r') as f:
            response = json.load(f)
        schema_path = 'file://{0}/'.format(
                os.path.dirname('beacon-verifier-v2/server/ref_schemas/models/json/beacon-v2-default-model/'+endpoint+'/defaultSchema.json').replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        for result in resultsets:
            JSONSchemaValidator.validate(result, response, resolver)
    elif granularity == 'count':
        with open('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconCountResponse.json', 'r') as f:
            response = json.load(f)
        schema_path = 'file:///{0}/'.format(
                os.path.dirname('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconCountResponse.json').replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        JSONSchemaValidator.validate(total_response, response, resolver)
    elif granularity == 'boolean':
        with open('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconBooleanResponse.json', 'r') as f:
            response = json.load(f)
        schema_path = 'file:///{0}/'.format(
                os.path.dirname('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconBooleanResponse.json').replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        JSONSchemaValidator.validate(total_response, response, resolver)

url = args.url + '/map'
f = requests.get(url)
total_response = json.loads(f.text)
resultsets = total_response["response"]
endpoints = resultsets["endpointSets"]
list_of_endpoints=[]
endpoints_to_verify = list_endpoints(list_of_endpoints, endpoints)

url = args.url + '/map'
print("{}".format(url))
f = requests.get(url)
total_response = json.loads(f.text)
with open('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconMapResponse.json', 'r') as f:
    map = json.load(f)
schema_path = 'file:///{0}/'.format(
        os.path.dirname('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconMapResponse.json').replace("\\", "/"))
resolver = RefResolver(schema_path, map)
JSONSchemaValidator.validate(total_response, map, resolver)

url = args.url + '/info'
print("{}".format(url))
f = requests.get(url)
total_response = json.loads(f.text)
with open('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconInfoResponse.json', 'r') as f:
    info = json.load(f)
schema_path = 'file:///{0}/'.format(
        os.path.dirname('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconInfoResponse.json').replace("\\", "/"))
resolver = RefResolver(schema_path, info)
JSONSchemaValidator.validate(total_response, info, resolver)

url = args.url + '/configuration'
print("{}".format(url))
f = requests.get(url)
total_response = json.loads(f.text)
with open('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconConfigurationResponse.json', 'r') as f:
    configuration = json.load(f)
schema_path = 'file:///{0}/'.format(
        os.path.dirname('beacon-verifier-v2/server/ref_schemas/framework/json/responses/beaconConfigurationResponse.json').replace("\\", "/"))
resolver = RefResolver(schema_path, configuration)
JSONSchemaValidator.validate(total_response, configuration, resolver)

for endpoint in endpoints_to_verify:
    if endpoint.endswith('analyses') and 'd}' not in endpoint:
        endpoint_check('analyses', False)
    elif endpoint.endswith('analyses'):
        endpoint_check(endpoint, True)
    elif endpoint.endswith('biosamples') and 'd}' not in endpoint:
        endpoint_check('biosamples', False)
    elif endpoint.endswith('biosamples'):
         endpoint_check(endpoint, True)
    elif endpoint.endswith('g_variants') and 'd}' not in endpoint:
        endpoint_check('genomicVariations', False)
    elif endpoint.endswith('g_variants'):
        endpoint_check(endpoint, True)
    elif endpoint.endswith('individuals') and 'd}' not in endpoint:
        endpoint_check('individuals', False)
    elif endpoint.endswith('individuals'):
        endpoint_check(endpoint, True)
    elif endpoint.endswith('runs') and 'd}' not in endpoint:
        endpoint_check('runs', False)
    elif endpoint.endswith('runs'):
        endpoint_check(endpoint, True)
    elif endpoint.endswith('datasets') and 'd}' not in endpoint:
        endpoint_check('datasets', False)
    elif endpoint.endswith('datasets'):
        endpoint_check(endpoint, True)
    elif endpoint.endswith('cohorts') and 'd}' not in endpoint:
        endpoint_check('cohorts', False)
    elif endpoint.endswith('cohorts'):
        endpoint_check(endpoint, True)
