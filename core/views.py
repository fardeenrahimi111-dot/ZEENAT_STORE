from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum
from django.utils import timezone

from xhtml2pdf import pisa
import io
import openpyxl

from .models import Product, Category, Sale, SaleItem
from .forms import ProductForm, SaleAddItemForm


@login_required
def dashboard(request):
    total_products = Product.objects.count()
    total_quantity = Product.objects.aggregate(total=Sum("quantity"))["total"] or 0
    today = timezone.now().date()
    today_sales_total = (
        Sale.objects.filter(created_at__date=today).aggregate(total=Sum("grand_total"))["total"]
        or Decimal("0")
    )
    context = {
        "total_products": total_products,
        "total_quantity": total_quantity,
        "today_sales_total": today_sales_total,
    }
    return render(request, "core/dashboard.html", context)


# ---------------- PRODUCT CRUD ----------------

@login_required
def product_list(request):
    products = Product.objects.select_related("category").all()
    return render(request, "inventory/product_list.html", {"products": products})


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()
    return render(request, "inventory/product_form.html", {"form": form, "title": "Add Product"})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, "inventory/product_form.html", {"form": form, "title": "Edit Product"})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "inventory/product_confirm_delete.html", {"product": product})


# ---------------- SALES ----------------

@login_required
def sale_create(request):
    """
    Sale creation view using session as a temporary cart.
    Supports barcode scanning or product dropdown selection.
    """
    cart = request.session.get("cart", {})

    if request.method == "POST":
        # Add item to cart
        if "add_item" in request.POST:
            form = SaleAddItemForm(request.POST)
            if form.is_valid():
                product = None
                barcode = form.cleaned_data.get("barcode")
                if barcode:
                    try:
                        product = Product.objects.get(barcode=barcode)
                    except Product.DoesNotExist:
                        product = None
                if not product:
                    product = form.cleaned_data.get("product")

                quantity = form.cleaned_data["quantity"]

                if product and quantity > 0:
                    # Only add if enough stock
                    if quantity <= product.quantity:
                        product_id = str(product.id)
                        if product_id in cart:
                            cart[product_id]["quantity"] += quantity
                        else:
                            cart[product_id] = {
                                "name": product.name,
                                "price": float(product.final_price()),
                                "quantity": quantity,
                            }
                        request.session["cart"] = cart
                return redirect("sale_create")

        # Checkout and save sale
        elif "checkout" in request.POST:
            customer_name = request.POST.get("customer_name", "").strip()
            if cart:
                sale = Sale.objects.create(customer_name=customer_name)
                total = Decimal("0")
                for pid, item in cart.items():
                    product = Product.objects.get(id=int(pid))
                    quantity = int(item["quantity"])
                    price = Decimal(str(item["price"]))
                    line_total = price * quantity

                    # reduce stock
                    if product.quantity >= quantity:
                        product.quantity -= quantity
                        product.save()

                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price_at_sale=price,
                        line_total=line_total,
                    )
                    total += line_total

                sale.total_amount = total
                sale.discount_amount = Decimal("0")
                sale.grand_total = total
                sale.save()

                # clear cart
                request.session["cart"] = {}
                return redirect("sale_detail", sale_id=sale.id)

    else:
        form = SaleAddItemForm()

    cart_total = sum(item["price"] * item["quantity"] for item in cart.values())

    context = {
        "form": form,
        "cart": cart,
        "cart_total": cart_total,
    }
    return render(request, "inventory/sale_create.html", context)


@login_required
def sale_list(request):
    sales = Sale.objects.order_by("-created_at")
    return render(request, "inventory/sale_list.html", {"sales": sales})


@login_required
def sale_detail(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    items = sale.items.select_related("product")
    return render(request, "inventory/sale_detail.html", {"sale": sale, "items": items})


@login_required
def sale_invoice_pdf(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    items = sale.items.select_related("product")

    html = render_to_string("inventory/invoice_pdf.html", {"sale": sale, "items": items})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{sale.id}.pdf"'

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response


# ---------------- REPORTS ----------------

@login_required
def inventory_report(request):
    products = Product.objects.select_related("category").all()
    return render(request, "inventory/inventory_report.html", {"products": products})


@login_required
def inventory_report_excel(request):
    products = Product.objects.select_related("category").all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventory"

    ws.append(["ID", "Name", "Category", "Size", "Color", "Price", "Discount", "Quantity"])

    for p in products:
        ws.append(
            [
                p.id,
                p.name,
                p.category.name,
                p.size,
                p.color,
                float(p.price),
                p.discount_percent,
                p.quantity,
            ]
        )

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="inventory_report.xlsx"'
    wb.save(response)
    return response


@login_required
def sales_report(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    sales = Sale.objects.all()
    if start_date:
        sales = sales.filter(created_at__date__gte=start_date)
    if end_date:
        sales = sales.filter(created_at__date__lte=end_date)

    total_sales = sales.aggregate(total=Sum("grand_total"))["total"] or Decimal("0")

    context = {
        "sales": sales,
        "total_sales": total_sales,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "inventory/sales_report.html", context)


@login_required
def sales_report_excel(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    sales = Sale.objects.all()
    if start_date:
        sales = sales.filter(created_at__date__gte=start_date)
    if end_date:
        sales = sales.filter(created_at__date__lte=end_date)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales"

    ws.append(["Sale ID", "Date", "Customer", "Grand Total"])

    for s in sales:
        ws.append(
            [
                s.id,
                s.created_at.strftime("%Y-%m-%d %H:%M"),
                s.customer_name or "",
                float(s.grand_total),
            ]
        )

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="sales_report.xlsx"'
    wb.save(response)
    return response
