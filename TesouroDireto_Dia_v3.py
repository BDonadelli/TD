import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--window-size=1920x1080')

# Remover arquivos existentes
try:
     os.remove(download_dir+"rendimento-resgatar-velho.csv")
     os.remove(download_dir+"rendimento-investir-velho.csv")
except FileNotFoundError:
    pass
try:
     os.rename(download_dir+"rendimento-resgatar.csv", download_dir+"rendimento-resgatar-velho.csv")
     os.rename(download_dir+"rendimento-investir.csv" , download_dir+"rendimento-investir-velho.csv")
except FileNotFoundError:
     pass

# URLs dos arquivos
resgate = "https://www.tesourodireto.com.br/documents/d/guest/rendimento-resgatar-csv?download=true"
investe = "https://www.tesourodireto.com.br/documents/d/guest/rendimento-investir-csv?download=true"

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
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service,options=chrome_options)

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
    driver.quit()  

# Verificar se os arquivos foram baixados
arquivos_esperados = ["rendimento-resgatar", "rendimento-investir"]
for arquivo in arquivos_esperados:
    caminho_completo = os.path.join(download_dir, arquivo+".csv")
    print(caminho_completo)
    if os.path.exists(caminho_completo):
        tamanho = os.path.getsize(caminho_completo)
        print(f"✓ {arquivo}: {tamanho} bytes")
    else:
        print(f"✗ {arquivo}: não encontrado")
        os.rename( os.path.join(download_dir, arquivo+"-velho.csv"),caminho_completo)


from datetime import datetime
import glob


os.chdir('data')

# 2. Procurar arquivo com formato DD-MM-AAAA_HH-MM-SS
arquivos_antigos = glob.glob('??-??-????_??-??-??.txt')

# 3. Remover arquivo se existir
if arquivos_antigos:
    os.remove(arquivos_antigos[0])
    print(f"Removido: {arquivos_antigos[0]}")

# 4. Criar novo arquivo com timestamp atual
timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
nome_arquivo = f"{timestamp}.txt"

with open(nome_arquivo, 'w', encoding='utf-8') as f:
    f.write(f"Criado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")

print(f"Criado: {nome_arquivo}")        
