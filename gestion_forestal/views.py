"""
Vistas de la API para el Geovisor de Costos Forestales v2.1.

Implementa la lógica de negocio para el cálculo de costos
de plantaciones forestales con:
- Smart Defaults
- Factor de Pendiente
- Factor de Densidad (geometría de siembra)
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from typing import Dict, List, Any

from .models import ZonaEconomica, Distrito, Cultivo, PaqueteTecnologico
from .serializers import (
    ZonaEconomicaSerializer,
    DistritoSerializer,
    CultivoSerializer,
    PaqueteTecnologicoSerializer,
    CalculoCostosInputSerializer,
    CalculoCostosOutputSerializer,
    SistemaSiembra,
    FACTOR_TRES_BOLILLO
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
    
    Filtros soportados:
    - ?departamento=San Martin
    - ?provincia=Tocache
    """
    
    queryset = Distrito.objects.select_related('zona_economica').all()
    serializer_class = DistritoSerializer
    lookup_field = 'cod_ubigeo'
    filterset_fields = ['departamento', 'provincia']
    ordering_fields = ['nombre', 'departamento', 'provincia']
    ordering = ['departamento', 'provincia', 'nombre']


class CultivoViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet para cultivos forestales (solo lectura)."""
    
    queryset = Cultivo.objects.all()
    serializer_class = CultivoSerializer


class PaqueteTecnologicoViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet para paquetes tecnológicos (solo lectura)."""
    
    queryset = PaqueteTecnologico.objects.select_related('cultivo').all()
    serializer_class = PaqueteTecnologicoSerializer
    filterset_fields = ['cultivo', 'anio_proyecto', 'rubro']


