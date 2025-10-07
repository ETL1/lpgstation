
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .models import CustomUserz
from .forms import RegisterForm, LoginForm

class RegisterView(CreateView):
    model = CustomUserz
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

class SignInView(LoginView):
    template_name = 'authentication/layouts/corporate/sign-in.html'
    authentication_form = LoginForm

class SignOutView(LogoutView):
    pass

