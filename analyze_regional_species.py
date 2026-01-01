import pandas as pd
import sys

# Analysis Configuration
CSV_PATH = r'c:\Users\WIGUSA\Documents\GitHub\geovisor_costos\data\4.1.4.BD_PRECIOS_MADERAS.csv'

def generate_report():
    print("=== INFORME DE ESPECIES MADERABLES REPRESENTATIVAS POR REGIÓN ===")
    print("Fuente: 4.1.4.BD_PRECIOS_MADERAS.csv")
    print("Criterio: Especies 'MADERABLE' con mayor frecuencia de reportes de precios (2016-2025)\n")

    try:
        # 1. Load Data
        try:
            df = pd.read_csv(CSV_PATH, encoding='utf-8', on_bad_lines='skip')
        except UnicodeDecodeError:
            df = pd.read_csv(CSV_PATH, encoding='latin-1', on_bad_lines='skip')

        # Clean headers
        df.columns = df.columns.str.strip()

        # 2. Filter Maderable
        if 'RECURSO' in df.columns:
            df = df[df['RECURSO'] == 'MADERABLE']
        else:
            print("ERROR: Columna 'RECURSO' no encontrada.")
            return

        # 3. Handle Departments
        if 'DEPART' not in df.columns:
            print("ERROR: Columna 'DEPART' no encontrada.")
            return

        # Get top 7 departments by activity (assuming these are the '7 regions' or covering them)
        top_depart = df['DEPART'].value_counts().head(10) # Show top 10 to be safe
        
        print(f"Regiones encontradas en la BD (Ordenadas por volumen de datos):")
        print(top_depart)
        print("\n" + "="*60 + "\n")

        # 4. Analyze each Region
        # We focus on the departments present in the data
        regions_of_interest = df['DEPART'].unique()
        
        for region in sorted(regions_of_interest):
            if pd.isna(region): continue
            
            print(f"📍 REGIÓN: {region}")
            
            # Subset for region
            df_reg = df[df['DEPART'] == region]
            
            # Count species occurrences (proxy for representativeness/trade activity)
            species_counts = df_reg['NOMCOM'].value_counts().head(5)
            
            if species_counts.empty:
                print("   (Sin datos de especies)")
                continue

            for species, count in species_counts.items():
                # Get scientific name (most common for this common name)
                sci_name = df_reg[df_reg['NOMCOM'] == species]['NOMCIE'].mode()
                sci_name = sci_name.iloc[0] if not sci_name.empty else "S/D"
                
                # Get Avg Price for most common unit to give context
                # Find most common unit for this species in this region
                common_unit_series = df_reg[df_reg['NOMCOM'] == species]['UNID'].mode()
                common_unit = common_unit_series.iloc[0] if not common_unit_series.empty else "N/A"
                
                # Calc avg price for that unit
                avg_price_series = df_reg[(df_reg['NOMCOM'] == species) & (df_reg['UNID'] == common_unit)]['PRECIO']
                avg_price = avg_price_series.mean()
                
                print(f"   - {species:<20} | {sci_name:<25} | Registros: {count:>3} | Precio prom ({common_unit}): {avg_price:.2f}")
            
            print("-" * 60)

    except FileNotFoundError:
        print(f"ERROR: Archivo no encontrado en {CSV_PATH}")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    generate_report()
