# %%
import os
import pandas as pd
import re

# %%
# Read and Load files from miscellaneous

folder_path = "./miscellaneous"
files = [f for f in os.listdir(folder_path) if f.startswith("results_raw")]

dataframes = [] # archive processed data by file

for file in files:
    file_path = os.path.join(folder_path, file)
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # Store content for later processing
        dataframes.append({"filename": file, "content": lines})

# %%
# Spread Header from Body
for df in dataframes:
    content = df["content"]
    header_start = content.index("HEADER\n")
    body_start = content.index("BODY\n")
    
    header_data = content[header_start + 1 : body_start] # slicing between HEADER and BODY
    body_data = content[body_start + 1 : ] # From BODY until the end of the file
    
    # Remove blank lines and extra spaces
    header_data = [line.strip() for line in header_data if line.strip()]
    body_data = [line.strip() for line in body_data if line.strip()]
    
    df["header"] = header_data
    df["body"] = body_data
    

# %% [markdown]
# ### Process HEADER
# 1. Extract the relevant fields like `numero_sorteo`, `primer_premio`, `fecha_sorteo`, etc., using regular expressions.
# 2. Create a DataFrame for the "sorteos" table.

# %%
# Extract the header data
sorteos_data = []
for df in dataframes:
    header = df["header"]
    numero_sorteo = re.search(r"NO. (\d+)", header[0]).group(1)
    tipo_sorteo = re.search(r"SORTEO (\w+)", header[0], re.IGNORECASE).group(1)
    fecha_sorteo = re.search(r"FECHA DEL SORTEO: ([\d/]+)", " ".join(header)).group(1)
    fecha_caducidad = re.search(r"FECHA DE CADUCIDAD: ([\d/]+)", " ".join(header)).group(1)
    premios = re.search(r"PRIMER PREMIO (\d+) \|\|\| SEGUNDO PREMIO (\d+) \|\|\| TERCER PREMIO (\d+)", " ".join(header))
    primer_premio, segundo_premio, tercer_premio = premios.groups()
    reintegros = re.search(r"REINTEGROS ([\d, ]+)", " ".join(header)).group(1).replace(" ", "")
    
    sorteos_data.append({
        "numero_sorteo": numero_sorteo,
        "tipo_sorteo": tipo_sorteo,
        "fecha_sorteo": fecha_sorteo,
        "fecha_caducidad": fecha_caducidad,
        "primer_premio": primer_premio,
        "segundo_premio": segundo_premio,
        "tercer_premio": tercer_premio,
        "reintegros": reintegros
    })

sorteos_df = pd.DataFrame(sorteos_data)

# Transform the column 'reintegros' into 3 different columns for better analysis
sorteos_df[[
    'reintegro_primer_premio', 
    'reintegro_segundo_premio', 
    'reintegro_tercer_premio'
    ]] = sorteos_df['reintegros'].str.split(',', expand=True)

# Convert the columns into a proper type
sorteos_df['numero_sorteo'] = sorteos_df['numero_sorteo'].astype(int)
sorteos_df['tipo_sorteo'] = sorteos_df['tipo_sorteo'].astype(str)
sorteos_df['primer_premio'] = sorteos_df['primer_premio'].astype(int)
sorteos_df['segundo_premio'] = sorteos_df['segundo_premio'].astype(int)
sorteos_df['tercer_premio'] = sorteos_df['tercer_premio'].astype(int)
sorteos_df['reintegro_primer_premio'] = sorteos_df['reintegro_primer_premio'].astype(int)
sorteos_df['reintegro_segundo_premio'] = sorteos_df['reintegro_segundo_premio'].astype(int)
sorteos_df['reintegro_tercer_premio'] = sorteos_df['reintegro_tercer_premio'].astype(int)

# Remove the 'reintegros' column
sorteos_df.drop(columns=['reintegros'], inplace=True)

sorteos_df

# %% [markdown]
# ### Process BODY
# 1. Split the data into `premios`, `terminaciones`, and `combinaciones_especiales`.
# 2. Identify reward patterns (`numero_premiado`, `letras`, `monto`) and `vendedor`.

# %%
premios_data = []

for df in dataframes:
    body = df["body"]
    for line in body:
        match = re.match(r"(\d+)\s+(\w+)\s+\.+\s+([\d,]+\.?\d*)", line)
        if match:
            numero_premiado, letras, monto = match.groups()
            vendedor = None
            if "VENDIDO POR" in line:
                vendedor = line.split("VENDIDO POR")[1].strip()
                
            premios_data.append({
                "numero_sorteo": df["filename"], # # You can map this with `numero_sorteo`
                "numero_premiado": numero_premiado,
                "letras": letras,
                "monto": monto.replace(",", ""),
                "vendido_por": vendedor
            })
        else:
            print(f"Línea ignorada en {df['filename']}: {line}")
premios_df = pd.DataFrame(premios_data)
premios_df['numero_sorteo'] = premios_df['numero_sorteo'].str.extract(r'no\._(\d+)', expand=False)
premios_df

# %%
premios_df.info()


