import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django import forms
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from core.models import Container
from rest_framework.authtoken.models import Token

from .managers import CustomUserManager

import random
import string
import re
from random import *

def genUid(): 
    _keys = uuid.uuid4().hex[:32]
    return _keys
    
def gen16(): 
    _keys = uuid.uuid4().hex[:16]
    return _keys

def gen8(): 
    _keys = uuid.uuid4().hex[:8]
    return _keys

def gen64(): 
    _keys = uuid.uuid4().hex[:64]
    return _keys

def gen128(): 
    _keys = uuid.uuid4().hex[:128]
    return _keys

def generateId():
    min_char = 10
    max_char = 16
    allchar = string.ascii_letters + string.digits
    x = ''.join(choice(allchar) for x in range(randint(min_char, max_char)))
    return x

def upload_image(self, filename):
    return 'userfiles/{}/{}'.format(self.uid, filename)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(_('email address '), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    is_member = models.BooleanField(default=False)
    uid = models.CharField(max_length=100, default=genUid)
    password = models.CharField(max_length=128, null=True)
    access_level = models.CharField(default=0, max_length=6)
    is_verified = models.BooleanField(default=True)
    username = models.CharField(max_length=60, null=True)
    title = models.CharField(max_length=60, null=True)
    fname = models.CharField(max_length=60, null=True)
    sname = models.CharField(max_length=60, null=True)
    availability = models.TextField(null=True)
    site_id = models.ForeignKey(Container, on_delete=models.CASCADE, related_name='containers', null=True)
    onlineStat = models.CharField(default=0, max_length=3)
    lastOnline = models.CharField(max_length=60, null=True)
    phone_num = models.CharField(max_length=60, null=True)
    acc_token = models.CharField(max_length=60, null=True)
    logi = models.CharField(max_length=60, null=True)
    lati = models.CharField(max_length=60, null=True)
    token = models.CharField(max_length=60, null=True)
    u_pic = models.ImageField(_('profile '), upload_to=upload_image, default='userfiles/avatar.jpg')
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def get_euser(self):
         return self.email

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)


def default_schedule():
    return {
    "monday": [
        {"start_time": "08:00", "end_time": "10:00", "status": "available"},
        {"start_time": "14:00", "end_time": "16:00", "status": "available"}
    ],
    "tuesday": [
        {"start_time": "09:00", "end_time": "11:00", "status": "booked",},
        {"start_time": "13:00", "end_time": "15:00", "status": "available"}
    ],
    "wednesday": [],
    "thursday": [
        {"start_time": "10:00", "end_time": "12:00", "status": "booked",},
        {"start_time": "15:00", "end_time": "17:00", "status": "available"}
    ],
    "friday": [
        {"start_time": "08:00", "end_time": "10:00", "status": "available"}
    ],
    "saturday": [
        {"start_time": "09:00", "end_time": "11:00", "status": "booked",}
    ],
    "sunday": []
}


class Instructor(models.Model):
    instructor_id = models.CharField(max_length=100, default=genUid)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='instructor_profile')
    expertise = models.TextField(help_text="Describe areas of expertise (e.g., Defensive Driving, Highway Driving).")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, help_text="Average instructor rating.")
    schedule = models.JSONField(default=default_schedule, help_text="Instructor's schedule in JSON format (e.g., available slots).")
    bio = models.TextField(blank=True, null=True, help_text="A brief biography of the instructor.")
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.fname} {self.user.sname} - {self.expertise[:20]}"

    def calculate_rating(self):
        # Example function to calculate the rating based on feedback.
        pass
    
    def calculate_average_rating(self):
        ratings = self.ratings.all()
        if not ratings.exists():
            return 0
        return sum(rating.rating_value for rating in ratings) / ratings.count()

    @property
    def average_rating(self):
        return self.calculate_average_rating()


class Student(models.Model):
    student_id = models.CharField(max_length=100, default=genUid)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    goals = models.TextField(blank=True, null=True, help_text="Driving goals (e.g., getting a license).")
    progress = models.JSONField(default=dict, help_text="Progress tracker (e.g., milestones completed).")
    lessons_taken = models.PositiveIntegerField(default=0, help_text="Number of lessons attended.")
    assigned_instructor = models.ForeignKey(
        Instructor, on_delete=models.SET_NULL, blank=True, null=True, related_name='students'
    )
    registration_date = models.DateField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True, help_text="Feedback from instructors.")
    # package_chosen = models.ForeignKey(Packages, blank=True, null=True, help_text="Package booked for.")

    def __str__(self):
        return f"{self.user.fname} {self.user.sname} - Lessons Taken: {self.lessons_taken}"

    def update_progress(self, milestone, status):
        """Update progress tracker."""
        self.progress[milestone] = status
        self.save()



from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.timezone import now

class Rating(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ratings')
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='ratings')
    rating_value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating value between 1 and 5."
    )
    review = models.TextField(blank=True, null=True, help_text="Optional written review.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating_value} by {self.student.user.username} for {self.instructor.user.username}"
