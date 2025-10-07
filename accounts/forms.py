
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUserz

class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUserz
        fields = ('username','email','phone','role')

class LoginForm(AuthenticationForm):
    pass
