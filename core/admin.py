from django.contrib import admin
from core.models import Category, Product, Sale, SaleItem



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "size", "color", "price", "quantity")
    search_fields = ("name", "barcode", "color")
    list_filter = ("category", "size")
    list_editable = ("price", "quantity")


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "created_at", "grand_total")
    inlines = [SaleItemInline]