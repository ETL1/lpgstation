from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.forms import ModelForm
from django import forms

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'fname', 'u_pic',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)

class CustomRegistForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = (
        'fname',
        'sname',
        'email',
        'phone_num',
        )

class EmploySignUpForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'fname', 'sname','password1', 'password2', 'access_level',)
        labels = {
            "fname": "First Name",
            "sname": "Last Name",
            "access_level": "Access"
        }
        
        IM_CHOICES = (
            ('0', 'System Admin'),
            ('1', 'Management User'),
            ('2', 'Finance User'),
            ('3', 'Container User'),
            ('4', 'Depot User'),
            ('5', 'Data Entry User'),
        )
        
        widgets = {
            'access_level': forms.Select(choices=IM_CHOICES,attrs={'class': 'form-select'}),
            'is_staff': forms.BooleanField(label='My Checkbox', required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})),
        }

class CustomCheckboxInput(forms.CheckboxInput):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {})
        kwargs['attrs'].update({'class': 'form-check-input'})
        super().__init__(*args, **kwargs)
        
class AdminUserAccountForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'fname', 'sname', 'password1', 'password2', 'access_level','uid')
        labels = {
            "fname": "First Name",
            "sname": "Last Name",
            "access_level": "Access",
        }
        IM_CHOICES = (
            ('0', 'System Admin'),
            ('1', 'Management User'),
            ('2', 'Finance User'),
            ('3', 'Container User'),
            ('4', 'Depot User'),
            ('5', 'Data Entry User'),
        )
        widgets = {
            'access_level': forms.Select(choices=IM_CHOICES,attrs={'class': 'form-select'}),
            'uid': forms.HiddenInput(),
        }
        
class CustomRegistExternalForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = (
        'title',
        'fname',
        'sname',
        'email',
        'phone_num',
        )