from django import forms

from app_resources.models import Persons
from dashboard.models import Department
from authentications.models import User


from .models import Config, Nabatshieh, Permission, Reasons, AddDuration


class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = '__all__'
    time_start_working = forms.TimeField(widget=forms.TimeInput(
        attrs={'class': 'form-control', 'type': 'time'}),required=False)
    num_end_permission =forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),required=False)
    num_hour_working = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),required=False)
    url_extract_data = forms.URLField(widget=forms.URLInput(
        attrs={'class': 'form-control', 'placeholder': 'https://www.example.com'}),required=False)
    url_image = forms.URLField(widget=forms.URLInput(
        attrs={'class': 'form-control', 'placeholder': 'https://www.example.com'}),required=False)
    url_extract_data_back = forms.URLField(widget=forms.URLInput(
        attrs={'class': 'form-control', 'placeholder': 'https://www.example.com'}),required=False)
    token_access = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'YOUR_FACEBOOK_ACCESS_TOKEN'}),required=False)
    url_whatsapp = forms.URLField(widget=forms.URLInput(
        attrs={'class': 'form-control', 'placeholder': 'https://graph.facebook.com/v17.0/119791417748534/messages'}),required=False)


class AddSheftForm(forms.ModelForm):
    class Meta:
        model = Nabatshieh
        fields = '__all__'
    time_start_working = forms.TimeField(widget=forms.TimeInput(
        attrs={'class': 'form-control', 'type': 'time'}), required=True)
    num_hour_working = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': 'form-control'}), required=True)
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}), required=True)
    persions = forms.ModelMultipleChoiceField(
        queryset=Persons.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control', 'id': 'assigned-team-members'}),
        required=False
    )


class WhenForm(forms.ModelForm):
    WHEN_CHOICES = [
        ('الدخول', 'الدخول'),
        ('الخروج', 'الخروج'),
    ]

    when = forms.ChoiceField(
        choices=WHEN_CHOICES, widget=forms.RadioSelect, initial='entry', required=True
    )
    fromm = forms.TimeField(widget=forms.TimeInput(
        attrs={'class': 'form-control', 'type': 'time'}), required=False)
    too = forms.TimeField(widget=forms.TimeInput(
        attrs={'class': 'form-control', 'type': 'time'}), required=False)
    persions = forms.ModelMultipleChoiceField(
        queryset=Persons.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control', 'id': 'assigned-team-members'}),
        required=False
    )
    num_reason = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control', 'type': 'number'}))

    class Meta:
        model = Reasons
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AddDurationForm(forms.ModelForm):
    class Meta:
        model = AddDuration
        fields = '__all__'
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}), required=True)
    num_hour_working = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': 'form-control'}), required=True)
    persions = forms.ModelMultipleChoiceField(
        queryset=Persons.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control', 'id': 'assigned-team-members'}),
        required=False
    )


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['for_emp','reason']

    for_emp = forms.ModelMultipleChoiceField(
        queryset=Persons.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control', 'id': 'assigned-team-members'}),
        required=True
    )
    reason = forms.ModelChoiceField(
        label='السبب',
        queryset=Reasons.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=True
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PermissionForm, self).__init__(*args, **kwargs)
        if user and user.person_id:
            persons=Persons.objects.filter(id=user.person_id)
            self.fields['for_emp'].queryset = persons
            self.fields['for_emp'].initial = persons


class DepartmentForm(forms.ModelForm):
    class Meta:
        model=Department
        fields=['name','user_manager']
    name=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=True)
    user_manager=forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control select2', 'placeholder': 'Manager'}),
        required=True
    )