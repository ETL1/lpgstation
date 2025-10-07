
from decimal import Decimal
from django.db import models
from django.conf import settings

from .utils import make_qr_png
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse
from datetime import datetime
from lpg_station.functions import gen32Id, gen64Id, generate_cylinder_sku, generate_sku
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta


class CloseOfDayOTP(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    is_used = models.BooleanField(default=False)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    start_date = models.DateTimeField()  # last closure + 1
    end_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_transactions = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"COD from {self.start_date.date()} to {self.end_date.date()}"

    def is_valid(self):
        return (
            not self.is_used
            and timezone.now() <= self.created_at + timedelta(minutes=5)
        )


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Item(TimeStamped):
    name = models.CharField(max_length=120)
    item_type = models.CharField(max_length=120, default=0)
    size_kg = models.PositiveIntegerField(choices=[(3,'3kg'),(5,'5kg'),(10,'10kg'),(14,'14kg'),(20,'20kg'),(25,'25kg'),(30,'30kg'),(40,'40kg'),(45,'45kg'),(48,'48kg'),(50,'50kg'),(60,'60kg')])
    base_price = models.DecimalField(max_digits=9, decimal_places=2)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} {self.size_kg}kg"

class Customer(TimeStamped):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=32)
    address = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return f"{self.name} ({self.phone})"


class Cylinder(TimeStamped):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='cylinders')
    qr_code = models.ImageField(upload_to='qr/', blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('full','Full'),
            ('empty','Empty'),
            ('in_use','In-Use'),
            ('with_customer','With Customer'),
            ('maintenance','Maintenance'),
            ('retired','Retired')
        ],
        default='full'
    )
    quantity_kg = models.FloatField(null=True)  # capacity
    assigned_state = models.CharField(max_length=3, default=0)
    sku = models.CharField(max_length=30, default=generate_cylinder_sku, null=False)
    location = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Cylinder {self.id} ({self.item})"

    def get_absolute_url(self):
        return reverse('core:cylinder-detail', args=[str(self.id)])

    def lpg_level_status(self):
        from core.models import Refill  # avoid circular import

        # Sum of all quantities of this product in GRNItems
        total_refilled = (
            Refill.objects.filter(qrcode=self.id)
            .aggregate(total=Sum('quantity_kg'))
            .get('total') or Decimal("0.00")
        )

        remaining = Decimal(str(self.quantity_kg or 0)) - (total_refilled or Decimal("0"))
        _vr = remaining.quantize(Decimal("0.01"))
        
        if _vr >= 5.00:
            return ("badge-light-success", "Stocked")
        elif _vr >= 3.00:
            return ("badge-light-warning", "Low Stock")
        elif _vr >= 1.00:
            return ("badge-light-danger", "Out of Stock")
        else:
            return ("badge-light-dark", "---")
    
    def remaining_quantity(self):
        from core.models import Refill  # avoid circular import

        total_refilled = (
            Refill.objects.filter(qrcode=self.id)
            .aggregate(total=Sum('quantity_kg'))
            .get('total') or Decimal("0.00")
        )
        remaining = Decimal(str(self.quantity_kg or 0)) - (total_refilled or Decimal("0.00"))
        # return (self.quantity_kg or Decimal("0.00")) - total_refilled
        return remaining.quantize(Decimal("0.01"))



class CylinderEvent(TimeStamped):
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE, related_name='events')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    event_type = models.CharField(max_length=12, choices=[
        ('create','Created'),('refill','Refill'),('sale','Sold'),('deliver','Delivered'),
        ('return','Returned'),('maint','Maintenance'),('status','Status')
    ])
    note = models.CharField(max_length=255, blank=True)

class Order(TimeStamped):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=[
        ('pending','Pending'),('approved','Approved'),('assigned','Assigned'),
        ('delivered','Delivered'),('cancelled','Cancelled')
    ], default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class OrderItem(TimeStamped):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)

