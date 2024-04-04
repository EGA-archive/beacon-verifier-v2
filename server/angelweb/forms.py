from django import forms

class BamForm(forms.Form):
    url_link = forms.CharField(max_length=100, required=False, help_text="<span class='hovertext' data-hover='Introduce the URI for the beacon to be verified'>Beacon URI</span>", label="")

    