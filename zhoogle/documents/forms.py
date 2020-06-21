from django import forms

from .models import Occurrence

class SearchForm(forms.Form):
    q = forms.CharField()