class Product(TimeStamped):
    item_id = models.CharField(max_length=90, default=gen64Id, null=False)
    name = models.CharField(max_length=120, unique=True)
    sku = models.TextField(max_length=90, null=True)
    more_info = models.TextField(null=True)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    item_pic = models.ImageField(upload_to='items/', blank=True)
    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='item_added')
    status = models.CharField(default=0, null=False, max_length=3)
    qr_code = models.ImageField(upload_to='qr/products/', blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def stock_status(self):
        from core.models import GRNItems  # avoid circular import

        # Sum of all quantities of this product in GRNItems
        total_grn_quantity = (
            GRNItems.objects.filter(item_id=self)  # assuming ForeignKey to Product
            .aggregate(total=Sum('quantity'))
            .get('total') or 0
        )

        remaining = (self.stock or 0) - total_grn_quantity
        
        if remaining >= 5:
            return ("badge-light-success", "Stocked")
        elif remaining >= 3:
            return ("badge-light-warning", "Low Stock")
        elif remaining >= 1:
            return ("badge-light-danger", "Out of Stock")
        else:
            return ("badge-light-dark", "---")

    
    def remaining_stock(self):
        from core.models import GRNItems  # avoid circular import

        # Sum of all quantities of this product in GRNItems
        total_grn_quantity = (
            GRNItems.objects.filter(item_id=self)  # assuming ForeignKey to Product
            .aggregate(total=Sum('quantity'))
            .get('total') or 0
        )

        remaining = (self.stock or 0) - total_grn_quantity
        return remaining
    
    
class Container(TimeStamped):
    name = models.CharField(max_length=120, unique=False)
    site_id = models.CharField(
        max_length=90,
        default=gen64Id,             # generate automatically
    )
    location = models.CharField(max_length=100, unique=False)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='site_made')
    added_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.location})"

class Refill(TimeStamped):
    cylinder = models.ForeignKey(Cylinder, on_delete=models.CASCADE, related_name='refills', null=True)
    # customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='refills')
    customer = models.TextField(null=True)
    quantity_kg =  models.DecimalField(max_digits=10, decimal_places=2, default=0, null=False)
    unit_price_per_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    handled_by = models.CharField(max_length=90, null=True)
    refill_id = models.CharField(max_length=90, default=gen64Id, null=False)
    address = models.TextField(null=True)
    qrcode = models.TextField(null=True)
    site_id = models.CharField(max_length=90, null=True)
    phone = models.CharField(max_length=90, null=True)

class Sale(TimeStamped):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sales')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='sales_made')

class BasePricing(TimeStamped):
    name = models.CharField(max_length=120, unique=True)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.unit_price})"
    
class ItemTypes(TimeStamped):
    name = models.CharField(max_length=120, unique=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name}"
    
class Configurations(models.Model):
    name = models.CharField(max_length=120, unique=True)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.unit_price})"
    

class GRN(models.Model):
    grn_Id = models.CharField(max_length=80, default=uuid.uuid4, null=True)
    initia = models.CharField(max_length=70, null=True)
    grn_number = models.CharField(max_length=90, unique=True)
    made_date = models.DateTimeField(default=datetime.now, blank=True)
    status = models.CharField(default=0, null=False, max_length=3)
    qr_code = models.ImageField(upload_to='qr/grn/', blank=True)
    rec_by = models.CharField(max_length=90, null=True)
    assigned_site = models.ForeignKey(
        'Container', on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.grn_Id

    
class GRNItems(models.Model):
    grn = models.ForeignKey(GRN, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name="grn_products")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True, related_name="grn_items")

    quantity = models.CharField(max_length=70, null=True)
    added_date = models.DateTimeField(default=datetime.now, blank=True)
    status = models.BooleanField(default=False)
    admin_comment = models.TextField(null=True)
    site_comment = models.TextField(null=True)

    def __str__(self):
        return f"{self.product or self.item} - ({self.grn})"



@receiver(pre_save, sender=GRN)
def generate_grn_number(sender, instance, **kwargs):
    if not instance.grn_number:
        instance.grn_number = generate_unique_grn_number()

def generate_unique_grn_number():
    prefix = "DN"
    unique_id = f"{prefix}-{str(uuid.uuid4())[:11].upper()}"
    while GRN.objects.filter(grn_number=unique_id).exists():
        unique_id = f"{prefix}-{str(uuid.uuid4())[:11].upper()}"
    return unique_id


class Stations(models.Model):
    site_id = models.CharField(max_length=80, default=gen32Id, null=False)
    initia = models.CharField(max_length=70, null=True)
    station_name = models.CharField(max_length=120, null=True)
    location = models.CharField(max_length=120, null=True)
    made_date = models.DateTimeField(default=datetime.now, blank=True)
    status = models.CharField(default=0, null=False, max_length=3)

    def __str__(self):
        return self.site_id