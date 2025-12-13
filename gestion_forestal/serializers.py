"""
Serializadores para la API del Geovisor de Costos Forestales v2.1.

Implementa Smart Defaults y Factor de Densidad basado en
geometría de siembra (Cuadrado, Rectangular, Tres Bolillo).
"""

from rest_framework import serializers
from decimal import Decimal
from .models import ZonaEconomica, Distrito, Cultivo, PaqueteTecnologico


class ZonaEconomicaSerializer(serializers.ModelSerializer):
    """Serializador para zonas económicas."""
    
    class Meta:
        model = ZonaEconomica
        fields = [
            'id',
            'nombre',
            'costo_jornal_referencial',
            'costo_planton_referencial'
        ]


class DistritoSerializer(serializers.ModelSerializer):
    """
    Serializador de Distrito con Smart Defaults.
    
    Incluye los costos referenciales de la zona económica
    para que el frontend pueda mostrarlos como sugerencia.
    """
    
    zona_economica_nombre = serializers.CharField(
        source='zona_economica.nombre',
        read_only=True
    )
    costo_jornal_sugerido = serializers.DecimalField(
        source='zona_economica.costo_jornal_referencial',
        max_digits=8,
        decimal_places=2,
        read_only=True
    )
    costo_planton_sugerido = serializers.DecimalField(
        source='zona_economica.costo_planton_referencial',
        max_digits=8,
        decimal_places=2,
        read_only=True
    )
    factor_pendiente = serializers.SerializerMethodField()
    
    class Meta:
        model = Distrito
        fields = [
            'cod_ubigeo',
            'nombre',
            'zona_economica',
            'zona_economica_nombre',
            'latitud',
            'longitud',
            'pendiente_promedio_estimada',
            'factor_pendiente',
            'costo_jornal_sugerido',
            'costo_planton_sugerido'
        ]
    
    def get_factor_pendiente(self, obj: Distrito) -> str:
        """Retorna el factor de pendiente calculado."""
        return str(obj.calcular_factor_pendiente())


class CultivoSerializer(serializers.ModelSerializer):
    """Serializador para cultivos forestales."""
    
    class Meta:
        model = Cultivo
        fields = [
            'id',
            'nombre',
            'turno_estimado',
            'densidad_base'
        ]


class PaqueteTecnologicoSerializer(serializers.ModelSerializer):
    """Serializador para paquetes tecnológicos."""
    
    cultivo_nombre = serializers.CharField(
        source='cultivo.nombre',
        read_only=True
    )
    rubro_display = serializers.CharField(
        source='get_rubro_display',
        read_only=True
    )
    
    class Meta:
        model = PaqueteTecnologico
        fields = [
            'id',
            'cultivo',
            'cultivo_nombre',
            'anio_proyecto',
            'rubro',
            'rubro_display',
            'actividad',
            'unidad_medida',
            'cantidad_tecnica',
            'sensible_pendiente',
            'sensible_densidad',
            'costo_unitario_referencial',
            'es_planton'
        ]


# ===========================================
# CONSTANTES PARA CÁLCULO DE DENSIDAD
# ===========================================

class SistemaSiembra:
    """Opciones de sistema de siembra."""
    CUADRADO = 'CUADRADO'
    RECTANGULAR = 'RECTANGULAR'
    TRES_BOLILLO = 'TRES_BOLILLO'
    
    CHOICES = [
        (CUADRADO, 'Cuadrado (distancia×distancia)'),
        (RECTANGULAR, 'Rectangular (largo×ancho)'),
        (TRES_BOLILLO, 'Tres Bolillo (triángulo equilátero)'),
    ]


# Factor para Tres Bolillo: sin(60°) = sqrt(3)/2 ≈ 0.866025
FACTOR_TRES_BOLILLO = Decimal('0.866025')


