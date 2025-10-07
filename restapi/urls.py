from django.urls import path
from django.conf.urls import url, include
from restapi import views as api_view
from .views import ChangePasswordView, UpdateAccount

urlpatterns = [
    # path('', ListInfor.as_view()),
    # path('<int:pk>/', DetailInfor.as_view()),

    # //// User Account Urls
    path('avail/', api_view.availx, name='status'),
    url(r'^connect-serv/$', api_view.allow_me_request, name='connect-serv'),

    # //// User Account Urls
    # path('users/', ListUserAccount.as_view(), name='users'),
    url(r'^user_details/(?P<id>\w+)/$', api_view.userInfo, name='user_details'),
    url(r'^activate/(?P<id>\w+)/$', api_view.activate_acct, name='user_activation'),
    url(r'^action-user/(?P<id>\w+)/$', api_view.activate_user, name='user_activate'),
    # url(r'^activa/(?P<id>\w+)/$', ListDrv.get_acct, name='activa'),
    # path('<int:pk>/', DetailUserAccount.as_view()),
    url(r'^update/(?P<pk>\w+)/$', api_view.updateuser_account),
    url(r'^delete/(?P<pk>\w+)/$', api_view.delete_account),
    # url(r'^student-list/(?P<id>\w+)/$', api_view.studentView, name='student-list'),
    # url(r'^assigned-lessons/(?P<id>\w+)/$', api_view.studentView, name='assigned-lessons'),
    url(r'^change-password/(?P<pk>\w+)/$', api_view.change_account, name='change-password'),
    url(r'^verify-account/(?P<pk>\w+)/$', UpdateAccount.confirm_account_verify, name='verify-account'),
    path('password-reset/', include('django_rest_passwordreset.urls')),
    path('password-reset/confirm/', include('django_rest_passwordreset.urls')),
    

    # //// Chats Urls
    # path('chats/', ListChat.as_view(), name='chats'),
    url(r'^url/(?P<resp>\w+)/$', api_view.chatItemView, name='chat_details'),

    # //// Delivery Urls
    # path('deliveries/', ListDelv.as_view(), name='deliveries'),
    # url(r'^delivery_details/(?P<id>\w+)/$',
        # api_view.deliveryItemView, name='delivery_details'),
    # url(r'^delivery_list/(?P<id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/', api_view.deliveryListView, name='delivery_list'),
    # url(r'^deli_complete/(?P<pk>\w+)/$', api_view.deli_complete, name='delivery_complete'),
    # url(r'^verify/(?P<pk>\w+)/$', api_view.veri_account, name='verify_account'),
]
