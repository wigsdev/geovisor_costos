"""
Modelos de datos para el Geovisor de Costos Forestales.

Define la estructura de la base de datos para el cálculo
de costos de inversión en plantaciones forestales comerciales.

NOTA: Versión sin dependencias geoespaciales (GDAL/GeoDjango).
Los campos de ubicación son simplificados para permitir la lógica
de cálculo de costos sin requerir análisis espacial real.
"""

from django.db import models
from decimal import Decimal
from typing import Optional


class ZonaEconomica(models.Model):
    """
    Agrupa distritos con costos laborales similares.
    
    Define el costo base del jornal y un factor de flete
    que refleja la dificultad de acceso a la zona.
    
    Attributes:
        nombre: Nombre descriptivo de la zona (ej: "Selva Alta Accesible").
        costo_jornal_base: Costo del día de trabajo en soles.
        factor_flete: Multiplicador por dificultad de acceso (1.0 = normal).
    """
    
    nombre: str = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la zona"
    )
    costo_jornal_base: Decimal = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Costo jornal base (S/)"
    )
    factor_flete: Decimal = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name="Factor de flete"
    )
    
    class Meta:
        verbose_name = "Zona Económica"
        verbose_name_plural = "Zonas Económicas"
        ordering = ['nombre']
    
    def __str__(self) -> str:
        return f"{self.nombre} (S/ {self.costo_jornal_base}/jornal)"


class Distrito(models.Model):
    """
    Unidad administrativa mínima del Perú.
    
    Cada distrito pertenece a una zona económica y tiene
    parámetros estimados de pendiente y acceso para el
    cálculo de costos.
    
    Attributes:
        cod_ubigeo: Código oficial INEI de 6 dígitos (PK).
        nombre: Nombre del distrito.
        zona_economica: Zona económica a la que pertenece.
        pendiente_promedio_estimada: Pendiente promedio en porcentaje (%).
        factor_acceso_temporal: Factor de ajuste por accesibilidad (1.0 = normal).
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
    pendiente_promedio_estimada: int = models.PositiveSmallIntegerField(
        default=15,
        verbose_name="Pendiente promedio (%)",
        help_text="Pendiente promedio estimada del terreno en porcentaje"
    )
    factor_acceso_temporal: Decimal = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name="Factor de acceso",
        help_text="Factor de ajuste por accesibilidad (1.0 = normal, >1 = difícil)"
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
        
        Basado en la pendiente promedio estimada:
        - 0-10%: Factor 1.00 (terreno plano)
        - 11-20%: Factor 1.10
        - 21-30%: Factor 1.20
        - >30%: Factor 1.35 (terreno muy inclinado)
        
        Returns:
            Decimal: Factor multiplicador para costos de mano de obra.
        """
        pendiente = self.pendiente_promedio_estimada
        
        if pendiente <= 10:
            return Decimal('1.00')
        elif pendiente <= 20:
            return Decimal('1.10')
        elif pendiente <= 30:
            return Decimal('1.20')
        else:
            return Decimal('1.35')


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
    
    La lógica de cálculo usa el campo sensible_pendiente así:
        if paquete.sensible_pendiente:
            costo = cantidad * costo_base * distrito.calcular_factor_pendiente()
    
    Attributes:
        cultivo: Especie forestal relacionada.
        anio_proyecto: Año del proyecto (0 = instalación).
        rubro: Categoría del costo.
        actividad: Descripción de la actividad.
        unidad_medida: Unidad de medición (Jornal, Kg, etc).
        cantidad_tecnica: Cantidad requerida por hectárea en terreno plano.
        costo_unitario: Costo por unidad (usado para insumos, servicios).
        sensible_pendiente: Si la pendiente afecta el rendimiento.
        es_recalce: Si es reposición por mortalidad de plantas.
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
    costo_unitario: Decimal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Costo unitario (S/)",
        help_text="Costo por unidad (para insumos/servicios). Si es 0, usa costo jornal."
    )
    sensible_pendiente: bool = models.BooleanField(
        default=False,
        verbose_name="Sensible a pendiente",
        help_text="Si la pendiente del terreno afecta el rendimiento de la actividad"
    )
    es_recalce: bool = models.BooleanField(
        default=False,
        verbose_name="Es recalce",
        help_text="Si es reposición por mortalidad de plantas"
    )
    
    class Meta:
        verbose_name = "Paquete Tecnológico"
        verbose_name_plural = "Paquetes Tecnológicos"
        ordering = ['cultivo', 'anio_proyecto', 'rubro', 'actividad']
        # Evitar duplicados de la misma actividad en el mismo año/cultivo
        unique_together = ['cultivo', 'anio_proyecto', 'actividad']
    
    def __str__(self) -> str:
        return f"{self.cultivo.nombre} - Año {self.anio_proyecto}: {self.actividad}"
    
    def calcular_costo(self, distrito: 'Distrito', hectareas: Decimal = Decimal('1.00')) -> Decimal:
        """
        Calcula el costo total de esta actividad para un distrito y área.
        
        Args:
            distrito: Distrito donde se realizará la actividad.
            hectareas: Número de hectáreas a trabajar.
        
        Returns:
            Decimal: Costo total en soles.
        """
        cantidad_ajustada = self.cantidad_tecnica * hectareas
        
        # Aplicar factor de pendiente si la actividad es sensible
        if self.sensible_pendiente:
            factor_pendiente = distrito.calcular_factor_pendiente()
            cantidad_ajustada = cantidad_ajustada * factor_pendiente
        
        # Determinar el costo base
        if self.rubro == self.Rubro.MANO_OBRA:
            # Usar costo del jornal de la zona económica
            if distrito.zona_economica:
                costo_base = distrito.zona_economica.costo_jornal_base
            else:
                costo_base = Decimal('50.00')  # Valor por defecto
        else:
            # Usar costo unitario definido
            costo_base = self.costo_unitario
        
        costo_total = cantidad_ajustada * costo_base
        
        # Aplicar factor de acceso
        costo_total = costo_total * distrito.factor_acceso_temporal
        
        return costo_total.quantize(Decimal('0.01'))
