
from decimal import Decimal
import random
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
from collections import defaultdict
from decimal import Decimal



BASE_PRICE_PER_KG = 47.00  # fixed base price

def generate_otp():
    return str(random.randint(100000, 999999))

def product_qr_upload_path(instance, filename):
    # Folder: qr/products/<SKU>/<filename>
    return f'qr/products/{instance.sku}/{filename}'

# class CloseOfDay(models.Model):
#     otp = models.CharField(max_length=6, null=True, blank=True)
#     requested_by = models.CharField(max_length=90, null=True)
#     approved_by = models.CharField(max_length=90, null=True)
#     date_closed = models.DateTimeField(auto_now_add=True)
#     start_date = models.DateTimeField(null=True)
#     end_date = models.DateTimeField(null=True)
#     total_refills = models.IntegerField(default=0)
#     total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     otp_verified = models.BooleanField(default=False)
#     site_id = models.CharField(max_length=90, null=True)

#     def __str__(self):
#         return f"CloseOfDay {self.id} ({self.date_closed.date()})"

#     def calculate_totals(self):
#         """Calculate totals based on base price from last close to now."""
#         from core.models import Refill  # avoid circular import

#         # Get last close record
#         last_close = CloseOfDay.objects.exclude(id=self.id).order_by('-date_closed').first()
#         start_date = last_close.end_date if last_close else timezone.make_aware(timezone.datetime(2000, 1, 1))
#         end_date = timezone.now()

#         # Filter refills since last closure
#         refills = Refill.objects.filter(created_at__gte=start_date, created_at__lte=end_date)

#         # Compute totals manually using base price
#         total_refills = refills.count()
#         total_kg = sum([float(r.quantity_kg) for r in refills])
#         total_amount = total_kg * BASE_PRICE_PER_KG

#         # Update fields
#         self.start_date = start_date
#         self.end_date = end_date
#         self.total_refills = total_refills
#         self.total_amount = total_amount
#         self.save()

#         return refills

    

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
        elif _vr >= 1.50:
            return ("badge-light-danger", "Out of Stock")
        else:
            return ("badge-light-danger", "Out of Stock")
    
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
    item_id = models.CharField(max_length=90, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=120, unique=False)
    sku = models.TextField(max_length=90, null=True)
    more_info = models.TextField(null=True)
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    item_pic = models.ImageField(upload_to='items/', blank=True)
    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='item_added')
    status = models.CharField(default=0, null=False, max_length=3)
    qr_code = models.ImageField(upload_to=product_qr_upload_path, blank=True)
    active = models.BooleanField(default=True)
    
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def stock_status(self):
        from core.models import GRNItems  # avoid circular import

        # Sum of all quantities of this product in GRNItems
        total_grn_quantity = (
            GRNItems.objects.filter(item_id=self.id)  # assuming ForeignKey to Product
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
            return ("badge-light-danger", "Out of Stock")

    
    def remaining_stock(self):
        from core.models import GRNItems  # avoid circular import

        # Sum of all quantities of this product in GRNItems
        total_grn_quantity = (
            GRNItems.objects.filter(item_id=self.id)  # assuming ForeignKey to Product
            .aggregate(total=Sum('quantity'))
            .get('total') or 0
        )

        remaining = (self.stock or 0) - total_grn_quantity
        return remaining

class ProductQR(TimeStamped):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='products')
    qr_code = models.ImageField(upload_to=product_qr_upload_path, blank=True)
    location = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Product {self.id} ({self.product})" 


class Measurables(TimeStamped):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ImageField(upload_to=product_qr_upload_path, blank=True)
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
    quantity_mtrs = models.FloatField(null=True)  # capacity
    assigned_state = models.CharField(max_length=3, default=0)
    sku = models.CharField(max_length=30, default=generate_cylinder_sku, null=False)
    location = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Consumable {self.id} ({self.quantity_mtrs})"

    def get_absolute_url(self):
        return reverse('core:cylinder-detail', args=[str(self.id)])

    def lpg_level_status(self):
        from core.models import ConsumerSales  # avoid circular import

        # Sum of all quantities of this product in GRNItems
        total_sold = (
            ConsumerSales.objects.filter(qrcode=self.id)
            .aggregate(total=Sum('quantity_mtrs'))
            .get('total') or Decimal("0.00")
        )

        remaining = Decimal(str(self.quantity_mtrs or 0)) - (total_sold or Decimal("0"))
        _vr = remaining.quantize(Decimal("0.01"))
        
        if _vr >= 5.00:
            return ("badge-light-success", "Stocked")
        elif _vr >= 3.00:
            return ("badge-light-warning", "Low Stock")
        elif _vr >= 0.30:
            return ("badge-light-danger", "Out of Stock")
        else:
            return ("badge-light-danger", "Out of Stock")
    
    def remaining_quantity(self):
        from core.models import ConsumerSales  # avoid circular import

        total_sold = (
            ConsumerSales.objects.filter(qrcode=self.id)
            .aggregate(total=Sum('quantity_kg'))
            .get('total') or Decimal("0.00")
        )
        remaining = Decimal(str(self.quantity_mtrs or 0)) - (total_sold or Decimal("0.00"))
        # return (self.quantity_kg or Decimal("0.00")) - total_refilled
        return remaining.quantize(Decimal("0.01"))

