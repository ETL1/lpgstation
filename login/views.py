import qrcode
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from login.forms import CustomUserCreationForm
import io
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.db.models import Q

from login.models import CustomUser as cus, Instructor, Student, gen8

# Create your views here.
#       LOGIN AND LOGOUT

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            if user.is_active and user.access_level == '0' or user.access_level == '2' or user.access_level == '1' or user.access_level == '3' or user.access_level == '4' or user.access_level == '5':
                auth.login(request, user)
                if user.access_level == '5':
                    return redirect("/")
                else:
                    return redirect("/")
            else:
                auth.logout(request)
                messages.info(request, 'Sorry! Account does not exist.')
                return redirect('/')
        else:
            messages.info(request, 'Sorry! Invalid email and password. Please try again')
            return redirect('/')
    else:
        return render(request, 'authentication/layouts/corporate/sign-in.html')


def user_page(request):
    user_list = cus.objects.all()
    context = {
        'user_list' : user_list,
    }
    return render(request, 'pages/apps/user-list.html', context)


@login_required
def logout(request):
    if request.user.access_level == '5':
        auth.logout(request)
        return redirect("/logged-out")
    else:
        auth.logout(request)
        return redirect("/")


def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/')


def read_file(request):
    f = open('.well-known/assetlinks.json', 'r')
    file_content = f.read()
    f.close()
    return HttpResponse(file_content, content_type="text/plain")
