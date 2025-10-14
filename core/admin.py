
from django.contrib import admin
from .models import GRN, CloseOfDay, Container, GRNItems, Item, Customer, Cylinder, CylinderEvent, Order, OrderItem, Product, Refill, Sale

admin.site.register(Item)
admin.site.register(Customer)
admin.site.register(Cylinder)
admin.site.register(CylinderEvent)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(Refill)
admin.site.register(Sale)
admin.site.register(Container)
admin.site.register(GRN)
admin.site.register(GRNItems)
admin.site.register(CloseOfDay)
