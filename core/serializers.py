from core.models import GRN, GRNItems, Item, Product, Refill, Sale
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

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'item_type', 'size_kg', 'base_price']
        
        
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
            'unit_price',
            'active',
            'stock',
        )
        model = Product
        

class GRNItemSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)
    item = ItemSerializer(read_only=True)

    class Meta:
        model = GRNItems
        fields = [
            'id',
            'product',
            'item',
            'quantity',
            'added_date',
            'status',
            'admin_comment',
            'site_comment',
        ]

class GRNSerializer(serializers.ModelSerializer):
    items = GRNItemSerializer(many=True, read_only=True)

    class Meta:
        model = GRN
        fields = [
            'grn_Id',
            'initia',
            'grn_number',
            'made_date',
            'status',
            'qr_code',
            'assigned_site',
            'rec_by',
            'items'
        ]