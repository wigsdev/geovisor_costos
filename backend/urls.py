"""
URL configuration for backend project.

Define las rutas principales del proyecto Geovisor.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('gestion_forestal.urls')),
]
