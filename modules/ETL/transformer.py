import os
import pandas as pd
import re

def read_files(folder_path):
    # Reads all files starting with 'results_raw' from a folder.
    files = [f for f in os.listdir(folder_path) if f.startswith("results_raw")]
    dataframes = []
    # Add the file name and it's content to a dictionary "dataframes"
    for file in files:
        with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
            lines = f.readlines()
            dataframes.append({"filename": file, "content": lines})
    return dataframes


def split_header_body(content):
    # Limpia las líneas antes de buscar
    content_cleaned = [line.strip() for line in content if line.strip()]
    
    try:
        header_start = content_cleaned.index("HEADER")
        body_start = content_cleaned.index("BODY")
    except ValueError:
        print("Content does not contain 'HEADER' or 'BODY'. Debugging content:")
        # print(content_cleaned)  # Imprime el contenido para depuración
        raise ValueError("The file does not contain expected HEADER or BODY sections.")
    
    header = content_cleaned[header_start + 1 : body_start]
    body = content_cleaned[body_start + 1 :]
    
    return header, body


def process_header(header):
    # print("Debugging header content:")
    # print(header)  # Verificar el contenido del header
    try:
        numero_sorteo = re.search(r"NO. (\d+)", header[0]).group(1)
        tipo_sorteo = re.search(r"SORTEO (\w+)", header[0], re.IGNORECASE).group(1)
        fecha_sorteo = re.search(r"FECHA DEL SORTEO: ([\d/]+)", " ".join(header)).group(1)
        fecha_caducidad = re.search(r"FECHA DE CADUCIDAD: ([\d/]+)", " ".join(header)).group(1)
        premios = re.search(r"PRIMER PREMIO (\d+) \|\|\| SEGUNDO PREMIO (\d+) \|\|\| TERCER PREMIO (\d+)", " ".join(header))
        primer_premio, segundo_premio, tercer_premio = premios.groups()
        reintegros = re.search(r"REINTEGROS ([\d, ]+)", " ".join(header)).group(1).replace(" ", "")
    except AttributeError as e:
        print("An error occurred while processing the HEADER.")
        raise ValueError("The HEADER does not contain the expected format.") from e
    
    return {
        "numero_sorteo": int(numero_sorteo),
        "tipo_sorteo": tipo_sorteo,
        "fecha_sorteo": fecha_sorteo,
        "fecha_caducidad": fecha_caducidad,
        "primer_premio": int(primer_premio),
        "segundo_premio": int(segundo_premio),
        "tercer_premio": int(tercer_premio),
        "reintegros": reintegros
    }



def process_body(body):
    # Processes the BODY and extracts relevant fields.
    premios_data = []
    current_vendedor = None  # Para asociar "VENDIDO POR" con el premio anterior

    print("Processing BODY:")
    for line in body:
        line = line.strip()  # Eliminar espacios en blanco al inicio y final
        print(f"Processing line: {line}")
        
        # Intentar coincidir con una línea de premio
        match = re.match(r"(\d+)\s+(\w+)\s+\.+\s+([\d,]+\.?\d*)", line)
        if match:
            numero_premiado, letras, monto = match.groups()
            monto = float(monto.replace(",", ""))  # Limpiar el monto
            premios_data.append({
                "numero_premiado": numero_premiado,
                "letras": letras,
                "monto": monto,
                "vendido_por": current_vendedor,  # Asociar el vendedor actual (si existe)
            })
            current_vendedor = None  # Resetear el vendedor después de asignarlo
        elif "VENDIDO POR" in line:
            # Capturar vendedor para asociarlo con el premio anterior
            current_vendedor = line.split("VENDIDO POR")[1].strip()
        elif "NO VENDIDO" in line:
            # Asignar "NO VENDIDO" al premio anterior si existe
            if premios_data:
                premios_data[-1]["vendido_por"] = "NO VENDIDO"
        else:
            # Ignorar las líneas que no coinciden (para depuración)
            print(f"Ignored line: {line}")

    print(f"Premios processed: {len(premios_data)}")
    return premios_data





def transform(folder_path, output_folder="./processed"):
    # Orchestrates the complete transformation process and exports to CSV.
    # Read and process files
    dataframes = read_files(folder_path)
    sorteos = []
    premios = []

    for df in dataframes:
        header, body = split_header_body(df["content"])

        # Process HEADER
        sorteos.append(process_header(header))

        # Process BODY
        body_data = process_body(body)
        for premio in body_data:
            premio["numero_sorteo"] = sorteos[-1]["numero_sorteo"]  # Map with the draw number
            premios.append(premio)

    # Convert results to DataFrames
    sorteos_df = pd.DataFrame(sorteos)
    premios_df = pd.DataFrame(premios)
    
    # Transform the column 'reintegros' into 3 different columns for better analysis
    sorteos_df[[
        'reintegro_primer_premio', 
        'reintegro_segundo_premio', 
        'reintegro_tercer_premio'
        ]] = sorteos_df['reintegros'].str.split(',', expand=True)
    
    # Remove the original 'reintegros' column
    sorteos_df.drop(columns=['reintegros'], inplace=True)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # reorder columns for "premios" (body dataframe)
    columns_order = ["numero_sorteo", "numero_premiado", "letras", "monto", "vendido_por"]
    premios_df = pd.DataFrame(premios, columns=columns_order)
    
    # Validate sorteos DataFrame
    if sorteos_df.isnull().values.any():
        print("Null values detected in sorteos.csv. Removing invalid rows")
        sorteos_df.dropna(inplace=True) # Remove rows with null values
        
    # Validate premios DataFrame
    if premios_df.isnull().values.any():
        print("Null values detected in premios.csv. Filling missing data.")
        premios_df['vendido_por'] = premios_df['vendido_por'].fillna("Vendedor desconocido")  # Replace nulls with default value
        premios_df.dropna(inplace=True) # Remove rows with null values

    # Export DataFrames to CSV
    sorteos_csv = os.path.join(output_folder, "sorteos.csv")
    premios_csv = os.path.join(output_folder, "premios.csv")
    sorteos_df.to_csv(sorteos_csv, index=False)
    premios_df.to_csv(premios_csv, index=False)

    print(f"Exported sorteos to {sorteos_csv}")
    print(f"Exported premios to {premios_csv}")
    # print(header)
    

    return sorteos_csv, premios_csv
