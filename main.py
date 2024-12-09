from modules.ETL.extract import extract_lottery_data
from modules.ETL.transformer import read_files, split_header_body, process_header, process_body, transform
from modules.ETL.loader import get_secret, connect_to_db, load_csv_to_table, close_db_connection

def main():
    # Step 1: Extract
    lottery_number = 207
    output_path = extract_lottery_data(lottery_number)
    print(f"Extracted file saved to: {output_path}")
    
    
    # Step 3: Load
    # user, password, host, db_name = get_secret()
    # connect_to_db(user, password, host, db_name)
    
if __name__ == "__main__":
    main()