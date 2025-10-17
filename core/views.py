
from datetime import datetime, timezone
import json
import os
import uuid
from django.utils import timezone

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from core import serializers
from .models import CloseOfDay, ContainerSales, ContainerStock, ProductQR, generate_otp
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Sum
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.serializers import GRNItemSerializer, GRNSerializer, ProductsSerializer, RefillSerializer, SalesSerializer
from login.models import CustomUser
from login.serializers import ActivaSerializer
from lpg_station.functions import generate_sku
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from django.db.models import Q
import io
import qrcode
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.core.files.base import ContentFile
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import ImageDraw, ImageFont
from django.db import transaction
from itertools import zip_longest

from templatetags.custom_tags import generate_unique_sku

from .models import GRN, Cylinder, CylinderEvent, GRNItems, Order, Refill, Sale, Customer, Container, Product, Item
from .forms import CylinderForm, DistributionForm, OrderForm, RefillForm, SaleForm, CustomerForm, ContainerForm, ProductForm

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'index-2.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cyl_total'] = Cylinder.objects.count()
        ctx['orders_pending'] = Order.objects.filter(status='pending').count()
        ctx['refill_count'] = Refill.objects.count()
        ctx['sales_amount'] = (Sale.objects.aggregate(s=Sum('total_price'))['s'] or 0)
        return ctx 

class CylinderList(LoginRequiredMixin, TemplateView):
    template_name = 'pages/apps/cylinder-list.html'
    paginate_by = 25
    ordering = ['-created_at']
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cylinders'] = Cylinder.objects.all()
        ctx['cylinder_type'] = Item.objects.filter(item_type='1')
        ctx['refill_count'] = Refill.objects.count()
        ctx['sales_amount'] = (Sale.objects.aggregate(s=Sum('total_price'))['s'] or 0)
        return ctx 

@login_required
def cylinder_list(request):
    from django.db.models import F, Sum, DecimalField, ExpressionWrapper
    refills = Refill.objects.all().order_by('-created_at')
    cylinders = Cylinder.objects.all()
    cylinder_type = Item.objects.filter(item_type='1')
    refill_count = Refill.objects.count()
    sales_amount = (Sale.objects.aggregate(s=Sum('total_price'))['s'] or 0)
    
    
    # compute (quantity_kg * 45) per row
    total_price = (
        refills.annotate(
            line_total=ExpressionWrapper(
                F("quantity_kg") * 45,   # or F("item__base_price")
                output_field=DecimalField()
            )
        ).aggregate(total=Sum("line_total"))["total"] or 0
    )
    
    context = {
        'cylinders' : cylinders,
        "refills": refills,
        "total_price": total_price,
        'cylinder_type': cylinder_type,
        'refill_count': refill_count,
        'sales_amount': sales_amount,
    }
    return render(request, 'pages/apps/cylinder-list.html', context) 
    
class CylinderDetail(LoginRequiredMixin, DetailView):
    model = Cylinder
    template_name = 'core/cylinder_detail.html'

class CylinderCreate(LoginRequiredMixin, CreateView):
    model = Cylinder
    form_class = CylinderForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:cylinder-list')
    def form_valid(self, form):
        resp = super().form_valid(form)
        CylinderEvent.objects.create(cylinder=self.object, user=self.request.user, event_type='create')
        return resp
    




@login_required
@csrf_exempt
def add_bulk_cylinder(request):
    if request.method == 'POST':
        item_id = request.POST.get('cylinder_size')
        qty = int(request.POST.get('qty', 0))
        item = get_object_or_404(Item, id=item_id)

        qr_data_list = []

        for i in range(qty):
            cyl = Cylinder.objects.create(
                item=item,
                status='full',
                location='',
                quantity_kg=item.size_kg
            )

            unique_code = f"{cyl.id}"
            

            # === QR code with Pillow for text ===
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4
            )
            qr.add_data(unique_code)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            # # Add text to QR image
            # draw = ImageDraw.Draw(img)
            # font = ImageFont.load_default()
            # draw.text((120, img.size[1] - 30), f"SIZE: {item.size_kg}", font=font, fill=(0,0,0))
            
            # draw = ImageDraw.Draw(img)
            # font = ImageFont.load_default()
            # draw.text((220, img.size[1] - 30), f"ID: {unique_num}", font=font, fill=(0,0,0))

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            cyl.qr_code.save(f'{unique_code}.png', ContentFile(buffer.getvalue()), save=False)

            # Keep for PDF
            qr_data_list.append((buffer.getvalue(), unique_code, item.size_kg))

        # === Generate PDF ===
        page_w, page_h = 75 * mm, 65 * mm
        qr_size = 50 * mm
        margin_top = 5 * mm

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=(page_w, page_h))
        for img_bytes, unique_code, cyl_size in qr_data_list:
            img_buffer = io.BytesIO(img_bytes)
            img_reader = ImageReader(img_buffer)

            x = (page_w - qr_size) / 2
            y = (page_h - qr_size) / 2
            
            px = (page_w - qr_size) / 1.4
            py = page_h - qr_size - margin_top

            c.drawImage(img_reader, px, py, width=qr_size, height=qr_size)
            c.saveState()
            # Move origin to center of page
            c.translate(x, y)
            # Rotate 90 degrees clockwise
            c.rotate(90)
            # After rotation, (0,0) is now the center
            
            # Generate unique 8-digit code
            unique_num = str(uuid.uuid4().hex[:8].upper())

            # Text in PDF below QR
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(page_w / 2.8, -15, f"ID: {cyl.sku}")
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(page_w / 2.8, 1, f"SIZE: {cyl_size} KG")

            c.showPage()

        c.save()
        pdf_buffer.seek(0)

        filename = f"cylinders_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

    return redirect('/cylinders')

    