def calcular_plantas_por_hectarea(
    sistema_siembra: str,
    distanciamiento_largo: Decimal,
    distanciamiento_ancho: Decimal = None
) -> int:
    """
    Calcula el número de plantas por hectárea según la geometría de siembra.
    
    Fórmulas:
    - CUADRADO: plantas = 10,000 / (largo × largo)
    - RECTANGULAR: plantas = 10,000 / (largo × ancho)
    - TRES_BOLILLO: plantas = 10,000 / ((largo × largo) × 0.866025)
    
    Args:
        sistema_siembra: Tipo de geometría ('CUADRADO', 'RECTANGULAR', 'TRES_BOLILLO')
        distanciamiento_largo: Distancia entre plantas en metros
        distanciamiento_ancho: Distancia entre hileras (solo para RECTANGULAR)
    
    Returns:
        int: Número de plantas por hectárea (redondeado)
    """
    AREA_HECTAREA = Decimal('10000')  # 10,000 m² = 1 hectárea
    
    if sistema_siembra == SistemaSiembra.CUADRADO:
        # Cuadrado: distancia × distancia
        area_por_planta = distanciamiento_largo * distanciamiento_largo
        plantas = AREA_HECTAREA / area_por_planta
        
    elif sistema_siembra == SistemaSiembra.RECTANGULAR:
        # Rectangular: largo × ancho
        if distanciamiento_ancho is None or distanciamiento_ancho <= 0:
            raise ValueError("distanciamiento_ancho es requerido para sistema RECTANGULAR")
        area_por_planta = distanciamiento_largo * distanciamiento_ancho
        plantas = AREA_HECTAREA / area_por_planta
        
    elif sistema_siembra == SistemaSiembra.TRES_BOLILLO:
        # Tres Bolillo: (largo × largo) × sin(60°)
        # sin(60°) = √3/2 ≈ 0.866025
        area_por_planta = distanciamiento_largo * distanciamiento_largo * FACTOR_TRES_BOLILLO
        plantas = AREA_HECTAREA / area_por_planta
        
    else:
        raise ValueError(f"Sistema de siembra no reconocido: {sistema_siembra}")
    
    # Redondear al entero más cercano
    return int(plantas.quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def calcular_factor_densidad(
    densidad_base: int,
    densidad_usuario: int
) -> Decimal:
    """
    Calcula el factor de densidad.
    
    factor = plantas_usuario / densidad_base
    
    Si el usuario elige más plantas que el estándar, el factor > 1
    y los costos sensibles a densidad aumentan proporcionalmente.
    
    Args:
        densidad_base: Densidad estándar del cultivo (plantas/ha)
        densidad_usuario: Densidad calculada del usuario (plantas/ha)
    
    Returns:
        Decimal: Factor de densidad (ej: 1.2500 si 25% más plantas)
    """
    if densidad_base <= 0:
        return Decimal('1.0000')
    
    factor = Decimal(densidad_usuario) / Decimal(densidad_base)
    return factor.quantize(Decimal('0.0001'))


class CalcularCostosView(APIView):
    """
    Endpoint principal para calcular costos de plantación forestal.
    
    POST /api/calcular-costos/
    
    Implementa la lógica de negocio v2.1:
    - Factor de Pendiente: ajusta mano de obra según topografía
    - Factor de Densidad: ajusta costos según geometría de siembra
    - Smart Defaults: el usuario define sus propios costos
    """
    
    def post(self, request) -> Response:
        """
        Calcula los costos totales de una plantación forestal.
        
        Args:
            request: Request con distrito_id, cultivo_id, hectareas,
                    costos del usuario, geometría de siembra, y rango de años.
        
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
        
        # Parámetros de geometría de siembra
        sistema_siembra = data['sistema_siembra']
        dist_largo = data['distanciamiento_largo']
        dist_ancho = data.get('distanciamiento_ancho')
        
        # ===========================================
        # CÁLCULO DE FACTORES
        # ===========================================
        
        # Factor de Pendiente (según topografía del distrito)
        factor_pendiente = distrito.calcular_factor_pendiente()
        
        # Factor de Densidad (según geometría de siembra del usuario)
        densidad_base = cultivo.densidad_base
        densidad_usuario = calcular_plantas_por_hectarea(
            sistema_siembra=sistema_siembra,
            distanciamiento_largo=dist_largo,
            distanciamiento_ancho=dist_ancho
        )
        factor_densidad = calcular_factor_densidad(densidad_base, densidad_usuario)
        
        # ===========================================
        # OBTENER ACTIVIDADES
        # ===========================================
        
        actividades = PaqueteTecnologico.objects.filter(
            cultivo=cultivo,
            anio_proyecto__gte=anio_inicio,
            anio_proyecto__lte=anio_fin
        ).order_by('anio_proyecto', 'rubro', 'actividad')
        
        # ===========================================
        # CÁLCULO DE COSTOS
        # ===========================================
        
        detalle_actividades = []
        resumen_por_anio: Dict[int, Dict[str, Decimal]] = defaultdict(
            lambda: {'mano_obra': Decimal('0'), 'insumos': Decimal('0'), 'servicios': Decimal('0')}
        )
        
        for actividad in actividades:
            # Cantidad base por hectárea
            cantidad_base = actividad.cantidad_tecnica * hectareas
            cantidad_ajustada = cantidad_base
            
            # 1. Aplicar Factor de Densidad (si aplica)
            if actividad.sensible_densidad:
                cantidad_ajustada = cantidad_ajustada * factor_densidad
            
            # 2. Aplicar Factor de Pendiente (si aplica, solo para mano de obra)
            if actividad.sensible_pendiente and actividad.rubro == PaqueteTecnologico.Rubro.MANO_OBRA:
                cantidad_ajustada = cantidad_ajustada * factor_pendiente
            
            # 3. Determinar costo unitario según rubro
            if actividad.rubro == PaqueteTecnologico.Rubro.MANO_OBRA:
                costo_unitario = costo_jornal
                categoria_resumen = 'mano_obra'
                
            elif actividad.rubro == PaqueteTecnologico.Rubro.INSUMO:
                if actividad.es_planton:
                    costo_unitario = costo_planton
                else:
                    costo_unitario = actividad.costo_unitario_referencial
                categoria_resumen = 'insumos'
                
            elif actividad.rubro in [
                PaqueteTecnologico.Rubro.SERVICIOS,
                PaqueteTecnologico.Rubro.LEGAL,
                PaqueteTecnologico.Rubro.ACTIVO
            ]:
                costo_unitario = actividad.costo_unitario_referencial
                categoria_resumen = 'servicios'
            else:
                costo_unitario = actividad.costo_unitario_referencial
                categoria_resumen = 'servicios'
            
            # 4. Calcular costo total de la actividad
            costo_total = (cantidad_ajustada * costo_unitario).quantize(Decimal('0.01'))
            
            # Agregar al detalle
            detalle_actividades.append({
                'anio': actividad.anio_proyecto,
                'rubro': actividad.get_rubro_display(),
                'actividad': actividad.actividad,
                'cantidad_base': cantidad_base.quantize(Decimal('0.01')),
                'cantidad_ajustada': cantidad_ajustada.quantize(Decimal('0.01')),
                'costo_unitario': costo_unitario,
                'costo_total': costo_total
            })
            
            # Agregar al resumen anual
            resumen_por_anio[actividad.anio_proyecto][categoria_resumen] += costo_total
        
        # ===========================================
        # CONSTRUIR RESUMEN ANUAL
        # ===========================================
        
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
        
        # ===========================================
        # CONSTRUIR RESPUESTA
        # ===========================================
        
        output = {
            'distrito': f"{distrito.nombre} ({distrito.cod_ubigeo})",
            'cultivo': cultivo.nombre,
            'hectareas': hectareas,
            'factor_pendiente': factor_pendiente,
            'factor_densidad': factor_densidad,
            'densidad_base': densidad_base,
            'densidad_usuario': densidad_usuario,
            'sistema_siembra': sistema_siembra,
            'costo_jornal_usado': costo_jornal,
            'costo_planton_usado': costo_planton,
            'detalle_actividades': detalle_actividades,
            'resumen_anual': resumen_anual,
            'costo_total_proyecto': costo_total_proyecto
        }
        
        output_serializer = CalculoCostosOutputSerializer(output)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
