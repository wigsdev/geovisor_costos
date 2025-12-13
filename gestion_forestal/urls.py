"""
URLs de la API para la aplicación gestion_forestal.

Define los endpoints para acceder a los recursos del geovisor.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ZonaEconomicaViewSet,
    DistritoViewSet,
    CultivoViewSet,
    PaqueteTecnologicoViewSet,
    CalcularCostosView
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'zonas', ZonaEconomicaViewSet, basename='zona')
router.register(r'distritos', DistritoViewSet, basename='distrito')
router.register(r'cultivos', CultivoViewSet, basename='cultivo')
router.register(r'paquetes', PaqueteTecnologicoViewSet, basename='paquete')

urlpatterns = [
    # Endpoints REST
    path('', include(router.urls)),
    
    # Endpoint de cálculo de costos
    path('calcular-costos/', CalcularCostosView.as_view(), name='calcular-costos'),
]
