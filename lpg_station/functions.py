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

def generate_otp(user):
    code = str(random.randint(100000, 999999))  # 6-digit OTP
    otp = models.CloseOfDayOTP.objects.create(user=user, code=code)
    # TODO: send via email/SMS — for now, print or return
    print(f"Generated OTP for {user.username}: {code}")
    return otp


def calculate_totals(user):
    last_closure = models.CloseOfDayOTP.objects.order_by("-end_date").first()
    start_date = last_closure.end_date if last_closure else timezone.make_aware(timezone.datetime.min)
    end_date = timezone.now()

    qs = models.Refill.objects.filter(created_at__gte=start_date, created_at__lt=end_date)
    total_amount = qs.aggregate(total=models.Sum("amount"))["total"] or 0
    total_transactions = qs.count()

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_amount": total_amount,
        "total_transactions": total_transactions,
    }


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

