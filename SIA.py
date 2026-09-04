print("==============================================")
print("============== nova atualização ==============")
print("====== Status Invest e Fundamentus ===========")

import os
import sys
import subprocess
import webbrowser
from time import sleep
from datetime import date

# Configurações
data_path = os.path.join(os.getcwd(), "data")
os.makedirs(data_path, exist_ok=True)

URL_BUSCA = 'https://statusinvest.com.br/acoes/busca-avancada'

# --- Abrir a página no seu navegador comum (sem automação nenhuma) ---
#
# O endpoint de exportação do Status Invest está atrás de uma proteção do
# Cloudflare que detecta sessões controladas via CDP (o protocolo que o
# Selenium usa) e nunca libera o download nelas, mesmo com clique manual.
# A única forma que funciona de verdade é usar seu navegador normal, sem
# nenhum controle automatizado por trás. Por isso essa etapa não usa mais
# Selenium/webdriver: só abrimos a URL no seu navegador padrão do sistema
# (como se você tivesse clicado no link), e o resto é com você.
print('====== Abrindo a página no seu navegador padrão')
try:
    webbrowser.open(URL_BUSCA)
except Exception as e:
    print(f'  Não consegui abrir automaticamente ({e}). Abra manualmente:')
    print(f'  {URL_BUSCA}')

print('====== Ação manual necessária')
print('  👉 Faça login se for pedido, clique em "Buscar" e depois em "Download".')
print('  👉 Salve (ou configure seu navegador pra sempre baixar) o CSV em:')
print(f'     {data_path}')
print(f'  ⏳ Aguardando um arquivo .csv novo aparecer em: {data_path}')
print('     (sem prazo — o script fica esperando; Ctrl+C para cancelar)')


def aguardar_arquivo_novo(arquivos_antes, timeout=None, lembrete_a_cada=20):
    """
    Espera um .csv novo em data_path que não existia antes. Se `timeout`
    for None, espera indefinidamente, imprimindo um lembrete a cada
    `lembrete_a_cada` segundos.
    """
    decorrido = 0.0
    proximo_lembrete = lembrete_a_cada
    while timeout is None or decorrido < timeout:
        atuais = set(os.listdir(data_path))
        novos = [f for f in (atuais - arquivos_antes) if f.endswith('.csv')]
        if novos:
            return novos[0]
        sleep(0.5)
        decorrido += 0.5
        if timeout is None and decorrido >= proximo_lembrete:
            print(f'     ...ainda esperando ({int(decorrido)}s)')
            proximo_lembrete += lembrete_a_cada
    return None


arquivos_antes_download = set(os.listdir(data_path))

try:
    arquivo_baixado = aguardar_arquivo_novo(arquivos_antes_download, timeout=None)
    print(f'  ✅ Arquivo detectado: {arquivo_baixado}')
except KeyboardInterrupt:
    print('\n  Cancelado pelo usuário — encerrando sem o download.')
    sys.exit(0)

# --- Renomear arquivo baixado ---
today = date.today().strftime('%d/%m/%Y')

for filename in os.listdir(data_path):
    if 'SI_Acoes' in filename:
        os.remove(os.path.join(data_path, filename))

# O navegador comum pode salvar com o nome padrão do site, ou com
# sufixo tipo "(1)" se já existia um arquivo com esse nome — pega
# o arquivo novo detectado acima, seja qual for o nome exato.
arquivo_origem = os.path.join(data_path, arquivo_baixado)
arquivo_destino = os.path.join(data_path, 'SI_Acoes.csv')

if os.path.exists(arquivo_origem):
    os.rename(arquivo_origem, arquivo_destino)
    print(f'====== Arquivo salvo em: {arquivo_destino}')
else:
    print('====== ATENÇÃO: arquivo não encontrado no caminho esperado.')


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
print('====== Fundamentus salvo em: data/fundamentuspp.csv')
