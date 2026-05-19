from django import forms
from bash.validations import endpoint_request, list_endpoints
import json

def get_map_endpoints_list(url):
    new_url = url + '/map'
    f, output_validation = endpoint_request(new_url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)
    resultsets = total_response["response"]
    endpoints = resultsets["endpointSets"]
    list_of_endpoints=[]
    endpoints_to_verify = list_endpoints(list_of_endpoints, endpoints)

    try:

        final_list=[]

        initial_list = [
            f"{url}/info",
            f"{url}/configuration",
            f"{url}/filtering_terms",
        ]

        for m in endpoints_to_verify:
            initial_list.append(m)

        for item in initial_list:
            final_list.append((item, item))

    except Exception as e:
        final_list = []
    return final_list

def get_datasets_list(url):
    initial_list=[]
    final_list=[]
    new_url = url + '/datasets'
    f, output_validation = endpoint_request(new_url)
    try:
        total_response = json.loads(f.text)
    except Exception as e:
        output_validation.append(e)
    datasets_records = total_response["response"]["collections"]
    for dataset_record in datasets_records:
        initial_list.append(dataset_record["id"])
    for item in initial_list:
        final_list.append((item, item))
    print(final_list, flush=True)
    return final_list

class SettingsForm(forms.Form):
    choices_irr = [("HIT", "HIT"), ("MISS", "MISS"), ("ALL", "ALL"), ("NONE", "NONE")]
    choices_granularity = [("record", "record"), ("count", "count"), ("boolean", "boolean")]
    choices_testmode = [("True", "True"), ("False", "False")]
    url_link = forms.CharField(widget=forms.TextInput(attrs={'size':50}), max_length=100, required=False, help_text="<div style='margin-bottom: 8px;'>Beacon URL</div>", label="")
    include_resultset_responses = forms.MultipleChoiceField(
        choices=choices_irr, 
        widget=forms.CheckboxSelectMultiple,
        help_text="<div style='margin-bottom: 8px;'>Response Type</div>", label=""
    )
    granularity = forms.MultipleChoiceField(
        choices=choices_granularity, 
        widget=forms.CheckboxSelectMultiple,
        help_text="<div style='margin-bottom: 8px;'>Granularity</div>", label=""
    )
    test_mode = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=choices_testmode, 
        help_text="<div style='margin-bottom: 8px;'>Test Mode</div>", label=""
    )

class EndpointsForm(forms.Form):

    endpoint_url = forms.CharField(
        widget=forms.HiddenInput(),
        help_text="<div style='margin-bottom: 8px;'>Endpoint Url</div>", label=""
    )
    include = forms.CharField(
        widget=forms.HiddenInput()
    )
    granularity = forms.CharField(
        widget=forms.HiddenInput()
    )
    test_mode = forms.CharField(
        widget=forms.HiddenInput()
    )

    endpoints_collected = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, endpoint_url=None, include=None, granularity=None, test_mode=None, **kwargs):
        super().__init__(*args, **kwargs)

        if endpoint_url:
            self.fields["endpoints_collected"].choices = get_map_endpoints_list(endpoint_url)
        if include:
            self.fields["include"].choices = [(include[0], include[0])]
        if granularity:
            self.fields["granularity"].choices = [(granularity[0], granularity[0])]
        if test_mode:
            self.fields["test_mode"].choices = [(test_mode[0], test_mode[0])]


class DatasetsForm(forms.Form):

    endpoint_url = forms.CharField(widget=forms.HiddenInput())
    include = forms.CharField(widget=forms.HiddenInput())
    granularity = forms.CharField(widget=forms.HiddenInput())
    test_mode = forms.CharField(widget=forms.HiddenInput())
    endpoints_collected = forms.CharField(widget=forms.HiddenInput())

    datasets_collected = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, endpoint_url=None, **kwargs):
        super().__init__(*args, **kwargs)

        if endpoint_url:
            self.fields["datasets_collected"].choices = get_datasets_list(endpoint_url)