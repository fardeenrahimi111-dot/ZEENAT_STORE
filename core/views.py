from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.db.models import Sum, Avg, Max, Count, Min, Q  # ✅ ADDED Min
from django.utils import timezone
from functools import wraps

from xhtml2pdf import pisa
import io
import openpyxl

from .models import Product, Category, Sale, SaleItem
from .forms import ProductForm, SaleAddItemForm
from django.contrib import messages

# --- Role helpers ---
def user_in_group(user, group_name):
    return user.is_authenticated and (
        user.is_superuser or 
        user.groups.filter(name__iexact=group_name).exists()
    )

def has_any_role(user, roles):
    return user.is_authenticated and (
        user.is_superuser or 
        any(user.groups.filter(name__iexact=r).exists() for r in roles)
    )

# ✅ 1.7 - ROLE-BASED PERMISSIONS IMPROVEMENTS
def get_user_role(user):
    """Get user's role for display purposes"""
    if not user.is_authenticated:
        return "Guest"
    if user.is_superuser:
        return "Administrator"
    if user.groups.exists():
        return user.groups.first().name
    return "User"

def role_required(required_roles):
    """
    Decorator to check if user has required role(s).
    Usage: @role_required(['admin', 'Manager'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please login to access this page.")
                return redirect('login')
            
            if not has_any_role(request.user, required_roles):
                # Log the attempt
                messages.error(
                    request, 
                    f"Access denied. Required role(s): {', '.join(required_roles)}"
                )
                # Pass context to 403 template
                return HttpResponseForbidden(
                    render(request, 'core/403.html', {
                        'required_roles': required_roles,
                        'user_role': get_user_role(request.user),
                        'current_user': request.user
                    })
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# ---------------- DASHBOARD ----------------

@login_required
def dashboard(request):
    """✅ 1.8 - OPTIMIZED DASHBOARD QUERIES"""
    today = timezone.now().date()
    
    # ✅ OPTIMIZED: Get multiple statistics in single queries
    
    # 1. Get all product statistics in ONE query
    product_stats = Product.objects.aggregate(
        total_count=Count('id'),
        low_stock_count=Count('id', filter=Q(quantity__lt=10)),
        out_of_stock_count=Count('id', filter=Q(quantity=0)),
        total_quantity=Sum('quantity'),
        total_inventory_value=Sum('price')
    )
    
    # 2. Get today's sales in ONE query
    today_sales_data = Sale.objects.filter(
        created_at__date=today
    ).aggregate(
        total_sales=Sum('grand_total'),
        sale_count=Count('id'),
        avg_sale_value=Avg('grand_total')
    )
    
    # 3. Get low stock products with related data
    low_stock_products = Product.objects.filter(
        quantity__lt=10
    ).select_related('category').order_by('quantity')[:10]  # Limit for performance
    
    # 4. Get recent sales with optimized query (prefetch related items)
    recent_sales = Sale.objects.select_related().prefetch_related(
        'items__product'
    ).order_by('-created_at')[:5]
    
    # 5. Get total value of low stock items
    low_stock_value = sum(p.price * p.quantity for p in low_stock_products)
    
    context = {
        "total_products": product_stats['total_count'] or 0,
        "total_quantity": product_stats['total_quantity'] or 0,
        "today_sales_total": today_sales_data['total_sales'] or Decimal("0"),
        "today_sales_count": today_sales_data['sale_count'] or 0,
        "avg_sale_value": today_sales_data['avg_sale_value'] or Decimal("0"),
        "low_stock_count": product_stats['low_stock_count'] or 0,
        "out_of_stock_count": product_stats['out_of_stock_count'] or 0,
        "low_stock_products": low_stock_products,
        "low_stock_value": low_stock_value,
        "recent_sales": recent_sales,
        "total_customers": 0,  # Update when you add Customer model
        "current_date": today,
        "total_inventory_value": product_stats['total_inventory_value'] or Decimal("0"),
    }
    return render(request, "core/dashboard.html", context)

# ---------------- PRODUCT CRUD ----------------

@login_required
@role_required(['admin', 'Manager'])  # ✅ 1.7 - Added role decorator
def product_list(request):
    """✅ 1.8 - OPTIMIZED PRODUCT LIST QUERY"""
    # Use select_related to avoid N+1 queries for category
    products = Product.objects.select_related("category").all().order_by('-created_at')
    return render(request, "core/product_list.html", {"products": products})

@login_required
@role_required(['admin', 'Manager'])  # ✅ 1.7 - Added role decorator
def product_create(request):
    # Already have permission check, but decorator handles it
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            new_cat = form.cleaned_data.get("new_category")

            if new_cat:
                # create category
                category = Category.objects.create(name=new_cat)
                form.instance.category = category

            form.save()
            messages.success(request, "Product created successfully!")
            return redirect("core:product_list")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ProductForm()

    return render(request, "core/product_form.html", {"form": form, "title": "Add Product"})

@login_required
@role_required(['admin', 'Manager'])  # ✅ 1.7 - Added role decorator
def product_update(request, pk):
    # Already have permission check, but decorator handles it
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            new_cat = form.cleaned_data.get("new_category")

            if new_cat:
                category = Category.objects.create(name=new_cat)
                form.instance.category = category

            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect("core:product_list")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ProductForm(instance=product)

    return render(request, "core/product_form.html", {"form": form, "title": "Edit Product"})

@login_required
@role_required(['admin'])  # ✅ 1.7 - Only admin can delete (stricter permission)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product_name = product.name
        product.delete()
        messages.success(request, f"Product '{product_name}' deleted successfully!")
        return redirect("core:product_list")

    return render(request, "core/product_confirm_delete.html", {"product": product})

# ---------------- SALES ----------------

@login_required
@role_required(['admin', 'Manager', 'Cashier'])  # ✅ 1.7 - Added role decorator
def sale_create(request):
    """Sale creation view using session as a temporary cart."""
    
    # Get cart from session
    cart = request.session.get("cart", {})
    
    if request.method == "POST":
        # 1. ADD ITEM TO CART
        if "add_item" in request.POST:
            form = SaleAddItemForm(request.POST)
            if form.is_valid():
                product = form.cleaned_data.get("product")
                quantity = form.cleaned_data.get("quantity")
                
                if product and quantity > 0:
                    # Check if product already in cart
                    product_id = str(product.id)
                    if product_id in cart:
                        cart[product_id]["quantity"] += quantity
                    else:
                        cart[product_id] = {
                            "name": product.name,
                            "price": float(product.price),
                            "quantity": quantity,
                        }
                    request.session["cart"] = cart
                    messages.success(request, f"Added {quantity} x {product.name} to cart")
                return redirect("core:sale_create")
            else:
                messages.error(request, "Please correct the form errors.")
        
        # 2. CHECKOUT (CREATE SALE)
        elif "checkout" in request.POST:
            customer_name = request.POST.get("customer_name", "").strip()
            
            if cart:
                # ✅ STEP 1: CHECK STOCK BEFORE CREATING SALE
                insufficient_stock = []
                for product_id, item in cart.items():
                    try:
                        product = Product.objects.get(id=int(product_id))
                        if product.quantity < item["quantity"]:
                            insufficient_stock.append(f"{product.name} (Available: {product.quantity}, Need: {item['quantity']})")
                    except Product.DoesNotExist:
                        pass
                
                # If any product has insufficient stock, show error
                if insufficient_stock:
                    messages.error(request, f"Insufficient stock for: {', '.join(insufficient_stock)}")
                    return redirect("core:sale_create")
                
                # ✅ STEP 2: CREATE SALE
                sale = Sale.objects.create(customer_name=customer_name)
                total = Decimal("0")
                
                for product_id, item in cart.items():
                    product = Product.objects.get(id=int(product_id))
                    quantity = item["quantity"]
                    price = Decimal(str(item["price"]))
                    line_total = price * quantity
                    
                    # ✅ STEP 3: REDUCE STOCK (IMPORTANT!)
                    product.quantity -= quantity
                    product.save()  # This saves the reduced quantity to database
                    
                    # Create sale item
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price_at_sale=price,
                        line_total=line_total,
                    )
                    total += line_total
                
                # Save sale totals
                sale.total_amount = total
                sale.grand_total = total
                sale.save()
                
                # Clear cart
                request.session["cart"] = {}
                messages.success(request, f"Sale #{sale.id} completed successfully! Total: ₹{total}")
                return redirect("core:sale_detail", sale_id=sale.id)
            else:
                messages.warning(request, "Cart is empty! Add items before checkout.")
                return redirect("core:sale_create")
    
    else:
        # GET request - show empty form
        form = SaleAddItemForm()
    
    # Calculate cart total for display
    cart_total = sum(item["price"] * item["quantity"] for item in cart.values())
    
    context = {
        "form": form,
        "cart": cart,
        "cart_total": cart_total,
    }
    return render(request, "core/sale_create.html", context)

@login_required
@role_required(['admin', 'Manager', 'Cashier'])  # ✅ 1.7 - Added role decorator
def sale_list(request):
    """✅ 1.8 - OPTIMIZED SALE LIST QUERY"""
    # Use select_related and prefetch_related to avoid N+1 queries
    sales = Sale.objects.select_related().prefetch_related(
        'items__product'
    ).order_by("-created_at")
    
    # Calculate summary statistics
    sales_summary = sales.aggregate(
        total_sales=Count('id'),
        total_revenue=Sum('grand_total'),
        avg_sale=Avg('grand_total')
    )
    
    return render(request, "core/sale_list.html", {
        "sales": sales,
        "total_sales": sales_summary['total_sales'] or 0,
        "total_revenue": sales_summary['total_revenue'] or Decimal('0'),
        "avg_sale": sales_summary['avg_sale'] or Decimal('0')
    })

@login_required
@role_required(['admin', 'Manager', 'Cashier'])  # ✅ 1.7 - Added role decorator
def sale_detail(request, sale_id):
    """✅ 1.8 - OPTIMIZED SALE DETAIL QUERY"""
    try:
        # Use get_object_or_404 with select_related for performance
        sale = get_object_or_404(
            Sale.objects.select_related(),
            id=sale_id
        )
        
        # Get items with product data in single query
        items = sale.items.select_related('product').all()
        
        return render(request, "core/sale_detail.html", {
            "sale": sale, 
            "items": items
        })
    except Exception as e:
        messages.error(request, f"Error loading sale details: {str(e)}")
        return redirect("core:sale_list")

@login_required
@role_required(['admin', 'Manager', 'Cashier'])  # ✅ 1.7 - Added role decorator
def sale_invoice_pdf(request, sale_id):
    """✅ 1.8 - OPTIMIZED INVOICE QUERY"""
    sale = get_object_or_404(
        Sale.objects.select_related(),
        id=sale_id
    )
    
    # Get items with product data
    items = sale.items.select_related('product').all()

    html = render_to_string("core/invoice_pdf.html", {"sale": sale, "items": items})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{sale.id}.pdf"'

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response)
    if pisa_status.err:
        messages.error(request, "Error generating PDF invoice")
        return redirect("core:sale_detail", sale_id=sale_id)
    
    return response

# ---------------- REPORTS ----------------

@login_required
@role_required(['admin', 'Manager'])  # ✅ 1.7 - Added role decorator
def inventory_report(request):
    """✅ 1.8 - OPTIMIZED INVENTORY REPORT QUERY"""
    # Use select_related to get category data in single query
    products = Product.objects.select_related("category").all().order_by('category__name', 'name')
    
    # Calculate summary statistics
    inventory_stats = products.aggregate(
        total_products=Count('id'),
        total_value=Sum('price'),
        total_quantity=Sum('quantity'),
        avg_price=Avg('price')
    )
    
    # Calculate low stock count separately
    low_stock_count = products.filter(quantity__lt=10).count()
    out_of_stock_count = products.filter(quantity=0).count()
    
    context = {
        "products": products,
        "total_products": inventory_stats['total_products'] or 0,
        "total_value": inventory_stats['total_value'] or Decimal('0'),
        "total_quantity": inventory_stats['total_quantity'] or 0,
        "avg_price": inventory_stats['avg_price'] or Decimal('0'),
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
    }
    return render(request, "core/inventory_report.html", context)

@login_required
@role_required(['admin', 'Manager'])  # ✅ 1.7 - Added role decorator
def inventory_report_excel(request):
    """✅ 1.8 - OPTIMIZED EXCEL REPORT QUERY"""
    # Use select_related to avoid N+1 queries
    products = Product.objects.select_related("category").all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventory Report"
    
    # Header with timestamp
    ws.append(["Zeenat Store - Inventory Report"])
    ws.append([f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    ws.append([])  # Empty row
    
    # Column headers
    ws.append(["ID", "Name", "Category", "Size", "Color", "Price", "Quantity", "Total Value", "Status"])

    for p in products:
        total_value = float(p.price) * p.quantity
        status = "In Stock"
        if p.quantity == 0:
            status = "Out of Stock"
        elif p.quantity < 10:
            status = "Low Stock"
        
        ws.append([
            p.id,
            p.name,
            p.category.name if p.category else "Uncategorized",
            p.size,
            p.color,
            float(p.price),
            p.quantity,
            total_value,
            status,
        ])
    
    # Add summary row
    ws.append([])
    ws.append(["SUMMARY", "", "", "", "", "", "", "", ""])
    
    total_products = products.count()
    total_quantity = products.aggregate(total=Sum('quantity'))['total'] or 0
    total_value = sum(float(p.price) * p.quantity for p in products)
    low_stock = products.filter(quantity__lt=10).count()
    out_of_stock = products.filter(quantity=0).count()
    
    ws.append(["Total Products", total_products])
    ws.append(["Total Quantity", total_quantity])
    ws.append(["Total Inventory Value", total_value])
    ws.append(["Low Stock Items", low_stock])
    ws.append(["Out of Stock Items", out_of_stock])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="inventory_report.xlsx"'
    wb.save(response)
    return response

@login_required
@role_required(['admin', 'Manager'])  # ✅ 1.7 - Added role decorator
def sales_report(request):
    """✅ 1.8 - OPTIMIZED SALES REPORT QUERY"""
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Base queryset with optimization
    sales = Sale.objects.select_related().prefetch_related('items')
    
    # Apply filters if provided
    if start_date:
        sales = sales.filter(created_at__date__gte=start_date)
    if end_date:
        sales = sales.filter(created_at__date__lte=end_date)

    # Get summary statistics in single query
    sales_summary = sales.aggregate(
        total_sales=Count('id'),
        total_revenue=Sum('grand_total'),
        avg_sale=Avg('grand_total'),
        max_sale=Max('grand_total')
    )

    context = {
        "sales": sales.order_by('-created_at'),
        "total_sales": sales_summary['total_sales'] or 0,
        "total_revenue": sales_summary['total_revenue'] or Decimal("0"),
        "avg_sale": sales_summary['avg_sale'] or Decimal("0"),
        "max_sale": sales_summary['max_sale'] or Decimal("0"),
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "core/sales_report.html", context)

@login_required
@role_required(['admin', 'Manager'])  # ✅ 1.7 - Added role decorator
def sales_report_excel(request):
    """✅ 1.8 - OPTIMIZED EXCEL EXPORT"""
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    sales = Sale.objects.all()

    # Only filter if valid values are provided
    if start_date and start_date.lower() != "none":
        sales = sales.filter(created_at__date__gte=start_date)
    if end_date and end_date.lower() != "none":
        sales = sales.filter(created_at__date__lte=end_date)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Report"
    
    # Header
    ws.append(["Zeenat Store - Sales Report"])
    if start_date or end_date:
        period = ""
        if start_date:
            period += f"From: {start_date} "
        if end_date:
            period += f"To: {end_date}"
        ws.append([period])
    ws.append([f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    ws.append([])
    
    # Column headers
    ws.append(["Sale ID", "Date", "Customer", "Items", "Grand Total"])

    # Get sales with items count in single query
    sales_with_counts = sales.annotate(
        item_count=Count('items')
    ).order_by('-created_at')

    for s in sales_with_counts:
        ws.append([
            s.id,
            s.created_at.strftime("%Y-%m-%d %H:%M"),
            s.customer_name or "Walk-in Customer",
            s.item_count,
            float(s.grand_total),
        ])
    
    # Summary section
    ws.append([])
    ws.append(["SUMMARY", "", "", "", ""])
    
    total_sales = sales.count()
    total_revenue = sales.aggregate(total=Sum('grand_total'))['total'] or 0
    avg_sale = sales.aggregate(avg=Avg('grand_total'))['avg'] or 0
    
    ws.append(["Total Sales", total_sales])
    ws.append(["Total Revenue", float(total_revenue)])
    ws.append(["Average Sale", float(avg_sale)])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="sales_report.xlsx"'
    wb.save(response)
    return response

@login_required
@role_required(['admin', 'Manager'])  # ✅ 1.7 - Added role decorator
def low_stock_report(request):
    """✅ 1.8 - OPTIMIZED LOW STOCK REPORT QUERY"""
    # Get low stock products
    low_stock_threshold = 10
    low_stock_products = Product.objects.filter(
        quantity__lt=low_stock_threshold
    ).select_related('category').order_by('quantity')
    
    # Calculate statistics in single query
    low_stock_stats = low_stock_products.aggregate(
        total_count=Count('id'),
        avg_quantity=Avg('quantity'),
        min_quantity=Min('quantity'),
        total_value=Sum('price')
    )
    
    # Get sales data for low stock items (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    
    # Use subquery to get sales data efficiently
    from django.db.models import Subquery, OuterRef
    from django.db.models.functions import Coalesce
    
    # Annotate each product with sales data
    products_with_sales = low_stock_products.annotate(
        recent_sales=Coalesce(
            Subquery(
                SaleItem.objects.filter(
                    product=OuterRef('pk'),
                    sale__created_at__gte=thirty_days_ago
                ).values('product').annotate(
                    total_sold=Sum('quantity')
                ).values('total_sold')[:1]
            ),
            0
        ),
        last_sold_date=Max(
            'saleitem__sale__created_at',
            filter=Q(saleitem__sale__created_at__gte=thirty_days_ago)
        )
    )
    
    context = {
        'low_stock_products': products_with_sales,
        'low_stock_count': low_stock_stats['total_count'] or 0,
        'out_of_stock_count': Product.objects.filter(quantity=0).count(),
        'total_low_stock_value': sum(p.price * p.quantity for p in low_stock_products),
        'avg_stock_level': low_stock_stats['avg_quantity'] or 0,
        'threshold': low_stock_threshold,
    }
    return render(request, "core/low_stock_report.html", context)