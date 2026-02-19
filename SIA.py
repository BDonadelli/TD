import os
from time import sleep
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configurações
data_path = os.path.join(os.getcwd(), "data")
os.makedirs(data_path, exist_ok=True)

# Configurar Chrome
service = Service(ChromeDriverManager().install())
opts = webdriver.ChromeOptions()
opts.add_experimental_option("detach", True)
opts.add_experimental_option("prefs", {
    "download.default_directory": data_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})



# Abrir navegador
driver = webdriver.Chrome(service=service, options=opts)
driver.get('https://statusinvest.com.br/acoes/busca-avancada')

# Definir XPaths
path_busca = '//div/button[contains(@class,"find")]'
path_download = '//*[@id="main-2"]/div[4]/div/div[1]/div[2]/a/span'

# Executar busca
# print('====== Busca')
driver.find_element(By.XPATH, path_busca).click()
sleep(3)

# Download
# print('====== Download')
driver.find_element(By.XPATH, path_download).click()
sleep(3)

driver.quit()
today = date.today().strftime('%d/%m/%Y')


for filename in os.listdir(data_path):
    if 'SI_Acoes' in filename:
        os.remove(data_path+'/'+filename)
os.rename(data_path+'/'+ 'statusinvest-busca-avancada.csv', data_path+'/'+'SI_Acoes.csv')

### Fundamentus 


import requests
import pandas as pd
from io import StringIO

url1 = 'https://www.fundamentus.com.br/resultado.php'
header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
}
r1 = requests.get(url1, headers=header)
dfs = pd.read_html(StringIO(r1.text), decimal=',', thousands='.')[0]

dfs.to_csv("data/fundamentuspp.csv" , sep=';' )