class ConsumerSales(TimeStamped):
    measurable = models.ForeignKey(Measurables, on_delete=models.CASCADE, related_name='measurables', null=True)
    quantity_mtrs =  models.DecimalField(max_digits=10, decimal_places=2, default=0, null=False)
    unit_price_per_mtr = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    handled_by = models.CharField(max_length=90, null=True)
    sale_id = models.CharField(max_length=90, default=gen64Id, null=False)
    qrcode = models.TextField(null=True)
    site_id = models.CharField(max_length=90, null=True)

    
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

class ContainerStock(TimeStamped):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='containerstock')
    container = models.ForeignKey(Container, on_delete=models.PROTECT, related_name='containerstock')
    stock_id = models.CharField(max_length=90, default=gen64Id, null=False)
    stock = models.PositiveIntegerField(default=0)
    sold_by = models.CharField(max_length=90, null=False)
    status = models.CharField(default=0, null=False, max_length=3)
    qrcode_txt = models.TextField(null=True)
    active = models.BooleanField(default=True)
    site_id = models.CharField(max_length=120, blank=True)
    sell_type = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.product.name} ({self.product.sku})"  
    
    def stock_status(self):
        from core.models import ContainerStock  # avoid circular import

        # Sum of all quantities of this product in GRNItems
        total_grn_quantity = (
            ContainerStock.objects.filter(product__item_id=self.id)  # assuming ForeignKey to Product
            .aggregate(total=Sum('stock'))
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
            return ("badge-light-danger", "Out of Stock")

    
class ContainerSales(TimeStamped):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='containersale')
    container = models.ForeignKey(Container, on_delete=models.PROTECT, related_name='containersale')
    stock_id = models.CharField(max_length=90, default=gen64Id, null=False)
    stock = models.PositiveIntegerField(default=0)
    sold_by = models.CharField(max_length=90, null=False)
    status = models.CharField(default=0, null=False, max_length=3)
    sell_type = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.product.name})"    
    
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
    isPaid = models.CharField(max_length=20, blank=True)
    

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
    # assigned_site = models.CharField(max_length=90, null=True)
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
        return f"{self.product or self.item}"



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
    
    
from django.db import models
from django.utils import timezone
from decimal import Decimal
from collections import defaultdict

BASE_PRICE_PER_KG = Decimal("47.00")  # base price for refills

class CloseOfDay(models.Model):
    otp = models.CharField(max_length=6, null=True, blank=True)
    requested_by = models.CharField(max_length=90, null=True)
    approved_by = models.CharField(max_length=90, null=True)
    date_closed = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    total_refills = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    otp_verified = models.BooleanField(default=False)
    site_id = models.CharField(max_length=90, null=True)

    def __str__(self):
        return f"CloseOfDay {self.id} ({self.date_closed.date()})"

    def calculate_totals(self):
        """
        Calculate totals from Refill and ContainerSales since last closure.
        Includes merged per-site totals and safe Decimal operations.
        """
        from core.models import Refill, ContainerSales

        # --- Determine date range ---
        last_close = CloseOfDay.objects.exclude(id=self.id).order_by('-date_closed').first()
        start_date = last_close.end_date if last_close else timezone.make_aware(timezone.datetime(2000, 1, 1))
        end_date = timezone.now()

        # --- REFILL TOTALS ---
        # refill_qs = Refill.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        refill_qs = Refill.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        if self.site_id:
            sitr = Container.objects.get(site_id=self.site_id)
            refill_qs = refill_qs.filter(site_id=sitr.id)

        total_refills = refill_qs.count()
        total_refill_amount = sum(Decimal(str(r.quantity_kg)) * BASE_PRICE_PER_KG for r in refill_qs)

        # --- CONTAINER SALES TOTALS ---
        sales_qs = ContainerSales.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        if self.site_id:
            sales_qs = sales_qs.filter(container__site_id=self.site_id)  # adjust if needed

        total_sales = sales_qs.count()
        total_sales_amount = sum(
            Decimal(s.stock) * Decimal(str(s.product.unit_price)) if hasattr(s.product, "unit_price") else Decimal("0")
            for s in sales_qs
        )

        # --- MERGE PER-SITE TOTALS ---
        site_totals = defaultdict(lambda: {"refills": 0, "refill_amount": Decimal("0"),
                                           "sales": 0, "sales_amount": Decimal("0")})

        for r in refill_qs:
            site = r.site_id or "Unknown"
            site_totals[site]["refills"] += 1
            site_totals[site]["refill_amount"] += Decimal(str(r.quantity_kg)) * BASE_PRICE_PER_KG

        for s in sales_qs:
            site = getattr(s.container, "site_id", "Unknown")
            unit_price = Decimal(str(s.product.unit_price)) if hasattr(s.product, "unit_price") else Decimal("0")
            site_totals[site]["sales"] += 1
            site_totals[site]["sales_amount"] += Decimal(s.stock) * unit_price

        # --- GRAND TOTAL ---
        grand_total_amount = total_refill_amount + total_sales_amount

        # --- Update model ---
        self.start_date = start_date
        self.end_date = end_date
        self.total_refills = total_refills
        self.total_sales = total_sales
        self.total_amount = grand_total_amount
        self.save()

        # --- JSON-like response ---
        return {
            "total_refills": total_refills,
            "total_sales": total_sales,
            "total_refill_amount": total_refill_amount,
            "total_sales_amount": total_sales_amount,
            "grand_total_amount": grand_total_amount,
            "refills": list(refill_qs.values()),  # optional serialized queryset
            "sales": list(sales_qs.values()),     # optional serialized queryset
            "site_totals": {k: {
                "refills": v["refills"],
                "refill_amount": v["refill_amount"],
                "sales": v["sales"],
                "sales_amount": v["sales_amount"]
            } for k, v in site_totals.items()},
        }
