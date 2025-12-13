"""
Configuración del panel de administración para Gestion Forestal.

Registra los modelos para permitir la gestión desde el admin de Django.
"""

from django.contrib import admin
from .models import ZonaEconomica, Distrito, Cultivo, PaqueteTecnologico


@admin.register(ZonaEconomica)
class ZonaEconomicaAdmin(admin.ModelAdmin):
    """Administración de zonas económicas."""
    
    list_display = ['nombre', 'costo_jornal_base', 'factor_flete']
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
        'factor_acceso_temporal'
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
        ('Parámetros de Cálculo', {
            'fields': ('pendiente_promedio_estimada', 'factor_acceso_temporal'),
            'description': 'Parámetros para el cálculo de costos'
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
        'costo_unitario',
        'sensible_pendiente'
    ]
    list_filter = [
        'cultivo', 
        'anio_proyecto', 
        'rubro', 
        'sensible_pendiente',
        'es_recalce'
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
        ('Costos', {
            'fields': ('cantidad_tecnica', 'costo_unitario')
        }),
        ('Ajustes', {
            'fields': ('sensible_pendiente', 'es_recalce'),
            'description': 'Factores que afectan el cálculo de costos'
        }),
    )
