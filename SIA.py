print("==============================================")
print("============== nova atualização ==============")
print("====== Status Invest e Fundamentus ===========")

import os
import sys
import webbrowser
from time import sleep
from datetime import date

import requests
import pandas as pd
from io import StringIO

import gspread
from google.oauth2.service_account import Credentials

# Configurações
#
# Usamos o diretório do próprio script (não os.getcwd()) para que o
# comportamento não dependa de onde o script foi chamado.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, "data")
os.makedirs(data_path, exist_ok=True)

URL_BUSCA = 'https://statusinvest.com.br/acoes/busca-avancada'

CREDENCIAIS_PATH = os.path.join(BASE_DIR, 'google_credentials.json')
SPREADSHEET_ID = '1Mse441x9H8uByQkSTVngIKUmH5iBFwEuhGjo1LhqGE8'


# --- Limpar CSVs residuais de execuções anteriores ---
#
# Se uma execução anterior falhou antes de renomear o arquivo baixado
# (ou antes de gerar o fundamentuspp.csv), pode sobrar um .csv "órfão"
# na pasta. Se ele ficar lá, ele entra em `arquivos_antes` do próximo
# ciclo de espera e o script nunca vai reconhecer o próximo download
# como "novo". Por isso limpamos todo .csv da pasta antes de começar
# (os dois arquivos finais são sempre regenerados nesta mesma execução).
for filename in os.listdir(data_path):
    if filename.endswith('.csv'):
        os.remove(os.path.join(data_path, filename))


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
    `lembrete_a_cada` segundos. Se mais de um .csv novo aparecer (ex.:
    o navegador salvou um "(1)" de uma tentativa duplicada), pega o
    modificado mais recentemente em vez de um elemento arbitrário do set.
    """
    decorrido = 0.0
    proximo_lembrete = lembrete_a_cada
    while timeout is None or decorrido < timeout:
        atuais = set(os.listdir(data_path))
        novos = [f for f in (atuais - arquivos_antes) if f.endswith('.csv')]
        if novos:
            novos.sort(
                key=lambda f: os.path.getmtime(os.path.join(data_path, f)),
                reverse=True,
            )
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

arquivo_origem = os.path.join(data_path, arquivo_baixado)
arquivo_destino = os.path.join(data_path, 'SI_Acoes.csv')

if os.path.exists(arquivo_origem):
    os.rename(arquivo_origem, arquivo_destino)
    print(f'====== Arquivo salvo em: {arquivo_destino}')
else:
    print('====== ATENÇÃO: arquivo não encontrado no caminho esperado.')


# --- Fundamentus ---

url1 = 'https://www.fundamentus.com.br/resultado.php'
header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
}

try:
    r1 = requests.get(url1, headers=header, timeout=30)
    r1.raise_for_status()
    dfs = pd.read_html(StringIO(r1.text), decimal=',', thousands='.')[0]
    dfs.to_csv(os.path.join(data_path, "fundamentuspp.csv"), sep=';', encoding='utf-8', index=False)
    print(f'====== Fundamentus salvo em: {os.path.join(data_path, "fundamentuspp.csv")}')
except requests.RequestException as e:
    print(f'  ⚠️ Falha ao buscar dados do Fundamentus ({e}) — pulando essa etapa.')
except (ValueError, IndexError) as e:
    print(f'  ⚠️ Não consegui interpretar a tabela do Fundamentus ({e}) '
          f'— o site pode ter mudado de estrutura. Pulando essa etapa.')


# --- Enviar para o Google Sheets ---
#
# Configuração única necessária antes de usar:
#   1. Criar conta de serviço no Google Cloud com Sheets API + Drive API
#      ativadas, e baixar a chave JSON.
#   2. Salvar essa chave como google_credentials.json nesta mesma pasta.
#   3. Compartilhar a planilha de destino (Editor) com o e-mail
#      "client_email" que está dentro do JSON.
#   4. Preencher SPREADSHEET_ID acima com o ID da planilha (o trecho da
#      URL entre "/d/" e "/edit").
#   5. pip install gspread google-auth

def _ler_csv_com_encoding(caminho_csv):
    """
    Tenta ler o CSV em utf-8 e cai para latin-1 se falhar. O Status
    Invest costuma exportar em ISO-8859-1 (latin-1), então um
    read_csv assumindo utf-8 direto pode estourar UnicodeDecodeError
    em nomes de empresas com acento.
    """
    try:
        return pd.read_csv(caminho_csv, sep=None, engine='python', encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(caminho_csv, sep=None, engine='python', encoding='latin-1')


def enviar_csv_para_sheets(caminho_csv, nome_aba, spreadsheet_id=SPREADSHEET_ID,
                            credenciais_path=CREDENCIAIS_PATH):
    """
    Sobe o conteúdo de um CSV para uma aba do Google Sheets, substituindo
    o conteúdo atual da aba inteira — assim ela sempre reflete o CSV mais
    recente, sem duplicar linhas de execuções anteriores.
    """
    if not os.path.exists(credenciais_path):
        print(f'  ⚠️ Credenciais do Google não encontradas em {credenciais_path} '
              f'— pulando envio ao Sheets. Veja as instruções no topo desta seção.')
        return
    if spreadsheet_id == 'COLOQUE_AQUI_O_ID_DA_SUA_PLANILHA':
        print('  ⚠️ SPREADSHEET_ID ainda não configurado — pulando envio ao Sheets.')
        return
    if not os.path.exists(caminho_csv):
        print(f'  ⚠️ {caminho_csv} não encontrado — pulando envio ao Sheets.')
        return

    escopos = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(credenciais_path, scopes=escopos)
    cliente = gspread.authorize(creds)
    planilha = cliente.open_by_key(spreadsheet_id)

    try:
        aba = planilha.worksheet(nome_aba)
    except gspread.WorksheetNotFound:
        aba = planilha.add_worksheet(title=nome_aba, rows=1000, cols=30)

    df = _ler_csv_com_encoding(caminho_csv)
    df = df.fillna('')  # NaN quebra o gspread

    # A1 guarda a data da atualização; cabeçalho + dados começam na
    # linha 2, para não conflitar com essa célula.
    data_atualizacao = date.today().strftime('%d/%m/%Y')

    aba.clear()
    aba.update([[f'Atualizado em: {data_atualizacao}']], 'A1')
    aba.update([df.columns.values.tolist()] + df.values.tolist(), 'A2')
    print(f'  ✅ Aba "{nome_aba}" atualizada no Google Sheets ({len(df)} linhas, '
          f'data em A1: {data_atualizacao})')


print('====== Enviando para o Google Sheets')
enviar_csv_para_sheets(arquivo_destino, 'StatusInvest')
enviar_csv_para_sheets(os.path.join(data_path, 'fundamentuspp.csv'), 'Fundamentus')