class CylinderEdit(LoginRequiredMixin, UpdateView):
    model = Cylinder
    fields = ['status','location']
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:cylinder-list')
    def form_valid(self, form):
        resp = super().form_valid(form)
        CylinderEvent.objects.create(cylinder=self.object, user=self.request.user, event_type='status', note=self.object.status)
        return resp

class OrderList(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/order_list.html'
    ordering = ['-created_at']

class OrderCreate(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:order-list')
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    
@login_required
def refill_list(request):
    refills = Refill.objects.all().order_by('-created_at')
    cylinders = Cylinder.objects.all()
    
    from django.db.models import F, Sum, DecimalField, ExpressionWrapper
    # compute (quantity_kg * 45) per row
    total_price = (
        refills.annotate(
            line_total=ExpressionWrapper(
                F("quantity_kg") * 47,   # or F("item__base_price")
                output_field=DecimalField()
            )
        ).aggregate(total=Sum("line_total"))["total"] or 0
    )
    
    context = {
        'cylinders' : cylinders,
        "refills": refills,
        "total_price": total_price,
    }
    return render(request, 'pages/apps/refill-list.html', context) 

class RefillCreate(LoginRequiredMixin, CreateView):
    model = Refill
    form_class = RefillForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:refill-list')
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.handled_by = self.request.user
        obj.total_price = (obj.quantity_kg or 0) * (obj.unit_price_per_kg or 0)
        obj.save()
        obj.cylinder.status = 'full'
        obj.cylinder.save(update_fields=['status'])
        CylinderEvent.objects.create(cylinder=obj.cylinder, user=self.request.user, event_type='refill')
        messages.success(self.request, f'Refill saved: {obj.total_price}')
        return redirect(self.success_url)

class SaleList(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'core/sale_list.html'
    ordering = ['-created_at']

class SaleCreate(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:sale-list')
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.sold_by = self.request.user
        obj.total_price = (obj.quantity or 0) * (obj.unit_price or 0)
        obj.save()
        messages.success(self.request, f'Sale saved: {obj.total_price}')
        return redirect(self.success_url)


class CustomerList(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'pages/apps/customer-list.html'
    paginate_by = 25
    ordering = ['-created_at']

class CustomerDetail(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'core/customer_detail.html'

class CustomerCreate(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:customer-list')
    def form_valid(self, form):
        resp = super().form_valid(form)
        return resp

class CustomerEdit(LoginRequiredMixin, UpdateView):
    model = Customer
    fields = ['status','location']
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:customer-list')
    def form_valid(self, form):
        resp = super().form_valid(form)
        return resp
    
    
class ContainerList(LoginRequiredMixin, ListView):
    model = Container
    template_name = 'pages/apps/container-list.html'
    paginate_by = 25
    ordering = ['-created_at']

class ContainerDetail(LoginRequiredMixin, DetailView):
    model = Container
    ordering = ['-created_at']
    template_name = 'core/container_detail.html'

@login_required
def container_view(request, pk):
    conts = Container.objects.filter(site_id=pk)
    site_id = Container.objects.get(site_id=pk)
    refills = Refill.objects.filter(site_id=site_id.id).order_by('-created_at')
    refill_count = Refill.objects.filter(site_id=site_id.id).count()
    cylinders = Cylinder.objects.filter(location=site_id.id).order_by('-created_at')
    cylinder_count = Cylinder.objects.filter(location=site_id.id).count()
    
    from django.db.models import F, Sum, DecimalField, ExpressionWrapper
    # compute (quantity_kg * 45) per row
    total_price = (
        refills.annotate(
            line_total=ExpressionWrapper(
                F("quantity_kg") * 47,   # or F("item__base_price")
                output_field=DecimalField()
            )
        ).aggregate(total=Sum("line_total"))["total"] or 0
    )
    
    context = {
        'conts' : conts,
        'refills': refills,
        'cylinders': cylinders,
        'total_price': total_price,
        'refcount': refill_count,
        'cylcount': cylinder_count
    }
    return render(request, 'pages/apps/view-container.html', context)  
    
@login_required
@csrf_exempt
def add_container(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')

        if not name or not location:
            messages.error(request, 'Name and location are required.')
            return redirect('/containers')

        handler = request.user  # no need to query again

        try:
            push_container = Container.objects.create(
                added_by=handler,
                location=location,
                name=name
            )
            messages.success(request, f'Container "{push_container.name}" added successfully.')
        except Exception as e:
            messages.error(request, f'There was an error adding the container: {str(e)}')

        return redirect('/containers')

    messages.error(request, 'Invalid request method.')
    return redirect('/containers')



class ContainerEdit(LoginRequiredMixin, UpdateView):
    model = Container
    fields = ['status','location']
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:container-list')
    def form_valid(self, form):
        resp = super().form_valid(form)
        return resp
    
@login_required
def distribution_list(request):
    _grn = GRN.objects.filter(Q(status=0) | Q(status=1)).order_by('-made_date')
    _grnItems = GRNItems.objects.all()
    items = Product.objects.all()
    
    context = {
        'grn' : _grn,
        'grnitems' : _grnItems,
        'items' : items,
    }
    return render(request, 'pages/apps/grn-list.html', context) 

@login_required
def grn_detail(request, pk):
    _grn = GRN.objects.filter(grn_Id=pk)
    xgrn = GRN.objects.get(grn_Id=pk)
    _items = GRNItems.objects.filter(grn=xgrn)
    context = {
        'items' : _items,
        'grn': _grn,
    }
    return render(request, 'pages/apps/grn-view.html', context)  


class DistributionCreate(LoginRequiredMixin, CreateView):
    model = GRN
    form_class = DistributionForm
    template_name = 'pages/apps/create-grn.html'
    success_url = reverse_lazy('core:grn-list')
    def form_valid(self, form):
        resp = super().form_valid(form)
        # dbupdate = Product(sku=generate_sku(request.POST.get()))
        # dbupdate.save()
        return resp
    
@login_required
def create_grn(request):
    _grn = GRN.objects.all()
    _grnItems = GRNItems.objects.all()
    items = Product.objects.all()
    cyls = Item.objects.all()
    containers = Container.objects.all()
    
    context = {
        'grn' : _grn,
        'grnitems' : _grnItems,
        'items' : items,
        'cyls' : cyls,
        'containers' : containers,
    }
    return render(request, 'pages/apps/create-grn.html', context)

# @csrf_exempt
# @login_required
# def make_grn(request):
#     if request.method == 'POST':
#         items = request.POST.getlist('item')
#         quantities = request.POST.getlist('quantity')
#         comments = request.POST.getlist('comments')
#         site_id = request.POST.get('site_id')
#         # create GRN first
#         push_grn = GRN.objects.create(initia=request.user.uid)
        

#         from itertools import zip_longest
#         for itm, qty, comm in zip_longest(items, quantities, comments, fillvalue=None):
#             if itm and qty:
#                 try:
#                     itmx = Item.objects.get(id=itm)
#                     GRNItems.objects.create(
#                     grn=push_grn,
#                     item=itmx,
#                     quantity=qty,
#                     admin_comment=comm
#                 )
#                 except:
#                     itmx = Product.objects.get(item_id=itm)
#                     bkstock = itmx.stock
#                     cont = Container.objects.get(site_id=site_id)
#                     if int(qty) <= int(itmx.stock):
#                         GRNItems.objects.create(
#                             grn=push_grn,
#                             product=itmx,
#                             quantity=qty,
#                             admin_comment=comm
#                         )
#                         ContainerStock.objects.create(
#                             container=cont,
#                             product=itmx,
#                             stock=qty
#                         )
#                         itmx.stock = int(itmx.stock)-int(qty)
#                         itmx.save()
#                     else:
#                         itmx.stock = bkstock
#                         itmx.save()
#                         push_grn.delete()
#                         messages.error(request,'You do not have enough stock left.')
#                         pass
        
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_H,
#             box_size=10,
#             border=4
#         )
#         qr.add_data(push_grn.grn_Id)
#         qr.make(fit=True)
#         img = qr.make_image(fill_color="black", back_color="white")

#         # Save QR code image to Cylinder field
#         buffer = io.BytesIO()
#         img.save(buffer, format='PNG')
#         push_grn.qr_code.save(f'{push_grn.grn_Id}.png', ContentFile(buffer.getvalue()), save=False)
        
#         return redirect('/grn')

#     return redirect('/grn')

from django.db import transaction
from django.db.models import F
@csrf_exempt
@login_required
def make_grn(request):
    if request.method == 'POST':
        items = request.POST.getlist('item')
        quantities = request.POST.getlist('quantity')
        comments = request.POST.getlist('comments')
        site_id = request.POST.get('site_id')

        try:
            # ✅ Start a transaction block
            with transaction.atomic():
                # Step 1: Create GRN record (no QR yet)
                push_grn = GRN.objects.create(initia=request.user.uid)

                # Step 2: Track changes for rollback clarity
                stock_changes = []

                # Step 3: Process each GRN item
                for itm, qty, comm in zip_longest(items, quantities, comments, fillvalue=None):
                    if not itm or not qty:
                        continue

                    try:
                        # Handle Items table
                        itmx = Item.objects.get(id=itm)
                        GRNItems.objects.create(
                            grn=push_grn,
                            item=itmx,
                            quantity=qty,
                            admin_comment=comm
                        )

                    except:
                        # Handle Product table
                        itmx = Product.objects.get(item_id=itm)
                        cont = Container.objects.get(site_id=site_id)

                        if int(qty) > int(itmx.stock):
                            raise ValueError(f"Insufficient stock for {itmx.name} (available: {itmx.stock}, requested: {qty})")

                        # Record stock for rollback clarity
                        stock_changes.append((itmx, itmx.stock))

                        # Deduct stock and record movement
                        GRNItems.objects.create(
                            grn=push_grn,
                            product=itmx,
                            quantity=qty,
                            admin_comment=comm
                        )
                        
                        # from django.db.models import F

                        # obj, created = ContainerStock.objects.get_or_create(
                        #     container=cont,
                        #     product=itmx,
                        #     defaults={'stock': qty}
                        # )

                        # if not created:
                        #     ContainerStock.objects.filter(
                        #         container=cont,
                        #         product=itmx
                        #     ).update(stock=F('stock') + qty)
                        

                        with transaction.atomic():
                            obj, created = ContainerStock.objects.select_for_update().get_or_create(
                                container=cont,
                                product=itmx,
                                defaults={'stock': qty}
                            )

                            if not created:
                                obj.stock = F('stock') + qty
                                obj.save(update_fields=['stock'])



                        itmx.stock = int(itmx.stock) - int(qty)
                        itmx.save()

                # ✅ Step 4: Commit happens here when block exits

            # ✅ Step 5: Only generate and save QR *after* transaction success
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4
            )
            qr.add_data(push_grn.grn_Id)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')

            # ✅ Convert UUID to string for folder name
            qr_path = os.path.join(str(push_grn.grn_Id), f'{push_grn.grn_Id}.png')
            push_grn.qr_code.save(f'{push_grn.grn_Id}.png', ContentFile(buffer.getvalue()), save=True)

            messages.success(request, f'GRN #{push_grn.grn_number} was created successfully.')
            return redirect('/grn')

        except Exception as e:
            messages.error(request, f"Transaction failed and was rolled back: {e}")
            return redirect('/grn')

    messages.error(request, 'Invalid request method.')
    return redirect('/grn')

  
@csrf_exempt
@login_required
@transaction.atomic
def delete_grn(request, pk):
    try:
        # Get the GRN record
        grn = get_object_or_404(GRN, id=pk)

        # Only allow reversal if status == 0
        if grn.status == 1 or grn.status == '1':
            messages.error(request, "Cannot delete this GRN because it has already been finalized.")
            return redirect('/grn')

        with transaction.atomic():
            # Get all GRNItems linked to this GRN
            grn_items = GRNItems.objects.filter(grn=grn)

            for item in grn_items:
                if item.product:
                    product = item.product
                    # Restore stock to product model
                    product.stock = int(product.stock) + int(item.quantity)
                    product.save()

            # Delete GRNItems and GRN itself
            grn_items.delete()
            grn.delete()

        messages.success(request, f"GRN #{grn.grn_number} was deleted successfully and stock restored.")
        return redirect('/grn')

    except Exception as e:
        messages.error(request, f"Error deleting GRN: {e}")
        return redirect('/grn')


@login_required
def edit_grn(request, pk):
    _grn = GRN.objects.filter(id=pk)
    xgrn = GRN.objects.get(id=pk)
    _items = GRNItems.objects.filter(grn=xgrn)
    _prod = Product.objects.all()
    context = {
        'items' : _items,
        'grn': _grn,
        'prod': _prod,
    }
    return render(request, 'pages/apps/edit-grn.html', context)  
 
@login_required
@csrf_exempt
def submit_edit_grn(request):
    if request.method == 'POST':
        items = request.POST.getlist('item')
        quantities = request.POST.getlist('quantity')
        comments = request.POST.getlist('comments')
        grn_id = request.POST.get('grn_id')  # single value, not list

        try:
            grn = GRN.objects.get(id=grn_id)
        except GRN.DoesNotExist:
            messages.error(request, 'GRN not found.')
            return redirect('/grn')

        for itm_id, qty, comm in zip(items, quantities, comments):
            try:
                itm = Product.objects.get(item_id=itm_id)
            except Product.DoesNotExist:
                continue  # skip invalid product

            GRNItems.objects.filter(grn=grn, item_id=itm).update(
                quantity=qty,
                admin_comment=comm
            )

        messages.success(request, 'Products updated successfully.')
        return redirect('/grn')

    messages.error(request, 'Invalid request method.')
    return redirect('/grn')


@login_required
def products_list(request):
    items = Product.objects.all()

    context = {
        'items' : items,
    }
    return render(request, 'pages/apps/product-list.html', context)  

class ProductDetail(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'core/product_detail.html'

class ProductCreate(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:product-list')
    def form_valid(self, form):
        resp = super().form_valid(form)
        return resp

class ProductEdit(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['status','location']
    template_name = 'core/form.html'
    success_url = reverse_lazy('core:product-list')
    def form_valid(self, form):
        resp = super().form_valid(form)
        return resp


@login_required
@csrf_exempt
def add_products(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            unit_price = request.POST.get('unit_price')
            stock = int(request.POST.get('stock', 0))
            more_info = request.POST.get('more_info')

            if not all([name, unit_price]) or stock <= 0:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('/products')

            handler = CustomUser.objects.get(uid=request.user.uid)
            sku = generate_unique_sku()

            # Create product
            product = Product.objects.create(
                handled_by=handler,
                sku=sku,
                name=name,
                unit_price=unit_price,
                more_info=more_info,
                stock=stock
            )

            # ✅ Generate multiple QR codes (one per unit in stock)
            # for i in range(stock):
            # Generate QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4
            )
            qr.add_data(f'{product.item_id}')
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Save QR code using Django’s upload_to logic
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            product.qr_code.save(f'{product.item_id}.png', ContentFile(buffer.getvalue()), save=True)

                # ProductQR.objects.create(
                #     product=product,
                #     qr_code=ContentFile(buffer.getvalue())
                # )

            messages.success(request, f'Product "{product.name}" added successfully with {stock} QR codes.')
            return redirect('/products')

        except Exception as e:
            messages.error(request, f'Error adding product: {e}')
            return redirect('/products')

    messages.error(request, 'Invalid request method.')
    return redirect('/products')


@api_view(['GET', ])
@permission_classes([AllowAny])
def productList(request, id):
    try:
        info_data = Product.objects.get(item_id=id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        serializer = ProductsSerializer(info_data)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def myStockInfo(request):
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = JSONParser().parse(request)
    qr_code_str = data.get('qr_code')
    uid = data.get('uid')
    
    try:
        user = CustomUser.objects.get(uid=uid)
        product = ContainerStock.objects.get(product__item_id__icontains=qr_code_str,container__site_id__icontains=user.site_id.site_id)
    except:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
            "name": product.product.name,
            "sku": product.product.sku,
            "more_info": product.product.more_info,
            "unit_price": product.product.unit_price,
            "stock": product.stock
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def sale_products(request):
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = JSONParser().parse(request)
    qr_code_str = data.get('qr_code')
    uid = data.get('uid')
    quantity = data.get('quantity')
    
    if not qr_code_str or not uid:
        return Response({'error': 'Missing qr_code or uid'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(uid=uid)
    except CustomUser.DoesNotExist:
        print(f"'error': 'User not found 2'")
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        item = ContainerStock.objects.get(product__item_id__icontains=qr_code_str,container__site_id__icontains=user.site_id.site_id)
    except ContainerStock.DoesNotExist:
        return Response({'response': 'Transaction was not successful',
        'resMssg': 1}, status=status.HTTP_404_NOT_FOUND)


    # Assign user and site
    clean_value = int(float(quantity))
    if  int(float(item.stock)) < clean_value:
        return Response({'response': 'Transaction was not successful',
        'resMssg': 1}, status=status.HTTP_404_NOT_FOUND)
    else:
        item.stock = int(item.stock) - clean_value
        item.sell_type = "full-deposit"
        item.save()
        ContainerSales.objects.create(
            product=item.product,
            container=item.container,
            stock_id=item.stock_id,
            stock=clean_value,
            sold_by=user.uid,
            status=0,
            sell_type="full-deposit",
        )

    return Response({
        'response': 'Transaction was successful',
        'resMssg': 1
    }, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def swap_products(request):
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = JSONParser().parse(request)
    qr_code_str = data.get('qr_code')
    uid = data.get('uid')
    quantity = data.get('quantity')
    
    if not qr_code_str or not uid:
        return Response({'error': 'Missing qr_code or uid'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(uid=uid)
    except CustomUser.DoesNotExist:
        print(f"'error': 'User not found 2'")
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        item = ContainerStock.objects.get(product__item_id__icontains=qr_code_str,container__site_id__icontains=user.site_id.site_id)
    except ContainerStock.DoesNotExist:
        return Response({'response': 'Swap was not successful',
        'resMssg': 1}, status=status.HTTP_404_NOT_FOUND)


    # Assign user and site
    clean_value = int(float(quantity))
    if  int(float(item.stock)) < clean_value:
        return Response({'response': 'Swap was not successful',
        'resMssg': 1}, status=status.HTTP_404_NOT_FOUND)
    else:
        item.stock = int(item.stock) - clean_value
        item.sell_type = "swap"
        item.save()
        
        ContainerSales.objects.create(
            product=item.product,
            container=item.container,
            stock_id=item.stock_id,
            stock=clean_value,
            sold_by=user.uid,
            status=0,
            sell_type="swap",
        )

    return Response({
        'response': 'Swap was successful',
        'resMssg': 1
    }, status=status.HTTP_200_OK)


@login_required
# @csrf_exempt
def add_bulk_product(request):
    if request.method == 'POST':
        try:
            item_id = request.POST.get('name')
            qty = int(request.POST.get('qty', 0))
            item = get_object_or_404(Product, item_id=item_id)
            

            qr_data_list = []

            for i in range(qty):
                unique_code = f"{item.item_id}"
                

                # === QR code with Pillow for text ===
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=10,
                    border=4
                )
                qr.add_data(unique_code)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                item.qr_code.save(f'{unique_code}.png', ContentFile(buffer.getvalue()), save=False)

                # Keep for PDF
                qr_data_list.append((buffer.getvalue(), unique_code, item.name))

            # === Generate PDF ===
            page_w, page_h = 75 * mm, 65 * mm
            qr_size = 50 * mm
            margin_top = 5 * mm

            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=(page_w, page_h))
            for img_bytes, unique_code, cyl_size in qr_data_list:
                img_buffer = io.BytesIO(img_bytes)
                img_reader = ImageReader(img_buffer)

                x = (page_w - qr_size) / 2
                y = (page_h - qr_size) / 2
                
                px = (page_w - qr_size) / 1.4
                py = page_h - qr_size - margin_top

                c.drawImage(img_reader, px, py, width=qr_size, height=qr_size)
                c.saveState()
                # Move origin to center of page
                c.translate(x, y)
                # Rotate 90 degrees clockwise
                c.rotate(90)
                # After rotation, (0,0) is now the center
                
                # Generate unique 8-digit code
                unique_num = str(uuid.uuid4().hex[:8].upper())

                # Text in PDF below QR
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(page_w / 2.8, -15, f"ID: {item.sku}")
                c.setFont("Helvetica", 10)
                c.drawCentredString(page_w / 2.8, 1, f"{cyl_size}")

                c.showPage()

            c.save()
            pdf_buffer.seek(0)

            filename = f"products_{datetime.now().strftime('%Y-%m-%d')}.pdf"
            return FileResponse(pdf_buffer, as_attachment=True, filename=filename)
        
        except Exception as e:
            messages.error(request, f'Error adding product: {e}')
            print(f'Error adding product: {e}')
            return redirect('/products')
    return redirect('/products')



@login_required
@csrf_exempt
def add_measurable_products(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            unit_price = request.POST.get('unit_price')
            stock = request.POST.get('stock')
            more_info = request.POST.get('more_info')

            if not all([name, unit_price, stock]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('/products')

            handler = CustomUser.objects.get(uid=request.user.uid)
            sku = generate_unique_sku()

            product = Product.objects.create(
                handled_by=handler,
                sku=sku,
                name=name,
                unit_price=unit_price,
                more_info=more_info,
                stock=stock
            )

            # ✅ Generate QR Code for product
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4
            )
            qr.add_data(product.item_id)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Save QR code image to Product field
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            product.qr_code.save(f'{product.item_id}.png', ContentFile(buffer.getvalue()), save=True)

            messages.success(request, f'Product "{product.name}" added successfully.')
            return redirect('/products')

        except Exception as e:
            messages.error(request, f'Error adding product: {e}')
            return redirect('/products')

    messages.error(request, 'Invalid request method.')
    return redirect('/products')

# @login_required
# @csrf_exempt
# def add_products(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         unit_price = request.POST.get('unit_price')
#         stock = request.POST.get('stock')
#         more_info = request.POST.get('more_info')
#         handler = CustomUser.objects.get(uid=request.user.uid)
#         sku = generate_unique_sku()
#         push_product = Product.objects.create(handled_by=handler, sku=sku, name=name, unit_price=unit_price, more_info=more_info, stock=stock)
#         push_product.save()
        
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_H,
#             box_size=10,
#             border=4
#         )
#         print(push_product.item_id)
#         qr.add_data(push_product.item_id)
#         qr.make(fit=True)
#         img = qr.make_image(fill_color="black", back_color="white")

#         # Save QR code image to Product field
#         buffer = io.BytesIO()
#         img.save(buffer, format='PNG')
#         push_product.qr_code.save(f'{push_product.item_id}.png', ContentFile(buffer.getvalue()), save=False)
        
#         messages.success(request, 'Product added successfully.')
#         return redirect('/products')
#     messages.error(request, 'There was an error. Please try again')
#     return redirect('/products')   
    
    
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
    

@api_view(['POST', ])
@permission_classes([AllowAny])
def _refill_func(request):
    # info_data = CustomUser.objects.get(uid=pk)
    if request.method == "POST":
        refill_data = JSONParser().parse(request)
        refill_serializer = RefillSerializer(data=refill_data)
        if refill_serializer.is_valid():
            refill_serializer.save()
            response = {
                'response': 'Transaction was successful',
                'resMssg': 1,
            }
            return Response(response, status=status.HTTP_200_OK)
        data = refill_serializer.errors
        print(refill_serializer.errors)
        
        return Response(data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def refill_func(request):
    if request.method == "POST":
        refill_data = JSONParser().parse(request)
        refill_serializer = RefillSerializer(data=refill_data)
        
        if refill_serializer.is_valid():
            try:
                qrc = Cylinder.objects.get(id=refill_data['qrcode'])
                if str(qrc.id) == refill_data['qrcode']: 
                    instance = refill_serializer.save()  # saved object already has refill_id + date_added
                    response = {
                        'response': 'Transaction was successful',
                        'resMssg': 1,
                        'refill_id': instance.refill_id,
                    }
                    dbpush = Cylinder.objects.get(id=refill_data['qrcode'])
                    dbpush.status = "in_use"
                    dbpush.location = refill_data['site_id']
                    dbpush.save()
                    return Response(response, status=status.HTTP_201_CREATED)
                else:
                    print(f'{refill_serializer.errors} if error')
                    return Response(refill_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    # return Response(response, status=status.HTTP_400_BAD_REQUEST)
            except:
                response = {
                        'response': 'Transaction was unsuccessful',
                        'resMssg': 0,
                        'refill_id': '',
                    }
                print(f"{response['response']} try error ")
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(refill_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([AllowAny])
def sale_func(request):
    if request.method == "POST":
        sale_data = JSONParser().parse(request)
        sale_serializer = SalesSerializer(data=sale_data)

        if sale_serializer.is_valid():
            instance = sale_serializer.save()  # saved object already has sale_id + date_added

            response = {
                'response': 'Transaction was successful',
                'resMssg': 1,
                'sale_id': instance.sale_id,
            }
            return Response(response, status=status.HTTP_201_CREATED)

        return Response(sale_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([AllowAny])
def myRefillList(request, pk):
    try:
        info_data = Refill.objects.filter(handled_by=pk)
    except Refill.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = RefillSerializer(info_data, many=True)  # 👈 important
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def myGRNList(request):
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = JSONParser().parse(request)
    qr_code_str = data.get('qr_code')
    try:
        grn = GRN.objects.get(grn_Id=qr_code_str)
    except GRN.DoesNotExist:
        return Response({'error': 'GRN not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = GRNSerializer(grn)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny])
def myGRNaccept(request):
    if request.method != "POST":
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    data = JSONParser().parse(request)
    qr_code_str = data.get('qr_code')
    uid = data.get('uid')
    
    if not qr_code_str or not uid:
        return Response({'error': 'Missing qr_code or uid'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        grn = GRN.objects.get(grn_Id__icontains=qr_code_str, status=0)  # search by filename
    except GRN.DoesNotExist:
        return Response({'response': 'Transaction was successful',
        'resMssg': 1}, status=status.HTTP_404_NOT_FOUND)

    try:
        user = CustomUser.objects.get(uid=uid)
    except CustomUser.DoesNotExist:
        print(f"'error': 'User not found 2'")
        print(uid)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Assign user and site
    grn.rec_by = user.uid
    grn.assigned_site = user.site_id
    grn.status = 1
    grn.save()

    return Response({
        'response': 'Transaction was successful',
        'resMssg': 1
    }, status=status.HTTP_201_CREATED)





@login_required
def token_list(request):
    items = Product.objects.all()
    _close = CloseOfDay.objects.all()

    context = {
        'close' : _close,
    }
    return render(request, 'pages/apps/token-list.html', context)


@login_required
def make_token(request):
    items = Product.objects.all()

    context = {
        'items' : items,
    }
    return render(request, 'pages/apps/create-token.html', context)  



@csrf_exempt
def request_close_of_day(request):
    """Initiate a new close-of-day request and generate OTP."""
    if request.method == "POST":
        try:
            # Try reading JSON
            data = json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fallback to form data
            data = request.POST

        requested_by = data.get("requested_by")
        usr = CustomUser.objects.get(uid=requested_by)

        if not requested_by:
            return JsonResponse({"error": "requested_by is required"}, status=400)

        close = CloseOfDay.objects.create(
            requested_by=requested_by,
            otp=generate_otp(),
            site_id=usr.site_id.site_id
        )

        close.calculate_totals()

        return JsonResponse({
            "message": "Close of Day OTP generated.",
            "otp": close.otp,
            "totals": {
                "refills": close.total_refills,
                "amount": str(close.total_amount)
            }
        })

    return JsonResponse({"error": "Invalid request method"}, status=405)


# @csrf_exempt
# def verify_close_of_day(request):
#     """Verify OTP and approve closure."""
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body.decode('utf-8'))
#         except (json.JSONDecodeError, UnicodeDecodeError):
#             data = request.POST

#         otp = data.get("otp")
#         approved_by = data.get("approved_by")

#         if not otp or not approved_by:
#             return JsonResponse({"error": "otp and approved_by are required"}, status=400)
        
#         usr = CustomUser.objects.get(uid=approved_by)
        
#         try:
#             close = CloseOfDay.objects.get(otp=otp, otp_verified=False, requested_by=approved_by)
#             close.otp_verified = True
#             close.approved_by = approved_by
#             close.site_id = usr.site_id.site_id
#             close.total_amount = str(close.total_amount)
#             close.total_refills = close.total_refills
#             close.save()

#             return JsonResponse({
#                 "message": "Close of Day approved successfully.",
#                 "from": close.start_date,
#                 "to": close.end_date,
#                 "total_refills": close.total_refills,
#                 "total_amount": str(close.total_amount)
#             })

#         except CloseOfDay.DoesNotExist:
#             return JsonResponse({"error": "Invalid or already used OTP."}, status=400)

#     return JsonResponse({"error": "Invalid request method"}, status=405)
@csrf_exempt
def verify_close_of_day(request):
    """Verify OTP and approve Close of Day, returning totals including per-site grand totals."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        data = request.POST

    otp = data.get("otp")
    approved_by = data.get("approved_by")

    if not otp or not approved_by:
        return JsonResponse({"error": "otp and approved_by are required"}, status=400)

    # --- Get approver user ---
    try:
        usr = CustomUser.objects.get(uid=approved_by)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "Approver not found"}, status=404)

    # --- Get CloseOfDay record ---
    try:
        close = CloseOfDay.objects.get(otp=otp, otp_verified=False, requested_by=approved_by)

        # --- Calculate totals dynamically ---
        totals_data = close.calculate_totals()

        # --- Approve close ---
        close.otp_verified = True
        close.approved_by = approved_by
        close.site_id = getattr(usr.site_id, "site_id", None)  # safe assignment
        close.save()

        # --- Prepare per-site totals for JSON ---
        site_totals_json = {
            site: {
                "refills": data["refills"],
                "refill_amount": str(data["refill_amount"]),
                "sales": data["sales"],
                "sales_amount": str(data["sales_amount"]),
                # "grand_total": str(data["grand_total"])
            } for site, data in totals_data.get("site_totals", {}).items()
        }

        # --- Full response ---
        response_data = {
            "message": "Close of Day approved successfully.",
            "from": close.start_date,
            "to": close.end_date,
            "total_refills": totals_data.get("total_refills", 0),
            "total_sales": totals_data.get("total_sales", 0),
            "total_refill_amount": str(totals_data.get("total_refill_amount", "0")),
            "total_sales_amount": str(totals_data.get("total_sales_amount", "0")),
            "grand_total_amount": str(totals_data.get("grand_total_amount", "0")),
            "site_totals": site_totals_json
        }

        return JsonResponse(response_data)

    except CloseOfDay.DoesNotExist:
        return JsonResponse({"error": "Invalid or already used OTP."}, status=400)




@csrf_exempt
def verify_admin_password(request):
    """
    Verifies if the given password belongs to an admin user.
    """
    if request.method == 'POST':
        password = request.POST.get('password', '')
        username = request.POST.get('username', '')

        # Get admin user (you can adapt this if multiple admins exist)
        from django.contrib.auth import get_user_model
        # User = get_user_model()
        admin_user = CustomUser.objects.filter(access_level=0, username=username).first()

        if admin_user and admin_user.check_password(password):
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Invalid admin password.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)
