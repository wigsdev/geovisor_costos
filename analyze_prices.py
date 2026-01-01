import pandas as pd
import os

# Load CSV
csv_path = r'c:\Users\WIGUSA\Documents\GitHub\geovisor_costos\data\4.1.4.BD_PRECIOS_MADERAS.csv'

try:
    # Try reading with utf-8 first, fallback to latin-1
    try:
        df = pd.read_csv(csv_path, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='latin-1', on_bad_lines='skip')

    # Clean column names (strip whitespace)
    df.columns = df.columns.str.strip()
    
    print("Columns found:", df.columns.tolist())
    
    # Check if 'AÑO' exists or maybe it's 'AÃ‘O' due to encoding
    if 'AÑO' not in df.columns:
        # Try to find a column that looks like it (e.g. contains 'AÑO' or 'ANO')
        possible_cols = [c for c in df.columns if 'A' in c and 'O' in c and len(c) < 5]
        print(f"Warning: 'AÑO' not found. Possible candidates: {possible_cols}")
        # Attempt to rename if obvious candidate found (optional, for now just print)

    # Filter for MADERABLE and recent years if column exists
    if 'AÑO' in df.columns:
        df_maderable = df[df['RECURSO'] == 'MADERABLE']
        df_recent = df_maderable[df_maderable['AÑO'] >= 2022]
        
        # Interest columns
        interest_cols = ['NOMCOM', 'NOMCIE', 'UNID', 'PRECIO', 'AÑO', 'DEPART']
        
        # Group by Species and Unit to see common units
        summary = df_recent.groupby(['NOMCOM', 'UNID']).agg(
            Avg_Price=('PRECIO', 'mean'),
            Min_Price=('PRECIO', 'min'),
            Max_Price=('PRECIO', 'max'),
            Count=('PRECIO', 'count'),
            Latest_Year=('AÑO', 'max')
        ).sort_values(by=['NOMCOM', 'Count'], ascending=[True, False])
        
        print("Shape of loaded data:", df.shape)
        print("Recent Maderable records:", len(df_recent))
        
        # Display summary for key species if they exist
        target_species = ['EUCALIPTO', 'BOLAINA', 'PINO', 'TORNILLO', 'CAOBA', 'CEDRO', 'MARUPA', 'CAPIRONA', 'TECA', 'SHIHUAHUACO', 'CUMALA']
        
        print("\n--- Summary by Species & Unit (2022-2025) ---")
        for species in target_species:
            # Fuzzy match or contains
            matches = summary[summary.index.get_level_values('NOMCOM').str.contains(species, case=False, na=False)]
            if not matches.empty:
                print(f"\nSPECIES: {species}")
                print(matches)
            else:
                print(f"\nSPECIES: {species} - No recent data found.")
    else:
        print("Critical error: Could not identify Year column.")

except Exception as e:
    print(f"Error analyzing CSV: {e}")
    # Print first few lines of file to debug structure
    with open(csv_path, 'r', encoding='latin-1') as f:
        print("\nFirst 3 lines of file:")
        for _ in range(3):
            print(f.readline().strip())
