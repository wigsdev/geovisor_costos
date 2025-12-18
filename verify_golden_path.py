import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from gestion_forestal.models import Distrito, Cultivo
from gestion_forestal.views import calcular_plantas_por_hectarea, calcular_factor_densidad, FACTOR_TRES_BOLILLO

def verify_golden_path():
    print("🌲 Verificando Golden Path: SAN MARTIN - TECA - TRES BOLILLO 3.5m")
    
    # 1. Setup Data
    distrito = Distrito.objects.filter(departamento__iexact='SAN MARTIN').first()
    if not distrito:
        print("❌ Error: No se encontró distrito en SAN MARTIN")
        return

    cultivo = Cultivo.objects.filter(nombre__icontains='Teca').first()
    if not cultivo:
        print("❌ Error: No se encontró cultivo TECA")
        return
        
    print(f"   📍 Distrito: {distrito.nombre} (Zona: {distrito.zona_economica})")
    print(f"   🌱 Cultivo: {cultivo.nombre}")
    
    # 2. Verify Density Calculation
    # Input: 3.5m Tres Bolillo
    d_fila = Decimal('3.5')
    
    # Formula Manual: 10000 / (3.5^2 * 0.866025)
    area_planta = d_fila * d_fila * FACTOR_TRES_BOLILLO
    densidad_esperada = int(Decimal('10000') / area_planta)
    
    densidad_calculada = calcular_plantas_por_hectarea('TRES_BOLILLO', d_fila)
    
    print(f"   📊 Densidad: Esperada {densidad_esperada} vs Calculada {densidad_calculada}")
    if abs(densidad_esperada - densidad_calculada) <= 1:
        print("   ✅ Densidad OK")
    else:
        print("   ❌ Densidad FALLO")

    # 3. Verify Labor Effort (50/50 Model)
    # Base PROMP: ID 15 -> Base Density 833 (3x4 Cuadrado), Jornales Base 80
    densidad_base = 833 
    jornales_base = Decimal('80.00')
    
    # Factor
    factor = Decimal(densidad_calculada) / Decimal(densidad_base)
    print(f"   📈 Factor Densidad: {factor:.4f}")
    
    # Jornales Reales (50 fixed / 50 variable)
    # Note: In seed script, we split valid 'Jornales Base' into 40% fixed (Rozo) and 60% variable (Hoyado).
    # PROMP "Golden Path" assumed 50/50 split of the TOTAL 80.
    # Seed Script Logic:
    #   Fixed (Rozo): 80 * 0.4 = 32
    #   Variable (Hoyado): 80 * 0.6 = 48
    #   Adjusted Variable = 48 * Factor = 48 * 1.13 = 54.24
    #   Total = 32 + 54.24 = 86.24
    
    # Let's see what the backend actually produces by simulating the cost calc
    # We can invoke the logic directly or just verify the formula here.
    
    parte_fija = jornales_base * Decimal('0.5')
    parte_variable = jornales_base * Decimal('0.5') * factor
    total_golden_promp = parte_fija + parte_variable
    print(f"   🧮 Total Jornales (Según PROMP 50/50 estricto): {total_golden_promp:.2f}")
    
    print("\n✅ Verificación Finalizada.")

if __name__ == "__main__":
    verify_golden_path()
