"""
Configuración del panel de administración para Gestion Forestal v2.0.

Registra los modelos con configuración optimizada para la gestión
de datos del geovisor de costos forestales.
"""

from django.contrib import admin
from .models import ZonaEconomica, Distrito, Cultivo, PaqueteTecnologico


@admin.register(ZonaEconomica)
class ZonaEconomicaAdmin(admin.ModelAdmin):
    """Administración de zonas económicas."""
    
    list_display = ['nombre', 'costo_jornal_referencial', 'costo_planton_referencial']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(Distrito)
class DistritoAdmin(admin.ModelAdmin):
    """Administración de distritos."""
    
    list_display = [
        'cod_ubigeo', 
        'nombre', 
        'zona_economica',
        'pendiente_promedio_estimada',
        'latitud',
        'longitud'
    ]
    list_filter = ['zona_economica', 'pendiente_promedio_estimada']
    search_fields = ['cod_ubigeo', 'nombre']
    ordering = ['nombre']
    autocomplete_fields = ['zona_economica']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('cod_ubigeo', 'nombre')
        }),
        ('Clasificación Económica', {
            'fields': ('zona_economica',)
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud'),
            'description': 'Coordenadas para visualización en mapa'
        }),
        ('Parámetros de Cálculo', {
            'fields': ('pendiente_promedio_estimada',),
            'description': 'Afecta el factor de pendiente en cálculos'
        }),
    )


@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    """Administración de cultivos forestales."""
    
    list_display = ['nombre', 'turno_estimado', 'densidad_base']
    search_fields = ['nombre']
    ordering = ['nombre']


@admin.register(PaqueteTecnologico)
class PaqueteTecnologicoAdmin(admin.ModelAdmin):
    """Administración de paquetes tecnológicos."""
    
    list_display = [
        'cultivo', 
        'anio_proyecto', 
        'rubro', 
        'actividad', 
        'cantidad_tecnica',
        'unidad_medida',
        'sensible_pendiente',
        'sensible_densidad',
        'es_planton'
    ]
    list_filter = [
        'cultivo', 
        'anio_proyecto', 
        'rubro', 
        'sensible_pendiente',
        'sensible_densidad',
        'es_planton'
    ]
    search_fields = ['actividad', 'cultivo__nombre']
    ordering = ['cultivo', 'anio_proyecto', 'rubro']
    autocomplete_fields = ['cultivo']
    
    fieldsets = (
        ('Cultivo y Temporalidad', {
            'fields': ('cultivo', 'anio_proyecto')
        }),
        ('Detalle de Actividad', {
            'fields': ('rubro', 'actividad', 'unidad_medida')
        }),
        ('Cantidad y Costo', {
            'fields': ('cantidad_tecnica', 'costo_unitario_referencial')
        }),
        ('Ajustes de Cálculo', {
            'fields': ('sensible_pendiente', 'sensible_densidad', 'es_planton'),
            'description': 'Determina cómo se calcula el costo final (pendiente y densidad)'
        }),
    )
