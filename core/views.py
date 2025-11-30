from django.shortcuts import render
from .models import product
# Create your views here.
def home(request):

    products = product.objects.all()
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