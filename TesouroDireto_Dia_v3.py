import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import time

# Definir o diretório de download
download_dir = "/home/yair/GHub/TD/data/"

# Configurações do Chrome
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False,  # Desabilitar para evitar bloqueios
    "safebrowsing.disable_download_protection": True,
    "profile.default_content_settings.popups": 0,
    "profile.default_content_setting_values.automatic_downloads": 1,
    "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
})

# Adicionar argumentos para melhor funcionamento
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920x1080')

# Remover arquivos existentes
# try:
#     os.remove("/home/yair/GHub/TD/data/rendimento-resgatar.csv")
#     os.remove("/home/yair/GHub/TD/data/rendimento-investir.csv")
# except FileNotFoundError:
#     pass

# URLs dos arquivos
resgate = "https://www.tesourodireto.com.br/documents/d/guest/rendimento-resgatar-csv"
investe = "https://www.tesourodireto.com.br/documents/d/guest/rendimento-investir-csv"

def wait_for_download(download_path, filename, timeout=30):
    """Aguarda o download ser concluído"""
    full_path = os.path.join(download_path, filename)
    temp_path = full_path + '.crdownload'  # Chrome adiciona .crdownload durante download
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(full_path) and not os.path.exists(temp_path):
            return True
        time.sleep(1)
    return False

# Inicializar o driver
driver = webdriver.Chrome(options=chrome_options)

try:
    print("Iniciando download do arquivo de resgate...")
    driver.get(resgate)
    
    # Aguardar o primeiro download
    if wait_for_download(download_dir, "rendimento-resgatar.csv"):
        print("✓ Arquivo de resgate baixado com sucesso!")
    else:
        print("✗ Timeout no download do arquivo de resgate")
    
    print("Iniciando download do arquivo de investimento...")
    driver.get(investe)
    
    # Aguardar o segundo download
    if wait_for_download(download_dir, "rendimento-investir.csv"):
        print("✓ Arquivo de investimento baixado com sucesso!")
    else:
        print("✗ Timeout no download do arquivo de investimento")

finally:
    driver.quit()  # Use quit() em vez de close() para fechar todas as janelas

# Verificar se os arquivos foram baixados
arquivos_esperados = ["rendimento-resgatar.csv", "rendimento-investir.csv"]
for arquivo in arquivos_esperados:
    caminho_completo = os.path.join(download_dir, arquivo)
    if os.path.exists(caminho_completo):
        tamanho = os.path.getsize(caminho_completo)
        print(f"✓ {arquivo}: {tamanho} bytes")
    else:
        print(f"✗ {arquivo}: não encontrado")