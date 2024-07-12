from django import forms
from bash.models import AgeOfOnset


class BamForm(forms.Form):
    url_link = forms.CharField(widget=forms.TextInput(attrs={'size':50}), max_length=100, required=False, help_text="<div style='margin-bottom: 8px;'>Beacon URL</div>", label="")

class AgeOfOnsetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AgeOfOnsetForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field 
    choices_time = [("P65Y", "P65Y")]
    choices_histological = [("ICDO3:8480/3", "ICDO3:8480/3")]
    choices_tumorProgression= [("ICD10:C18.6", "ICD10:C18.6")]
    choices_tumorGrade= [("NCIT:C27982", "NCIT:C27982")]
    choices_procedure= [("No Neoadjuvant Therapy Given", "No Neoadjuvant Therapy Given")]
    timeOfCollection2 = forms.ChoiceField(choices=choices_time, label="timeOfCollection")
    histologicalDiagnosis2 = forms.ChoiceField(choices=choices_histological, label="histologicalDiagnosis")
    tumorProgression2 = forms.ChoiceField(choices=choices_tumorProgression, label="tumorGrade")
    tumorGrade2 = forms.ChoiceField(choices=choices_tumorGrade, label="tumorGrade")
    procedure2 = forms.ChoiceField(choices=choices_procedure, label="procedure")

class NewForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(NewForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field 
    biosampleId = forms.BooleanField(initial=False, required=False,help_text="id=sample2")
    individualId = forms.BooleanField(initial=False, required=False,help_text="individualId=patient1")
    sampledTissue = forms.BooleanField(initial=False, required=False,help_text="sampledTissue.id=ICD10:C18.7")
    timeOfCollection = forms.BooleanField(initial=False,required=False,help_text="timeOfCollection.age.iso8601duration=P77Y")
    histologicalDiagnosis = forms.BooleanField(initial=False,required=False,help_text="histologicalDiagnosis.id=ICDO3:8480/3")
    tumorProgression = forms.BooleanField(initial=False,required=False,help_text="tumorProgression.id=NCIT:C27982")
    tumorGrade = forms.BooleanField(initial=False,required=False,help_text="tumorGrade.id=NCIT:C27982")
    


