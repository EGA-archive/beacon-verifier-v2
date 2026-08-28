import requests
import json
import os
from classes import JSONSchemaValidator
from jsonschema import RefResolver

def list_endpoints(list_of_endpoints, endpoints):
    for k, v in endpoints.items():
        if v['entryType'] not in ['analysis', 'biosample', 'cohort', 'dataset', 'individual', 'genomicVariant', 'run']:
            continue
        for k2, v2 in v.items():
            if k2 == 'rootUrl' and v['entryType'] in ['analysis', 'biosample', 'cohort', 'dataset', 'individual', 'genomicVariant', 'run']:
                list_of_endpoints.append(v2)
            elif k2 == 'endpoints':
                try:
                    for k3, v3 in v2.items():
                        for k4, v4 in v3.items():
                            if k4 == 'url' and v3['returnedEntryType'] in ['analysis', 'biosample', 'cohort', 'dataset', 'individual', 'genomicVariant', 'run']:
                                list_of_endpoints.append(v4)
                except Exception:
                    pass

    return list_of_endpoints

def get_url_entry_type(endpoints, url):
    entry_type_dict={}
    for k, v in endpoints.items():
        if v['entryType'] not in ['analysis', 'biosample', 'cohort', 'dataset', 'individual', 'genomicVariant', 'run']:
            continue
        for k2, v2 in v.items():
            if v['rootUrl'] == url and v['entryType'] in ['analysis', 'biosample', 'cohort', 'dataset', 'individual', 'genomicVariant', 'run']:
                return v['entryType']
            elif k2 == 'endpoints':
                try:
                    for k3, v3 in v2.items():
                        for k4, v4 in v3.items():
                            if v3['url'] == url and v3['returnedEntryType'] in ['analysis', 'biosample', 'cohort', 'dataset', 'individual', 'genomicVariant', 'run']:
                                return v3['returnedEntryType']
                except Exception:
                    pass

    return entry_type_dict

def list_dataset_endpoint(endpoints):
    for k, v in endpoints["response"].items():
        if k == 'endpointSets':
            for k2, v2 in v.items():
                if 'dataset' in k2:
                    for k3, v3 in v2.items():
                        if k3 == 'rootUrl':
                            return v3

    return ''

def endpoint_request(url):
    output_validation=[]
    new_url = url
    output_validation.append(new_url)
    f = requests.get(new_url)
    return f, output_validation

def resolve_validation_path(path):
    # Resolve bundled schema files relative to the project root, so the tool works both
    # inside the Docker image (code at /app) and in a local checkout or test run.
    root_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '')
    with open(root_path+path, 'r') as f:
        spec_json = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+path).replace("\\", "/"))
    resolver = RefResolver(schema_path, spec_json)
    return resolver, spec_json

def verify_response(path, output_validation, total_response):
    resolver, spec_json = resolve_validation_path(path)
    output_validation.append(JSONSchemaValidator.validate(total_response, spec_json, resolver))
    return output_validation

def verifier_check(url, path):
    f, output_validation = endpoint_request(url)
    try:
        total_response = json.loads(f.text)
    except Exception:
        output_validation.append('Internal Server Error. Cannot decode JSON. Look if this endpoint is working')
        return output_validation
    output_validation=verify_response(path,output_validation,total_response)
    return output_validation