"""
Comando para poblar la base de datos con datos de prueba v2.2.

Incluye 4 especies forestales con paquetes tecnológicos diferenciados:
- Bolaina Blanca (Selva)
- Capirona (Selva - madera valiosa)
- Pino (Sierra/Selva Alta)
- Eucalipto (Sierra/Selva)

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


# =====================================================
# DEFINICIÓN DE ESPECIES FORESTALES
# =====================================================

ESPECIES = [
    {
        'nombre': 'Bolaina Blanca',
        'turno_estimado': 8,
        'densidad_base': 1111,  # 3x3
        'costo_planton': Decimal('0.80'),
        'descripcion': 'Especie de rápido crecimiento para Selva'
    },
    {
        'nombre': 'Capirona',
        'turno_estimado': 15,
        'densidad_base': 1111,  # 3x3
        'costo_planton': Decimal('1.20'),
        'descripcion': 'Madera valiosa, crecimiento medio'
    },
    {
        'nombre': 'Pino (Pinus tecunumanii)',
        'turno_estimado': 20,
        'densidad_base': 1111,  # 3x3
        'costo_planton': Decimal('1.50'),
        'descripcion': 'Para Sierra/Selva Alta, requiere vivero tecnificado'
    },
    {
        'nombre': 'Eucalipto (E. grandis)',
        'turno_estimado': 12,
        'densidad_base': 1111,  # 3x3
        'costo_planton': Decimal('0.70'),
        'descripcion': 'Especie masiva, bajo costo'
    },
]


def generar_actividades_base(cultivo_nombre, costo_planton):
    """
    Genera las actividades base para cualquier especie forestal.
    
    Args:
        cultivo_nombre: Nombre del cultivo para identificar plantones
        costo_planton: Costo referencial del plantón
    
    Returns:
        Lista de actividades para años 0-5
    """
    actividades = []
    
    # =====================================================
    # AÑO 0 - INSTALACIÓN
    # =====================================================
    
    actividades.extend([
        # Mano de obra - Año 0
        {
            'anio_proyecto': 0,
            'rubro': 'MANO_OBRA',
            'actividad': 'Limpieza y rozo de terreno',
            'unidad_medida': 'Jornal',
            'cantidad_tecnica': Decimal('12.00'),
            'sensible_pendiente': True,
            'sensible_densidad': False,
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
            'sensible_densidad': True,
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
            'sensible_densidad': True,
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
            'sensible_densidad': True,
            'costo_unitario_referencial': Decimal('0.00'),
            'es_planton': False,
        },
        # Insumos - Año 0
        {
            'anio_proyecto': 0,
            'rubro': 'INSUMO',
            'actividad': f'Plantones de {cultivo_nombre}',
            'unidad_medida': 'Unidad',
            'cantidad_tecnica': Decimal('1111.00'),
            'sensible_pendiente': False,
            'sensible_densidad': True,
            'costo_unitario_referencial': costo_planton,
            'es_planton': True,
        },
        {
            'anio_proyecto': 0,
            'rubro': 'INSUMO',
            'actividad': 'Fertilizante NPK (Dosis 150g/planta)',
            'unidad_medida': 'Saco 50kg',
            'cantidad_tecnica': Decimal('3.33'),
            'sensible_pendiente': False,
            'sensible_densidad': True,
            'costo_unitario_referencial': Decimal('120.00'),
            'es_planton': False,
        },
    ])
    
    # =====================================================
    # AÑO 1 - MANTENIMIENTO INICIAL
    # =====================================================
    
    actividades.extend([
        {
            'anio_proyecto': 1,
            'rubro': 'MANO_OBRA',
            'actividad': 'Control de malezas (2 veces)',
            'unidad_medida': 'Jornal',
            'cantidad_tecnica': Decimal('8.00'),
            'sensible_pendiente': True,
            'sensible_densidad': False,
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
            'sensible_densidad': True,
            'costo_unitario_referencial': Decimal('0.00'),
            'es_planton': False,
        },
        {
            'anio_proyecto': 1,
            'rubro': 'INSUMO',
            'actividad': f'Plantones recalce (10%) - {cultivo_nombre}',
            'unidad_medida': 'Unidad',
            'cantidad_tecnica': Decimal('111.00'),
            'sensible_pendiente': False,
            'sensible_densidad': True,
            'costo_unitario_referencial': costo_planton,
            'es_planton': True,
        },
    ])
    
    # =====================================================
    # AÑOS 0-5 - VIGILANCIA Y GASTOS GENERALES
    # =====================================================
    
    for anio in range(0, 6):
        actividades.append({
            'anio_proyecto': anio,
            'rubro': 'SERVICIOS',
            'actividad': f'Vigilancia y Gastos Generales (Año {anio})',
            'unidad_medida': 'Global',
            'cantidad_tecnica': Decimal('1.00'),
            'sensible_pendiente': False,
            'sensible_densidad': False,
            'costo_unitario_referencial': Decimal('50.00'),
            'es_planton': False,
        })
    
    # =====================================================
    # AÑOS 2-3 - CONTROL DE MALEZAS
    # =====================================================
    
    for anio in [2, 3]:
        actividades.append({
            'anio_proyecto': anio,
            'rubro': 'MANO_OBRA',
            'actividad': f'Mantenimiento y Control de Malezas (Año {anio})',
            'unidad_medida': 'Jornal',
            'cantidad_tecnica': Decimal('6.00'),
            'sensible_pendiente': True,
            'sensible_densidad': False,
            'costo_unitario_referencial': Decimal('0.00'),
            'es_planton': False,
        })
    
    # =====================================================
    # AÑO 3 - PODA DE FORMACIÓN
    # =====================================================
    
    actividades.append({
        'anio_proyecto': 3,
        'rubro': 'MANO_OBRA',
        'actividad': 'Poda de formación (1ra)',
        'unidad_medida': 'Jornal',
        'cantidad_tecnica': Decimal('5.00'),
        'sensible_pendiente': False,
        'sensible_densidad': True,
        'costo_unitario_referencial': Decimal('0.00'),
        'es_planton': False,
    })
    
    # =====================================================
    # AÑOS 4-5 - MANTENIMIENTO LIGERO
    # =====================================================
    
    for anio in [4, 5]:
        actividades.append({
            'anio_proyecto': anio,
            'rubro': 'MANO_OBRA',
            'actividad': f'Mantenimiento ligero (Año {anio})',
            'unidad_medida': 'Jornal',
            'cantidad_tecnica': Decimal('4.00'),
            'sensible_pendiente': True,
            'sensible_densidad': False,
            'costo_unitario_referencial': Decimal('0.00'),
            'es_planton': False,
        })
    
    # =====================================================
    # AÑO 5 - PODA DE ALTURA
    # =====================================================
    
    actividades.append({
        'anio_proyecto': 5,
        'rubro': 'MANO_OBRA',
        'actividad': 'Poda de altura y limpieza de fuste',
        'unidad_medida': 'Jornal',
        'cantidad_tecnica': Decimal('8.00'),
        'sensible_pendiente': False,
        'sensible_densidad': True,
        'costo_unitario_referencial': Decimal('0.00'),
        'es_planton': False,
    })
    
    return actividades


class Command(BaseCommand):
    """Comando para cargar datos de prueba multi-especie."""
    
    help = 'Carga datos de prueba v2.2: 4 especies forestales con paquetes tecnológicos'
    
    def handle(self, *args, **options):
        """Ejecuta la carga de datos."""
        self.stdout.write('='*60)
        self.stdout.write('🌲 Iniciando carga de datos v1.0 (Producción)...')
        self.stdout.write('='*60 + '\n')
        
        # =====================================================
        # 1. CREAR ZONA ECONÓMICA
        # =====================================================
        
        zona, created = ZonaEconomica.objects.update_or_create(
            nombre='Selva Alta',
            defaults={
                'costo_jornal_referencial': Decimal('50.00'),
                'costo_planton_referencial': Decimal('0.80'),
            }
        )
        status = '✨ creada' if created else '✓ actualizada'
        self.stdout.write(f'  {status}: Zona Económica "{zona.nombre}"')
        
        # =====================================================
        # 2. CREAR DISTRITO DE PRUEBA
        # =====================================================
        
        distrito, created = Distrito.objects.update_or_create(
            cod_ubigeo='220903',
            defaults={
                'nombre': 'Uchiza',
                'zona_economica': zona,
                'latitud': Decimal('-8.4600000'),
                'longitud': Decimal('-76.4600000'),
                'pendiente_promedio_estimada': 20,
            }
        )
        status = '✨ creado' if created else '✓ actualizado'
        self.stdout.write(f'  {status}: Distrito "{distrito.nombre}" ({distrito.cod_ubigeo})')
        
        # =====================================================
        # 3. CREAR CULTIVOS (4 ESPECIES)
        # =====================================================
        
        self.stdout.write('\n📋 Creando/Actualizando cultivos...')
        
        cultivos_creados = []
        for especie in ESPECIES:
            cultivo, created = Cultivo.objects.update_or_create(
                nombre=especie['nombre'],
                defaults={
                    'turno_estimado': especie['turno_estimado'],
                    'densidad_base': especie['densidad_base'],
                }
            )
            status = '✨' if created else '✓'
            self.stdout.write(
                f"  {status} {cultivo.nombre} (Turno: {cultivo.turno_estimado} años, "
                f"Densidad: {cultivo.densidad_base}, Plantón: S/ {especie['costo_planton']})"
            )
            cultivos_creados.append((cultivo, especie['costo_planton']))
        
        # =====================================================
        # 4. CREAR PAQUETES TECNOLÓGICOS POR ESPECIE
        # =====================================================
        
        self.stdout.write('\n📦 Creando/Actualizando paquetes tecnológicos...')
        
        total_creadas = 0
        total_actualizadas = 0
        
        for cultivo, costo_planton in cultivos_creados:
            actividades = generar_actividades_base(
                cultivo.nombre.split(' (')[0],  # Quitar paréntesis del nombre
                costo_planton
            )
            
            creadas = 0
            actualizadas = 0
            
            for act_data in actividades:
                obj, created = PaqueteTecnologico.objects.update_or_create(
                    cultivo=cultivo,
                    anio_proyecto=act_data['anio_proyecto'],
                    actividad=act_data['actividad'],
                    defaults={
                        'rubro': act_data['rubro'],
                        'unidad_medida': act_data['unidad_medida'],
                        'cantidad_tecnica': act_data['cantidad_tecnica'],
                        'sensible_pendiente': act_data['sensible_pendiente'],
                        'sensible_densidad': act_data['sensible_densidad'],
                        'costo_unitario_referencial': act_data['costo_unitario_referencial'],
                        'es_planton': act_data['es_planton'],
                    }
                )
                if created:
                    creadas += 1
                else:
                    actualizadas += 1
            
            self.stdout.write(
                f"  📦 {cultivo.nombre}: {creadas} nuevas, {actualizadas} actualizadas"
            )
            total_creadas += creadas
            total_actualizadas += actualizadas
        
        # =====================================================
        # RESUMEN FINAL
        # =====================================================
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Datos v1.0 cargados exitosamente!'))
        self.stdout.write('='*60)
        
        self.stdout.write(f'''
📊 Resumen:
  • Zona Económica: {zona.nombre}
  • Distrito: {distrito.nombre} ({distrito.cod_ubigeo})
  • Cultivos: {len(cultivos_creados)} especies
  • Actividades: {total_creadas} nuevas, {total_actualizadas} actualizadas

🌳 Especies disponibles:''')
        
        for cultivo, costo in cultivos_creados:
            self.stdout.write(f'  • {cultivo.nombre} (ID: {cultivo.id})')
        
        self.stdout.write('''
🧪 Endpoints de prueba:
  GET  /api/cultivos/         → Lista de especies
  POST /api/calcular-costos/  → Cálculo de costos
''')
