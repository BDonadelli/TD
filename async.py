import asyncio
import aiohttp
import aiofiles
import os

# Nomes dos arquivos CSV
arquivo_csv = "PrecoTaxaTesouroDireto.csv"           
arquivo_csv_rendimento = "rendimento_investir.csv"     
arquivo_csv_rendimento_resgatar = "rendimento_resgatar.csv"

# URLs dos arquivos
URL_FILE_TESOURO = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/"
    "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
    "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv"
)

# NOVO link do CSV "rendimento-investir"
URL_FILE_RENDIMENTO_INVESTIR = (
    "https://www.tesourodireto.com.br/documents/d/guest/"
    "rendimento-investir-csv"#?download=true"
)

# NOVO link do CSV "rendimento-resgatar"
URL_FILE_RENDIMENTO_RESGATAR = (
    "https://www.tesourodireto.com.br/documents/d/guest/"
    "rendimento-resgatar-csv"#?download=true"
)


async def download_arquivo(session, arquivo, url):
    """
    Faz o download de um arquivo de uma URL e salva localmente.
    
    Args:
        session: Sessão aiohttp para fazer requisições
        arquivo: Nome do arquivo local onde salvar
        url: URL do arquivo para download
    """
    print(f"Iniciando download do arquivo {arquivo}...")
    
    try:
        headers = {
            'Accept': 'text/csv,application/octet-stream;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.tesourodireto.com.br/',
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/114.0 Safari/537.36'
            )
        }
        
        async with session.get(
            url, 
            headers=headers,
            max_redirects=5
        ) as response:
            response.raise_for_status()
            
            async with aiofiles.open(arquivo, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)
        
        print(f"{arquivo} salvo localmente.")
        
    except Exception as error:
        print(f"Erro ao baixar o arquivo {arquivo}: {error}")
        raise error


async def main():
    """Função principal que coordena os downloads."""
    try:
        # Configurações da sessão com cookies habilitados
        connector = aiohttp.TCPConnector(ssl=False)
        cookie_jar = aiohttp.CookieJar()
        
        async with aiohttp.ClientSession(
            connector=connector,
            cookie_jar=cookie_jar,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            
            # Download sequencial para evitar sobrecarga do servidor
            print("Fazendo downloads sequencialmente para evitar bloqueios...")
            
            try:
                # CSV antigo (mantém compatibilidade)
                await download_arquivo(session, arquivo_csv, URL_FILE_TESOURO)
                await asyncio.sleep(2)  # Pausa entre downloads
                
                # CSV novo (rendimento-investir)
                await download_arquivo(session, arquivo_csv_rendimento, URL_FILE_RENDIMENTO_INVESTIR)
                await asyncio.sleep(2)  # Pausa entre downloads
                
                # CSV novo (rendimento-resgatar)
                await download_arquivo(session, arquivo_csv_rendimento_resgatar, URL_FILE_RENDIMENTO_RESGATAR)
                
            except Exception as e:
                print(f"Erro em download específico: {e}")
                # Continua com os outros downloads mesmo se um falhar
                
        print("Processo de download finalizado.")
        
    except Exception as error:
        print(f"Falha geral no processo: {error}")


if __name__ == "__main__":
    # Executa a função principal
    asyncio.run(main())