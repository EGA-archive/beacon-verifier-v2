from django.shortcuts import render
from django.views.generic import View
import subprocess
from verifierweb.forms import SettingsForm, EndpointsForm, DatasetsForm, SummaryForm, ChannelForm
import logging
from classes import JSONSchemaValidator
import requests
import json
from jsonschema import validate, RefResolver, Draft202012Validator
import os
from bash.tasks import verification
import json
import requests
from celery.result import AsyncResult
from django.http import JsonResponse
from bash.errors import return_unhandled_error, error_message_to_return, error_message_with_dataset_to_return
from bash.validations import verifier_check, endpoint_request, verify_response, resolve_validation_path, list_endpoints, get_url_entry_type
import ast
import re
from allauth.socialaccount.models import SocialAccount, SocialToken
import jwt
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime
import time

logger = logging.getLogger(__name__)





def endpoint_check(url, include, requestedgranularity, test_mode, access_token):
    endpoint_validation=[]
    for gran in requestedgranularity:
        for inc in include:
            if gran == 'record' and inc == 'NONE':
                continue
            if test_mode == 0:
                test_mode = True
            else:
                test_mode = False
            is_error = False
            is_appended = False
            if 'd}' in url:
                id_parameter = True
            else:
                id_parameter = False
            url_part = url.split('/')
            endpoint = url_part[-1]
            if endpoint not in ['analyses', 'biosamples', 'cohorts', 'datasets', 'g_variants', 'individuals', 'runs']:
                url_map = url_part[0]+url_part[1]+'/map'
                map_dict = requests.get(url_map)
                if 'response' in map_dict:
                    entry_type=get_url_entry_type(map_dict['response']['endpointSets'], url)
                else:
                    url_map = url_part[0]+'/map'
                    map_dict = requests.get(url_map)
                    if 'response' in map_dict:
                        entry_type=get_url_entry_type(map_dict['response']['endpointSets'], url)
                    else:
                        url_map = url_part[0]+url_part[1]+url_part[2]+'/map'
                        map_dict = requests.get(url_map)
                        entry_type=get_url_entry_type(map_dict['response']['endpointSets'], url)
                if entry_type == 'analysis':
                    endpoint = 'analyses'
                elif entry_type == 'biosample':
                    endpoint = 'biosamples'
                elif entry_type == 'cohort':
                    endpoint = 'cohorts'
                elif entry_type == 'dataset':
                    endpoint = 'datasets'
                elif entry_type == 'genomicVariant':
                    endpoint = 'g_variants'
                elif entry_type == 'individual':
                    endpoint = 'individuals'
                elif entry_type == 'run':
                    endpoint = 'runs'
            myobj = {
                "meta": {
                    "apiVersion": "2.2"
                },
                "query": {
                    "includeResultsetResponses": inc,
                    "pagination": {
                        "skip": 0,
                        "limit": 10
                    },
                    "testMode": test_mode,
                    "requestedGranularity": gran
                }
            }
            if id_parameter == False:
                if access_token != None:
                    f = requests.post(url, json = myobj, headers={
                "Authorization": f"Bearer {access_token}"
            })
                else:
                    f = requests.post(url, json = myobj)
                try:
                    total_response = json.loads(f.text)
                except Exception as e:
                    endpoint_validation.append(e)
            else:
                last_part = url.split('{')
                new_url = last_part[0][0:-1]
                try:
                    if access_token != None:
                        f = requests.post(new_url, json = myobj, headers={
                    "Authorization": f"Bearer {access_token}"
                })
                    else:
                        f = requests.post(new_url, json = myobj)
                    total_response = json.loads(f.text)
                except Exception as e:
                    endpoint_validation.append(e)
                    continue
                try:
                    if url_part[-3] not in ['analyses', 'biosamples', 'cohorts', 'datasets', 'g_variants', 'individuals', 'runs']:
                        url_map = url_part[0]+url_part[1]+'/map'
                        map_dict = requests.get(url_map)
                        if 'response' in map_dict:
                            entry_type=get_url_entry_type(map_dict['response']['endpointSets'], url)
                        else:
                            url_map = url_part[0]+'/map'
                            map_dict = requests.get(url_map)
                            if 'response' in map_dict:
                                entry_type=get_url_entry_type(map_dict['response']['endpointSets'], url)
                            else:
                                url_map = url_part[0]+url_part[1]+url_part[2]+'/map'
                                map_dict = requests.get(url_map)
                                entry_type=get_url_entry_type(map_dict['response']['endpointSets'], url)
                        if entry_type == 'analysis':
                            url_part[-3] = 'analyses'
                        elif entry_type == 'biosample':
                            url_part[-3] = 'biosamples'
                        elif entry_type == 'cohort':
                            url_part[-3] = 'cohorts'
                        elif entry_type == 'dataset':
                            url_part[-3] = 'datasets'
                        elif entry_type == 'genomicVariant':
                            url_part[-3] = 'g_variants'
                        elif entry_type == 'individual':
                            url_part[-3] = 'individuals'
                        elif entry_type == 'run':
                            url_part[-3] = 'runs'               
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
                except Exception as exc:
                    if is_appended:
                        pass
                    else:
                        if url not in endpoint_validation:
                            endpoint_validation.append(url)
                    with open("ref_schemas/framework/json/responses/sections/beaconResultsets.json", 'r') as f:
                        definition = json.load(f)
                    error_validation_to_return_in_json = return_unhandled_error(["response", "resultSets", 0, "results", 0], total_response, definition, exc, inc, gran)
                    endpoint_validation.append(error_validation_to_return_in_json)
                    continue
                if access_token != None:
                    f = requests.post(url, json = myobj, headers={
                "Authorization": f"Bearer {access_token}"
            })
                else:
                    f = requests.post(url, json = myobj)
                if url not in endpoint_validation:
                    endpoint_validation.append(url)
                is_appended = True
                try:
                    total_response = json.loads(f.text)
                except Exception as e:
                    if is_appended:
                        pass
                    else:
                        if url not in endpoint_validation:
                            endpoint_validation.append(url)
                    endpoint_validation.append('Internal Server Error. Cannot decode JSON. Look if this endpoint is working')
                    continue
            if endpoint == 'g_variants':
                endpoint = 'genomicVariations'

            if is_appended:
                pass
            else:
                if url not in endpoint_validation:
                    endpoint_validation.append(url)
            
            try:
                meta = total_response["meta"]
                gran = meta["returnedGranularity"]
                inc = meta["receivedRequestSummary"]["includeResultsetResponses"]
            except Exception:
                try:
                    meta = total_response["meta"]
                    gran = meta["returnedGranularity"]
                    inc = 'ALL'
                except Exception:
                    gran = 'record'
            if is_error == True:
                path='ref_schemas/framework/json/responses/beaconErrorResponse.json'
                resolver, response = resolve_validation_path(path)
                logs=JSONSchemaValidator.validate(total_response, response, resolver)
                for log in logs:
                    json_object_with_the_log_of_the_error_to_return = error_message_to_return(log, inc, gran)
                    endpoint_validation.append(json_object_with_the_log_of_the_error_to_return)
            else:
                path='ref_schemas/framework/json/responses/sections/beaconResponseMeta.json'
                resolver, response = resolve_validation_path(path)
                logs=JSONSchemaValidator.validate(meta, response, resolver)
                for log in logs:
                    json_object_with_the_log_of_the_error_to_return = error_message_to_return(log, inc, gran)
                    endpoint_validation.append(json_object_with_the_log_of_the_error_to_return)
                if inc != 'NONE':
                    if endpoint in ['cohorts', 'datasets']:
                        if gran == 'record':
                            LOG.warning('again this is my endpoint: {}'.format(endpoint))
                            path='ref_schemas/framework/json/responses/beaconCollectionsResponse.json'
                            resolver, response = resolve_validation_path(path)
                    else:
                        path='ref_schemas/framework/json/responses/beaconResultsetsResponse.json'
                        resolver, response = resolve_validation_path(path)
                        logs=JSONSchemaValidator.validate(total_response, response, resolver)
                        for log in logs:
                            json_object_with_the_log_of_the_error_to_return = error_message_to_return(log, inc, gran)
                            endpoint_validation.append(json_object_with_the_log_of_the_error_to_return)
                    path='ref_schemas/models/json/beacon-v2-default-model/' +endpoint+'/defaultSchema.json'
                    resolver, response = resolve_validation_path(path)
                    if endpoint in ['cohorts', 'datasets']:
                        if gran == 'record':
                            try:
                                resultsets=total_response["response"]["collections"]
                                for resultset in resultsets:
                                    logs_2=JSONSchemaValidator.validate(resultset, response, resolver)
                                try:
                                    for log in logs_2:
                                        json_object_with_the_log_of_the_error_to_return = error_message_to_return(log, inc, gran)
                                        endpoint_validation.append(json_object_with_the_log_of_the_error_to_return)
                                except Exception:
                                    pass
                            except Exception as exc:
                                with open("ref_schemas/framework/json/responses/beaconCollectionsResponse.json", 'r') as f:
                                    definition = json.load(f)
                                error_validation_to_return_in_json = return_unhandled_error(["response", "collections"], total_response, definition, exc, inc, gran)
                                endpoint_validation.append(error_validation_to_return_in_json)
                        elif gran == 'count':
                            path='ref_schemas/framework/json/responses/beaconCountResponse.json'
                            resolver, response = resolve_validation_path(path)
                            logs=JSONSchemaValidator.validate(total_response, response, resolver)
                            for log in logs:
                                json_object_with_the_log_of_the_error_to_return = error_message_to_return(log, inc, gran)
                                endpoint_validation.append(json_object_with_the_log_of_the_error_to_return)
                        elif gran == 'boolean':
                            path='ref_schemas/framework/json/responses/beaconBooleanResponse.json'
                            resolver, response = resolve_validation_path(path)
                            logs=JSONSchemaValidator.validate(total_response, response, resolver)
                            for log in logs:
                                json_object_with_the_log_of_the_error_to_return = error_message_to_return(log, inc, gran)
                                endpoint_validation.append(json_object_with_the_log_of_the_error_to_return)
                    else:
                        try:
                            resultsets=total_response["response"]["resultSets"]
                        except Exception as exc:
                            with open("ref_schemas/framework/json/responses/sections/beaconResultsets.json", 'r') as f:
                                definition = json.load(f)
                            error_validation_to_return_in_json = return_unhandled_error(["response", "resultSets"], total_response, definition, exc, inc, gran)
                            endpoint_validation.append(error_validation_to_return_in_json)
                            continue
                        if gran == 'record':
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
                                        json_object_with_the_log_of_the_error_to_return = error_message_with_dataset_to_return(log, datasetId, inc, gran)
                                        endpoint_validation.append(json_object_with_the_log_of_the_error_to_return)
                                except Exception:
                                    pass
                
                elif gran == 'count' and inc == 'NONE':
                    path='ref_schemas/framework/json/responses/beaconCountResponse.json'
                    resolver, response = resolve_validation_path(path)
                    logs=JSONSchemaValidator.validate(total_response, response, resolver)
                    for log in logs:
                        json_object_with_the_log_of_the_error_to_return = error_message_to_return(log, inc, gran)
                        endpoint_validation.append(json_object_with_the_log_of_the_error_to_return)


                elif gran == 'boolean' and inc == 'NONE':
                    path='ref_schemas/framework/json/responses/beaconBooleanResponse.json'
                    resolver, response = resolve_validation_path(path)
                    logs=JSONSchemaValidator.validate(total_response, response, resolver)
                    for log in logs:
                        json_object_with_the_log_of_the_error_to_return = error_message_to_return(log, inc, gran)
                        endpoint_validation.append(json_object_with_the_log_of_the_error_to_return)
    return endpoint_validation

