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
    is_error = False
    root_path = '/usr/src/app/'
    if endpoint != 'genomicVariations' and id_parameter == False:
        url = url + '/' + endpoint
        f = requests.get(url)
        try:
            total_response = json.loads(f.text)
        except Exception as e:
            endpoint_validation.append(e)
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
        try:
            error = total_response["error"]
            is_error = True
        except Exception:
            try:
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
            except Exception:
                pass

       
        f = requests.get(url)
        total_response = json.loads(f.text)
        endpoint = last_part[-1]
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


def bash_view(request):
    template = "home.html"
    form =BamForm()
    context = {'form': form}
    if request.user.is_authenticated:
        current_email=request.user.email
        #print(current_email)
        #LOG.debug(current_email)
    else:
        current_email = ''
    if request.method == 'POST':
        form = BamForm(request.POST)
        
        if form.is_valid():
            count=0
            bash_out = general_checks(form.cleaned_data['url_link'])
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


   
            context = {
                'url_link': form.cleaned_data['url_link'],
                'bash_out': new_bash_out,
                'success': success,
                'form': form

            }


            return render(request, 'base.html', context)

            
    
    return render(request, template, context)

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