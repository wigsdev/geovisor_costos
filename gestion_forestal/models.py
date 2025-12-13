"""
Modelos de datos para el Geovisor de Costos Forestales v2.0.

Define la estructura de la base de datos para el cálculo
de costos de inversión en plantaciones forestales comerciales.

VERSIÓN 2.0: Arquitectura simplificada con "Smart Defaults".
- Sin dependencias de GeoDjango/GDAL
- Coordenadas como DecimalField
- Precios referenciales que el usuario puede editar
"""

from django.db import models
from decimal import Decimal
from typing import Optional


class ZonaEconomica(models.Model):
    """
    Agrupa distritos con costos laborales y de insumos similares.
    
    Proporciona valores referenciales (Smart Defaults) que el
    frontend mostrará al usuario para su validación.
    
    Attributes:
        nombre: Nombre descriptivo de la zona (ej: "Selva Alta").
        costo_jornal_referencial: Costo sugerido del día de trabajo (S/).
        costo_planton_referencial: Costo sugerido por plantón (S/).
    """
    
    nombre: str = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la zona"
    )
    costo_jornal_referencial: Decimal = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Costo jornal referencial (S/)",
        help_text="Valor sugerido para el frontend"
    )
    costo_planton_referencial: Decimal = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.50'),
        verbose_name="Costo plantón referencial (S/)",
        help_text="Valor sugerido para el frontend"
    )
    
    class Meta:
        verbose_name = "Zona Económica"
        verbose_name_plural = "Zonas Económicas"
        ordering = ['nombre']
    
    def __str__(self) -> str:
        return f"{self.nombre} (Jornal: S/ {self.costo_jornal_referencial})"


class Distrito(models.Model):
    """
    Unidad administrativa mínima del Perú.
    
    Cada distrito pertenece a una zona económica que sugiere
    precios referenciales. Incluye coordenadas para visualización
    en mapa y pendiente estimada para cálculos.
    
    Attributes:
        cod_ubigeo: Código oficial INEI de 6 dígitos (PK).
        nombre: Nombre del distrito.
        zona_economica: Zona económica a la que pertenece.
        latitud: Coordenada para marcador en mapa.
        longitud: Coordenada para marcador en mapa.
        pendiente_promedio_estimada: Pendiente promedio en % para cálculos.
    """
    
    cod_ubigeo: str = models.CharField(
        max_length=6,
        primary_key=True,
        verbose_name="Código UBIGEO"
    )
    nombre: str = models.CharField(
        max_length=100,
        verbose_name="Nombre del distrito"
    )
    zona_economica = models.ForeignKey(
        ZonaEconomica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='distritos',
        verbose_name="Zona económica"
    )
    latitud: Decimal = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Latitud",
        help_text="Coordenada para marcador visual en mapa"
    )
    longitud: Decimal = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name="Longitud",
        help_text="Coordenada para marcador visual en mapa"
    )
    pendiente_promedio_estimada: int = models.PositiveSmallIntegerField(
        default=15,
        verbose_name="Pendiente promedio (%)",
        help_text="Pendiente promedio estimada del terreno"
    )
    
    class Meta:
        verbose_name = "Distrito"
        verbose_name_plural = "Distritos"
        ordering = ['nombre']
    
    def __str__(self) -> str:
        return f"{self.nombre} ({self.cod_ubigeo})"
    
    def calcular_factor_pendiente(self) -> Decimal:
        """
        Calcula el factor de ajuste por pendiente del terreno.
        
        Según PROMPT_MAESTRO v2.0:
        - < 15%: Factor 1.00 (Plano)
        - 15% - 30%: Factor 1.15 (Ondulado)
        - > 30%: Factor 1.30 (Ladera fuerte)
        
        Returns:
            Decimal: Factor multiplicador para mano de obra.
        """
        pendiente = self.pendiente_promedio_estimada
        
        if pendiente < 15:
            return Decimal('1.00')
        elif pendiente <= 30:
            return Decimal('1.15')
        else:
            return Decimal('1.30')


