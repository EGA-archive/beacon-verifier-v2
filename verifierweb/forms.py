from django import forms
from bash.validations import endpoint_request, list_endpoints, list_dataset_endpoint
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
            item = "..." +item.split('.')[-1]
            final_list.append((item, item))
    except Exception as e:
        final_list = []
    return final_list

def get_datasets_list(url):
    initial_list=[]
    final_list=[]
    f, output_validation = endpoint_request(url+'/map')
    total_response = json.loads(f.text)
    new_url = list_dataset_endpoint(total_response)

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
    return final_list

class SettingsForm(forms.Form):
    choices_irr = [("HIT", "HIT"), ("MISS", "MISS"), ("ALL", "ALL"), ("NONE", "NONE")]
    choices_granularity = [("record", "record"), ("count", "count"), ("boolean", "boolean")]
    choices_testmode = [("True", "True"), ("False", "False")]
    url_link = forms.CharField(widget=forms.TextInput(attrs={'size':50}), max_length=100, required=False, help_text="<div style='margin-bottom: 8px;'>Beacon URL</div>", label="")
    include_resultset_responses = forms.MultipleChoiceField(
        choices=choices_irr, 
        widget=forms.CheckboxSelectMultiple,
        initial=[choice[0] for choice in choices_irr]
    )
    granularity = forms.MultipleChoiceField(
        choices=choices_granularity, 
        widget=forms.CheckboxSelectMultiple,
        initial=[choice[0] for choice in choices_granularity]
    )
    test_mode = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'ios-switch'},),
        initial=True
    )

class EndpointsForm(forms.Form):

    map_url = forms.CharField(
        widget=forms.TextInput(attrs={'size':50}), max_length=100, help_text="<div style='margin-bottom: 8px;'>Loaded URL</div>", label=""
    )
    endpoint_url = forms.CharField(
        widget=forms.HiddenInput()
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

    number_of_endpoints = forms.CharField(widget=forms.TextInput(attrs={'size':0}))

    endpoints_collected = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, endpoint_url=None, include=None, granularity=None, test_mode=None, endpoints_collected=None,**kwargs):
        super().__init__(*args, **kwargs)

        if endpoint_url:
            self.fields["endpoints_collected"].choices = get_map_endpoints_list(endpoint_url)
            self.fields["endpoints_collected"].initial = [choice[0] for choice in self.fields["endpoints_collected"].choices]
            self.fields['map_url'].widget.attrs['readonly'] = True
            self.fields['map_url'].widget.attrs['class'] = 'form-control bg-light text-muted'
            self.fields['map_url'].initial=endpoint_url+'/map'
            self.fields['number_of_endpoints'].widget.attrs['readonly'] = True
            self.fields['number_of_endpoints'].initial = len(self.fields["endpoints_collected"].choices)
        if include:
            self.fields["include"].choices = [(include[0], include[0])]
        if granularity:
            self.fields["granularity"].choices = [(granularity[0], granularity[0])]
        if test_mode:
            self.fields["test_mode"].choices = [(test_mode[0], test_mode[0])]


class DatasetsForm(forms.Form):
    datasets_url = forms.CharField(
        widget=forms.TextInput(attrs={'size':50}), max_length=100, help_text="<div style='margin-bottom: 8px;'>Loaded URL</div>", label=""
    )
    endpoint_url = forms.CharField(widget=forms.HiddenInput())
    include = forms.CharField(widget=forms.HiddenInput())
    granularity = forms.CharField(widget=forms.HiddenInput())
    test_mode = forms.CharField(widget=forms.HiddenInput())
    endpoints_collected = forms.CharField(widget=forms.HiddenInput())

    number_of_datasets = forms.CharField(widget=forms.TextInput(attrs={'size':0}))

    datasets_collected = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, endpoint_url=None, include=None, granularity=None, test_mode=None, endpoints_collected=None, **kwargs):
        super().__init__(*args, **kwargs)

        if endpoint_url:
            self.fields["datasets_collected"].choices = get_datasets_list(endpoint_url)
            self.fields["datasets_collected"].initial = [choice[0] for choice in self.fields["datasets_collected"].choices]
            self.fields['number_of_datasets'].widget.attrs['readonly'] = True
            self.fields['number_of_datasets'].initial = len(self.fields["datasets_collected"].choices)
            self.fields['datasets_url'].widget.attrs['readonly'] = True
            self.fields['datasets_url'].widget.attrs['class'] = 'form-control bg-light text-muted'
            self.fields['datasets_url'].initial=endpoint_url+'/datasets'

class SummaryForm(forms.Form):
    datasets_url = forms.CharField(
       widget=forms.HiddenInput()
    )
    url_link = forms.CharField(widget=forms.HiddenInput())
    include_resultset_responses = forms.CharField(widget=forms.HiddenInput())
    granularity = forms.CharField(widget=forms.HiddenInput())
    test_mode = forms.CharField(widget=forms.HiddenInput())
    endpoints_collected = forms.CharField(widget=forms.HiddenInput())

    number_of_datasets = forms.CharField(widget=forms.HiddenInput())

    datasets_collected = forms.MultipleChoiceField(
        choices=[],
        widget=forms.HiddenInput()
    )

class ChannelForm(forms.Form):
    url_link = forms.CharField(widget=forms.HiddenInput())
    include_resultset_responses = forms.CharField(widget=forms.HiddenInput())
    granularity = forms.CharField(widget=forms.HiddenInput())
    test_mode = forms.CharField(widget=forms.HiddenInput())
    endpoints_collected = forms.CharField(widget=forms.HiddenInput())
    datasets_collected = forms.CharField(widget=forms.HiddenInput())