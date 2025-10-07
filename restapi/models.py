from ipaddress import ip_address
from django.db import models
from datetime import datetime
import random
import string
import re
from random import *

from login.models import CustomUser, gen16


def keygen():
    min_char = 12
    max_char = 19
    allchar = string.ascii_letters + string.digits
    uid = ''.join(choice(allchar) for x in range(randint(min_char, max_char)))
    return uid


def upload_image(self, filename):
    # filename = keygen();
    return 'userfiles/{}/{}'.format(self.uid, filename)


class ChatList(models.Model):
    id = models.BigAutoField(primary_key=True)
    mid = models.CharField(max_length=60, null=False)
    isTyping = models.CharField(default=0, max_length=3)
    messType = models.CharField(default=0, max_length=3)
    rec_status = models.CharField(default=0, max_length=3)
    snd_status = models.CharField(default=0, max_length=3)
    rec_usr =  models.CharField(max_length=60, null=True)
    snd_usr =  models.CharField(max_length=60, null=True)
    conv_id =  models.CharField(max_length=60, null=True)
    message = models.TextField(null=True)
    messStat = models.CharField(default=0, max_length=3)
    lastOnline = models.CharField(max_length=60, null=True)
    sent_date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.mid


class Infor(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=60, null=True)
    desc = models.CharField(max_length=60, null=True)
    def __str__(self):
        return self.title


class AssignedLessons(models.Model):
    id = models.BigAutoField(primary_key=True)
    instructor = models.CharField(max_length=60, null=False)
    student = models.CharField(max_length=60, null=False)
    lesson = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assign_id = models.CharField(max_length=60, null=False, default=gen16)
    descript = models.TextField(null=True)
    lesson_date = models.CharField(max_length=20, null=True)
    lesson_time = models.CharField(max_length=20, null=True)
    status = models.CharField(max_length=3, default=0, null=True)
    added_date = models.DateTimeField(default=datetime.now, blank=True)
    
    def __str__(self):
        return self.assign_id