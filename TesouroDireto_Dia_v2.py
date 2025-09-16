import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())

chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": "/home/yair/GHub/TD/data/",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "safebrowsing.disable_download_protection": True,
    "profile.default_content_settings.popups": 0,
    "profile.default_content_setting_values.automatic_downloads": 1
})
chrome_options.add_argument('--headless')  # modo sem GUI

# try:
#     os.remove("/home/yair/GHub/TD/data/rendimento-resgatar.csv")
#     os.remove("/home/yair/GHub/TD/data/rendimento-investir.csv")    
# except :   
#     pass

resgate = "https://www.tesourodireto.com.br/documents/d/guest/rendimento-resgatar-csv?download=true"
investe = "https://www.tesourodireto.com.br/documents/d/guest/rendimento-investir-csv?download=true"

driver = webdriver.Chrome(service=service,options=chrome_options)
driver.get(resgate)
driver.get(investe)
driver.close()