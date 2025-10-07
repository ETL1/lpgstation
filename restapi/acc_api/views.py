import email
from genericpath import exists
from unicodedata import name
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from login.models import CustomUser
from restapi.acc_api.serializers import RegisterSerializer
from rest_framework.authtoken.models import Token
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail
from decouple import config
import uuid
import string
from random import *
from django.utils import timezone


def genAccountVerify(): 
        _keys = uuid.uuid4().hex[:16]
        return _keys

def verify_key():
    min_char = 6
    max_char = 6
    allchar = string.digits + string.digits
    uid = ''.join(choice(allchar) for x in range(randint(min_char, max_char)))
    return uid

# //////////    App Registration via API   /////////
@api_view(['POST', ])
@permission_classes([AllowAny | HasAPIKey])
def registration_view(request):
    key = request.META["HTTP_X_API_KEY"].split()[0]
    try:
        api_key = APIKey.objects.get(name=key)
        if request.method == 'POST':
            serializer = RegisterSerializer(data=request.data)
            data = {}
            now = timezone.now()
            verify = verify_key()
            tokn = genAccountVerify()
            if serializer.is_valid():    
                account = serializer.save()
                data['response'] = "Successfully registered a new user."
                data['email'] = account.email
                data['fname'] = account.fname
                data['sname'] = account.sname
                data['phone_num'] = account.phone_num
                token = Token.objects.get(user=account).key
                data['token'] = token
                
                merge_data = {
                'link': "{}".format(verify)
                }
                html_body = render_to_string("../templates/register_page.html", merge_data)

                message = EmailMultiAlternatives(
                subject='Account Registration: Camnet TV',
                body=html_body,
                from_email=config('EMAIL_HOST_USER'),
                to=[data['email']],
                headers = {'From': 'Camnet TV', 'Reply-To': config('EMAIL_HOST_USER'), 'format': 'flowed'}
                )
                message.attach_alternative(html_body, "text/html")
                message.send(fail_silently=False)
                usr_data = CustomUser.objects.filter(email=data['email']).update(acc_token=verify, token=tokn, lastOnline=now)
                usr_data.save()
            else:
                data = serializer.errors
            return Response(data)
    except APIKey.DeosNotExist:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@permission_classes([AllowAny | HasAPIKey])
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # key = request.META["HTTP_X_API_KEY"].split()[0]
        # api_key = APIKey.objects.get(name=key)
        try:
            if request.method == 'POST':
                serializer = self.serializer_class(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                user = serializer.validated_data['user']
                if user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    print(serializer.errors)
                    return Response({
                    'token': token.key,
                    'fname': user.fname,
                    'acc_token': user.acc_token,
                    'site_id': str(user.site_id),
                    'sname': user.sname,
                    'phone_num': user.phone_num,
                    'uid': user.uid
                    })
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                
            else:
                Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
            
