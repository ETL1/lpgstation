
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('login.urls')),
    path('', include('core.urls')),
    path('rest/v1/core/', include('core.urls')),
    #  API URLs (core_sys)
    path('rest/v1/', include('restapi.urls')),
    path('rest/v1/users/', include('restapi.urls')),
    path('rest/v1/account/', include('restapi.urls')),
    path('rest/v1/accounts/', include('restapi.acc_api.urls', 'account_api')),
    #   ///////////////////////////////////////////////////
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
