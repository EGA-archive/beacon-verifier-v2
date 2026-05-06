import requests
import json
import os
from classes import JSONSchemaValidator
from jsonschema import RefResolver

def endpoint_request(url):
    output_validation=[]
    new_url = url
    output_validation.append(new_url)
    f = requests.get(new_url)
    return f, output_validation

def resolve_validation_path(path):
    root_path = '/app/'
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
    except Exception as e:
        output_validation.append(e)
    output_validation=verify_response(path,output_validation,total_response)
    return output_validation