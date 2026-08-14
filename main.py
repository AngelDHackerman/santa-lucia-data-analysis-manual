import os
from modules.ETL.extract import extract_lottery_range
from modules.ETL.transformer import transform

def main():
    # Step 1: Extract
    # Range of lottery URL ids to extract. These are the ids in the award-detail
    # URL, not the sorteo numbers: id=266 is sorteo 409, id=290 is sorteo 3132.
    # Ids already present in ./Data/raw/ are skipped.
    lottery_numbers = range(266, 291)

    extracted, skipped, failed = extract_lottery_range(lottery_numbers)
    print(f"Extracted {len(extracted)} new file(s), skipped {len(skipped)} already present.")
    if failed:
        print(f"Could not extract these ids, they are left out of this run: {failed}")

    # Step 2: Transform the raw data
    input_folder = "./Data/raw/"
    output_folder = "./Data/processed"
    
    try:
        sorteos_csv, premios_csv = transform(input_folder, output_folder)
        print(f"Processing completed. CSVs generated:\n - Sorteos: {sorteos_csv}\n - Premios: {premios_csv}")
    except Exception as e:
        print(f"An error occurred during transformation: {e}")
        return  # Exit on error#

if __name__ == "__main__":
    main()

