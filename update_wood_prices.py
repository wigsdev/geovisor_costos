from decimal import Decimal
from gestion_forestal.models import Cultivo

# Mapping based on CSV Analysis (2022-2025 M3 Averages)
# Data source: data/4.1.4.BD_PRECIOS_MADERAS.csv
updates = {
    'Eucalipto Globulus': Decimal('163.06'),
    'Eucalipto (E. grandis)': Decimal('163.06'),
    'Eucalipto Tropical': Decimal('163.06'),
    'Eucalipto Urograndis': Decimal('163.06'),
    'Bolaina Blanca': Decimal('142.63'),
    'Capirona': Decimal('66.59'),
    'Pino Radiata': Decimal('260.34'),
    'Pino Tecunumanii': Decimal('241.08'),
    'Pino (Pinus tecunumanii)': Decimal('241.08'),
    'Shihuahuaco': Decimal('179.71'),
    # Using generic/related averages for others if needed, or keeping defaults
}

print("--- Updating Wood Prices from CSV Analysis (2022-2025) ---")

count = 0
for name, price in updates.items():
    try:
        cultivo = Cultivo.objects.get(nombre=name)
        old_price = cultivo.precio_madera_referencial
        cultivo.precio_madera_referencial = price
        cultivo.save()
        print(f"✅ Updated {name}: {old_price} -> {price}")
        count += 1
    except Cultivo.DoesNotExist:
        print(f"⚠️  Cultivo not found: {name}")

print(f"\nTotal records updated: {count}")
