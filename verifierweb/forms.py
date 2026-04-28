from django import forms
from bash.models import AgeOfOnset


class BamForm(forms.Form):
    choices_irr = [("HIT", "HIT"), ("MISS", "MISS"), ("ALL", "ALL"), ("NONE", "NONE")]
    choices_granularity = [("record", "record"), ("count", "count"), ("boolean", "boolean")]
    choices_testmode = [("True", "True"), ("False", "False")]
    url_link = forms.CharField(widget=forms.TextInput(attrs={'size':50}), max_length=100, required=False, help_text="<div style='margin-bottom: 8px;'>Beacon URL</div>", label="")
    include_resultset_responses = forms.ChoiceField(choices=choices_irr, label="includeResultsetResponses")
    granularity = forms.ChoiceField(choices=choices_granularity, label="granularity")
    test_mode = forms.ChoiceField(choices=choices_testmode, label="testMode")
    


