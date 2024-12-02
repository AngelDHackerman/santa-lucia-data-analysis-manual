from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

lotter_number = 177

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
    
    # Wait for the page to load and close add
    close_ad = wait.until(EC.visibility_of_element_located((By.ID, "ocultarAnuncio"))) # //*[@id="ocultarAnuncio"]
    # click on the "close button" using javascript
    driver.execute_script("arguments[0].click();", close_ad)
    
    # Click on the lottery number
    element = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, 'id={lotter_number}')]")))
    driver.execute_script("arguments[0].click();", element)
    time.sleep(10)
    
    # Look for the header
    header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "heading_s1.text-center")))
    # Extract the text information for the winner numbers, date, lotter number and refunds
    header_text = header.text
    print(header_text)
    
    # Look for the body
    body_content = wait.until(EC.presence_of_element_located(
        (By.XPATH, "(//div[@class='card-body']//div[@class='row'])[3]") # # Third 'row' inside 'card-body'
    ))
    # Extract the information for he body card with all the winner numbers, combinations and total prizes 
    body_results = body_content.text
    print(body_results)
    
finally:
    # Close Browser
    driver.quit()
    
