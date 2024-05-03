from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from .models import AgeOfOnset
import subprocess
from verifierweb.forms import BamForm, AgeOfOnsetForm, NewForm
import time
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging
from classes import JSONSchemaValidator
import requests
import json
from jsonschema import validate, RefResolver, Draft202012Validator
import os
from bash.tasks import sample_task, task_retry, sample_task_info, sample_task_endpoints, sample_task_configuration, sample_task_error, sample_task_filtering_terms
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
                for k3, v3 in v2.items():
                    for k4, v4 in v3.items():
                        if k4 == 'url':
                            list_of_endpoints.append(v4)

    return list_of_endpoints


def endpoint_check(url: str):
    endpoint_validation=[]
    is_error = False
    root_path = '/app/'
    if 'd}' in url:
        LOG.error('eoeoeoeo is {}'.format(url))
        id_parameter = True
    else:
        id_parameter = False
    url_part = url.split('/')
    endpoint = url_part[-1]
    
    if id_parameter == False:
        f = requests.get(url)
        try:
            total_response = json.loads(f.text)
        except Exception as e:
            endpoint_validation.append(e)
    else:

        last_part = url.split('{')
        new_url = last_part[0][0:-1]
        LOG.error('the endpoint is {} and the url is.... {}'.format(endpoint,new_url))
        try:
            f = requests.get(new_url)
            total_response = json.loads(f.text)
        except Exception as e:
            LOG.error('what happened to ... {}'.format(new_url))
            endpoint_validation.append(e)
        try:
            if url_part[-3] == 'g_variants':
                id = total_response["response"]["resultSets"][0]["results"][0]["variantInternalId"]
                LOG.error('the urlis {} and the id is.... {}'.format(url,id))
                url = url.replace('{variantInternalId}', id)
            elif url_part[-3] == 'cohorts':
                LOG.error('cohorts response is...')
                LOG.error(total_response)
                id = total_response["response"]["collections"][0]["id"]
                LOG.error('the urlis {} and the id is.... {}'.format(url,id))
                url = url.replace('{id}', id)
            elif url_part[-3] == 'datasets':
                id = total_response["response"]["collections"][0]["id"]
                LOG.error('the urlis {} and the id is.... {}'.format(url,id))
                url = url.replace('{id}', id)
            else:
                id = total_response["response"]["resultSets"][0]["results"][0]["id"]
                LOG.error('the urlis {} and the id is.... {}'.format(url,id))
                url = url.replace('{id}', id)
        except Exception as e:
            LOG.error('what happened 2 to ... {}'.format(new_url))

        LOG.error('the brand new url is ... {}'.format(url))
        f = requests.get(url)
        try:
            total_response = json.loads(f.text)
            LOG.error(total_response)
        except Exception as e:
            endpoint_validation.append(e)
    if endpoint == 'g_variants':
        endpoint = 'genomicVariations'

        
    endpoint_validation.append(url)
    try:
        meta = total_response["meta"]
        granularity = meta["returnedGranularity"]
    except Exception:
        try:
            meta = total_response["meta"]
            granularity = meta["receivedRequestSummary"]["requestedGranularity"]
        except Exception:
            granularity = 'record'
    if endpoint in ['cohorts', 'datasets']:
        try:
            resultsets = total_response["response"]["collections"]
        except Exception:
            resultsets = total_response["response"]["resultSets"]
    else:
        try:
            resultsets=total_response["response"]["resultSets"][0]["results"]
        except Exception:
            granularity = 'boolean'
    if is_error == True:
        with open(root_path+'ref_schemas/framework/json/responses/beaconErrorResponse.json', 'r') as f:
            response = json.load(f)
        schema_path = 'file:///{0}/'.format(
                os.path.dirname(root_path+'ref_schemas/framework/json/responses/beaconErrorResponse.json').replace("\\", "/"))
        resolver = RefResolver(schema_path, response)
        endpoint_validation.append(JSONSchemaValidator.validate(total_response, response, resolver))
    else:
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
                try:
                    resultsets = total_response["response"]["collections"]
                except Exception:
                    resultsets = total_response["response"]["resultSets"]
                for resultset in resultsets:
                    try:
                        dataset = resultset["id"]
                    except Exception:
                        dataset = 'dataset unknown'
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


def map_check(url: str):
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
    output_validation.append(JSONSchemaValidator.validate(total_response, map, resolver))
    return endpoints_to_verify, output_validation

def info_check(url: str):
    output_validation=[]
    root_path = '/app/'
    new_url = url
    output_validation.append(new_url)
    f = requests.get(new_url)
    LOG.error(f.text)
    try:
        LOG.error('jajajaaj')
        total_response = json.loads(f.text)
        LOG.error(total_response)
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

