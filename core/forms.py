
from django import forms
from .models import GRN, Cylinder, Order, Refill, Sale, Container, Customer, Product

class CylinderForm(forms.ModelForm):
    class Meta:
        model = Cylinder
        fields = ['item','status','location']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer']

class RefillForm(forms.ModelForm):
    class Meta:
        model = Refill
        fields = ['cylinder','customer','quantity_kg','unit_price_per_kg']

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product','customer','quantity','unit_price']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name','phone','address']

class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ['name','location']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','sku','unit_price','stock','active']
        
class DistributionForm(forms.ModelForm):
    class Meta:
        model = GRN
        fields = ['grn_Id','initia','grn_number','status']
