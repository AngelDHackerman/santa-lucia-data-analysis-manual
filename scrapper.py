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
    driver.execute_script("arguments[0].click();", close_ad)
    
    # Click on the lottery number
    element = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, 'id={lotter_number}')]")))
    driver.execute_script("arguments[0].click();", element)
    time.sleep(10)
finally:
    # Close Browser
    driver.quit()