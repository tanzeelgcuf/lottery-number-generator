"""
URL configuration for lottery_generator project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('generator.urls')),  # Fixed: was 'lottery_generator.urls'
]
