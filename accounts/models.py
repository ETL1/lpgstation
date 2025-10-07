
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUserz(AbstractUser):
    ROLE_CHOICES = [
        ('admin','Admin'),
        ('manager','Manager'),
        ('stock','Stock'),
        ('delivery','Delivery'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='manager')
    phone = models.CharField(max_length=32, blank=True)
