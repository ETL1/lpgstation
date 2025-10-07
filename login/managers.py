# from lib2to3.pgen2 import token
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail
from decouple import config
import uuid
import string
from random import *


def genAccountVerify(): 
        _keys = uuid.uuid4().hex[:16]
        return _keys

def verify_key():
    min_char = 6
    max_char = 6
    allchar = string.digits + string.digits
    uid = ''.join(choice(allchar) for x in range(randint(min_char, max_char)))
    return uid

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        verify = verify_key()
        token = genAccountVerify()
        user = self.model(email=email,lastOnline=now, acc_token=verify, token=token, date_joined=now, **extra_fields)
        
        user.set_password(password)
        user.save()
        
        merge_data = {
        'link': "{}".format(verify)
        }
        html_body = render_to_string("../templates/register_page.html", merge_data)

        message = EmailMultiAlternatives(
        subject='Account Registration: Abbies App',
        body=html_body,
        from_email=config('EMAIL_HOST_USER'),
        to=[email],
        headers = {'From': 'Abbies DS', 'Reply-To': config('EMAIL_HOST_USER'), 'format': 'flowed'}
        )
        message.attach_alternative(html_body, "text/html")
        message.send(fail_silently=False)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_member', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
