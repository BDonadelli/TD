import requests

# URL do CSV
url = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv"

# Nome do arquivo de saída
output_file = "data/precotaxatesourodireto.csv"

# Faz o download
response = requests.get(url)
response.raise_for_status()  # levanta erro se falhar

# Salva o conteúdo em arquivo
with open(output_file, "wb") as f:
    f.write(response.content)

print(f"Arquivo salvo como {output_file}")


# import pandas as pd

# url = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv"

# df = pd.read_csv(url, sep=";")  # separador é ";"
# print(df.head())
