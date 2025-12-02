from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import localdate

from .models import Product, Sale, SaleItem, InventoryMovement


# ---------- PRODUCT CRUD ----------

def product_list(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'core/product_list.html', {'products': products})


def product_create(request):
    if request.method == 'POST':
        Product.objects.create(
            name=request.POST['name'],
            sku=request.POST['sku'],
            category=request.POST.get('category') or '',
            purchase_price=request.POST['purchase_price'],
            selling_price=request.POST['selling_price'],
            stock=request.POST['stock'],
        )
        return redirect('product_list')

    return render(request, 'core/product_form.html')


def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.name = request.POST['name']
        product.sku = request.POST['sku']
        product.category = request.POST.get('category') or ''
        product.purchase_price = request.POST['purchase_price']
        product.selling_price = request.POST['selling_price']
        product.stock = request.POST['stock']
        product.save()
        return redirect('product_list')

    return render(request, 'core/product_form.html', {'product': product})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')

    return render(request, 'core/product_confirm_delete.html', {'product': product})


# ---------- CREATE SALE + RECEIPT + UPDATE STOCK ----------

@transaction.atomic
def sale_create(request):
    products = Product.objects.all()

    if request.method == 'POST':
        sale = Sale.objects.create(
            invoice_number=f"INV-{int(timezone.now().timestamp())}",
            customer_name=request.POST.get('customer_name'),
        )

        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')

        for pid, qty_str in zip(product_ids, quantities):
            if not qty_str:
                continue
            quantity = int(qty_str)
            if quantity <= 0:
                continue

            product = Product.objects.get(pk=pid)

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=product.selling_price,
            )

            product.stock -= quantity
            product.save()

            InventoryMovement.objects.create(
                product=product,
                movement_type=InventoryMovement.OUT,
                quantity=quantity,
                reason=f"Sale {sale.invoice_number}",
            )

        return redirect('sale_receipt', pk=sale.pk)

    return render(request, 'core/sale_form.html', {'products': products})


def sale_receipt(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'core/sale_receipt.html', {'sale': sale})


# ---------- INVENTORY + DAILY RECONCILIATION ----------

def inventory_overview(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'core/inventory_overview.html', {'products': products})


def daily_reconciliation(request):
    today = localdate()
    sales_today = Sale.objects.filter(date__date=today)
    total_sales_amount = sum(s.total_amount for s in sales_today)
    invoices_count = sales_today.count()

    context = {
        'today': today,
        'sales_today': sales_today,
        'total_sales_amount': total_sales_amount,
        'invoices_count': invoices_count,
    }
    return render(request, 'core/daily_reconciliation.html', context)
