"""
Comando para poblar la base de datos con datos CALIBRADOS v2.1.
Basado en PROMPT_MAESTRO.md Tables 1 & 2.

Ejecuta:
    python manage.py seed_data_v1_1
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from gestion_forestal.models import (
    ZonaEconomica,
    Distrito,
    Cultivo,
    PaqueteTecnologico,
    ParametroMantenimiento
)

# =====================================================
# TABLA 2: PARÁMETROS DE MANTENIMIENTO
# =====================================================
MANTENIMIENTO_DATA = [
    # Region, Nivel Maleza, Dias Limpieza, Dias Poda, Costo Insumos/Global, Jornal Ref
    ('CAJAMARCA', 'BAJO', 15, 5, 20, 40),
    ('ANCASH', 'BAJO', 17, 5, 22, 40),
    ('PASCO', 'MEDIO', 20, 6, 26, 45),
    ('JUNIN', 'MEDIO', 22, 6, 28, 50),
    ('HUANUCO', 'ALTO', 25, 7, 32, 50),
    ('SAN MARTIN', 'ALTO', 25, 8, 33, 55),
    ('MADRE DE DIOS', 'MEDIO', 20, 5, 25, 60),
]

# =====================================================
# TABLA 1: COEFICIENTES DE INSTALACIÓN
# =====================================================
# ID, REGION, ESPECIE, SISTEMA, D_FILA, D_PLANTA, P_PLANTON, JORNALES_BASE, INSUMOS, GESTION
COEFICIENTES_DATA = [
    (1, 'CAJAMARCA', 'Pino Radiata', 'TRES_BOLILLO', 3, 3, 0.8, 60, 1200, 0.1),
    (2, 'CAJAMARCA', 'Pino Patula', 'TRES_BOLILLO', 3, 3, 0.8, 60, 1200, 0.1),
    (3, 'CAJAMARCA', 'Eucalipto Globulus', 'CUADRADO', 3, 3, 0.8, 55, 1100, 0.1),
    (4, 'ANCASH', 'Eucalipto Globulus', 'CUADRADO', 3, 3, 1.0, 60, 1200, 0.1),
    (5, 'ANCASH', 'Pino Radiata', 'CUADRADO', 3, 3, 1.0, 65, 1300, 0.1),
    (6, 'ANCASH', 'Tara (Caesalpinia)', 'RECTANGULO', 4, 4, 2.5, 50, 800, 0.1),
    (7, 'PASCO', 'Pino Tecunumanii', 'RECTANGULO', 4, 3, 1.5, 70, 1400, 0.12),
    (8, 'PASCO', 'Eucalipto Urograndis', 'RECTANGULO', 3, 3, 2.0, 65, 1500, 0.12),
    (9, 'PASCO', 'Ulcumano (Nativa)', 'RECTANGULO', 4, 4, 3.0, 75, 1200, 0.12),
    (10, 'JUNIN', 'Eucalipto Tropical', 'RECTANGULO', 3, 2.5, 2.5, 70, 1800, 0.12),
    (11, 'JUNIN', 'Pino Tecunumanii', 'RECTANGULO', 3, 3, 1.8, 75, 1600, 0.12),
    (12, 'JUNIN', 'Bolaina Blanca', 'CUADRADO', 3, 3, 1.5, 80, 1500, 0.12),
    (13, 'HUANUCO', 'Bolaina Blanca', 'CUADRADO', 3, 3, 1.5, 85, 1400, 0.12),
    (14, 'HUANUCO', 'Capirona', 'RECTANGULO', 4, 3, 1.8, 85, 1400, 0.12),
    (15, 'SAN MARTIN', 'Teca (Clonal)', 'CUADRADO', 3, 4, 3.5, 80, 1800, 0.15),
    (16, 'SAN MARTIN', 'Capirona', 'RECTANGULO', 4, 3, 1.5, 80, 1500, 0.15),
    (17, 'SAN MARTIN', 'Eucalipto Urograndis', 'CUADRADO', 3, 3, 2.5, 75, 1800, 0.15),
    (18, 'MADRE DE DIOS', 'Shihuahuaco', 'RECTANGULO', 4, 4, 5.0, 85, 2000, 0.15),
    (19, 'MADRE DE DIOS', 'Teca', 'RECTANGULO', 4, 4, 4.0, 80, 2000, 0.15),
    (20, 'MADRE DE DIOS', 'Castaña (Injerto)', 'RECTANGULO', 7, 7, 15.0, 60, 1500, 0.15),
]

class Command(BaseCommand):
    help = 'Carga datos calibrados v2.1'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Iniciando carga de datos v2.1...'))
        
        # 1. Crear Zonas Económicas y Parametros de Mantenimiento
        zonas_creadas = {}
        for reg, nivel, d_limp, d_poda, c_insumos, jornada_ref in MANTENIMIENTO_DATA:
            # Crear Zona
            zona, _ = ZonaEconomica.objects.update_or_create(
                nombre=reg,
                defaults={
                    'costo_jornal_referencial': Decimal(jornada_ref),
                    'costo_planton_referencial': Decimal('1.00') # Default global
                }
            )
            zonas_creadas[reg] = zona
            
            # Crear Parametro (para uso futuro, aunque aqui ya usamos los valores directos)
            ParametroMantenimiento.objects.update_or_create(
                region=reg,
                defaults={
                    'nivel_maleza': nivel,
                    'dias_limpieza': d_limp,
                    'dias_poda': d_poda,
                    'costo_insumos': c_insumos,
                    'jornal_referencial': jornada_ref
                }
            )
            
            # Actualizar distritos existentes
            count_dist = Distrito.objects.filter(departamento__iexact=reg).update(zona_economica=zona)
            self.stdout.write(f"  📍 Zona {reg}: {count_dist} distritos asignados.")

        # 2. Procesar Cultivos y Paquetes Tecnológicos
        self.stdout.write(self.style.WARNING('\n📦 Generando Paquetes Tecnológicos Específicos...'))
        
        for idx, region, especie, sistema, df, dp, cost_plant, jornal_base, insumos_base, gestion in COEFICIENTES_DATA:
            
            zona = zonas_creadas.get(region)
            if not zona:
                continue

            # Crear/Get Cultivo
            cultivo_obj, _ = Cultivo.objects.get_or_create(
                nombre=especie,
                defaults={
                    'turno_estimado': 20, # Default generico, ajustaremos si es necesario
                    'densidad_base': 1111 
                }
            )
            
            # Limpiar paquetes previos para este cultivo en esta zona
            PaqueteTecnologico.objects.filter(cultivo=cultivo_obj, zona_economica=zona).delete()
            
            # --- AÑO 0: INSTALACIÓN (Datos de Tabla 1) ---
            
            # Insumos (Fertilizantes etc)
            PaqueteTecnologico.objects.create(
                cultivo=cultivo_obj, zona_economica=zona, anio_proyecto=0,
                rubro='INSUMO', actividad='Insumos Instalación (Fertilizantes/Hidrogel)',
                unidad_medida='Global', cantidad_tecnica=1, sensible_densidad=True,
                costo_unitario_referencial=Decimal(insumos_base), es_planton=False
            )
            
            # Plantones
            densidad_aprox = 10000 / (df * dp) if sistema != 'TRES_BOLILLO' else 10000 / ((df * df) * 0.866)
            PaqueteTecnologico.objects.create(
                cultivo=cultivo_obj, zona_economica=zona, anio_proyecto=0,
                rubro='INSUMO', actividad=f'Plantones {especie}',
                unidad_medida='Unidad', cantidad_tecnica=Decimal(densidad_aprox), sensible_densidad=True,
                costo_unitario_referencial=Decimal(cost_plant), es_planton=True
            )
            
            # Mano de Obra (Jornales Base de Tabla 1)
            # Desglosamos genericamente el jornal base: 
            # 50% Hoyado/Siembra (variable), 50% Rozo/Trazo (Fijo) -> Segun modelo
            # Pero aqui el 'jornal_base' ya es el total. Lo dividiremos en actividades representativas.
            
            jornales_variables = Decimal(jornal_base) * Decimal('0.6') # Hoyado y siembra pesan mas
            jornales_fijos = Decimal(jornal_base) * Decimal('0.4')
            
            PaqueteTecnologico.objects.create(
                cultivo=cultivo_obj, zona_economica=zona, anio_proyecto=0,
                rubro='MANO_OBRA', actividad='Limpieza, Rozo y Trazo',
                unidad_medida='Jornal', cantidad_tecnica=jornales_fijos, sensible_densidad=False,
                costo_unitario_referencial=0
            )
            PaqueteTecnologico.objects.create(
                cultivo=cultivo_obj, zona_economica=zona, anio_proyecto=0,
                rubro='MANO_OBRA', actividad='Hoyado y Siembra',
                unidad_medida='Jornal', cantidad_tecnica=jornales_variables, sensible_densidad=True,
                costo_unitario_referencial=0
            )
            
            # --- AÑOS 1-20: MANTENIMIENTO (Datos de Tabla 2) ---
            # Recuperar param mantenimiento de la zona
            param = ParametroMantenimiento.objects.get(region=region)
            
            # Limpieza (Años 2-5 según usuario: "mantenimiento hasta cierre de copas")
            for anio in range(2, 6): # Años 2, 3, 4, 5
                PaqueteTecnologico.objects.create(
                    cultivo=cultivo_obj, zona_economica=zona, anio_proyecto=anio,
                    rubro='MANO_OBRA', actividad=f'Mantenimiento y Control Malezas (Año {anio})',
                    unidad_medida='Jornal', cantidad_tecnica=param.dias_limpieza, sensible_densidad=False, sensible_pendiente=True,
                    costo_unitario_referencial=0
                )
            
            # Poda (A partir del año 3 hasta el 5)
            for anio in range(3, 6): # Años 3, 4, 5
                 PaqueteTecnologico.objects.create(
                    cultivo=cultivo_obj, zona_economica=zona, anio_proyecto=anio,
                    rubro='MANO_OBRA', actividad=f'Podas y Manejo (Año {anio})',
                    unidad_medida='Jornal', cantidad_tecnica=param.dias_poda, sensible_densidad=True,
                    costo_unitario_referencial=0
                )
            
            # Gastos de Gestión (Todos los años)
            for anio in range(0, 11): # Hasta año 10
                 PaqueteTecnologico.objects.create(
                    cultivo=cultivo_obj, zona_economica=zona, anio_proyecto=anio,
                    rubro='SERVICIOS', actividad=f'Gestión y Administración {int(gestion*100)}%',
                    unidad_medida='Global', cantidad_tecnica=1,
                    # Esto es un % del costo, pero aqui lo ponemos como costo fijo aprox para simplificar el seed inicial
                    # Lo ideal seria que el backend calcule el % dinamicamente.
                    # Por ahora pondremos un monto fijo representativo: 10% de la inversion aprox
                    costo_unitario_referencial=Decimal('500.00') 
                )

            self.stdout.write(f"    ✅ {region} | {especie}")

        self.stdout.write(self.style.SUCCESS('\n✨ Carga v2.1 completada con éxito.'))
