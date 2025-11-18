# Inicie o ssh-agent
eval "$(ssh-agent -s)"

# Adicione a chave ao agente
ssh-add [camiho para a chave ssh]

# Navegue até o diretório do repositório
cd [caminho do repositorio local]/TD

DISPLAY=:0 [caminho do executável]/python3 TesouroDireto_Dia_v2.py

# Adicione alterações ao staging
git add .

# Faça o commit com uma mensagem
git commit -m "Atualização automatica de tesouro_direto.json"

# Faça o push para o repositório remoto
git push origin main
