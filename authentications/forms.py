from django import forms
from app_resources.models import Persons
from authentications.models import Branch, User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
class LoginForm(forms.Form):
    email = forms.EmailField(label='email',required=True,widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'email'}))
    password = forms.CharField(label='password',required=True,widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'password'}))
    branches = forms.ModelChoiceField(
        label='Branch',
        queryset=Branch.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=True
    )

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['branch','username','first_name','last_name','is_active','groups','person_id']
    
    branch=forms.ModelChoiceField(
        label='Branch',
        queryset=Branch.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'Branch'}),
        required=True
    )
    username=forms.EmailField(required=True,widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name=forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','id':'first_name'}))
    last_name=forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','id':'last_name'}))
    is_active=forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'form-check-input','role':'switch'}),required=False)
    password=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),required=True)
    groups=forms.ModelMultipleChoiceField(
        label='المجموعة', 
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control', 'id': 'assigned-team-members'}),
        required=False
        )
    person_id=forms.ModelChoiceField(
         label='ربط موظف',
        queryset=Persons.objects.all(),
        widget=forms.Select(
        attrs={
            'class':'form-control',
           'id':"choices-single-default",
           'onchange':'setNames(event)'
        }
        
    ),
        required=False)
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.person_id = self.cleaned_data.get('person_id').id
        if commit:
            instance.save()
        return instance
class UpdateForm(UserForm):
    password=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),required=False)


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class GroupsForm(forms.ModelForm):
    class Meta:
        model=Group
        fields=['name','permissions']
    name=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    permissions=forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'form-control', 'id': 'assigned-team-members'}),
        required=True
    )
class PermissionForm(forms.ModelForm):
    class Meta:
        model=Permission
        fields=['name','content_type','codename']
    name=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    codename=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    content_type=forms.ModelChoiceField(
        label='content_type',
        queryset=ContentType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'placeholder': 'content type'}),
        required=True
    )