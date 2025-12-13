"""
Vistas de la API para el Geovisor de Costos Forestales v2.0.

Implementa la lógica de negocio para el cálculo de costos
de plantaciones forestales con Smart Defaults.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal
from collections import defaultdict
from typing import Dict, List, Any

from .models import ZonaEconomica, Distrito, Cultivo, PaqueteTecnologico
from .serializers import (
    ZonaEconomicaSerializer,
    DistritoSerializer,
    CultivoSerializer,
    PaqueteTecnologicoSerializer,
    CalculoCostosInputSerializer,
    CalculoCostosOutputSerializer
)


class ZonaEconomicaViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet para zonas económicas (solo lectura)."""
    
    queryset = ZonaEconomica.objects.all()
    serializer_class = ZonaEconomicaSerializer


class DistritoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet para distritos (solo lectura).
    
    Incluye los costos referenciales de la zona económica
    para implementar Smart Defaults en el frontend.
    """
    
    queryset = Distrito.objects.select_related('zona_economica').all()
    serializer_class = DistritoSerializer
    lookup_field = 'cod_ubigeo'


class CultivoViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet para cultivos forestales (solo lectura)."""
    
    queryset = Cultivo.objects.all()
    serializer_class = CultivoSerializer


class PaqueteTecnologicoViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet para paquetes tecnológicos (solo lectura)."""
    
    queryset = PaqueteTecnologico.objects.select_related('cultivo').all()
    serializer_class = PaqueteTecnologicoSerializer
    filterset_fields = ['cultivo', 'anio_proyecto', 'rubro']


class CalcularCostosView(APIView):
    """
    Endpoint principal para calcular costos de plantación forestal.
    
    POST /api/calcular-costos/
    
    Implementa la lógica de negocio v2.0:
    - MANO_OBRA: usa costo_jornal_usuario * cantidad * factor_pendiente
    - INSUMO (plantones): usa costo_planton_usuario * cantidad
    - INSUMO (otros) / SERVICIOS: usa costo_unitario_referencial * cantidad
    """
    
    def post(self, request) -> Response:
        """
        Calcula los costos totales de una plantación forestal.
        
        Args:
            request: Request con distrito_id, cultivo_id, hectareas,
                    costo_jornal_usuario, costo_planton_usuario,
                    anio_inicio, anio_fin.
        
        Returns:
            Response: Detalle de costos por actividad y resúmenes anuales.
        """
        # Validar input
        input_serializer = CalculoCostosInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(
                input_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = input_serializer.validated_data
        
        # Obtener objetos de la base de datos
        try:
            distrito = Distrito.objects.select_related('zona_economica').get(
                cod_ubigeo=data['distrito_id']
            )
        except Distrito.DoesNotExist:
            return Response(
                {'error': f"Distrito con UBIGEO {data['distrito_id']} no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            cultivo = Cultivo.objects.get(id=data['cultivo_id'])
        except Cultivo.DoesNotExist:
            return Response(
                {'error': f"Cultivo con ID {data['cultivo_id']} no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Extraer parámetros del request
        hectareas = data['hectareas']
        costo_jornal = data['costo_jornal_usuario']
        costo_planton = data['costo_planton_usuario']
        anio_inicio = data['anio_inicio']
        anio_fin = data['anio_fin']
        
        # Calcular factor de pendiente
        factor_pendiente = distrito.calcular_factor_pendiente()
        
        # Obtener actividades del paquete tecnológico
        actividades = PaqueteTecnologico.objects.filter(
            cultivo=cultivo,
            anio_proyecto__gte=anio_inicio,
            anio_proyecto__lte=anio_fin
        ).order_by('anio_proyecto', 'rubro', 'actividad')
        
        # Calcular costos
        detalle_actividades = []
        resumen_por_anio: Dict[int, Dict[str, Decimal]] = defaultdict(
            lambda: {'mano_obra': Decimal('0'), 'insumos': Decimal('0'), 'servicios': Decimal('0')}
        )
        
        for actividad in actividades:
            # Cantidad base por hectárea
            cantidad_base = actividad.cantidad_tecnica * hectareas
            cantidad_ajustada = cantidad_base
            
            # Determinar costo unitario según rubro
            if actividad.rubro == PaqueteTecnologico.Rubro.MANO_OBRA:
                # Mano de obra usa el jornal del usuario
                costo_unitario = costo_jornal
                
                # Aplicar factor pendiente si es sensible
                if actividad.sensible_pendiente:
                    cantidad_ajustada = cantidad_base * factor_pendiente
                
                categoria_resumen = 'mano_obra'
                
            elif actividad.rubro == PaqueteTecnologico.Rubro.INSUMO:
                if actividad.es_planton:
                    # Plantones usan el precio del usuario
                    costo_unitario = costo_planton
                else:
                    # Otros insumos usan el precio referencial de BD
                    costo_unitario = actividad.costo_unitario_referencial
                
                categoria_resumen = 'insumos'
                
            elif actividad.rubro in [
                PaqueteTecnologico.Rubro.SERVICIOS,
                PaqueteTecnologico.Rubro.LEGAL,
                PaqueteTecnologico.Rubro.ACTIVO
            ]:
                # Servicios y otros usan precio referencial
                costo_unitario = actividad.costo_unitario_referencial
                categoria_resumen = 'servicios'
            else:
                # Por defecto
                costo_unitario = actividad.costo_unitario_referencial
                categoria_resumen = 'servicios'
            
            # Calcular costo total de la actividad
            costo_total = (cantidad_ajustada * costo_unitario).quantize(Decimal('0.01'))
            
            # Agregar al detalle
            detalle_actividades.append({
                'anio': actividad.anio_proyecto,
                'rubro': actividad.get_rubro_display(),
                'actividad': actividad.actividad,
                'cantidad_base': cantidad_base,
                'cantidad_ajustada': cantidad_ajustada,
                'costo_unitario': costo_unitario,
                'costo_total': costo_total
            })
            
            # Agregar al resumen anual
            resumen_por_anio[actividad.anio_proyecto][categoria_resumen] += costo_total
        
        # Construir resumen anual
        resumen_anual = []
        costo_total_proyecto = Decimal('0')
        
        for anio in sorted(resumen_por_anio.keys()):
            datos = resumen_por_anio[anio]
            total_anio = datos['mano_obra'] + datos['insumos'] + datos['servicios']
            costo_total_proyecto += total_anio
            
            resumen_anual.append({
                'anio': anio,
                'mano_obra': datos['mano_obra'],
                'insumos': datos['insumos'],
                'servicios': datos['servicios'],
                'total': total_anio
            })
        
        # Construir respuesta
        output = {
            'distrito': f"{distrito.nombre} ({distrito.cod_ubigeo})",
            'cultivo': cultivo.nombre,
            'hectareas': hectareas,
            'factor_pendiente': factor_pendiente,
            'costo_jornal_usado': costo_jornal,
            'costo_planton_usado': costo_planton,
            'detalle_actividades': detalle_actividades,
            'resumen_anual': resumen_anual,
            'costo_total_proyecto': costo_total_proyecto
        }
        
        output_serializer = CalculoCostosOutputSerializer(output)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
