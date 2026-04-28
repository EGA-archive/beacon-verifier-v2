from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, View
from .models import AgeOfOnset
import subprocess
from verifierweb.forms import BamForm
import time
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from classes import JSONSchemaValidator
import requests
import json
from jsonschema import validate, RefResolver, Draft202012Validator
import os
from bash.tasks import verification
import json
import random

import requests
from celery.result import AsyncResult
from django.http import JsonResponse, HttpResponse                   # update
from django.views.decorators.csrf import csrf_exempt                 # new


logger = logging.getLogger(__name__)


def list_endpoints(list_of_endpoints, endpoints):
    for k, v in endpoints.items():
        for k2, v2 in v.items():
            if k2 == 'rootUrl':
                list_of_endpoints.append(v2)
            elif k2 == 'endpoints':
                try:
                    for k3, v3 in v2.items():
                        for k4, v4 in v3.items():
                            if k4 == 'url':
                                list_of_endpoints.append(v4)
                except Exception:
                    pass

    return list_of_endpoints


def endpoint_check(url, include, requestedgranularity, test_mode):
    LOG.error(url)
    if test_mode == 0:
        test_mode = True
    else:
        test_mode = False
    endpoint_validation=[]
    is_error = False
    is_appended = False
    root_path = '/app/'
    if 'd}' in url:
        id_parameter = True
    else:
        id_parameter = False
    url_part = url.split('/')
    endpoint = url_part[-1]
    myobj = {
        "meta": {
            "apiVersion": "2.2"
        },
        "query": {
            "includeResultsetResponses": include,
            "pagination": {
                "skip": 0,
                "limit": 10
            },
            "testMode": test_mode,
            "requestedGranularity": requestedgranularity
        }
    }
    
    if id_parameter == False:
        f = requests.post(url, json = myobj)
        try:
            total_response = json.loads(f.text)
        except Exception as e:
            endpoint_validation.append(e)
    else:
        last_part = url.split('{')
        new_url = last_part[0][0:-1]
        try:
            f = requests.post(new_url, json = myobj)
            total_response = json.loads(f.text)
        except Exception as e:
            endpoint_validation.append(e)
            return endpoint_validation
        try:                
            if url_part[-3] == 'g_variants':
                for resultSetsarray in total_response["response"]["resultSets"]:
                    try:
                        id = resultSetsarray["results"][0]["variantInternalId"]
                        url = url.replace('{id}', id)
                        break
                    except Exception:
                        continue
            elif url_part[-3] == 'cohorts':
                for collectionsarray in total_response["response"]["collections"]:
                    try:
                        id = collectionsarray["id"]
                        url = url.replace('{id}', id)
                        break
                    except Exception:
                        continue
            elif url_part[-3] == 'datasets':
                for collectionsarray in total_response["response"]["collections"]:
                    try:
                        id = collectionsarray["id"]
                        url = url.replace('{id}', id)
                        break
                    except Exception:
                        continue
            else:
                for resultSetsarray in total_response["response"]["resultSets"]:
                    try:
                        id = resultSetsarray["results"][0]["id"]
                        url = url.replace('{id}', id)
                        break
                    except Exception:
                        continue
        except Exception as e:
            if is_appended:
                pass
            else:
                endpoint_validation.append(url)
            endpoint_validation.append({
                                    "errorMessage": 'Internal Server Error (500)',
                                    "schema": {
                                        "path": ["response", "resultSets", 0, "results", 0],
                                        "definition": {
                                            "$defs": {
                                                "ResultsetInstance": {
                                                    "additionalProperties": True,
                                                    "properties": {
                                                        "countAdjustedTo": {
                                                            "$ref": "../../common/beaconCommonComponents.json#/$defs/CountAdjustedTo"
                                                        },
                                                        "countPrecision": {
                                                            "$ref": "../../common/beaconCommonComponents.json#/$defs/CountPrecision"
                                                        },
                                                        "exists": {
                                                            "type": "boolean"
                                                        },
                                                        "id": {
                                                            "description": "id of the resultset",
                                                            "example": "datasetA",
                                                            "type": "string"
                                                        },
                                                        "info": {
                                                            "$ref": "../../common/info.json"
                                                        },
                                                        "results": {
                                                            "items": {
                                                                "type": "object"
                                                            },
                                                            "minItems": 0,
                                                            "type": "array"
                                                        },
                                                        "resultsCount": {
                                                            "description": "Precise or approximate number of results in this Resultset.",
                                                            "type": "integer"
                                                        },
                                                        "resultsHandovers": {
                                                            "$ref": "../../common/beaconCommonComponents.json#/$defs/ListOfHandovers",
                                                            "description": "List of handover objects that apply to this resultset, not to the whole Beacon or to a result in particular."
                                                        },
                                                        "setType": {
                                                            "default": "dataset",
                                                            "description": "Entry type of resultSet. It SHOULD MATCH an entry type declared as collection in the Beacon configuration.",
                                                            "type": "string"
                                                        }
                                                    },
                                                    "required": [
                                                        "id",
                                                        "setType",
                                                        "exists"
                                                    ],
                                                    "type": "object"
                                                }
                                            },
                                            "$schema": "https://json-schema.org/draft/2020-12/schema",
                                            "additionalProperties": True,
                                            "description": "Sets of results to be returned as query response.",
                                            "properties": {
                                                "$schema": {
                                                    "$ref": "../../common/beaconCommonComponents.json#/$defs/$schema"
                                                },
                                                "resultSets": {
                                                    "items": {
                                                        "$ref": "#/$defs/ResultsetInstance"
                                                    },
                                                    "minItems": 0,
                                                    "type": "array"
                                                }
                                            },
                                            "required": [
                                                "resultSets"
                                            ],
                                            "title": "Beacon ResultSet",
                                            "type": "object"
                                        }
                                                                            },
                                    "received": {
                                        "path": ["response", "resultSets", 0, "results", 0],
                                        "value": total_response,
                                    }
                                })
            return endpoint_validation

        f = requests.post(url, json = myobj)
        endpoint_validation.append(url)
        is_appended = True
        try:
            total_response = json.loads(f.text)
        except Exception as e:
            if is_appended:
                pass
            else:
                endpoint_validation.append(url)
            endpoint_validation.append('Internal Server Error. Cannot decode JSON. Look if this endpoint is working')
            return endpoint_validation
    if endpoint == 'g_variants':
        endpoint = 'genomicVariations'

    if is_appended:
        pass
    else:
        endpoint_validation.append(url)
    
    try:
        meta = total_response["meta"]
        granularity = meta["returnedGranularity"]
        include_resultset = meta["receivedRequestSummary"]["includeResultsetResponses"]
    except Exception:
        try:
            meta = total_response["meta"]
            granularity = meta["returnedGranularity"]
            include_resultset = meta["receivedRequestSummary"]["includeResultsetResponses"]
        except Exception:
            granularity = 'record'
    if endpoint in ['cohorts', 'datasets']:
        try:
            resultsets = total_response["response"]["collections"]
        except Exception:
            endpoint_validation.append({
                                        "errorMessage": 'Internal Server Error (500)',
                                        "schema": {
                                            "path": ["response", "collections"],
                                            "definition": {
                                                    "additionalProperties": True,
                                                    "description": "Returning the Beacon Collections list, filtered or unfiltered.",
                                                    "properties": {
                                                        "collections": {
                                                            "items": {
                                                                "type": "object"
                                                            },
                                                            "minItems": 0,
                                                            "type": "array"
                                                        }
                                                    },
                                                    "required": [
                                                        "collections"
                                                    ],
                                                    "type": "object"
                                                }
                                                                                },
                                        "received": {
                                            "path": ["response", "collections"],
                                            "value": total_response,
                                        }
                                    })
        return endpoint_validation
    if is_error == True:
        with open(root_path+'ref_schemas/framework/json/responses/beaconErrorResponse.json', 'r') as f:
            response = json.load(f)
        schema_path = 'file:///{0}/'.format(
                os.path.dirname(os.path.abspath("."+root_path+'ref_schemas/framework/json/responses/beaconErrorResponse.json')).replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        logs=JSONSchemaValidator.validate(total_response, response, resolver)
        for log in logs:
            endpoint_validation.append({
                "errorMessage": log["message"],
                "schema": {
                    "path": log["schema_path"],
                    "definition": log["schema"],
                },
                "received": {
                    "path": log["instance_path"],
                    "value": log["instance"],
                }
            })
    else:
        if granularity == 'record' and include_resultset != 'NONE':
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
            

            logs=JSONSchemaValidator.validate(total_response, response, resolver)
            for log in logs:
                endpoint_validation.append({
                    "errorMessage": log["message"],
                    "schema": {
                        "path": log["schema_path"],
                        "definition": log["schema"],
                    },
                    "received": {
                        "path": log["instance_path"],
                        "value": log["instance"],
                    }
                })
            with open(root_path+'ref_schemas/models/json/beacon-v2-default-model/' +endpoint+'/defaultSchema.json', 'r') as f:
                response = json.load(f)
            schema_path = 'file://{0}/'.format(
                    os.path.dirname(root_path+'ref_schemas/models/json/beacon-v2-default-model/'+endpoint+'/defaultSchema.json').replace("\\", "/"))
            resolver = RefResolver(schema_path, response)
            if endpoint in ['cohorts', 'datasets']:
                try:
                    resultsets=total_response["response"]["collections"]
                    for resultset in resultsets:
                        logs_2=JSONSchemaValidator.validate(resultset, response, resolver)
                except Exception:
                    endpoint_validation.append({
                                            "errorMessage": 'Internal Server Error (500)',
                                            "schema": {
                                                "path": ["response", "collections"],
                                                "definition": {
                                                        "additionalProperties": True,
                                                        "description": "Returning the Beacon Collections list, filtered or unfiltered.",
                                                        "properties": {
                                                            "collections": {
                                                                "items": {
                                                                    "type": "object"
                                                                },
                                                                "minItems": 0,
                                                                "type": "array"
                                                            }
                                                        },
                                                        "required": [
                                                            "collections"
                                                        ],
                                                        "type": "object"
                                                    }
                                                                                    },
                                            "received": {
                                                "path": ["response", "collections"],
                                                "value": total_response,
                                            }
                                        })
                    return endpoint_validation
            else:
                try:
                    resultsets=total_response["response"]["resultSets"]
                except Exception:
                    endpoint_validation.append({
                                    "errorMessage": 'Internal Server Error (500)',
                                    "schema": {
                                        "path": ["response", "resultSets"],
                                        "definition": {
                                            "$defs": {
                                                "ResultsetInstance": {
                                                    "additionalProperties": True,
                                                    "properties": {
                                                        "countAdjustedTo": {
                                                            "$ref": "../../common/beaconCommonComponents.json#/$defs/CountAdjustedTo"
                                                        },
                                                        "countPrecision": {
                                                            "$ref": "../../common/beaconCommonComponents.json#/$defs/CountPrecision"
                                                        },
                                                        "exists": {
                                                            "type": "boolean"
                                                        },
                                                        "id": {
                                                            "description": "id of the resultset",
                                                            "example": "datasetA",
                                                            "type": "string"
                                                        },
                                                        "info": {
                                                            "$ref": "../../common/info.json"
                                                        },
                                                        "results": {
                                                            "items": {
                                                                "type": "object"
                                                            },
                                                            "minItems": 0,
                                                            "type": "array"
                                                        },
                                                        "resultsCount": {
                                                            "description": "Precise or approximate number of results in this Resultset.",
                                                            "type": "integer"
                                                        },
                                                        "resultsHandovers": {
                                                            "$ref": "../../common/beaconCommonComponents.json#/$defs/ListOfHandovers",
                                                            "description": "List of handover objects that apply to this resultset, not to the whole Beacon or to a result in particular."
                                                        },
                                                        "setType": {
                                                            "default": "dataset",
                                                            "description": "Entry type of resultSet. It SHOULD MATCH an entry type declared as collection in the Beacon configuration.",
                                                            "type": "string"
                                                        }
                                                    },
                                                    "required": [
                                                        "id",
                                                        "setType",
                                                        "exists"
                                                    ],
                                                    "type": "object"
                                                }
                                            },
                                            "$schema": "https://json-schema.org/draft/2020-12/schema",
                                            "additionalProperties": True,
                                            "description": "Sets of results to be returned as query response.",
                                            "properties": {
                                                "$schema": {
                                                    "$ref": "../../common/beaconCommonComponents.json#/$defs/$schema"
                                                },
                                                "resultSets": {
                                                    "items": {
                                                        "$ref": "#/$defs/ResultsetInstance"
                                                    },
                                                    "minItems": 0,
                                                    "type": "array"
                                                }
                                            },
                                            "required": [
                                                "resultSets"
                                            ],
                                            "title": "Beacon ResultSet",
                                            "type": "object"
                                        }
                                                                            },
                                    "received": {
                                        "path": ["response", "resultSets"],
                                        "value": total_response,
                                    }
                                })
                    return endpoint_validation
                if granularity == 'record':
                    for resultset in resultsets:
                        datasetId=resultset["id"]
                        LOG.warning('validating model record for {} and dataset {}'.format(url, datasetId))
                        try:
                            results = resultset["results"]
                        except Exception:
                            continue
                        for result in results:
                            logs_2=JSONSchemaValidator.validate(result, response, resolver)
                        try:
                            for log in logs_2:
                                endpoint_validation.append({
                                    "datasetId": datasetId,
                                    "errorMessage": log["message"],
                                    "schema": {
                                        "path": log["schema_path"],
                                        "definition": log["schema"],
                                    },
                                    "received": {
                                        "path": log["instance_path"],
                                        "value": log["instance"],
                                    }
                                })
                        except Exception:
                            pass
        
        elif granularity == 'count' and include_resultset == 'NONE':
            LOG.warning(granularity)
            with open(root_path+'ref_schemas/framework/json/responses/beaconCountResponse.json', 'r') as f:
                response = json.load(f)
            schema_path = 'file:///{0}/'.format(
                    os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconCountResponse.json').replace("\\", "/"))
            resolver = RefResolver(schema_path, response)
            logs=JSONSchemaValidator.validate(total_response, response, resolver)
            for log in logs:
                endpoint_validation.append({
                    "errorMessage": log["message"],
                    "schema": {
                        "path": log["schema_path"],
                        "definition": log["schema"],
                    },
                    "received": {
                        "path": log["instance_path"],
                        "value": log["instance"],
                    }
                })


        elif granularity == 'boolean' and include_resultset == 'NONE':
            with open(root_path+'ref_schemas/framework/json/responses/beaconBooleanResponse.json', 'r') as f:
                response = json.load(f)
            schema_path = 'file:///{0}/'.format(
                    os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconBooleanResponse.json').replace("\\", "/"))
            resolver = RefResolver(schema_path, response)
            logs=JSONSchemaValidator.validate(total_response, response, resolver)
            for log in logs:
                endpoint_validation.append({
                    "errorMessage": log["message"],
                    "schema": {
                        "path": log["schema_path"],
                        "definition": log["schema"],
                    },
                    "received": {
                        "path": log["instance_path"],
                        "value": log["instance"],
                    }
                })
    LOG.error(endpoint_validation)
    return endpoint_validation


def map_check(url, include, granularity, test_mode):
    output_validation=[]
    LOG.error(url)
    root_path = '/app/'
    new_url = url + '/map'
    f = requests.get(new_url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)
    resultsets = total_response["response"]
    endpoints = resultsets["endpointSets"]
    list_of_endpoints=[]
    endpoints_to_verify = list_endpoints(list_of_endpoints, endpoints)
    new_url = url + '/map'
    output_validation.append(new_url)
    f = requests.get(new_url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)
    with open(root_path+'ref_schemas/framework/json/responses/beaconMapResponse.json', 'r') as f:
        map = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconMapResponse.json').replace("\\", "/"))
    resolver = RefResolver(schema_path, map)
    logs=JSONSchemaValidator.validate(total_response, map, resolver)
    for log in logs:
        if 'JSONDecodeError' not in str(log):
            output_validation.append(str(log))
        else:
            output_validation.append('Internal Server Error. Cannot decode JSON. Look if this endpoint is working')
    return endpoints_to_verify, output_validation

def info_check(url, include, granularity, test_mode):
    output_validation=[]
    root_path = '/app/'
    new_url = url
    output_validation.append(new_url)
    f = requests.get(new_url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)

    try:
        beaconId=total_response['response']['id']
        beaconName=total_response['response']['name']
    except Exception:
        beaconId=''
        beaconName=''
    try:
        beaconVersion=total_response['response']['apiVersion']
    except Exception:
        beaconVersion=''
    with open(root_path+'ref_schemas/framework/json/responses/beaconInfoResponse.json', 'r') as f:
        info = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconInfoResponse.json').replace("\\", "/"))
    resolver = RefResolver(schema_path, info)
    output_validation.append(JSONSchemaValidator.validate(total_response, info, resolver))
    return output_validation, beaconId, beaconName, beaconVersion

def configuration_check(url, include, granularity, test_mode):
    output_validation=[]
    root_path = '/app/'
    new_url = url
    output_validation.append(new_url)
    f = requests.get(new_url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)
    with open(root_path+'ref_schemas/framework/json/responses/beaconConfigurationResponse.json', 'r') as f:
        configuration = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconConfigurationResponse.json').replace("\\", "/"))
    resolver = RefResolver(schema_path, configuration)
    output_validation.append(JSONSchemaValidator.validate(total_response, configuration, resolver))
    return output_validation

def error_check(url, include, granularity, test_mode):
    output_validation=[]
    root_path = '/app/'
    new_url = url
    output_validation.append(new_url)
    f = requests.get(new_url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)
    with open(root_path+'ref_schemas/framework/json/responses/beaconErrorResponse.json', 'r') as f:
        error = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconErrorResponse.json').replace("\\", "/"))
    resolver = RefResolver(schema_path, error)
    output_validation.append(JSONSchemaValidator.validate(total_response, error, resolver))
    return output_validation

def filtering_terms_check(url, include, granularity, test_mode):
    output_validation=[]
    root_path = '/app/'
    new_url = url
    output_validation.append(new_url)
    f = requests.get(new_url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)
    with open(root_path+'ref_schemas/framework/json/responses/beaconFilteringTermsResponse.json', 'r') as f:
        filtering_terms = json.load(f)
    schema_path = 'file:///{0}/'.format(
            os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconFilteringTermsResponse.json').replace("\\", "/"))
    resolver = RefResolver(schema_path, filtering_terms)
    output_validation.append(JSONSchemaValidator.validate(total_response, filtering_terms, resolver))
    return output_validation


LOG = logging.getLogger(__name__)

def verify_command(value):
    value = str(value)
    
    bash_string = 'python verifier.py -url ' + value

    try:
        bash = subprocess.check_output([bash_string], shell=True)
        bash = bash.decode()
    except subprocess.CalledProcessError as e:
        bash = e.output

    return bash

class LandingPage(View):
    template_name = "home.html"

    def get(self, request):
        form = BamForm()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = BamForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data["url_link"]
            include = form.cleaned_data["include_resultset_responses"]
            granularity = form.cleaned_data["granularity"]
            test_mode = form.cleaned_data["test_mode"]

            task = verification.delay(url, include, granularity, test_mode, "map_check")
            map_out = task.get()
            context = {
                "task_id": task.task_id,
                "bash_out": map_out,
                "include": include,
                "granularity": granularity,
                "test_mode": test_mode
            }
            LOG.warning(context)
            return render(request, self.template_name, context)

        return render(request, self.template_name, {"form": form})

def task_status(request):
    task_id = request.GET.get('task_id')

    if task_id:
        task = AsyncResult(task_id)
        state = task.state

        if state == 'FAILURE':
            error = str(task.result)
            response = {
                'state': state,
                'error': error,
            }
        else:
            response = {
                'state': state,
            }
        return JsonResponse(response)

class ChannelView(View):

    template_name = "home.html"

    def get(self, request):
        form = BamForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = BamForm(request.POST)

        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        url = form.cleaned_data["url_link"]
        include = form.cleaned_data["include_resultset_responses"]
        granularity = form.cleaned_data["granularity"]
        test_mode = form.cleaned_data["test_mode"]

        if url.endswith("info"):
            return self.handle_info(url, include, granularity, test_mode)

        elif url.endswith("configuration"):
            return self.handle_configuration(url, include, granularity, test_mode)

        elif url.endswith("filtering_terms"):
            return self.handle_filtering_terms(url, include, granularity, test_mode)

        elif url.endswith((
            "analyses", "biosamples", "cohorts",
            "datasets", "g_variants", "individuals", "runs"
        )):
            return self.handle_endpoint(url, include, granularity, test_mode)

        else:
            return self.handle_map(url, include, granularity, test_mode)

    def format_validation(self, validation):
        validated = ""
        for v in validation:
            if v:
                validated += "<br/>" + str(v)
        return validated

    def handle_info(self, url, include, granularity, test_mode):
        validation = []
        task = verification.delay(url, include, granularity, test_mode, "info_check")

        try:
            map_out = task.get()
            validation = map_out[0][1:]
            beaconId = map_out[1]
            beaconName = map_out[2]
            beaconVersion = map_out[3]
        except Exception as e:
            validation = [e]
            map_out = [url]
            beaconId = beaconName = beaconVersion = ""

        return JsonResponse({
            "task_id": task.task_id,
            "map_out": map_out,
            "validation": self.format_validation(validation),
            "beaconId": beaconId,
            "beaconName": beaconName,
            "beaconVersion": beaconVersion,
            "include": include,
            "granularity": granularity,
            "test_mode": test_mode
        })

    def handle_configuration(self, url, include, granularity, test_mode):
        validation = []
        task = verification.delay(url, include, granularity, test_mode, "configuration_check")

        try:
            map_out = task.get()
            validation = map_out[1:-1]
        except Exception as e:
            validation = [e]
            map_out = [url]

        return JsonResponse({
            "task_id": task.task_id,
            "map_out": map_out,
            "validation": self.format_validation(validation),
            "include": include,
            "granularity": granularity,
            "test_mode": test_mode
        })

    def handle_filtering_terms(self, url, include, granularity, test_mode):
        validation = []
        task = verification.delay(url, include, granularity, test_mode, "filtering_terms_check")

        try:
            map_out = task.get()
            validation = map_out[1:-1]
        except Exception as e:
            validation = [e]
            map_out = [url]

        return JsonResponse({
            "task_id": task.task_id,
            "map_out": map_out,
            "validation": self.format_validation(validation),
            "include": include,
            "granularity": granularity,
            "test_mode": test_mode
        })

    def handle_endpoint(self, url, include, granularity, test_mode):
        validation = []
        task = verification.delay(url, include, granularity, test_mode, "endpoint_check")

        try:
            map_out = task.get()
            validation = map_out[1:]
        except Exception as e:
            validation = [e]
            map_out = [url]

        return JsonResponse({
            "task_id": task.task_id,
            "map_out": map_out,
            "validation": self.format_validation(validation),
            "include": include,
            "granularity": granularity,
            "test_mode": test_mode
        })

    def handle_map(self, url, include, granularity, test_mode):
        validation = []
        task = verification.delay(url, include, granularity, test_mode, "map_check")

        try:
            map_out = task.get()
            validation = map_out[1][1:]

            initial_list = [
                f"{url}/info",
                f"{url}/configuration",
                f"{url}/filtering_terms",
            ]

            for m in map_out[0]:
                initial_list.append(m)

        except Exception as e:
            validation = [e]
            initial_list = []

        return JsonResponse({
            "task_id": task.task_id,
            "bash_out": initial_list,
            "include": include,
            "granularity": granularity,
            "test_mode": test_mode,
            "map": f"{url}/map",
            "validation": self.format_validation(validation),
        })


