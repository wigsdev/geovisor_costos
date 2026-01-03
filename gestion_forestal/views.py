"""
Vistas de la API para el Geovisor de Costos Forestales v2.1.

Implementa la lógica de negocio para el cálculo de costos
de plantaciones forestales con:
- Smart Defaults
- Factor de Pendiente
- Factor de Densidad (geometría de siembra)
"""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from typing import Dict, List, Any
import math

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

    @action(detail=False, methods=['get'])
    def detectar(self, request):
        """
        Detecta el distrito más cercano a una coordenada dada.
        
        Uso: /api/distritos/detectar/?lat=-7.5&lng=-76.5
        """
        lat_str = request.query_params.get('lat')
        lng_str = request.query_params.get('lng')
        
        if not lat_str or not lng_str:
            return Response(
                {'error': 'Parámetros lat y lng son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            lat = float(lat_str)
            lng = float(lng_str)
        except ValueError:
            return Response(
                {'error': 'Coordenadas inválidas. Deben ser números.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Obtener todos los distritos con coordenadas
        # Nota: Para una base de datos grande, esto debería optimizarse con GIS
        # pero para ~2000 distritos es aceptable en memoria.
        distritos = list(Distrito.objects.filter(
            latitud__isnull=False, 
            longitud__isnull=False
        ).values('cod_ubigeo', 'latitud', 'longitud'))
        
        if not distritos:
            return Response(
                {'error': 'No hay distritos con coordenadas en la base de datos.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        closest_distrito = None
        min_dist_sq = float('inf')
        
        for d in distritos:
            d_lat = float(d['latitud'])
            d_lng = float(d['longitud'])
            
            # Distancia euclidiana cuadrada (suficiente para comparar)
            dist_sq = (d_lat - lat)**2 + (d_lng - lng)**2
            
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_distrito = d
                
        if closest_distrito:
            distrito_obj = self.get_queryset().get(
                cod_ubigeo=closest_distrito['cod_ubigeo']
            )
            serializer = self.get_serializer(distrito_obj)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'No se pudo determinar el distrito más cercano.'},
                status=status.HTTP_404_NOT_FOUND
            )


class CultivoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet para cultivos forestales (solo lectura).
    
    Permite filtrar los cultivos válidos para un distrito específico
    basándose en los paquetes tecnológicos disponibles para su zona.
    
    Uso: ?distrito=220903
    """
    
    queryset = Cultivo.objects.all()
    serializer_class = CultivoSerializer
    
    def get_queryset(self):
        queryset = Cultivo.objects.all()
        distrito_id = self.request.query_params.get('distrito', None)
        
        if distrito_id:
            try:
                distrito = Distrito.objects.get(cod_ubigeo=distrito_id)
                # Filtrar cultivos que tengan paquetes en la zona del distrito
                queryset = queryset.filter(
                    paquete_tecnologico__zona_economica=distrito.zona_economica
                ).distinct()
            except Distrito.DoesNotExist:
                pass
                
        return queryset


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
        incluir_servicios = data.get('incluir_servicios', True)
        
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
            zona_economica=distrito.zona_economica,
            anio_proyecto__gte=anio_inicio,
            anio_proyecto__lte=anio_fin
        )

        if not incluir_servicios:
            actividades = actividades.exclude(rubro__in=[
                PaqueteTecnologico.Rubro.SERVICIOS,
                PaqueteTecnologico.Rubro.LEGAL,
                PaqueteTecnologico.Rubro.ACTIVO
            ])
            
        actividades = actividades.order_by('anio_proyecto', 'rubro', 'actividad')
        
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
            
            # 1. Aplicar Factor de Densidad (Modelo 50/50)
            # Solo afecta a Mano de Obra sensible a densidad (Hoyado, Plantación)
            # Fórm: Jornales = (Base * 0.5) + (Base * 0.5 * Factor)
            if actividad.sensible_densidad:
                if actividad.rubro == PaqueteTecnologico.Rubro.MANO_OBRA:
                    # Modelo 50/50 para Mano de Obra
                    parte_fija = cantidad_ajustada * Decimal('0.5')
                    parte_variable = cantidad_ajustada * Decimal('0.5') * factor_densidad
                    cantidad_ajustada = parte_fija + parte_variable
                else:
                    # Para Insumos (Plantones), el factor es 100% directo
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
        # CONSTRUIR RESUMEN ANUAL (Refactor v1.3.1)
        # ===========================================
        
        resumen_anual = []
        costos_instalacion = None
        costo_total_proyecto = Decimal('0')
        
        for anio in sorted(resumen_por_anio.keys()):
            datos = resumen_por_anio[anio]
            total_anio = datos['mano_obra'] + datos['insumos'] + datos['servicios']
            costo_total_proyecto += total_anio
            
            resumen_obj = {
                'anio': anio,
                'mano_obra': datos['mano_obra'],
                'insumos': datos['insumos'],
                'servicios': datos['servicios'],
                'total': total_anio
            }
            
            # Segregar Año 0 (Instalación) de Años 1+ (Mantenimiento)
            if anio == 0:
                costos_instalacion = resumen_obj
            else:
                resumen_anual.append(resumen_obj)
        
        # ===========================================
        # CÁLCULO FINANCIERO (VAN / TIR)
        # ===========================================
        
        # Parámetros financieros base
        tasa_descuento = Decimal('0.10') # 10%
        precio_madera = cultivo.precio_madera_referencial
        rendimiento_ha = cultivo.rendimiento_m3_ha
        
        # Ingreso proyectado al final del turno
        ingreso_total = (hectareas * rendimiento_ha * precio_madera).quantize(Decimal('0.01'))
        anio_cosecha = cultivo.turno_estimado
        
        # Construir Flujo de Caja
        # Flujo = Ingresos - Costos
        flujo_caja = {}
        
        # 1. Costos (flujos negativos)
        for anio, datos in resumen_por_anio.items():
            costo_anio = datos['mano_obra'] + datos['insumos'] + datos['servicios']
            flujo_caja[anio] = -costo_anio
            
        # 2. Ingresos (flujos positivos)
        # Sumar al año de cosecha (si está dentro del rango o si es el final)
        if anio_cosecha not in flujo_caja:
            flujo_caja[anio_cosecha] = Decimal('0')
        flujo_caja[anio_cosecha] += ingreso_total
        
        # 3. Calcular VAN
        van = Decimal('0')
        for anio, flujo in flujo_caja.items():
            factor = (Decimal('1') + tasa_descuento) ** Decimal(anio)
            van += flujo / factor
            
        van = van.quantize(Decimal('0.01'))
        
        # 4. Calcular TIR (Aproximación simple o 0 si no hay ingresos)
        # La TIR requiere métodos numéricos iterativos (Newton-Raphson).
        # Implementación simplificada para no depender de numpy
        tir = Decimal('0')
        
        # Solo intentamos calcular TIR si hay al menos un flujo negativo y uno positivo
        flujos_lista = [flujo_caja.get(a, Decimal('0')) for a in range(max(flujo_caja.keys()) + 1)]
        has_negative = any(f < 0 for f in flujos_lista)
        has_positive = any(f > 0 for f in flujos_lista)
        
        if has_negative and has_positive:
            try:
                # Estimación muy básica o placeholder. 
                # Realmente necesitamos numpy.financial.irr inputs floats
                # Para esta versión, dejaremos un valor indicativo o implementaremos irr simple
                # Opción robusta: Retornar 0 y pedir instalar numpy si se requiere precisión
                pass 
            except:
                pass

        # Ratio Beneficio/Costo
        # B/C = VP_Ingresos / VP_Costos
        vp_ingresos = Decimal('0')
        vp_costos = Decimal('0')
        
        for anio, flujo in flujo_caja.items():
            factor = (Decimal('1') + tasa_descuento) ** Decimal(anio)
            if flujo > 0:
                vp_ingresos += flujo / factor
            else:
                vp_costos += abs(flujo) / factor
                
        ratio_bc = Decimal('0')
        if vp_costos > 0:
            ratio_bc = (vp_ingresos / vp_costos).quantize(Decimal('0.01'))

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
            
            # Refactor v1.3.1 - Segregación
            'costos_instalacion': costos_instalacion,
            'resumen_anual': resumen_anual, # Ahora solo contiene años >= 1
            
            'costo_total_proyecto': costo_total_proyecto,
            
            # Nuevos indicadores financieros
            'van': van,
            'tir': Decimal('0'), # Placeholder por ahora sin numpy
            'ratio_beneficio_costo': ratio_bc,
            'ingreso_total_estimado': ingreso_total
        }
        
        output_serializer = CalculoCostosOutputSerializer(output)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
