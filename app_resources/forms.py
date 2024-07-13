import base64
import io
from django import forms

from .models import *
from django_select2.forms import Select2MultipleWidget


class CamerasForm(forms.ModelForm):
    class Meta:
        model = Cameras
        fields = ['name', 'camera_type', 'status',
                  'description', 'connection_string']

    camera_type = forms.ChoiceField(
        choices=[('indoor', 'Indoor'), ('outdoor', 'Outdoor')])
    status = forms.ChoiceField(
        choices=[('enable', 'Enable'), ('disable', 'Disable')])

    def __init__(self, *args, **kwargs):
        super(CamerasForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Name of Camera'
        self.fields['connection_string'].widget.attrs['placeholder'] = 'connection string'
        self.fields['description'].widget = forms.Textarea(
            attrs={'class': 'form-control', 'rows': 5})


class PersonsForm(forms.ModelForm):
    class Meta:
        model = Persons
        fields = ['name', 'gender', 'date_of_birth', 'image', 'status', 'allowed_cameras', 'front_national_img',
                  'back_national_img',
                  'id_national', 'address', 'job_title','type_register','department','registration_number','mobile_whatsapp']
        widgets = {
            'image': forms.ClearableFileInput(
                attrs={'class': 'single-fileupload3', 'required': False,'accept':'image/png, image/jpeg, image/gif' }),
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': False ,'accept':'image/png, image/jpeg, image/gif'}),
            'date_of_birth': forms.TextInput(attrs={
                'class': 'form-control',
                'id':'date',
                'required': False,
            }),
            'front_national_img': forms.ClearableFileInput(
                attrs={'class': 'single-fileupload1','required': False,'accept':'image/png, image/jpeg, image/gif'}),
            'back_national_img': forms.ClearableFileInput(
                attrs={'class': 'single-fileupload2', 'required': False,'accept':'image/png, image/jpeg, image/gif'}),
            'id_national': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'registration_number':forms.NumberInput(attrs={'class': 'form-control', 'required': False}),
            'mobile_whatsapp':forms.TextInput(attrs={'class': 'form-control', 'required': False})
        }

        
        labels = {
            'image': 'الصور الشخصية',
            'front_national_img': 'صورة البطاقة الامامية',
            'back_national_img': 'صورة البطاقة الخلفية',
            'job_title': 'الاسم الوظيفة',
            'mobile_whatsapp':"رقم واتساب"
        }
        allowed_cameras = forms.ModelMultipleChoiceField(
            queryset=Cameras.objects.all(),
            widget=Select2MultipleWidget(attrs={'style': 'width: 100%;',
                                                'class': "select2", 'multiple': "multiple",
                                                'data-placeholder': "Select a State",

                                                }),
            required=True,

        )
    department = forms.ModelChoiceField(
        label='القسم', 
        queryset=Department.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=False
        )
    GENDER_CHOICES = [
        ('ذكر', 'ذكر'),
        ('انثي', 'انثي'),
    ]
    TYPE_CHOICES = [
             ('زائر', 'زائر'),
            ('موظف', 'موظف'),
]
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES, widget=forms.RadioSelect, initial='ذكر')
    type_register = forms.ChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='موظف'
    )
    status = forms.ChoiceField(choices=[(
        'whitelist', 'whitelist'), ('blacklist', 'blacklist'), ('unknown', 'unknown')])

    def __init__(self, *args, **kwargs):
        super(PersonsForm, self).__init__(*args, **kwargs)
        self.fields['date_of_birth'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-control'
    
    def clean_id_national(self):
        id_national = self.cleaned_data['id_national']
        if self.instance.id is not None:
            if self.instance.id_national == id_national:
                return id_national
        else:
            exists = Persons.objects.filter(id_national=id_national)
            if exists:
                raise forms.ValidationError('هذ الشخص مسجل سابقا')
        return id_national


class InformationsForm(forms.ModelForm):
    class Meta:
        model = Information
        fields = ['department', 'type', 'reason', 'other', 'visior_type']
    department = forms.ModelChoiceField(
        label='القسم',
        queryset=Department.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=False
    )
    empolyee= forms.ModelChoiceField(
        label='الموظف',
        queryset=Persons.objects.filter(type_register='موظف'),
        widget=forms.Select(
            attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=False
    )
    type = forms.ModelChoiceField(
        label='النوع',
        queryset=Type.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=False
    )
    reason = forms.ModelChoiceField(
        label='السبب',
        queryset=Reason.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=False
    )
    other = forms.ModelChoiceField(
        label='اخري',
        queryset=Other.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=False
    )
    visior_type = forms.ModelChoiceField(
        label='نوع الزياره',
        queryset=VisiTortype.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=False
    )
