from django import forms

from dashboard.models import *


class SearchIDForm(forms.Form):
   frontImage = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'single-fileupload w-100', "accept":"image/png, image/jpeg, image/gif"}),
        label='National Image',
        required=False
    )
   National_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

class FilterForm(forms.Form):
    date_rang=forms.CharField(label="date range",widget=forms.TextInput(attrs={'class':'form-control float-right','id':'reservation'}))
    
    department = forms.ModelChoiceField(
        label='Department',
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Department'}),
       required=False
    )

    type = forms.ModelChoiceField(
        label='type',
        queryset=Type.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'type'}),
       required=False
    )

    typeVisitor = forms.ModelChoiceField(
        label='visitor type',
        queryset=VisiTortype.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'type Visitor'}),
         required=False
    )

    reason = forms.ModelChoiceField(
        label='reason',
        queryset=Reason.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'reason'}),
         required=False
    )

    other = forms.ModelChoiceField(
        label='other',
        queryset=Other.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'other'}),
      required=False   
    )