def configuration_check(url: str):
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

def error_check(url: str):
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

def filtering_terms_check(url: str):
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

def validate_beacon(url_link):
    
    count=0
    bash_out = general_checks(url_link)
    new_bash_out=[]
    for bashed in bash_out:
        if bashed != []:
            if isinstance(bashed, list):
                count+=1
                for basheditem in bashed:
                    new_bash_out.append(basheditem)
            else:
                new_bash_out.append(bashed)


    

    if count ==0:
        success = 'CONGRATULATIONS! The review finished and your beacon has successfully passed the tests.'
    else:
        success = 'ERRORS FOUND! Your beacon has some errors, please review them and verify it back.'
    return new_bash_out, success


def bash_view(request):
    template = "home.html"
    form =BamForm()
    context = {'form': form}
    if request.method == 'POST':
        form = BamForm(request.POST)
        
        if form.is_valid():
            if form.cleaned_data['url_link'] == '':
                task = sample_task.delay(request['url_link'])
                map_out = task.get()
                

                # return the task id so the JS can poll the state
                context={
                    'task_id': task.task_id,
                    'bash_out': map_out
                }
                return render(request, template, context)
            else:
                task = sample_task.delay(form.cleaned_data['url_link'])
                map_out = task.get()
                

                # return the task id so the JS can poll the state
                context={
                    'task_id': task.task_id,
                    'bash_out': map_out
                }
                return render(request, template, context)

    return render(request, template, context)

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

def phenopackets_view(request):
    template = "phenopackets.html"
    form =AgeOfOnsetForm()
    file = 'not loaded'
    context = {'form': form, 'file': file}
    view = 'YES'
    if request.method == 'POST':
        view = 'YES'
        file = 'loaded'
        form = NewForm()
        context = {
            'file':file,
            'form': form,
            'view': view

        }
        view='YES'
        if request.method == 'POST':
            form = NewForm(request.POST)
            
            
            if form.is_valid():

                form = NewForm(request.POST)
                if form.is_valid():
                    
                    filters=[]
                    if form.cleaned_data['biosampleId'] == True:
                        biosampleId={"id":"diseases.ageOfOnset.iso8601duration","operator": "=", "value": "P0Y","scope":"individual"}
                        filters.append(biosampleId)
                    if form.cleaned_data['individualId'] == True:
                        individualId={"id":"diseases.ageOfOnset.iso8601duration","operator": "=", "value": "P0Y","scope":"individual"}
                        filters.append(individualId)
                    if form.cleaned_data['sampledTissue'] == True:
                        sampledTissue={"id":"ICD10:C18.7", "scope":"biosample"}
                        filters.append(sampledTissue)
                    if form.cleaned_data['timeOfCollection'] == True:
                        timeOfCollection={"id":"diseases.ageOfOnset.iso8601duration","operator": "=", "value": "P77Y","scope":"individual"}
                        filters.append(timeOfCollection)
                    if form.cleaned_data['histologicalDiagnosis'] == True:
                        histologicalDiagnosis={"id":"ICDO3:8480/3", "scope":"biosample"}
                        filters.append(histologicalDiagnosis)
                    if form.cleaned_data['tumorProgression'] == True:
                        tumorProgression={"id":"NCIT:C27979", "scope":"biosample"}
                        filters.append(tumorProgression)
                    if form.cleaned_data['tumorGrade'] == True:
                        tumorGrade={"id":"NCIT:C27979", "scope":"individual"}
                        filters.append(tumorGrade)


                    post_data = {"meta": {"apiVersion": "2.0"},
            "query":{ "requestParameters": {        },
                "filters": filters,
                "includeResultsetResponses": "HIT",
                "pagination": {
                    "skip": 0,
                    "limit": 10
                },
                "requestedGranularity": "record"
            }



                    }
                    response = requests.post('https://beacon-apis-demo.ega-archive.org/api/individuals', json=post_data)
                    content = response.content
                    content = json.loads(content)
                    try:
                        count = content['responseSummary']['numTotalResults']
                    except Exception:
                        count = '0'



        
                    context = {
                        'file':file,
                        'prequest': post_data,
                        'bash_out': count,
                        'view': view,
                        'form': form

                    }
                    

                    return render(request, 'phenopackets.html', context)
            
        return render(request, 'phenopackets.html', context)
    return render(request, template, context)

@csrf_exempt
def web(request):
    print('ok')

    #requests.post('https://...')
    return HttpResponse('ok')

@csrf_exempt
def async_web(request):
    task = task_retry.delay()
    logger.info(task.id)
    return HttpResponse('ok')