class CalculoCostosInputSerializer(serializers.Serializer):
    """
    Serializador para el input del endpoint de cálculo de costos.
    
    Valida los datos enviados por el usuario incluyendo los
    costos editados y la configuración de geometría de siembra.
    """
    
    # Campos básicos
    distrito_id = serializers.CharField(
        max_length=6,
        help_text="Código UBIGEO del distrito"
    )
    cultivo_id = serializers.IntegerField(
        help_text="ID del cultivo seleccionado"
    )
    hectareas = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        help_text="Número de hectáreas a cultivar"
    )
    
    # Costos definidos por usuario (Smart Defaults editables)
    costo_jornal_usuario = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=Decimal('1.00'),
        help_text="Costo del jornal definido por el usuario (S/)"
    )
    costo_planton_usuario = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=Decimal('0.01'),
        help_text="Costo del plantón definido por el usuario (S/)"
    )
    
    # Rango de años
    anio_inicio = serializers.IntegerField(
        default=0,
        min_value=0,
        help_text="Año inicial del cálculo (0 = instalación)"
    )
    anio_fin = serializers.IntegerField(
        min_value=0,
        help_text="Año final del cálculo"
    )
    
    # Geometría de siembra (Factor de Densidad)
    sistema_siembra = serializers.ChoiceField(
        choices=SistemaSiembra.CHOICES,
        default=SistemaSiembra.CUADRADO,
        help_text="Geometría de plantación"
    )
    distanciamiento_largo = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.50'),
        max_value=Decimal('20.00'),
        help_text="Distancia entre plantas (metros)"
    )
    distanciamiento_ancho = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('20.00'),
        required=False,
        allow_null=True,
        default=None,
        help_text="Distancia entre hileras (metros). Solo para RECTANGULAR."
    )
    
    def validate(self, data):
        """
        Valida los datos del request.
        
        - anio_fin >= anio_inicio
        - Si es RECTANGULAR, distanciamiento_ancho es requerido y > 0
        """
        # Validar rango de años
        if data['anio_fin'] < data['anio_inicio']:
            raise serializers.ValidationError({
                'anio_fin': 'El año final debe ser mayor o igual al año inicial.'
            })
        
        # Validar distanciamiento para sistema rectangular
        if data['sistema_siembra'] == SistemaSiembra.RECTANGULAR:
            ancho = data.get('distanciamiento_ancho')
            if ancho is None or ancho <= Decimal('0'):
                raise serializers.ValidationError({
                    'distanciamiento_ancho': 'Requerido y debe ser > 0 para sistema RECTANGULAR.'
                })
        
        return data


class ActividadCostoSerializer(serializers.Serializer):
    """Serializador para una actividad con su costo calculado."""
    
    anio = serializers.IntegerField()
    rubro = serializers.CharField()
    actividad = serializers.CharField()
    cantidad_base = serializers.DecimalField(max_digits=10, decimal_places=2)
    cantidad_ajustada = serializers.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)
    costo_total = serializers.DecimalField(max_digits=12, decimal_places=2)


class ResumenAnualSerializer(serializers.Serializer):
    """Serializador para el resumen de costos por año."""
    
    anio = serializers.IntegerField()
    mano_obra = serializers.DecimalField(max_digits=12, decimal_places=2)
    insumos = serializers.DecimalField(max_digits=12, decimal_places=2)
    servicios = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class CalculoCostosOutputSerializer(serializers.Serializer):
    """
    Serializador para el output del cálculo de costos.
    
    Retorna el detalle de costos por actividad, factores aplicados
    y resúmenes anuales.
    """
    
    # Identificación
    distrito = serializers.CharField()
    cultivo = serializers.CharField()
    hectareas = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Factores aplicados
    factor_pendiente = serializers.DecimalField(max_digits=4, decimal_places=2)
    factor_densidad = serializers.DecimalField(max_digits=6, decimal_places=4)
    
    # Densidades
    densidad_base = serializers.IntegerField()
    densidad_usuario = serializers.IntegerField()
    sistema_siembra = serializers.CharField()
    
    # Costos usados
    costo_jornal_usado = serializers.DecimalField(max_digits=8, decimal_places=2)
    costo_planton_usado = serializers.DecimalField(max_digits=8, decimal_places=2)
    
    # Detalle y resúmenes
    detalle_actividades = ActividadCostoSerializer(many=True)
    resumen_anual = ResumenAnualSerializer(many=True)
    costo_total_proyecto = serializers.DecimalField(max_digits=14, decimal_places=2)
