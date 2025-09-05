
'''
para executar no terminal, atualiza 'tesouro_direto.json' 
'''
url = 'https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json'
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')  # modo sem GUI
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

driver.get(url)
page_source = driver.page_source
start = page_source.find("{")
end = page_source.rfind("}") + 1
json_text = page_source[start:end]
import json
data_json = json.loads(json_text)
driver.close()

from pathlib import Path
# Caminho relativo à localização do script
output_path = Path(__file__).resolve().parent / 'data' / 'tesouro_direto.json'

with open(output_path, 'w', encoding='utf-8') as json_file:
    json.dump(data_json, json_file, ensure_ascii=False, indent=4)
    
