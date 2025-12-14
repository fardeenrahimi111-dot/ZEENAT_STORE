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

 # Custom method to show low stock warning
    def is_low_stock(self, obj):
        return obj.quantity < 10
    is_low_stock.boolean = True  # Shows as green/red icon
    is_low_stock.short_description = "Low Stock"

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'total_amount', 'created_at', 'item_count']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'  # Adds date navigation
    readonly_fields = ['created_at']  # Can't edit creation date
    
    # Inlines - show sale items within sale page
    class SaleItemInline(admin.TabularInline):
        model = SaleItem
        extra = 0  # Don't show empty forms
        readonly_fields = ['product', 'quantity', 'price_at_sale', 'line_total']
    
    inlines = [SaleItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Items"