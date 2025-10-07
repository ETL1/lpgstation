from django.urls import path
from django.conf.urls import url, include
from restapi.acc_api.views import registration_view, CustomAuthToken
# from rest_framework.authtoken.views import obtain_auth_token

app_name = "api_dom"

urlpatterns = [
    path('app_register', registration_view, name='register'),
    # path('login', obtain_auth_token, name='login'),
    path('login', CustomAuthToken.as_view()),
]
