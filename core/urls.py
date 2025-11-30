from django.urls import path 
from .import views

app_name = 'core'

urlpatterns = [
#staff routes will here

path('staff/login/', views.staff_login, name='staff_login'),
# Add more paths as needed for other views
]