from django import forms
from bash.models import AgeOfOnset


class BamForm(forms.Form):
    url_link = forms.CharField(max_length=100, required=False, help_text="<span class='hovertext' data-hover='Introduce the URI for the beacon to be verified'>Beacon URI</span>", label="")

class AgeOfOnsetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AgeOfOnsetForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field 
    choices_time = [("P65Y", "P65Y")]
    choices_histological = [("ICDO3:8480/3", "ICDO3:8480/3")]
    choices_tumorProgression= [("ICD10:C18.6", "ICD10:C18.6")]
    choices_tumorGrade= [("NCIT:C27982", "NCIT:C27982")]
    choices_procedure= [("No Neoadjuvant Therapy Given", "No Neoadjuvant Therapy Given")]
    timeOfCollection = forms.ChoiceField(choices=choices_time, label="timeOfCollection")
    histologicalDiagnosis = forms.ChoiceField(choices=choices_histological, label="histologicalDiagnosis")
    tumorProgression = forms.ChoiceField(choices=choices_tumorProgression, label="tumorGrade")
    tumorGrade = forms.ChoiceField(choices=choices_tumorGrade, label="tumorGrade")
    procedure = forms.ChoiceField(choices=choices_procedure, label="procedure")

