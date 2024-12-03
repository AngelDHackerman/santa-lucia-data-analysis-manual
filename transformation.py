import os
import pandas as pd
import re

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
    
    