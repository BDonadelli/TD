import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

# Configura o diretório de download
download_dir = "/tmp/downloads_td"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Configurações do Chrome
chrome_options = Options()
# A linha abaixo é útil para rodar em ambientes sem interface gráfica (ex: servidor)
# chrome_options.add_argument("--headless")
chrome_options.add_experimental_option(
    "prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
)
chrome_options.add_argument("--window-size=1920,1080")

# Inicializa o navegador
try:
    service = Service()  # O selenium gerencia o driver automaticamente
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("Navegador iniciado. Acessando a página de rendimentos...")
    
    # URL da página que contém o link de download
    url_pagina = "https://www.tesourodireto.com.br/titulos/rendimento-e-imposto-de-renda.htm"
    driver.get(url_pagina)
    
    # Dá um tempo para a página carregar
    time.sleep(5) 
    
    # Encontra o botão de download pelo seu link e clica nele
    # O link do botão de download é o mesmo que você tentou usar
    print("Tentando encontrar o botão de download...")
    link_download = driver.find_element(By.CSS_SELECTOR, 'a[href*="rendimento-resgatar-csv"]')
    link_download.click()
    
    print("Clique no botão de download realizado. Aguardando o download...")
    
    # Aguarda um tempo para o download ser concluído
    time.sleep(10) 
    
    # Localiza o arquivo baixado
    caminho_arquivo = os.path.join(download_dir, "Rendimento_e_IR.csv")
    
    # Verifica se o arquivo foi baixado e carrega com pandas
    if os.path.exists(caminho_arquivo):
        print("Arquivo CSV baixado com sucesso! Lendo com pandas...")
        df = pd.read_csv(caminho_arquivo, sep=';', decimal=',')
        print(df.head())
        print("\nDataFrame carregado com sucesso!")
        print(df.info())
    else:
        print("O arquivo não foi encontrado. Verifique se o download foi concluído corretamente.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
finally:
    if 'driver' in locals():
        driver.quit()
        print("Navegador fechado.")
