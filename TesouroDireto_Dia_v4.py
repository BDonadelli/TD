import pandas as pd
import requests
import os
from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Definir o diretório de download
download_dir = "/home/yair/GHub/TD/data/"

# Garantir que o diretório existe
Path(download_dir).mkdir(parents=True, exist_ok=True)

# Remover arquivos existentes
arquivos_para_remover = [
    "rendimento-resgatar.csv",
    "rendimento-investir.csv"
]

for arquivo in arquivos_para_remover:
    try:
        os.remove(os.path.join(download_dir, arquivo))
        print(f"Arquivo {arquivo} removido")
    except FileNotFoundError:
        print(f"Arquivo {arquivo} não encontrado (ok)")

def setup_driver():
    """Configura o driver do Chrome com configurações anti-detecção"""
    chrome_options = Options()
    
    # Configurações de download
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1,
    })
    
    # Configurações anti-detecção
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Para debug, comentar a linha abaixo
    # chrome_options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Remover propriedades que indicam automação
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    return driver

def wait_for_download(filename, timeout=60):
    """Aguarda o download ser concluído"""
    full_path = os.path.join(download_dir, filename)
    temp_path = full_path + '.crdownload'
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(full_path) and not os.path.exists(temp_path):
            size = os.path.getsize(full_path)
            if size > 0:  # Arquivo não vazio
                return True
        time.sleep(2)
    return False

