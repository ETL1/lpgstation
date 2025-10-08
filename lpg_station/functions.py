from datetime import datetime
import time
from uuid import uuid4
import string
import re
from random import *
import random
from django.utils import timezone

from core import models

def generate_transaction_id():
    """
    Generate a unique transaction ID.
    Combines the current timestamp with a UUID to ensure uniqueness.
    """
    timestamp = int(time.time() * 1000)  # Current time in milliseconds
    unique_id = uuid4()  # Generate a random UUID
    transaction_id = f"Txn-{timestamp}-{unique_id}"
    return transaction_id

def gen32Id(): 
    _keys = uuid4().hex[:32]
    return _keys

def gen64Id(): 
    _keys = uuid4().hex[:64]
    return _keys

def gen16Id():
    _keys = uuid4().hex[:16]
    return _keys

def gen16Id():
    _keys = uuid4().hex[:16]
    return _keys

import random, string

def generate_sku(product_name):
    initials = ''.join(word[0] for word in product_name.split()[:2]).upper()
    rand_part = ''.join(random.choices(string.digits, k=4))
    return f"{initials}-{rand_part}"

def generate_cylinder_sku():
    rand_part = ''.join(random.choices(string.digits, k=6))
    return f"{rand_part}"




# def generate_otp(user):
#     """Generate and log a 6-digit OTP"""
#     code = str(random.randint(100000, 999999))
#     otp = models.CloseOfDayOTP.objects.create(user=user, code=code)
#     print(f"Generated OTP for {user.username}: {code}")  # simulate SMS/email
#     return otp


# def calculate_refill_totals():
#     """Calculate totals from last closure to now."""
#     last_closure = models.CloseOfDay.objects.order_by("-end_date").first()

#     if last_closure:
#         start_date = last_closure.end_date
#     else:
#         # Use earliest refill date or safe default
#         first_refill = models.Refill.objects.order_by("created_at").first()
#         if first_refill:
#             start_date = first_refill.created_at
#         else:
#             # fallback: 1 Jan 2000 (safe for all databases)
#             start_date = timezone.make_aware(datetime(2000, 1, 1))

#     end_date = timezone.now()

#     qs = models.Refill.objects.filter(created_at__gte=start_date, created_at__lt=end_date)

#     total_amount = qs.aggregate(total=models.Sum("total_price"))["total"] or 0
#     total_quantity = qs.aggregate(total=models.Sum("quantity_kg"))["total"] or 0
#     total_refills = qs.count()

#     return {
#         "start_date": start_date,
#         "end_date": end_date,
#         "total_amount": total_amount,
#         "total_quantity": total_quantity,
#         "total_refills": total_refills,
#     }


# def get_company_status(access, owner):
#     node = NodeAccounts.objects.get(node_Id=owner)
#     __ca = 0
#     if node.status == 0:
#         __ca = 0
#     elif node.status == 1:
#         __ca = 1
#     elif node.status == 2:
#         __ca = 2
    
#     __url = ""
#     if access == '0':
#         __url = "pages/home-dash.html"
#     elif access == '1':
#         if __ca == 0:
#             __url = "/activation"
#         elif __ca == 2:
#             __url = "/suspended"
#         else:
#             __url = "/companies/profile/"+node
#     elif access == '2':
#         __url = "/companies/profile/"+node
#     elif access == '3':
#         if __ca == 0:
#             __url = "/activation"
#         elif __ca == 2:
#             __url = "/suspended"
#         else:
#             __url = "/companies/profile/"+node
#     elif access == '4':
#         if __ca == 0:
#             __url = "/activation"
#         elif __ca == 2:
#             __url = "/suspended"
#         else:
#             __url = "/companies/profile/"+node
#     elif access == '5':
#         if __ca == 0:
#             __url = "/activation"
#         elif __ca == 2:
#             __url = "/suspended"
#         else:
#             __url = "/companies/profile/"+node
#     return __url

