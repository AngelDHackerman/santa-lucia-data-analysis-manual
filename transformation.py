import os
import pandas as pd
import re

# Load files from miscellaneous
folder_path = "./miscellaneous"
files = [f for f in os.listdir(folder_path) if f.startswith("results_raw")]

dataframes = [] # archive processed data by file

for file in files:
    pass