class Cultivo(models.Model):
    """
    Catálogo de especies forestales cultivables.
    
    Define las características técnicas base de cada especie
    como el turno de corta y la densidad de siembra.
    
    Attributes:
        nombre: Nombre común de la especie (ej: "Bolaina Blanca").
        turno_estimado: Años hasta la cosecha final.
        densidad_base: Número de árboles por hectárea.
    """
    
    nombre: str = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del cultivo"
    )
    turno_estimado: int = models.PositiveIntegerField(
        verbose_name="Turno estimado (años)",
        help_text="Años desde la siembra hasta la cosecha"
    )
    densidad_base: int = models.PositiveIntegerField(
        default=1111,
        verbose_name="Densidad base (árboles/ha)",
        help_text="Número de árboles por hectárea en siembra inicial"
    )
    
    class Meta:
        verbose_name = "Cultivo"
        verbose_name_plural = "Cultivos"
        ordering = ['nombre']
    
    def __str__(self) -> str:
        return f"{self.nombre} ({self.turno_estimado} años)"


class PaqueteTecnologico(models.Model):
    """
    Define la 'receta' de actividades por año para cada cultivo.
    
    Es la tabla más importante del sistema. Contiene todas las
    actividades necesarias para el cultivo, agrupadas por año
    y rubro de costo.
    
    Lógica de cálculo v2.0:
    - MANO_OBRA: usa costo_jornal_usuario (del request)
    - INSUMO (plantones): usa costo_planton_usuario (del request)
    - INSUMO (otros) / SERVICIOS: usa costo_unitario_referencial (de BD)
    
    Attributes:
        cultivo: Especie forestal relacionada.
        anio_proyecto: Año del proyecto (0 = instalación).
        rubro: Categoría del costo.
        actividad: Descripción de la actividad.
        unidad_medida: Unidad de medición (Jornal, Kg, etc).
        cantidad_tecnica: Cantidad requerida por hectárea en terreno plano.
        sensible_pendiente: Si la pendiente afecta el rendimiento.
        costo_unitario_referencial: Costo fijo para insumos/servicios NO plantones.
    """
    
    class Rubro(models.TextChoices):
        """Categorías de rubros de costo."""
        MANO_OBRA = 'MANO_OBRA', 'Mano de Obra'
        INSUMO = 'INSUMO', 'Insumos'
        SERVICIOS = 'SERVICIOS', 'Servicios'
        LEGAL = 'LEGAL', 'Legal/Administrativo'
        ACTIVO = 'ACTIVO', 'Activos Fijos'
    
    cultivo = models.ForeignKey(
        Cultivo,
        on_delete=models.CASCADE,
        related_name='paquete_tecnologico',
        verbose_name="Cultivo"
    )
    anio_proyecto: int = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Año del proyecto",
        help_text="0 = año de instalación"
    )
    rubro: str = models.CharField(
        max_length=20,
        choices=Rubro.choices,
        verbose_name="Rubro de costo"
    )
    actividad: str = models.CharField(
        max_length=200,
        verbose_name="Actividad"
    )
    unidad_medida: str = models.CharField(
        max_length=50,
        verbose_name="Unidad de medida",
        help_text="Ej: Jornal, Kg, Unidad, Global"
    )
    cantidad_tecnica: Decimal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Cantidad técnica",
        help_text="Cantidad requerida por hectárea en terreno plano"
    )
    sensible_pendiente: bool = models.BooleanField(
        default=False,
        verbose_name="Sensible a pendiente",
        help_text="Si la pendiente afecta el rendimiento (solo para mano de obra)"
    )
    costo_unitario_referencial: Decimal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Costo unitario referencial (S/)",
        help_text="Para insumos/servicios que NO son plantones ni mano de obra"
    )
    es_planton: bool = models.BooleanField(
        default=False,
        verbose_name="Es plantón",
        help_text="True si este insumo corresponde a plantones forestales"
    )
    
    class Meta:
        verbose_name = "Paquete Tecnológico"
        verbose_name_plural = "Paquetes Tecnológicos"
        ordering = ['cultivo', 'anio_proyecto', 'rubro', 'actividad']
        unique_together = ['cultivo', 'anio_proyecto', 'actividad']
    
    def __str__(self) -> str:
        return f"{self.cultivo.nombre} - Año {self.anio_proyecto}: {self.actividad}"
