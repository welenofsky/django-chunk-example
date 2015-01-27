from django import forms

class MediaForm(forms.Form):
    title = forms.CharField(max_length='255')
    description = forms.CharField(max_length='500')
    file = forms.FileField()