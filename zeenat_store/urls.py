from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ✅ FIXED: Correct parameter name
    path('login/', 
         auth_views.LoginView.as_view(
             template_name='core/login.html',
             redirect_authenticated_user=True  # ✅ CORRECT PARAMETER NAME
         ), 
         name='login'),
    
    path('logout/', 
         auth_views.LogoutView.as_view(
             next_page='login',
             template_name='registration/logged_out.html'
         ), 
         name='logout'),
    
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html',
             success_url='/password_change/done/'
         ), 
         name='password_change'),
    
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html'
         ), 
         name='password_change_done'),
    
    # Your core app URLs
    path('', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)