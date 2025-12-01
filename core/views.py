from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from core.models import Product
# Create your views here.
def home(request):
    products = Product.objects.all()
    return render(request, 'core/home.html', {'products': products})

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('new_sale')  # Redirect to home after successful login
        else:
            return render(request, 'core/staff_login.html', {'error': 'Invalid credentials or not a staff member.'})
    return render(request, 'core/staff_login.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Product, Sale, SaleItem
from decimal import Decimal
import datetime


@login_required
def new_sale(request):
    """
    Cashier screen: search products, add qty, see live total.
    """
    products = Product.objects.select_related('category').all()
    cart = request.session.get('cart', {})   # session cart
    cart_items = []
    sub_total = Decimal('0.00')

    for prod_id, qty in cart.items():
        product = get_object_or_404(Product, id=prod_id)
        line_total = product.price * qty
        sub_total += line_total
        cart_items.append({'product': product, 'qty': qty, 'line_total': line_total})

    tax = sub_total * Decimal('0.15')   # 15 % tax
    grand_total = sub_total + tax

    if request.method == 'POST' and 'add_item' in request.POST:
        prod_id = request.POST['product_id']
        qty = int(request.POST['qty'])
        if qty <= 0:
            qty = 1
        cart[prod_id] = cart.get(prod_id, 0) + qty
        request.session['cart'] = cart
        return redirect('core:new_sale')

    context = {
        'products': products,
        'cart_items': cart_items,
        'sub_total': sub_total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'core/new_sale.html', context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Sale
import datetime
import random




@login_required
def sale_receipt(request, pk):
    """
    Display receipt for a completed sale.
    """
    sale = get_object_or_404(Sale, pk=pk)
    if not sale.reciept_number:
        # Generate a unique receipt number
        sale.reciept_number = f"REC{datetime.datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        sale.save()
        
    return render(request, 'core/sale_receipt.html', {'sale': sale})

@login_required
def checkout(request):
    """
    Finalize the sale, save to DB, clear cart.
    """
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('core:new_sale')

    sub_total = Decimal('0.00')
    for prod_id, qty in cart.items():
        product = get_object_or_404(Product, id=prod_id)
        line_total = product.price * qty
        sub_total += line_total
        item.append({'product': product, 'qty': qty, 'line_total': line_total})

    discount = Decimal('0.00')  # For simplicity, no discount logic here
    grand_total = sub_total - discount

    sale = Sale.objects.create(
        cashier=request.user,
        sub_total=sub_total,
        discount=discount,
        grand_total=grand_total
    )

    for item in item:
        SaleItem.objects.create(
            sale=sale,
            product=item['product'],
            qty=item['qty'],
            unit_price=item['product'].price,
            line_total=item['line_total']
        )
        # Update stock
        item['product'].stock_quantity -= item['qty']
        item['product'].save()

del request.session['cart']  # Clear cart
    return redirect('core:sale_receipt', pk=sale.pk)