def map_check(url, include, granularity, test_mode, access_token):
    new_url = url + '/map'
    path='ref_schemas/framework/json/responses/beaconMapResponse.json'
    f, output_validation = endpoint_request(new_url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)
    resultsets = total_response["response"]
    endpoints = resultsets["endpointSets"]
    list_of_endpoints=[]
    endpoints_to_verify = list_endpoints(list_of_endpoints, endpoints)
    resolver, response = resolve_validation_path(path)
    logs=JSONSchemaValidator.validate(total_response, response, resolver)
    for log in logs:
        if 'JSONDecodeError' not in str(log):
            output_validation.append(str(log))
        else:
            output_validation.append('Internal Server Error. Cannot decode JSON. Look if this endpoint is working')
    return endpoints_to_verify, output_validation

def info_check(url, include, granularity, test_mode, access_token):
    path='ref_schemas/framework/json/responses/beaconInfoResponse.json'
    f, output_validation = endpoint_request(url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)
        return output_validation
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
    output_validation=verify_response(path, output_validation, total_response)
    return output_validation, beaconId, beaconName, beaconVersion

def configuration_check(url, include, granularity, test_mode, access_token):
    path='ref_schemas/framework/json/responses/beaconConfigurationResponse.json'
    output_validation=verifier_check(url,path)
    return output_validation

