"""paydesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from login.views import login, logout
from django.conf import settings
from django.conf.urls.static import static

from django.shortcuts import redirect, render
from .views import user_page


urlpatterns = [
    # url(r'^$', app_views.index, name='home'),
    # url('homepage/', app_views.home_page, name='home'),
    # url('cancellation/', app_views.cancel_page, name='cancel'),
    # url('dashboard/', app_views.dashboard, name='dashboard-page'),
    path('admin/', admin.site.urls),
    url('login/', login, name='login'), 
    # url(r'^register$', app_views.register_user),
    url('logout/', logout, name='logout'),
    url('user-list/', user_page, name='user-list'),
    # url('logged-out/', user_login_page, name='logged-out'),
    # url(r'^delete-account/(?P<id>\w+)/$', api_view.deleteUserAcct, name='delete-account'),
    # path('recover-account/', api_view.recover_account, name='recover-account'),
    # path('change-admin-password', api_view.change_admin_passwd, name='change-admin-password'),
    # path('recover-account/', api_view.recover_account, name='recover-account'),
    # path('.well-known/assetlinks.json', app_views.read_file, name='well-known'),
    #   ///////////////////////////////////////////////////

    # #  API URLs (core_sys)
    # path('rest/v1/', include('restapi.urls')),
    # path('rest/v1/users/', include('restapi.urls')),
    # path('rest/v1/account/', include('restapi.urls')),
    # path('rest/v1/accounts/', include('restapi.acc_api.urls', 'account_api')),
    
    # #  Payment URLs (payapi)
    # path('payment/', include('payapi.urls')),
    # path('shopping/', include('payapi.urls')),
    # path('subsys/', include('payapi.urls')),
    # path('rest/v1/payment/', include('payapi.urls')),
    # #   ///////////////////////////////////////////////////

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = lpg_station.views.handler404
# handler500 = lpg_station.views.handler500
