import os
import pandas as pd
import re


def read_files(folder_path):
    # Reads all files starting with 'results_raw' from a folder.
    files = [f for f in os.listdir(folder_path) if f.startswith("results_raw")]
    dataframes = []
    for file in files:
        with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
            lines = f.readlines()
            dataframes.append({"filename": file, "content": lines})
    return dataframes


def split_header_body(content):
    # Splits content into HEADER and BODY sections.
    try:
        header_start = content.index("HEADER\\n")
        body_start = content.index("BODY\\n")
    except ValueError:
        raise ValueError("The file does not contain expected HEADER or BODY sections.")
    
    header = content[header_start + 1 : body_start]
    body = content[body_start + 1 :]
    
    # Clean up empty lines and extra spaces
    header = [line.strip() for line in header if line.strip()]
    body = [line.strip() for line in body if line.strip()]
    
    return header, body


def process_header(header):
    # Processes the HEADER and extracts relevant fields.
    try:
        numero_sorteo = re.search(r"NO. (\\d+)", header[0]).group(1)
        tipo_sorteo = re.search(r"SORTEO (\\w+)", header[0], re.IGNORECASE).group(1)
        fecha_sorteo = re.search(r"FECHA DEL SORTEO: ([\\d/]+)", " ".join(header)).group(1)
        fecha_caducidad = re.search(r"FECHA DE CADUCIDAD: ([\\d/]+)", " ".join(header)).group(1)
        premios = re.search(r"PRIMER PREMIO (\\d+) \\|\\|\\| SEGUNDO PREMIO (\\d+) \\|\\|\\| TERCER PREMIO (\\d+)", " ".join(header))
        primer_premio, segundo_premio, tercer_premio = premios.groups()
        reintegros = re.search(r"REINTEGROS ([\\d, ]+)", " ".join(header)).group(1).replace(" ", "")
    except AttributeError:
        raise ValueError("The HEADER does not contain the expected format.")
    
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
    for line in body:
        match = re.match(r"(\\d+)\\s+(\\w+)\\s+\\.\\.\\.\\s+([\\d,]+\\.?\\d*)", line)
        if match:
            numero_premiado, letras, monto = match.groups()
            vendedor = None
            if "VENDIDO POR" in line:
                vendedor = line.split("VENDIDO POR")[1].strip()
            premios_data.append({
                "numero_premiado": numero_premiado,
                "letras": letras,
                "monto": float(monto.replace(",", "")),
                "vendido_por": vendedor
            })
        else:
            print(f"Ignored line: {line}")
    return premios_data


def transform(folder_path, output_folder="./processed"):
    """Orchestrates the complete transformation process and exports to CSV."""
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

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Export DataFrames to CSV
    sorteos_csv = os.path.join(output_folder, "sorteos.csv")
    premios_csv = os.path.join(output_folder, "premios.csv")
    sorteos_df.to_csv(sorteos_csv, index=False)
    premios_df.to_csv(premios_csv, index=False)

    print(f"Exported sorteos to {sorteos_csv}")
    print(f"Exported premios to {premios_csv}")

    return sorteos_csv, premios_csv
