from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

lottery_number = 177

# Setup for ChromeDriver
driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Look for the lottery number
try:
    url = 'https://loteria.org.gt/site/award' # Target URL
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    # Wait and close the pop up
    close_ad = wait.until(EC.visibility_of_element_located((By.ID, "ocultarAnuncio"))) # //*[@id="ocultarAnuncio"]
    # click on the "close button" using javascript
    driver.execute_script("arguments[0].click();", close_ad)
    
    # Click on the lottery number
    element = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, 'id={lottery_number}')]")))
    driver.execute_script("arguments[0].click();", element)
    time.sleep(5) # give time to load information of the lottery
    
    # Look and extract the main information in the header
    header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "heading_s1.text-center")))
    header_text = header.text.strip()
    # Remove extra newlines from the header
    header_text = "\n".join(filter(lambda line: line.strip() != "", header_text.splitlines()))
    
    # Extract information for th file name
    header_sorteo_number = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text.strip()
    header_sorteo_number = header_sorteo_number.lower()
    
    # Format the header text for the filename
    header_filename = header_sorteo_number.replace(" ", "_")
    
    # Extract the information for he body card with all the winner numbers, combinations and total prizes 
    body_content = wait.until(EC.presence_of_element_located(
        (By.XPATH, "(//div[@class='card-body']//div[@class='row'])[3]") # # Third 'row' inside 'card-body'
    ))
    body_results = body_content.text
    
    # Save in a .txt file
    with open(f"./miscellaneous/results_raw_lottery_url_id_{lottery_number}_{header_filename}.txt", "w", encoding="utf-8") as file:
        file.write("HEADER\n")
        file.write(header_text + "\n\n")
        file.write("BODY\n")
        # Check if the first group lacks a title
        if not body_results.startswith("00MIL"):
            file.write("CENTENARES\n") # Add title to the first group
            
        file.write(body_results)
    
    print(f"Information extracted and saved in 'results_raw_loterry_url_id_{lottery_number}_{header_filename}.txt")
finally:
    # Close Browser
    driver.quit()
    
