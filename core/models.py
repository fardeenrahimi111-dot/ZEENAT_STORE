from django.db import models
from django.utils import timezone


class Product(models.Model):
    """Each clothing item in ZEENAT STORE."""
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Sale(models.Model):
    """One sale = one invoice / receipt."""
    invoice_number = models.CharField(max_length=30, unique=True)
    date = models.DateTimeField(default=timezone.now)
    customer_name = models.CharField(max_length=150, blank=True, null=True)

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        return f"Invoice {self.invoice_number}"


class SaleItem(models.Model):
    """Line item inside a Sale (one product row)."""
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class InventoryMovement(models.Model):
    """Track stock in / stock out for reconciliation."""
    IN = 'IN'
    OUT = 'OUT'
    MOVEMENT_TYPES = [
        (IN, 'Stock In'),
        (OUT, 'Stock Out'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} {self.movement_type} {self.quantity}"