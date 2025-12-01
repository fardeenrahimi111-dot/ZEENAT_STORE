from django.urls import path 
from . import views

app_name = 'core'

urlpatterns = [
#staff routes will here
# Add more paths as needed for other views
path('staff/login/', views.staff_login, name='staff_login'),
path('sale/new/', views.new_sale, name='new_sale'),
path('sale/checkout/', views.sale_checkout, name='sale_checkout'),
path('sale/receipt/<int:pk>/', views.sale_receipt, name='sale_receipt'),
path('reports/view/', views.reports, name='reports'),
]