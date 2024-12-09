from modules.ETL.transformer import transform

# Run the transformer and generate CSV files
sorteos_csv, premios_csv = transform("./miscellaneous")

print(f"Sorteos CSV: {sorteos_csv}")
print(f"Premios CSV: {premios_csv}")
