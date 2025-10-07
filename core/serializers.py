from core.models import Product, Refill, Sale
from rest_framework import serializers


class RefillSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'customer',
            'quantity_kg',
            'handled_by',
            'address',
            'qrcode',
            'refill_id',
            'phone',
            'site_id',
        )
        model = Refill

class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'product',
            'quantity',
            'unit_price',
            'total_price',
            'qrcode',
            'sold_by',
        )
        model = Sale
        
class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'item_id',
            'name',
            'sku',
            'item_pic',
            'status',
        )
        model = Product