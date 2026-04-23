
print("==============================================")
print("============== nova atualização ==============")
print("==============================================")

import os
from time import sleep
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
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
    "safebrowsing.enabled": True,
    # Bloqueia imagens e fontes para carregar mais rápido
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.fonts": 2,
})

# Não espera a página carregar 100% — evita o timeout do Selenium
# O script aguarda os elementos específicos que precisa via WebDriverWait
opts.page_load_strategy = 'none'

# Argumentos que reduzem consumo e aumentam velocidade
opts.add_argument('--disable-extensions')
opts.add_argument('--disable-gpu')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--blink-settings=imagesEnabled=false')

# Abrir navegador
service_obj = Service(
    ChromeDriverManager().install(),
    # Aumenta o timeout interno do ChromeDriver para 300s
    service_args=['--timeout=300']
)
driver = webdriver.Chrome(service=service_obj, options=opts)

# Timeout global de página (fallback, em ms)
driver.set_page_load_timeout(180)
driver.set_script_timeout(60)

# WebDriverWait com 30s para elementos (página pode ser lenta)
wait = WebDriverWait(driver, 30)

print('====== Abrindo página')
try:
    driver.get('https://statusinvest.com.br/acoes/busca-avancada')
except TimeoutException:
    # Com page_load_strategy='none' isso não deve ocorrer,
    # mas se ocorrer com outra estratégia, continua mesmo assim
    print('  Timeout no carregamento — continuando (page_load_strategy=none)')

# Aguarda o botão de busca estar presente como sinal de que o DOM está pronto
print('====== Aguardando DOM carregar')
try:
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//div/button[contains(@class,"find")]'))
    )
    print('  DOM pronto')
except TimeoutException:
    print('  ATENÇÃO: botão de busca não encontrado em 60s. A página pode não ter carregado.')

sleep(2)


def fechar_popups():
    """
    Tenta fechar qualquer popup/propaganda visível na página.
    Cobre múltiplos seletores possíveis para ser robusto a mudanças no site.
    """
    seletores = [
        # Botão de fechar por classe comum de modais
        (By.CSS_SELECTOR, '.popup-fixed .btn-close'),   # combina dois identificadores únicos — a div pai popup-fixed e o botão btn-close 
        (By.CSS_SELECTOR, '.modal.open .modal-close'),
        (By.CSS_SELECTOR, '.modal.open button.btn-flat'),
        # Botão de fechar por ícone "close" dentro de modal aberto
        (By.XPATH, '//div[contains(@class,"modal") and contains(@style,"display: block")]//button[.//i[text()="close"]]'),
        (By.XPATH, '//div[contains(@class,"modal") and contains(@style,"display: block")]//i[text()="close"]'),
        # XPath original do script (div[16] — pode mudar conforme a página)
        (By.XPATH, '/html/body/div[16]/div/div/div[1]/button/i'),
        (By.XPATH, '/html/body/div[15]/div/div/div[1]/button/i'),
        (By.XPATH, '/html/body/div[17]/div/div/div[1]/button/i'),
        # Overlay/backdrop genérico
        (By.CSS_SELECTOR, '#plano-invalido-modal .modal-close'),
        (By.CSS_SELECTOR, '#main-modal .modal-close'),
    ]

    fechou = False
    for by, seletor in seletores:
        try:
            elemento = driver.find_element(by, seletor)
            if elemento.is_displayed():
                elemento.click()
                print(f'  Popup fechado com seletor: {seletor}')
                sleep(1)
                fechou = True
                break
        except (NoSuchElementException, ElementClickInterceptedException):
            continue

    if not fechou:
        # Última tentativa: pressionar ESC para fechar qualquer modal aberto
        try:
            from selenium.webdriver.common.keys import Keys
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            sleep(0.5)
        except Exception:
            pass


def clicar_com_retry(xpath, descricao, tentativas=3):
    """
    Tenta clicar num elemento. Se o clique for interceptado por um popup,
    fecha o popup e tenta novamente.
    """
    for i in range(tentativas):
        try:
            elemento = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
            sleep(0.5)
            elemento.click()
            print(f'  {descricao}: OK')
            return True
        except ElementClickInterceptedException:
            print(f'  {descricao}: clique bloqueado por popup (tentativa {i+1}/{tentativas}), tentando fechar...')
            fechar_popups()
            sleep(1)
        except TimeoutException:
            print(f'  {descricao}: elemento não encontrado (tentativa {i+1}/{tentativas})')
            sleep(1)

    # Fallback: clicar via JavaScript
    try:
        elemento = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", elemento)
        print(f'  {descricao}: OK (via JavaScript)')
        return True
    except Exception as e:
        print(f'  {descricao}: FALHOU — {e}')
        return False


# --- Fluxo principal ---

# 1. Fechar popup inicial (se houver)
print('====== Verificando popups iniciais')
fechar_popups()

# 2. Executar busca
print('====== Busca')
path_busca = '//div/button[contains(@class,"find")]'
clicar_com_retry(path_busca, 'Botão Buscar')
sleep(3)

# 3. Fechar popup que pode aparecer após a busca
print('====== Verificando popups pós-busca')
fechar_popups()

# 4. Download
print('====== Download')
path_download = '//*[@id="main-2"]/div[4]/div/div[1]/div[2]/a'
if not clicar_com_retry(path_download, 'Botão Download'):
    # Tenta seletor alternativo (sem o /span no fim)
    path_download_alt = '//a[contains(@class,"btn-download")]'
    clicar_com_retry(path_download_alt, 'Botão Download (alternativo)')

sleep(5)  # Aguarda o arquivo terminar de baixar

driver.quit()

# --- Renomear arquivo baixado ---
today = date.today().strftime('%d/%m/%Y')

for filename in os.listdir(data_path):
    if 'SI_Acoes' in filename:
        os.remove(os.path.join(data_path, filename))

arquivo_origem = os.path.join(data_path, 'statusinvest-busca-avancada.csv')
arquivo_destino = os.path.join(data_path, 'SI_Acoes.csv')

if os.path.exists(arquivo_origem):
    os.rename(arquivo_origem, arquivo_destino)
    print(f'====== Arquivo salvo em: {arquivo_destino}')
else:
    print('====== ATENÇÃO: arquivo CSV não encontrado em data/. Verifique se o download foi concluído.')


# ---  Fundamentus 
 

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

dfs.to_csv("data/fundamentuspp.csv", sep=';', encoding='utf-8', index=False)
