from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import boto3
import os
import random
import time

def upload_to_s3(local_file_path, s3_bucket, s3_key):
    """
    Uploads a file to an S3 bucket.
    """
    s3 = boto3.client('s3')
    s3.upload_file(local_file_path, s3_bucket, s3_key)
    print(f"File uploaded to S3: s3://{s3_bucket}/{s3_key}")


def build_driver():
    """
    Builds the Chrome WebDriver used by the extraction functions.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def find_existing_extract(lottery_number, output_folder="./Data/raw/"):
    """
    Returns the path of an already extracted file for this lottery id, or None.

    The sorteo name is only known after extracting, so files are matched by the
    'url_id_<lottery_number>_' part of the name.
    """
    prefix = f"results_raw_lottery_url_id_{lottery_number}_"
    if not os.path.isdir(output_folder):
        return None
    for filename in sorted(os.listdir(output_folder)):
        if filename.startswith(prefix):
            return os.path.join(output_folder, filename)
    return None


def extract_lottery_data(lottery_number, output_folder="./Data/raw/", driver=None):
    """
    Extracts raw lottery data for a given lottery number or the latest lottery.
    Saves the data to a .txt file and optionally uploads it to S3.

    Args:
        lottery_number (int, optional): The ID of the lottery to extract. If None, extracts the latest lottery.
        output_folder (str): Folder where the extracted data will be temporarily saved.
        s3_bucket (str, optional): S3 bucket to upload the extracted file.
        driver (WebDriver, optional): Existing browser session to reuse. When omitted,
            a new one is created and closed before returning.

    Returns:
        str: Path to the saved .txt file.
    """
    # Reuse the caller's browser when given one, so extracting several lotteries
    # does not open a new Chrome per lottery
    owns_driver = driver is None
    if owns_driver:
        driver = build_driver()
    try:
        # Open the target URL
        url = 'https://loteria.org.gt/site/award'
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Close pop-up ad, if the site is currently showing one
        try:
            close_ad = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "ocultarAnuncio"))
            )
            # Click on the "close button" using javascript
            driver.execute_script("arguments[0].click();", close_ad)
        except TimeoutException:
            pass  # No ad shown, nothing to close

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
        # Only close the browser when this call opened it
        if owns_driver:
            driver.quit()


def extract_lottery_range(lottery_numbers, output_folder="./Data/raw/",
                          min_delay=5.0, max_delay=12.0, skip_existing=True):
    """
    Extracts several lotteries in one browser session, pausing between them.

    The pause keeps the request rate close to what a person browsing the site
    would produce, instead of hitting it as fast as the driver allows.

    Args:
        lottery_numbers (iterable): Lottery URL ids to extract, e.g. range(266, 291).
        output_folder (str): Folder where the extracted data will be saved.
        min_delay (float): Lower bound, in seconds, of the pause between lotteries.
        max_delay (float): Upper bound, in seconds, of the pause between lotteries.
        skip_existing (bool): Skip ids already present in output_folder.

    Returns:
        tuple: (extracted paths, skipped paths, failed ids).
    """
    extracted, skipped, failed = [], [], []
    driver = build_driver()
    try:
        for lottery_number in lottery_numbers:
            existing = find_existing_extract(lottery_number, output_folder)
            if skip_existing and existing:
                print(f"Skipping id={lottery_number}, already extracted: {existing}")
                skipped.append(existing)
                continue

            # Pause before every request except the first one actually sent
            if extracted or failed:
                pause = random.uniform(min_delay, max_delay)
                print(f"Waiting {pause:.1f}s before requesting id={lottery_number}...")
                time.sleep(pause)

            try:
                extracted.append(extract_lottery_data(lottery_number, output_folder, driver=driver))
            except Exception as e:
                # One missing or broken id should not stop the rest of the range
                print(f"Could not extract id={lottery_number}: {type(e).__name__}")
                failed.append(lottery_number)
    finally:
        driver.quit()

    print(f"\nExtraction summary: {len(extracted)} new, {len(skipped)} already present, "
          f"{len(failed)} failed")
    if failed:
        print(f"Ids that could not be extracted: {failed}")
    return extracted, skipped, failed
