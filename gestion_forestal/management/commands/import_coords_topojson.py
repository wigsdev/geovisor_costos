
import json
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from gestion_forestal.models import Distrito

class Command(BaseCommand):
    help = 'Actualiza las coordenadas de los distritos calculando centroides desde el TopoJSON'

    def handle(self, *args, **options):
        topo_path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'public', 'geo', 'DISTRITOS_PI7.topojson')
        
        if not os.path.exists(topo_path):
            self.stdout.write(self.style.ERROR(f'No se encontró el archivo: {topo_path}'))
            return

        self.stdout.write(f'Leyendo {topo_path}...')
        with open(topo_path, 'r', encoding='utf-8') as f:
            topology = json.load(f)

        if 'objects' not in topology or 'arcs' not in topology:
            self.stdout.write(self.style.ERROR('Formato TopoJSON inválido'))
            return

        # 1. Decodificar la Transformación (si existe)
        transform = topology.get('transform')
        scale = transform['scale'] if transform else [1, 1]
        translate = transform['translate'] if transform else [0, 0]

        def decode_arc(arc_index):
            """Decodifica un arco de TopoJSON a coordenadas reales"""
            encoded_arc = topology['arcs'][arc_index]
            decoded = []
            x, y = 0, 0
            for pt in encoded_arc:
                x += pt[0]
                y += pt[1]
                real_x = x * scale[0] + translate[0]
                real_y = y * scale[1] + translate[1]
                decoded.append((real_x, real_y))
            return decoded

        # Cache de arcos decodificados para velocidad (opcional, pero buena práctica)
        decoded_arcs = {} 

        def get_decoded_arc(idx):
            # Manejo de índices negativos (arcos invertidos)
            real_idx = idx if idx >= 0 else ~idx
            if real_idx not in decoded_arcs:
                decoded_arcs[real_idx] = decode_arc(real_idx)
            points = decoded_arcs[real_idx]
            if idx < 0:
                return points[::-1] # Invertir si el índice es negativo
            return points

        layer_name = list(topology['objects'].keys())[0]
        geometries = topology['objects'][layer_name]['geometries']
        
        self.stdout.write(f'Calculando centroides para {len(geometries)} distritos...')
        
        updated_count = 0
        
        for geom in geometries:
            props = geom.get('properties', {})
            # Ajustar clave del UBIGEO según tus datos (UBIGEO, IDDIST, etc)
            ubigeo = props.get('UBIGEO') or props.get('IDDIST')
            
            if not ubigeo:
                continue

            # Calcular Bounding Box de la geometría
            min_x, min_y = float('inf'), float('inf')
            max_x, max_y = float('-inf'), float('-inf')
            
            has_points = False
            
            # TopoJSON GeometryCollection o Polygon/MultiPolygon
            geom_type = geom.get('type')
            arcs_list = []
            
            if geom_type == 'Polygon':
                arcs_list = geom.get('arcs', [])
            elif geom_type == 'MultiPolygon':
                # MultiPolygon es una lista de listas de arcos
                for poly in geom.get('arcs', []):
                    arcs_list.extend(poly)
            
            # Aplanar lista de arcos (puede ser lista de listas)
            flat_arcs = []
            if arcs_list:
                # Arcs structure: [[arc1, arc2], [hole1]]
                # Flattening simple one level deep logic
                for ring in arcs_list:
                    if isinstance(ring, list):
                        flat_arcs.extend(ring)
                    else:
                        flat_arcs.append(ring)

            for arc_idx in flat_arcs:
                points = get_decoded_arc(arc_idx)
                for x, y in points:
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y
                    has_points = True
            
            if has_points:
                # Centroide aproximado (centro del Bounding Box)
                center_lng = (min_x + max_x) / 2
                center_lat = (min_y + max_y) / 2
                
                try:
                    distrito = Distrito.objects.get(cod_ubigeo=ubigeo)
                    distrito.latitud = Decimal(str(center_lat))
                    distrito.longitud = Decimal(str(center_lng))
                    distrito.save()
                    updated_count += 1
                    if updated_count % 50 == 0:
                        self.stdout.write(f'   Actualizado: {distrito.nombre}')
                except Distrito.DoesNotExist:
                    pass

        self.stdout.write(self.style.SUCCESS(f'✅ Proceso terminado. Distritos actualizados: {updated_count}'))