def channel(request):
    if request.method == 'POST':
        form = BamForm(request.POST)
        if form.is_valid():
            LOG.error(form.cleaned_data['url_link'])
            if form.cleaned_data['url_link'].endswith('info'):
                task = sample_task_info.delay(form.cleaned_data['url_link'])
                map_out = task.get()
                LOG.error(map_out)
                validation = map_out[0][1:-1]
                beaconId = map_out[1]
                beaconName = map_out[2]
                beaconVersion = map_out[3]
                validation.append('Validation finished')
                validated=''
                for validating in validation:
                    if validating != []:
                        validating=str(validating)
                        validated=validated+'<br/>'+validating
                # return the task id so the JS can poll the state
                return JsonResponse({
                    'task_id': task.task_id,
                    'map_out': map_out,
                    'validation':validation,
                    'beaconId': beaconId,
                    'beaconName': beaconName,
                    'beaconVersion': beaconVersion
                })
            elif form.cleaned_data['url_link'].endswith('configuration'):
                task = sample_task_configuration.delay(form.cleaned_data['url_link'])
                map_out = task.get()
                LOG.error(map_out)
                validation = map_out[1:-1]
                validation.append('Validation finished')
                validated=''
                for validating in validation:
                    if validating != []:
                        validating=str(validating)
                        validated=validated+'<br/>'+validating
                # return the task id so the JS can poll the state
                return JsonResponse({
                    'task_id': task.task_id,
                    'map_out': map_out,
                    'validation':validation
                })
            elif form.cleaned_data['url_link'].endswith('error'):
                task = sample_task_error.delay(form.cleaned_data['url_link'])
                map_out = task.get()
                LOG.error(map_out)
                validation = map_out[1:-1]
                validation.append('Validation finished')
                validated=''
                for validating in validation:
                    if validating != []:
                        validating=str(validating)
                        validated=validated+'<br/>'+validating
                # return the task id so the JS can poll the state
                return JsonResponse({
                    'task_id': task.task_id,
                    'map_out': map_out,
                    'validation':validation
                })
            elif form.cleaned_data['url_link'].endswith('filtering_terms'):
                task = sample_task_filtering_terms.delay(form.cleaned_data['url_link'])
                map_out = task.get()
                LOG.error(map_out)
                validation = map_out[1:-1]
                validation.append('Validation finished')
                validated=''
                for validating in validation:
                    if validating != []:
                        validating=str(validating)
                        validated=validated+'<br/>'+validating
                # return the task id so the JS can poll the state
                return JsonResponse({
                    'task_id': task.task_id,
                    'map_out': map_out,
                    'validation':validation
                })
            elif form.cleaned_data['url_link'].endswith('analyses') or form.cleaned_data['url_link'].endswith('biosamples') or form.cleaned_data['url_link'].endswith('cohorts') or form.cleaned_data['url_link'].endswith('datasets') or form.cleaned_data['url_link'].endswith('g_variants') or form.cleaned_data['url_link'].endswith('individuals') or form.cleaned_data['url_link'].endswith('runs'):
                task = sample_task_endpoints.delay(form.cleaned_data['url_link'])
                map_out = task.get()
                LOG.error(map_out)
                validation = map_out[1:-1]
                validation.append('Validation finished')
                validated=''
                for validating in validation:
                    if validating != []:
                        validating=str(validating)
                        validated=validated+'<br/>'+validating
                # return the task id so the JS can poll the state
                return JsonResponse({
                    'task_id': task.task_id,
                    'map_out': map_out,
                    'validation':validated
                })
            else:
                LOG.error(type(form.cleaned_data['url_link']))
                LOG.error('yeaaaaaah')
                task = sample_task.delay(form.cleaned_data['url_link'])
                map_out = task.get()
                initial_list=[]
                initial_list.append(form.cleaned_data['url_link']+'/info')
                initial_list.append(form.cleaned_data['url_link']+'/configuration')
                initial_list.append(form.cleaned_data['url_link']+'/error')
                initial_list.append(form.cleaned_data['url_link']+'/filtering_terms')
                mapstring= form.cleaned_data['url_link']+'/map'
                for map in map_out[0]:
                    initial_list.append(map)
                validation = map_out[1:-1]
                validation.append('Validation finished')
                validated=''
                for validating in validation:
                    if validating != []:
                        validating=str(validating)
                        validated=validated+'<br/>'+validating
                # return the task id so the JS can poll the state
                return JsonResponse({
                    'task_id': task.task_id,
                    'bash_out': initial_list,
                    'map': mapstring,
                    'validation':validated
                })



    form = BamForm()
    return render(request, 'home.html', {'form': form})


