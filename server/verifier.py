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

root_path = '/usr/src/app/'

def list_endpoints(list_of_endpoints, endpoints):
    for k, v in endpoints.items():
        for k2, v2 in v.items():
            if k2 == 'rootUrl':
                list_of_endpoints.append(v2)
            elif k2 == 'endpoints':
                for k3, v3 in v2.items():
                    for k4, v4 in v3.items():
                        if k4 == 'url':
                            list_of_endpoints.append(v4)

    return list_of_endpoints

def endpoint_check(endpoint:str, id_parameter: bool, url: str):
    endpoint_validation=[]
    root_path = '/usr/src/app/'
    if endpoint != 'genomicVariations' and id_parameter == False:
        url = url + '/' + endpoint
        f = requests.get(url)
        total_response = json.loads(f.text)
    elif id_parameter == False:
        url = url + '/' + 'g_variants'
        f = requests.get(url)
        total_response = json.loads(f.text)
    else:
        last_part = endpoint.split('/')
        url = url + '/' + last_part[-3]
        try:
            f = requests.get(url)
            total_response = json.loads(f.text)
        except Exception:
            raise ValueError('{} is not a valid URL. Please review urls from /map endpoint'.format(url))
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
        
        
    meta = total_response["meta"]
    endpoint_validation.append(url)
    try:
        granularity = meta["returnedGranularity"]
    except Exception:
        granularity = meta["receivedRequestSummary"]["requestedGranularity"]
    if endpoint in ['cohorts', 'datasets']:
        resultsets = total_response["response"]["collections"]
    else:
        try:
            resultsets=total_response["response"]["resultSets"][0]["results"]
        except Exception:
            granularity = 'boolean'
    if granularity == 'record':
        if endpoint in ['cohorts', 'datasets']:
            with open(root_path+'ref_schemas/framework/json/responses/beaconCollectionsResponse.json', 'r') as f:
                response = json.load(f)
            schema_path = 'file:///{0}/'.format(
                    os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconCollectionsResponse.json').replace("\\", "/"))
        else:
            with open(root_path+'ref_schemas/framework/json/responses/beaconResultsetsResponse.json', 'r') as f:
                response = json.load(f)
            schema_path = 'file:///{0}/'.format(
                    os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconResultsetsResponse.json').replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        endpoint_validation.append(JSONSchemaValidator.validate(total_response, response, resolver))

        with open(root_path+'ref_schemas/models/json/beacon-v2-default-model/' +endpoint+'/defaultSchema.json', 'r') as f:
            response = json.load(f)
        schema_path = 'file://{0}/'.format(
                os.path.dirname(root_path+'ref_schemas/models/json/beacon-v2-default-model/'+endpoint+'/defaultSchema.json').replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        if endpoint in ['cohorts', 'datasets']:
            resultsets=total_response["response"]["collections"]
            for resultset in resultsets:
                dataset = resultset["id"]
                endpoint_validation.append(dataset)
                endpoint_validation.append(JSONSchemaValidator.validate(resultset, response, resolver))
        else:
            resultsets=total_response["response"]["resultSets"]
            for resultset in resultsets:
                dataset = resultset["id"]
                results = resultset["results"]
                endpoint_validation.append(dataset)
                for result in results:
                    endpoint_validation.append(JSONSchemaValidator.validate(result, response, resolver))
    
    elif granularity == 'count':
        with open(root_path+'ref_schemas/framework/json/responses/beaconCountResponse.json', 'r') as f:
            response = json.load(f)
        schema_path = 'file:///{0}/'.format(
                os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconCountResponse.json').replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        endpoint_validation.append(JSONSchemaValidator.validate(total_response, response, resolver))

    elif granularity == 'boolean':
        with open(root_path+'ref_schemas/framework/json/responses/beaconBooleanResponse.json', 'r') as f:
            response = json.load(f)
        schema_path = 'file:///{0}/'.format(
                os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconBooleanResponse.json').replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        endpoint_validation.append(JSONSchemaValidator.validate(total_response, response, resolver))
    return endpoint_validation


def general_checks(url: str):
    output_validation=[]
    root_path = '/usr/src/app/'
    new_url = url + '/map'
    f = requests.get(new_url)
    total_response = json.loads(f.text)
    resultsets = total_response["response"]
    endpoints = resultsets["endpointSets"]
    list_of_endpoints=[]
    endpoints_to_verify = list_endpoints(list_of_endpoints, endpoints)
    new_url = url + '/map'
    output_validation.append(new_url)
    f = requests.get(new_url)
    total_response = json.loads(f.text)
    with open(root_path+'ref_schemas/framework/json/responses/beaconMapResponse.json', 'r') as f:
        map = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconMapResponse.json').replace("\\", "/"))
    resolver = RefResolver(schema_path, map)
    output_validation.append(JSONSchemaValidator.validate(total_response, map, resolver))

    new_url = url + '/info'
    output_validation.append(new_url)
    f = requests.get(new_url)
    total_response = json.loads(f.text)
    with open(root_path+'ref_schemas/framework/json/responses/beaconInfoResponse.json', 'r') as f:
        info = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconInfoResponse.json').replace("\\", "/"))
    resolver = RefResolver(schema_path, info)
    output_validation.append(JSONSchemaValidator.validate(total_response, info, resolver))

    new_url = url + '/configuration'
    output_validation.append(new_url)
    f = requests.get(new_url)
    total_response = json.loads(f.text)
    with open(root_path+'ref_schemas/framework/json/responses/beaconConfigurationResponse.json', 'r') as f:
        configuration = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconConfigurationResponse.json').replace("\\", "/"))
    resolver = RefResolver(schema_path, configuration)
    output_validation.append(JSONSchemaValidator.validate(total_response, configuration, resolver))

    new_url = url + '/filtering_terms'
    output_validation.append(new_url)
    f = requests.get(new_url)
    total_response = json.loads(f.text)
    with open(root_path+'ref_schemas/framework/json/responses/beaconFilteringTermsResponse.json', 'r') as f:
        filtering_terms = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconFilteringTermsResponse.json').replace("\\", "/"))
    resolver = RefResolver(schema_path, filtering_terms)
    output_validation.append(JSONSchemaValidator.validate(total_response, filtering_terms, resolver))

    for endpoint in endpoints_to_verify:
        if endpoint.endswith('analyses') and 'd}' not in endpoint:
            endpoint_validation=endpoint_check('analyses', False, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('analyses'):
            endpoint_validation=endpoint_check(endpoint, True, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('biosamples') and 'd}' not in endpoint:
            endpoint_validation=endpoint_check('biosamples', False, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('biosamples'):
            endpoint_validation=endpoint_check(endpoint, True, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('g_variants') and 'd}' not in endpoint:
            endpoint_validation=endpoint_check('genomicVariations', False, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('g_variants'):
            endpoint_validation=endpoint_check(endpoint, True, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('individuals') and 'd}' not in endpoint:
            endpoint_validation=endpoint_check('individuals', False, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('individuals'):
            endpoint_validation=endpoint_check(endpoint, True, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('runs') and 'd}' not in endpoint:
            endpoint_validation=endpoint_check('runs', False, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('runs'):
            endpoint_validation=endpoint_check(endpoint, True, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('datasets') and 'd}' not in endpoint:
            endpoint_validation=endpoint_check('datasets', False, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('datasets'):
            endpoint_validation=endpoint_check(endpoint, True, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('cohorts') and 'd}' not in endpoint:
            endpoint_validation=endpoint_check('cohorts', False, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
        elif endpoint.endswith('cohorts'):
            endpoint_validation=endpoint_check(endpoint, True, url)
            for validated_endpoint in endpoint_validation:
                output_validation.append(validated_endpoint)
    return output_validation

general_checks(args.url)



