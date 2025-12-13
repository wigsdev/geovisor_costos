"""
Comando para poblar la base de datos con datos de prueba.

Crea datos iniciales para verificar el funcionamiento del
sistema de cálculo de costos forestales.

Uso:
    python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from gestion_forestal.models import (
    ZonaEconomica,
    Distrito,
    Cultivo,
    PaqueteTecnologico
)


class Command(BaseCommand):
    """Comando para cargar datos de prueba en la base de datos."""
    
    help = 'Carga datos de prueba: Zona Selva Alta, Distrito Uchiza, Cultivo Bolaina'
    
    def handle(self, *args, **options):
        """Ejecuta la carga de datos."""
        self.stdout.write('Iniciando carga de datos de prueba...\n')
        
        # 1. Crear Zona Económica
        zona, created = ZonaEconomica.objects.update_or_create(
            nombre='Selva Alta',
            defaults={
                'costo_jornal_referencial': Decimal('50.00'),
                'costo_planton_referencial': Decimal('0.80'),
            }
        )
        status = 'creada' if created else 'actualizada'
        self.stdout.write(f'  ✓ Zona Económica "{zona.nombre}" {status}')
        
        # 2. Crear Distrito Uchiza
        distrito, created = Distrito.objects.update_or_create(
            cod_ubigeo='220903',  # UBIGEO real de Uchiza
            defaults={
                'nombre': 'Uchiza',
                'zona_economica': zona,
                'latitud': Decimal('-8.4600000'),
                'longitud': Decimal('-76.4600000'),
                'pendiente_promedio_estimada': 20,  # Ondulado
            }
        )
        status = 'creado' if created else 'actualizado'
        self.stdout.write(f'  ✓ Distrito "{distrito.nombre}" {status}')
        
        # 3. Crear Cultivo Bolaina
        cultivo, created = Cultivo.objects.update_or_create(
            nombre='Bolaina Blanca',
            defaults={
                'turno_estimado': 8,
                'densidad_base': 1111,  # Espaciamiento 3x3
            }
        )
        status = 'creado' if created else 'actualizado'
        self.stdout.write(f'  ✓ Cultivo "{cultivo.nombre}" {status}')
        
        # 4. Crear Paquete Tecnológico para Bolaina
        actividades_anio_0 = [
            # Mano de obra - Año 0
            {
                'anio_proyecto': 0,
                'rubro': 'MANO_OBRA',
                'actividad': 'Limpieza y rozo de terreno',
                'unidad_medida': 'Jornal',
                'cantidad_tecnica': Decimal('12.00'),
                'sensible_pendiente': True,
                'costo_unitario_referencial': Decimal('0.00'),
                'es_planton': False,
            },
            {
                'anio_proyecto': 0,
                'rubro': 'MANO_OBRA',
                'actividad': 'Trazado y marcación',
                'unidad_medida': 'Jornal',
                'cantidad_tecnica': Decimal('4.00'),
                'sensible_pendiente': False,
                'costo_unitario_referencial': Decimal('0.00'),
                'es_planton': False,
            },
            {
                'anio_proyecto': 0,
                'rubro': 'MANO_OBRA',
                'actividad': 'Hoyado 30x30x30',
                'unidad_medida': 'Jornal',
                'cantidad_tecnica': Decimal('15.00'),
                'sensible_pendiente': True,
                'costo_unitario_referencial': Decimal('0.00'),
                'es_planton': False,
            },
            {
                'anio_proyecto': 0,
                'rubro': 'MANO_OBRA',
                'actividad': 'Siembra de plantones',
                'unidad_medida': 'Jornal',
                'cantidad_tecnica': Decimal('6.00'),
                'sensible_pendiente': False,
                'costo_unitario_referencial': Decimal('0.00'),
                'es_planton': False,
            },
            # Insumos - Año 0
            {
                'anio_proyecto': 0,
                'rubro': 'INSUMO',
                'actividad': 'Plantones de Bolaina',
                'unidad_medida': 'Unidad',
                'cantidad_tecnica': Decimal('1111.00'),
                'sensible_pendiente': False,
                'costo_unitario_referencial': Decimal('0.00'),
                'es_planton': True,
            },
            {
                'anio_proyecto': 0,
                'rubro': 'INSUMO',
                'actividad': 'Fertilizante NPK (saco 50kg)',
                'unidad_medida': 'Saco',
                'cantidad_tecnica': Decimal('4.00'),
                'sensible_pendiente': False,
                'costo_unitario_referencial': Decimal('120.00'),
                'es_planton': False,
            },
        ]
        
        actividades_anio_1 = [
            # Mano de obra - Año 1
            {
                'anio_proyecto': 1,
                'rubro': 'MANO_OBRA',
                'actividad': 'Control de malezas (2 veces)',
                'unidad_medida': 'Jornal',
                'cantidad_tecnica': Decimal('8.00'),
                'sensible_pendiente': True,
                'costo_unitario_referencial': Decimal('0.00'),
                'es_planton': False,
            },
            {
                'anio_proyecto': 1,
                'rubro': 'MANO_OBRA',
                'actividad': 'Recalce (10% mortalidad)',
                'unidad_medida': 'Jornal',
                'cantidad_tecnica': Decimal('2.00'),
                'sensible_pendiente': False,
                'costo_unitario_referencial': Decimal('0.00'),
                'es_planton': False,
            },
            # Insumos - Año 1
            {
                'anio_proyecto': 1,
                'rubro': 'INSUMO',
                'actividad': 'Plantones recalce (10%)',
                'unidad_medida': 'Unidad',
                'cantidad_tecnica': Decimal('111.00'),
                'sensible_pendiente': False,
                'costo_unitario_referencial': Decimal('0.00'),
                'es_planton': True,
            },
        ]
        
        todas_actividades = actividades_anio_0 + actividades_anio_1
        
        creadas = 0
        actualizadas = 0
        
        for act_data in todas_actividades:
            obj, created = PaqueteTecnologico.objects.update_or_create(
                cultivo=cultivo,
                anio_proyecto=act_data['anio_proyecto'],
                actividad=act_data['actividad'],
                defaults={
                    'rubro': act_data['rubro'],
                    'unidad_medida': act_data['unidad_medida'],
                    'cantidad_tecnica': act_data['cantidad_tecnica'],
                    'sensible_pendiente': act_data['sensible_pendiente'],
                    'costo_unitario_referencial': act_data['costo_unitario_referencial'],
                    'es_planton': act_data['es_planton'],
                }
            )
            if created:
                creadas += 1
            else:
                actualizadas += 1
        
        self.stdout.write(f'  ✓ Paquete Tecnológico: {creadas} actividades creadas, {actualizadas} actualizadas')
        
        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Datos de prueba cargados exitosamente!'))
        self.stdout.write('='*50)
        self.stdout.write(f'''
Resumen:
  - Zona Económica: {zona.nombre}
    • Jornal referencial: S/ {zona.costo_jornal_referencial}
    • Plantón referencial: S/ {zona.costo_planton_referencial}
  
  - Distrito: {distrito.nombre} ({distrito.cod_ubigeo})
    • Pendiente: {distrito.pendiente_promedio_estimada}%
    • Factor pendiente: {distrito.calcular_factor_pendiente()}
  
  - Cultivo: {cultivo.nombre}
    • Turno: {cultivo.turno_estimado} años
    • Densidad: {cultivo.densidad_base} árboles/ha
  
  - Actividades: {len(todas_actividades)} (Año 0 y Año 1)

Prueba el endpoint con:
  POST /api/calcular-costos/
  {{
    "distrito_id": "220903",
    "cultivo_id": {cultivo.id},
    "hectareas": 1,
    "costo_jornal_usuario": 50.00,
    "costo_planton_usuario": 0.80,
    "anio_inicio": 0,
    "anio_fin": 1
  }}
''')