def error_check(url, include, granularity, test_mode, access_token):
    path='ref_schemas/framework/json/responses/beaconErrorResponse.json'
    output_validation=verifier_check(url,path)
    return output_validation

def filtering_terms_check(url, include, granularity, test_mode, access_token):
    path='ref_schemas/framework/json/responses/beaconFilteringTermsResponse.json'
    output_validation=verifier_check(url,path)
    return output_validation

def get_token_data(self, request):
    if not request.user.is_authenticated:
        return None, None, None

    account = SocialAccount.objects.filter(
        user=request.user,
        provider="my-server"
    ).first()

    access_token = None

    social_token = account.socialtoken_set.first()

    if social_token:
        access_token = social_token.token

    if access_token == None:
        return account, None, True

    try:
        payload = jwt.decode(
            access_token,
            options={"verify_signature": False}
        )
        exp = payload.get("exp")

        token_expired = (
            exp is None or
            timezone.now().timestamp() >= exp
        )

        return account, access_token, token_expired

    except Exception:
        return account, access_token, True

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
    template_name = "settings.html"



    def get(self, request, *args, **kwargs):

        account, access_token, token_expired = get_token_data(self, request)

        form = SettingsForm()
        context = {"form": form, "token_expired": token_expired,
        "access_token": access_token }
        return render(request, self.template_name, context)
    


    def post(self, request, *args, **kwargs):
        account, access_token, token_expired = get_token_data(self, request)

        if "settings" in request.POST:
            form = SettingsForm(request.POST)
            msg = None
            if form.is_valid():
                url = form.cleaned_data["url_link"]
                include = form.cleaned_data["include_resultset_responses"]
                granularity = form.cleaned_data["granularity"]
                test_mode = form.cleaned_data["test_mode"]
                try:
                    msg = form.cleaned_data["msg"]
                    if msg is not None:
                        return render(request, "settings.html", {"form": form, "msg": msg})
                except Exception as e:
                    msg = None
                endpoints_form = EndpointsForm(
                    endpoint_url=url,
                    initial={
                        "endpoint_url": url,
                        "include": include,
                        "granularity": granularity,
                        "test_mode": test_mode
                    }
                )
                test_mode=str(test_mode)
                granularity=str(granularity)
                include=str(include)
                context = {
                    "form": endpoints_form,
                    "url": url,
                    "include": include,
                    "granularity": granularity,
                    "test_mode": test_mode,
                    "token_expired": token_expired
                }
                return render(request, "endpoints.html", context)
            else:
                return render(request, "settings.html", {"form": form})
        elif "endpoints" in request.POST and ast.literal_eval(request.POST.get("include")) == ['NONE']:
            endpoint_url=request.POST.get("endpoint_url")
            endpoints=request.POST.get("endpoints_collected")

            include=request.POST.get("include")
            granularity=request.POST.get("granularity")
            test_mode=request.POST.get("test_mode")

            datasets='Dataset selection is not applicable when only NONE is selected, as responses are returned per beacon.'
            form = EndpointsForm(
                request.POST,
                endpoints_collected=request.POST.get("endpoints_collected"),
                endpoint_url=request.POST.get("endpoint_url"),
                include=request.POST.get("include"),
                granularity=request.POST.get("granularity"),
                test_mode=request.POST.get("test_mode")
            )
            if form.is_valid():
                endpoints = form.cleaned_data["endpoints_collected"]
                endpoint_url = form.cleaned_data["endpoint_url"]
                datasets_form = SummaryForm(
                    initial={
                        "url_link": endpoint_url,
                        "include_resultset_responses": include,
                        "granularity": granularity,
                        "test_mode": test_mode,
                        "endpoints_collected": endpoints,
                        "datasets_collected": datasets
                    }
                )
                final_endpoints_list=[]
                count_dict = {}
                granularity=granularity.replace('[','')
                granularity=granularity.replace(']','')
                granularity=granularity.replace("'",'')
                include=include.replace('[','')
                include=include.replace(']','')
                include=include.replace("'",'')
                for endpoint in endpoints:
                    endpoint_new = endpoint.split('/')[-1]

                    if '/'+endpoint_new not in count_dict:
                        count_dict['/'+endpoint_new] = 1
                        final_endpoints_list.append('/'+endpoint_new)
                    else:
                        count_dict['/'+endpoint_new] += 1
                count_dict=str(count_dict)
                count_dict=count_dict.replace('{','')
                count_dict=count_dict.replace('}','')
                count_dict=count_dict.replace("'",'')
                count_dict=count_dict.replace(":",'')
                count_dict=count_dict.replace("1",'')
                count_dict=count_dict.replace(" ,",',')
                count_dict = re.sub(r'(\d+)', lambda m: f"({m.group(1)})", count_dict)
                context = {
                        "datasets": datasets,
                        "endpoints": count_dict,
                        "endpoint_url": endpoint_url,
                        "include": include,
                        "granularity": granularity,
                        "test_mode": test_mode,
                        "form": datasets_form,
                        "token_expired": token_expired
                    }

                return render(request, "summary.html", context)
        elif "endpoints" in request.POST:
            endpoint_url=request.POST.get("endpoint_url")
            endpoints=request.POST.get("endpoints_collected")

            include=request.POST.get("include")
            granularity=request.POST.get("granularity")
            test_mode=request.POST.get("test_mode")
            form = EndpointsForm(
                request.POST,
                endpoints_collected=request.POST.get("endpoints_collected"),
                endpoint_url=request.POST.get("endpoint_url"),
                include=request.POST.get("include"),
                granularity=request.POST.get("granularity"),
                test_mode=request.POST.get("test_mode")
            )
            if form.is_valid():

                endpoints = form.cleaned_data["endpoints_collected"]
                endpoint_url = form.cleaned_data["endpoint_url"]
                datasets_form = DatasetsForm(
                    endpoint_url=endpoint_url,
                    initial={
                        "endpoint_url": endpoint_url,
                        "include": include,
                        "granularity": granularity,
                        "test_mode": test_mode,
                        "endpoints_collected": endpoints
                    }
                )

                context = {
                    "form": datasets_form,
                    "endpoints": endpoints,
                    "endpoint_url": endpoint_url,
                    "include": include,
                    "granularity": granularity,
                    "test_mode": test_mode,
                    "token_expired": token_expired
                }
                return render(request, "datasets.html", context)
        elif "datasets" in request.POST:
            endpoint_url=request.POST.get("endpoint_url")
            include=request.POST.get("include")
            granularity=request.POST.get("granularity")
            test_mode=request.POST.get("test_mode")
            endpoints=request.POST.get("endpoints_collected")
            datasets_collected=request.POST.get("datasets_collected")
            datasets_form = SummaryForm(
                initial={
                    "url_link": endpoint_url,
                    "include_resultset_responses": include,
                    "granularity": granularity,
                    "test_mode": test_mode,
                    "endpoints_collected": endpoints,
                    "datasets_collected": datasets_collected
                }
            )
            final_endpoints_list=[]
            count_dict = {}
            endpoints=ast.literal_eval(endpoints)
            granularity=granularity.replace('[','')
            granularity=granularity.replace(']','')
            granularity=granularity.replace("'",'')
            include=include.replace('[','')
            include=include.replace(']','')
            include=include.replace("'",'')
            for endpoint in endpoints:
                endpoint_new = endpoint.split('/')[-1]

                if '/'+endpoint_new not in count_dict:
                    count_dict['/'+endpoint_new] = 1
                    final_endpoints_list.append('/'+endpoint_new)
                else:
                    count_dict['/'+endpoint_new] += 1
            count_dict=str(count_dict)
            count_dict=count_dict.replace('{','')
            count_dict=count_dict.replace('}','')
            count_dict=count_dict.replace("'",'')
            count_dict=count_dict.replace(":",'')
            count_dict=count_dict.replace("1",'')
            count_dict=count_dict.replace(" ,",',')
            count_dict = re.sub(r'(\d+)', lambda m: f"({m.group(1)})", count_dict)
            datasets=request.POST.getlist("datasets_collected")
            datasets=str(datasets)
            datasets=datasets.replace('[','')
            datasets=datasets.replace(']','')
            datasets=datasets.replace("'",'')
            context = {
                    "datasets": datasets,
                    "endpoints": count_dict,
                    "endpoint_url": endpoint_url,
                    "include": include,
                    "granularity": granularity,
                    "test_mode": test_mode,
                    "form": datasets_form,
                    "token_expired": token_expired
                }

            return render(request, "summary.html", context)


        return render(request, self.template_name, {})

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
        account, access_token, token_expired = get_token_data(self, request)
        form = SettingsForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        account, access_token, token_expired = get_token_data(self, request)
        form = ChannelForm(request.POST)

        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        url = form.cleaned_data["url_link"]
        include = form.cleaned_data["include_resultset_responses"]
        granularity = form.cleaned_data["granularity"]
        test_mode = form.cleaned_data["test_mode"]
        endpoints_collected = form.cleaned_data["endpoints_collected"]
        final_endpoints_collected=[]
        url=url.replace('[','')
        url=url.replace(']','')
        url=url.replace("'",'')
        if ',' in endpoints_collected:
            endpoints_collected=endpoints_collected.split(',')
        else:
            endpoints_collected=[endpoints_collected]
        postfix=url.split('/')
        for m in endpoints_collected:
            suffix = m.split("/",1)[-1].split("'")[0]
            if postfix[-1] in suffix:
                suffix=suffix.split('/',1)[-1]
            result = url + '/'+ suffix
            final_endpoints_collected.append(result)
        datasets_collected = form.cleaned_data["datasets_collected"]

        if token_expired:
            access_token = None

        if url.endswith("info"):
            return self.handle_info(url, include, granularity, test_mode, final_endpoints_collected, datasets_collected, access_token)

        elif url.endswith("configuration"):
            return self.handle_configuration(url, include, granularity, test_mode, final_endpoints_collected, datasets_collected, access_token)

        elif url.endswith("filtering_terms"):
            return self.handle_filtering_terms(url, include, granularity, test_mode, final_endpoints_collected, datasets_collected, access_token)

        elif url.endswith((
            "analyses", "biosamples", "cohorts",
            "datasets", "g_variants", "individuals", "runs"
        )):
            return self.handle_endpoint(url, include, granularity, test_mode, final_endpoints_collected, datasets_collected, access_token)

        else:
            return self.handle_map(url, include, granularity, test_mode, final_endpoints_collected, datasets_collected, access_token)

    def format_validation(self, validation):
        validated = ""
        for v in validation:
            if v:
                validated += "<br/>" + str(v)
        return validated

    def handle_info(self, url, include, granularity, test_mode, endpoints_collected, datasets_collected, access_token):
        validation = []
        task = verification.delay(url, include, granularity, test_mode, "info_check", access_token)
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
        LOG.warning({
            "task_id": task.task_id,
            "map_out": map_out,
            "validation": self.format_validation(validation),
            "beaconId": beaconId,
            "beaconName": beaconName,
            "beaconVersion": beaconVersion,
            "include": include,
            "granularity": granularity,
            "test_mode": test_mode,
            "endpoints_collected": endpoints_collected,
            "datasets_collected": datasets_collected
        })
        return JsonResponse({
            "task_id": task.task_id,
            "map_out": map_out,
            "validation": self.format_validation(validation),
            "beaconId": beaconId,
            "beaconName": beaconName,
            "beaconVersion": beaconVersion,
            "include": include,
            "granularity": granularity,
            "test_mode": test_mode,
            "endpoints_collected": endpoints_collected,
            "datasets_collected": datasets_collected
        })

    def handle_configuration(self, url, include, granularity, test_mode, endpoints_collected, datasets_collected, access_token):
        validation = []
        task = verification.delay(url, include, granularity, test_mode, "configuration_check", access_token)

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
            "test_mode": test_mode,
            "endpoints_collected": endpoints_collected,
            "datasets_collected": datasets_collected
        })

    def handle_filtering_terms(self, url, include, granularity, test_mode, endpoints_collected, datasets_collected, access_token):
        validation = []
        task = verification.delay(url, include, granularity, test_mode, "filtering_terms_check", access_token)

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
            "test_mode": test_mode,
            "endpoints_collected": endpoints_collected,
            "datasets_collected": datasets_collected
        })

    def handle_endpoint(self, url, include, granularity, test_mode, endpoints_collected, datasets_collected, access_token):
        if isinstance(datasets_collected, str):
            datasets_collected=[datasets_collected]
        validation = []
        global_validation=[]
        include=ast.literal_eval(include)
        granularity=ast.literal_eval(granularity)

        task = verification.delay(url, include, granularity, test_mode, "endpoint_check", access_token)
        try:
            map_out = task.get()
            validation = map_out[1:]
        except Exception as e:
            validation = [e]
            map_out = [url]
        global_validation+=validation


        return JsonResponse({
            "task_id": task.task_id,
            "map_out": map_out,
            "validation": self.format_validation(global_validation),
            "include": include,
            "granularity": granularity,
            "test_mode": test_mode,
            "endpoints_collected": endpoints_collected,
            "datasets_collected": datasets_collected
        })

    def handle_map(self, url, include, granularity, test_mode, endpoints_collected, datasets_collected, access_token):
        validation = []
        task = verification.delay(url, include, granularity, test_mode, "map_check", access_token)

        try:
            map_out = task.get()
            validation = map_out[1][1:]

        except Exception as e:
            validation = [e]

        return JsonResponse({
            "task_id": task.task_id,
            "bash_out": endpoints_collected,
            "include": include,
            "granularity": granularity,
            "test_mode": test_mode,
            "map": f"{url}/map",
            "validation": self.format_validation(validation),
            "endpoints_collected": endpoints_collected,
            "datasets_collected": datasets_collected
        })