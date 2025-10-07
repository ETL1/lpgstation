import email
from urllib import response
import uuid
from django.shortcuts import redirect, render
import json
from rest_framework import generics
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from django.contrib import messages
from restapi import models
from login.models import CustomUser
from .serializers import ActivaSerializer, ChangePasswordSerializer, DataSerializer, UserSerializer, ChatSerializer, DrvSerializer, UserUpdateSerializer
import string
from random import *
from uuid import uuid4
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from decouple import config


@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
def veri_account(request, pk):
    # try:
    info_data = CustomUser.objects.get(uid=pk)
    # except Delivery_lst.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "PUT":
        deli_data = JSONParser().parse(request)
        deli_serializer = UserSerializer(info_data, data=deli_data)
        if deli_serializer.is_valid():
            deli_serializer.save()
            return Response(deli_serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)


def api_end_keygen():
    _keys = uuid.uuid4().hex[:32]
    return _keys

@api_view(['GET', ])
@permission_classes([AllowAny])
def availx(request):
    try:
        info_data = CustomUser.objects.all().count()
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = UserSerializer(info_data)
        return Response(serializer.data)
  
# /////  Generate API KEY for non authenticated access for APP.    
@api_view(['POST', ])
@permission_classes([AllowAny])
def allow_me_request(request):
    api_key, key = APIKey.objects.create_key(name='ltv-sess-'+api_end_keygen())
    response = {
        'response': 'Welcome to Vivo App',
        'resMssg': str(api_key),
    }
    return Response(response, status=status.HTTP_200_OK) 


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def info_detail(request, id):
    try:
        info_data = models.Infor.objects.get(id=id)
    except models.Infor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = DataSerializer(info_data)
        return Response(serializer.data)


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def userInfo(request, id):
    try:
        info_data = CustomUser.objects.get(uid=id)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = UserSerializer(info_data)
        return Response(serializer.data)
    
@permission_classes([IsAuthenticated])
def deleteUserAcct(request, id):
   if request.method == "GET":
       try:
        info_data = CustomUser.objects.get(uid=id)
        info_data.delete()
        return redirect('/user-list')
       except info_data.DoesNotExist:
        return redirect('/user-list')
   else:
      return redirect('/user-list') 


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def activate_acct(request, id):
    try:
        info_data = CustomUser.objects.get(act_code=id)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = DrvSerializer(info_data)
        return Response(serializer.data)
    

@api_view(['GET', ])
@permission_classes([AllowAny])
def activate_user(request, id):
    try:
        info_data = CustomUser.objects.get(acc_token=id)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ActivaSerializer(info_data)
        return Response(serializer.data)


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def chatItemView(request, id):
    try:
        info_data = models.ChatList.objects.get(mid=id)
    except models.ChatList.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ChatSerializer(info_data)
        return Response(serializer.data)



#//////////////////////////////////////////////////
#   APP USER FUNCTIONS PROTECTED BY ENCRYPTION KEY
@api_view(['PUT', ])
@permission_classes([AllowAny])
def updateuser_account(request, pk):
    info_data = CustomUser.objects.get(uid=pk)
    if request.method == "PUT":
        deli_data = JSONParser().parse(request)
        deli_serializer = UserUpdateSerializer(info_data, data=deli_data)
        if deli_serializer.is_valid():
            deli_serializer.save()
            return Response(deli_serializer.data)
        data = deli_serializer.errors
        print(deli_serializer.errors)
        return Response(data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


######################################
### CHANGE PASSWORD CODE
class UpdateAccount(generics.ListCreateAPIView):
    @api_view(['PUT', ])
    @permission_classes([IsAuthenticated])
    def confirm_account_verify(request, pk):
        try:
            info_data = CustomUser.objects.get(uid=pk)
        except CustomUser.DoesNotExist:
            response = {
                    'status': 'error',
                    'code': status.HTTP_200_OK,
                    'message': "",
                    'data': []
                    }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        if request.method == "PUT":
            if info_data is not None:
                # info_data.update(is_verified=True)
                CustomUser.objects.filter(uid=pk).update(is_verified=True)
                response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Account has been successfully verified',
                'data': []
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    'status': 'error-invalid',
                    'code': status.HTTP_200_OK,
                    'message': "Invalid code",
                    'data': []
                    }
                return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(response, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
def delete_account(request, pk):
    info_data = CustomUser.objects.get(uid=pk)
    if request.method == "PUT":
        deli_data = request.data
        # serializer = UserDeleteSerializer(data=deli_data)
        # if serializer.is_valid():
        #     uid = serializer.data.get('uid')
        if info_data is None:
            response = {
            'status': 'error',
            'code': status.HTTP_400_BAD_REQUEST,
            'message': 'This account has not been verified.',
            'data': []
            }
            return Response(response)
        else:
            CustomUser.objects.filter(uid=pk).update(is_active=False)
            response = {
            'status': 'success',
            'code': status.HTTP_200_OK,
            'message': 'Account was Deleted successfully',
            'data': []
        }
            return Response(response, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
def change_account(request, pk):
    # try:
    info_data = CustomUser.objects.get(uid=pk)
    # except CustomUser.DoesNotExist:
        # return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "PUT":
        deli_data = request.data
        serializer = ChangePasswordSerializer(data=deli_data)
        if serializer.is_valid():
                # Check old password
            old_password = serializer.data.get('old_password')
            new_password = serializer.data.get('new_password')
            if not info_data.check_password(old_password):
                response = {
                'status': 'error',
                'code': status.HTTP_200_OK,
                'message': 'Old password incorrect.',
                'data': []
            }
                return Response(response)
            # # set_password also hashes the password that the user will get
            else:
                info_data.set_password(new_password)
                info_data.save()
                response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
                return Response(response, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


# @api_view(['POST', ])
# @permission_classes([IsAuthenticated])
def change_admin_passwd(request):
    # try:
    info_data = CustomUser.objects.get(uid=request.user.uid)
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        # Check old password
        if not info_data.check_password(old_password):
            messages.info(request, 'Old password is incorrect. Try Again')
            if request.user.access_level == '0':
                return redirect('/user-list?resp=deny')
            else:
                return redirect('/?resp=deny')
        # # set_password also hashes the password that the user will get
        else:
            info_data.set_password(new_password)
            info_data.save()
            messages.info(request, 'Password change successfully completed.')
            return redirect('/?resp=amend')
    return redirect('/user-list?resp=rejected')



class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated,)
    
    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    merge_data = {
        'link': "?token={}".format(reset_password_token.key)
    }
    html_body = render_to_string("../templates/email_page.html", merge_data)

    message = EmailMultiAlternatives(
       subject='Reset Password: Abbies App',
       body=html_body,
       from_email=config('EMAIL_HOST_USER'),
       to=[reset_password_token.user.email],
       headers = {'From': 'Abbies App', 'Reply-To': config('EMAIL_HOST_USER'), 'format': 'flowed'}
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)


@permission_classes([AllowAny])
def recover_account(request):
    return render(request, 'html/auth-forgot-password-basic.html')