def download_tesouro_direto():
    """Baixa os arquivos do Tesouro Direto usando Selenium"""
    driver = setup_driver()
    
    try:
        print("=== MÉTODO 1: TENTANDO URLs DIRETAS COM SELENIUM ===")
        
        urls = {
            "rendimento-resgatar.csv": "https://www.tesourodireto.com.br/documents/d/guest/rendimento-resgatar-csv?download=true",
            "rendimento-investir.csv": "https://www.tesourodireto.com.br/documents/d/guest/rendimento-investir-csv?download=true"
        }
        
        # Primeiro, visitar a página principal para estabelecer sessão
        print("Visitando página principal...")
        driver.get("https://www.tesourodireto.com.br/")
        time.sleep(5)
        
        # Aceitar cookies se necessário
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceitar') or contains(text(), 'Accept')]"))
            )
            cookie_button.click()
            print("Cookies aceitos")
            time.sleep(2)
        except:
            print("Botão de cookies não encontrado ou não necessário")
        
        # Tentar baixar cada arquivo
        for filename, url in urls.items():
            print(f"\n--- Baixando {filename} ---")
            
            try:
                print(f"Acessando: {url}")
                driver.get(url)
                time.sleep(3)
                
                # Verificar se houve redirecionamento ou erro
                current_url = driver.current_url
                print(f"URL atual: {current_url}")
                
                if "403" in driver.page_source or "forbidden" in driver.page_source.lower():
                    print("❌ Acesso negado (403)")
                    continue
                
                # Aguardar o download
                print("Aguardando download...")
                if wait_for_download(filename, timeout=30):
                    filepath = os.path.join(download_dir, filename)
                    size = os.path.getsize(filepath)
                    print(f"✅ {filename} baixado com sucesso! ({size} bytes)")
                else:
                    print(f"❌ Timeout no download de {filename}")
                    
            except Exception as e:
                print(f"❌ Erro ao baixar {filename}: {e}")
        
        print("\n=== MÉTODO 2: NAVEGAÇÃO PELA PÁGINA DE PREÇOS ===")
        
        # Tentar navegar pela página de preços e taxas
        try:
            print("Navegando para página de preços e taxas...")
            driver.get("https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm")
            time.sleep(5)
            
            print(f"Título da página: {driver.title}")
            
            # Procurar por botões ou links de download/export
            download_elements = []
            
            # Diferentes seletores para procurar
            selectors = [
                "//a[contains(@href, 'csv')]",
                "//button[contains(text(), 'CSV')]",
                "//a[contains(text(), 'Download')]",
                "//button[contains(text(), 'Export')]",
                "//*[contains(@class, 'download')]",
                "//*[contains(@onclick, 'csv')]"
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    download_elements.extend(elements)
                except:
                    continue
            
            if download_elements:
                print(f"Encontrados {len(download_elements)} elementos de download:")
                for i, elem in enumerate(download_elements[:10]):  # Máximo 10
                    try:
                        tag = elem.tag_name
                        text = elem.text[:50] if elem.text else "sem texto"
                        href = elem.get_attribute('href') or "sem href"
                        onclick = elem.get_attribute('onclick') or "sem onclick"
                        print(f"  {i+1}. {tag}: '{text}' | href: {href} | onclick: {onclick}")
                    except:
                        print(f"  {i+1}. Elemento não acessível")
                
                # Tentar clicar no primeiro elemento promissor
                for elem in download_elements[:3]:
                    try:
                        if 'csv' in (elem.get_attribute('href') or '').lower() or \
                           'csv' in elem.text.lower():
                            print(f"Tentando clicar em: {elem.text}")
                            elem.click()
                            time.sleep(5)
                            break
                    except:
                        continue
            else:
                print("Nenhum elemento de download encontrado")
                
                # Mostrar o HTML da página para debug
                print("\n--- CONTEÚDO DA PÁGINA (primeiros 1000 chars) ---")
                page_source = driver.page_source[:1000]
                print(page_source)
                
        except Exception as e:
            print(f"Erro na navegação: {e}")
        
        print("\n=== MÉTODO 3: TENTANDO API/JSON ===")
        
        # Tentar encontrar chamadas de API que retornem dados JSON
        try:
            # Verificar se existe algum endpoint JSON
            json_urls = [
                "https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json",
                "https://www.tesourodireto.com.br/api/dados",
                "https://www.tesourodireto.com.br/data/precos"
            ]
            
            for json_url in json_urls:
                try:
                    print(f"Testando API: {json_url}")
                    driver.get(json_url)
                    time.sleep(3)
                    
                    if "json" in driver.page_source.lower() or "{" in driver.page_source:
                        print("✅ Dados JSON encontrados!")
                        json_data = driver.page_source
                        print(f"Primeiros 200 chars: {json_data[:200]}")
                        
                        # Salvar os dados JSON para análise
                        with open(os.path.join(download_dir, "api_data.json"), "w") as f:
                            f.write(json_data)
                        break
                        
                except Exception as e:
                    print(f"Erro com {json_url}: {e}")
                    
        except Exception as e:
            print(f"Erro na busca por APIs: {e}")
        
        # Pausa para análise manual (remover em produção)
        print("\n=== ANÁLISE MANUAL ===")
        print("O navegador está aberto. Você pode:")
        print("1. Inspecionar elementos na página")
        print("2. Verificar a aba Network no DevTools")
        print("3. Procurar manualmente por opções de download")
        input("Pressione Enter quando terminar...")
        
    except Exception as e:
        print(f"Erro geral: {e}")
    
    finally:
        driver.quit()

def verificar_downloads():
    """Verifica quais arquivos foram baixados com sucesso"""
    print("\n=== RELATÓRIO FINAL ===")
    arquivos_esperados = ["rendimento-resgatar.csv", "rendimento-investir.csv"]
    
    for arquivo in arquivos_esperados:
        caminho_completo = os.path.join(download_dir, arquivo)
        if os.path.exists(caminho_completo):
            tamanho = os.path.getsize(caminho_completo)
            if tamanho > 0:
                print(f"✅ {arquivo}: {tamanho} bytes")
                
                # Tentar ler as primeiras linhas
                try:
                    with open(caminho_completo, 'r', encoding='utf-8') as f:
                        primeira_linha = f.readline().strip()
                        print(f"   Primeira linha: {primeira_linha[:100]}...")
                except Exception as e:
                    try:
                        with open(caminho_completo, 'r', encoding='latin-1') as f:
                            primeira_linha = f.readline().strip()
                            print(f"   Primeira linha (latin-1): {primeira_linha[:100]}...")
                    except:
                        print(f"   Erro ao ler arquivo: {e}")
            else:
                print(f"❌ {arquivo}: arquivo vazio")
        else:
            print(f"❌ {arquivo}: não encontrado")

if __name__ == "__main__":
    print("=== DOWNLOAD TESOURO DIRETO COM BYPASS CLOUDFLARE ===")
    download_tesouro_direto()
    verificar_downloads()