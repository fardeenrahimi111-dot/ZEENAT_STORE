from django.contrib import admin
from .models import Product, Sale, SaleItem, InventoryMovement


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'stock', 'selling_price')
    search_fields = ('sku', 'name', 'category')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'date', 'customer_name', 'total_amount')
    inlines = [SaleItemInline]


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'reason', 'created_at')
    list_filter = ('movement_type', 'created_at')