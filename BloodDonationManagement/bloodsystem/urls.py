"""
URL configuration for bloodsystem project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mainapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-donor/', views.add_donor, name='add_donor'),
    path('donors/', views.donor_list, name='donor_list'),
    path('edit-donor/<int:id>/', views.edit_donor, name='edit_donor'),
    path('delete-donor/<int:id>/', views.delete_donor, name='delete_donor'),
    path('request-blood/', views.request_blood, name='request_blood'),
    path('requests/', views.request_list, name='request_list'),
    path('approve-request/<int:id>/', views.approve_request, name='approve_request'),
    path('delete-request/<int:id>/', views.delete_request, name='delete_request'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
