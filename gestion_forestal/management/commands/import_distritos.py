"""
Comando para importar distritos desde archivo CSV.

Lee el archivo UBIGEO_DISTRITOS.csv y crea los registros
de Zonas Económicas y Distritos correspondientes.

Formato esperado del CSV:
UBIGEO,NOM_DEP,NOM_PROV,NOM_DIST,COD_REG_NAT,REGION NATURAL

Uso:
    python manage.py import_distritos
"""

import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from decimal import Decimal
from gestion_forestal.models import ZonaEconomica, Distrito


# Mapeo de regiones naturales a zonas económicas
REGION_TO_ZONA = {
    'COSTA': 'Costa',
    'SIERRA': 'Sierra',
    'SELVA ALTA': 'Selva Alta',
    'SELVA BAJA': 'Selva Baja',
}

# Configuración de zonas económicas con costos referenciales
ZONAS_CONFIG = {
    'Sierra': {
        'costo_jornal_referencial': Decimal('45.00'),
        'costo_planton_referencial': Decimal('0.90'),
    },
    'Selva Alta': {
        'costo_jornal_referencial': Decimal('50.00'),
        'costo_planton_referencial': Decimal('0.80'),
    },
    'Selva Baja': {
        'costo_jornal_referencial': Decimal('55.00'),
        'costo_planton_referencial': Decimal('0.75'),
    },
    'Costa': {
        'costo_jornal_referencial': Decimal('60.00'),
        'costo_planton_referencial': Decimal('1.00'),
    },
}

# Pendientes estimadas por región natural
PENDIENTES_POR_REGION = {
    'COSTA': 5,
    'SIERRA': 30,
    'SELVA ALTA': 25,
    'SELVA BAJA': 10,
}


class Command(BaseCommand):
    """Comando para importar distritos desde CSV."""
    
    help = 'Importa distritos desde UBIGEO_DISTRITOS.csv'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=os.path.join(settings.BASE_DIR, 'gestion_forestal', 'fixtures', 'UBIGEO_DISTRITOS.csv'),
            help='Ruta al archivo CSV (default: gestion_forestal/fixtures/UBIGEO_DISTRITOS.csv)'
        )
    
    def handle(self, *args, **options):
        """Ejecuta la importación de distritos."""
        csv_path = options['file']
        
        # Validar archivo
        if not os.path.exists(csv_path):
            self.stderr.write(
                self.style.ERROR(f'❌ Archivo no encontrado: {csv_path}')
            )
            return
        
        self.stdout.write('='*60)
        self.stdout.write('🗺️  Importando distritos desde CSV...')
        self.stdout.write('='*60 + '\n')
        
        # =====================================================
        # 1. CREAR ZONAS ECONÓMICAS
        # =====================================================
        
        self.stdout.write('📍 Creando/Actualizando Zonas Económicas...')
        zonas_cache = {}
        
        for nombre, config in ZONAS_CONFIG.items():
            zona, created = ZonaEconomica.objects.update_or_create(
                nombre=nombre,
                defaults=config
            )
            zonas_cache[nombre] = zona
            status = '✨' if created else '✓'
            self.stdout.write(
                f"   {status} {nombre} (Jornal: S/ {config['costo_jornal_referencial']})"
            )
        
        # =====================================================
        # 2. IMPORTAR DISTRITOS
        # =====================================================
        
        self.stdout.write('\n🏘️  Importando distritos...')
        
        creados = 0
        actualizados = 0
        errores = 0
        por_departamento = {}
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Leer campos del CSV del usuario
                    ubigeo_raw = row['UBIGEO'].strip()
                    departamento = row['NOM_DEP'].strip().upper()
                    provincia = row['NOM_PROV'].strip().upper()
                    distrito = row['NOM_DIST'].strip().upper()
                    region_natural = row['REGION NATURAL'].strip().upper()
                    
                    # Normalizar UBIGEO a 6 dígitos (agregar 0 al inicio si tiene 5)
                    if len(ubigeo_raw) == 5:
                        cod_ubigeo = '0' + ubigeo_raw
                    else:
                        cod_ubigeo = ubigeo_raw.zfill(6)
                    
                    # Mapear región a zona económica
                    zona_nombre = REGION_TO_ZONA.get(region_natural)
                    if not zona_nombre:
                        self.stderr.write(
                            f"   ⚠️ Región '{region_natural}' no reconocida para {distrito}"
                        )
                        errores += 1
                        continue
                    
                    zona = zonas_cache[zona_nombre]
                    
                    # Pendiente estimada por región
                    pendiente = PENDIENTES_POR_REGION.get(region_natural, 20)
                    
                    # Coordenadas placeholder
                    lat = Decimal('-9.0')
                    lon = Decimal('-76.0')
                    
                    # Crear/Actualizar distrito
                    distrito_obj, created = Distrito.objects.update_or_create(
                        cod_ubigeo=cod_ubigeo,
                        defaults={
                            'nombre': distrito,
                            'departamento': departamento,
                            'provincia': provincia,
                            'zona_economica': zona,
                            'latitud': lat,
                            'longitud': lon,
                            'pendiente_promedio_estimada': pendiente,
                        }
                    )
                    
                    if created:
                        creados += 1
                    else:
                        actualizados += 1
                    
                    # Contador por departamento
                    if departamento not in por_departamento:
                        por_departamento[departamento] = 0
                    por_departamento[departamento] += 1
                    
                except Exception as e:
                    self.stderr.write(f"   ❌ Error en fila: {row} - {e}")
                    errores += 1
        
        # =====================================================
        # RESUMEN
        # =====================================================
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Importación completada!'))
        self.stdout.write('='*60)
        
        self.stdout.write(f'''
📊 Resumen:
   • Distritos creados: {creados}
   • Distritos actualizados: {actualizados}
   • Errores: {errores}
   • Total procesados: {creados + actualizados}

🗺️  Por departamento:''')
        
        for depto, count in sorted(por_departamento.items()):
            self.stdout.write(f'   • {depto}: {count} distritos')
        
        self.stdout.write(f'''
📡 API disponible en:
   GET /api/distritos/           → Lista todos los distritos
   GET /api/distritos/?departamento=SAN MARTIN → Filtrar por departamento
   GET /api/distritos/?provincia=TOCACHE → Filtrar por provincia
''')
