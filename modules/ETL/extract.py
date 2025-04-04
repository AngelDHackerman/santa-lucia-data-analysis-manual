from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import boto3
import os
import time

def upload_to_s3(local_file_path, s3_bucket, s3_key):
    """
    Uploads a file to an S3 bucket.
    """
    s3 = boto3.client('s3')
    s3.upload_file(local_file_path, s3_bucket, s3_key)
    print(f"File uploaded to S3: s3://{s3_bucket}/{s3_key}")

def extract_lottery_data(lottery_number, output_folder="./Data/raw/"):
    """
    Extracts raw lottery data for a given lottery number or the latest lottery.
    Saves the data to a .txt file and optionally uploads it to S3.

    Args:
        lottery_number (int, optional): The ID of the lottery to extract. If None, extracts the latest lottery.
        output_folder (str): Folder where the extracted data will be temporarily saved.
        s3_bucket (str, optional): S3 bucket to upload the extracted file.

    Returns:
        str: Path to the saved .txt file.
    """
    # Configure WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    try:
        # Open the target URL
        url = 'https://loteria.org.gt/site/award'
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Close pop-up ad
        close_ad = wait.until(EC.visibility_of_element_located((By.ID, "ocultarAnuncio")))
        # Click on the "close button" using javascript
        driver.execute_script("arguments[0].click();", close_ad)

        # Click on the lottery number link
        element = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, 'id={lottery_number}')]")))
        driver.execute_script("arguments[0].click();", element)
        time.sleep(5)  # Allow time for the information to load

        # Extract HEADER information
        header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "heading_s1.text-center")))
        header_text = header.text.strip()
        header_text = "\n".join(filter(lambda line: line.strip() != "", header_text.splitlines()))

        # Extract filename from HEADER
        header_sorteo_number = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text.strip()
        header_sorteo_number = header_sorteo_number.lower()
        header_filename = header_sorteo_number.replace(" ", "_")

        # Extract BODY information
        body_content = wait.until(EC.presence_of_element_located(
            (By.XPATH, "(//div[@class='card-body']//div[@class='row'])[3]")  # Third 'row' inside 'card-body'
        ))
        body_results = body_content.text

        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Save data to a .txt file
        output_path = os.path.join(output_folder, f"results_raw_lottery_url_id_{lottery_number}_{header_filename}.txt")
        with open(output_path, "w", encoding="utf-8") as file:
            file.write("HEADER\n")
            file.write(header_text + "\n\n")
            file.write("BODY\n")
            if not body_results.startswith("00MIL"):
                file.write("CENTENARES\n")  # Add title to the first group
            file.write(body_results)

        print(f"Data extracted and saved to: {output_path}")
        return output_path
    finally:
        # Always close the browser
        driver.quit()
