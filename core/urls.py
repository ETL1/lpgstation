
from django.urls import path
from django.conf.urls import url, include
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('cylinders/', views.cylinder_list, name='cylinder-list'),
    path('cylinders/new/', views.CylinderCreate.as_view(), name='cylinder-create'),
    path('cylinders/bulk/', views.add_bulk_cylinder, name='cylinder-bulk-create'),
    path('cylinders/<uuid:pk>/', views.CylinderDetail.as_view(), name='cylinder-detail'),
    path('cylinders/<uuid:pk>/edit/', views.CylinderEdit.as_view(), name='cylinder-edit'),

    path('orders/', views.OrderList.as_view(), name='order-list'),
    path('orders/new/', views.OrderCreate.as_view(), name='order-create'),

    path('refills/', views.refill_list, name='refill-list'),
    url(r'^refill-list/(?P<pk>\w+)/$', views.myRefillList, name='get-orders'),
    path('refills/new/', views.RefillCreate.as_view(), name='refill-create'),
    path('refill-order/', views.refill_func, name='refill-order'),

    path('sales/', views.SaleList.as_view(), name='sale-list'),
    path('sales/new/', views.SaleCreate.as_view(), name='sale-create'),
    path('token/', views.token_list, name='token-list'),
    path('token/make/', views.make_token, name='token-make'),
    
    path('customers/', views.CustomerList.as_view(), name='customer-list'),
    path('customers/new/', views.CustomerCreate.as_view(), name='customer-create'),
    path('customers/<uuid:pk>/', views.CustomerDetail.as_view(), name='customer-detail'),
    path('customers/<uuid:pk>/edit/', views.CustomerEdit.as_view(), name='customer-edit'),
    
    path('products/', views.products_list, name='products-list'),
    path('products/new/', views.add_products, name='products-create'),
    path('item-sale/', views.sale_products, name='products-sale'),
    path('pull-item/', views.myStockInfo, name='products-find'),
    path('products/qr-gen/', views.add_bulk_product, name='products-qr-create'),
    path('products/new/measurable', views.add_measurable_products, name='products-create'),
    path('products/api/<uuid:id>/', views.productList, name='products-detail'),
    path('products/<uuid:pk>/', views.ProductDetail.as_view(), name='products-detail'),
    path('products/<uuid:pk>/edit/', views.ProductEdit.as_view(), name='products-edit'),
    
    path('grn/', views.distribution_list, name='grn-list'),
    path('grn/new/', views.create_grn, name='grn-create'),
    path('grn/make/', views.make_grn, name='grn-make'),
    # path('grn/<uuid:pk>/', views.DistributionDetail.as_view(), name='grn-detail'),
    path('grn/<uuid:pk>/', views.grn_detail, name='grn-detail'),
    path('grn-scan/', views.myGRNList, name='get-grnitems'),
    path('grn-accept/', views.myGRNaccept, name='accept-grn'),
    url(r'^edit-grn/(?P<pk>\w+)/$', views.edit_grn, name='edit-grn'),
    path('grn/save-edit/', views.submit_edit_grn, name='grn-edit-save'),
    # url(r'^delete-grn/(?P<pk>\w+)/$', views.delete_grn, name='delete-grn'),
    path('delete-grn/<str:pk>/', views.delete_grn, name='delete-grn'),
    
    
    path('containers/', views.ContainerList.as_view(), name='container-list'),
    path('containers/new/', views.add_container, name='container-create'),
    path('containers/<str:pk>/', views.container_view, name='container-detail'),
    path('containers/<uuid:pk>/edit/', views.ContainerEdit.as_view(), name='container-edit'),
    
    # path("close-day/", views.close_day_request, name="close_day_request"),
    # path("close-day/verify/", views.close_day_verify, name="close_day_verify"),
    # path("close-day/success/", views.close_day_success, name="close_day_success"),
    
    path('close-request/', views.request_close_of_day, name='request_close_of_day'),
    path('close-verify/', views.verify_close_of_day, name='verify_close_of_day'),
    
    path('verify-admin-password/', views.verify_admin_password, name='verify_admin_password'),

    
]
