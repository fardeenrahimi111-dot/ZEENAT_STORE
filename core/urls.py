from django.urls import path
from . import views

urlpatterns = [
    # Product CRUD
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Sales / receipts
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/receipt/', views.sale_receipt, name='sale_receipt'),

    # Inventory and reconciliation
    path('inventory/', views.inventory_overview, name='inventory_overview'),
    path('reconciliation/', views.daily_reconciliation, name='daily_reconciliation'),
]