# Inicie o ssh-agent
eval "$(ssh-agent -s)"

# Adicione a chave ao agente
ssh-add ~/.ssh/id_rsa

# Navegue até o diretório do repositório
cd ~/GHub/TD

# Ative o ambiente Python pythorix
source ~/bin/pythorix/bin/activate

DISPLAY=:0 ~/bin/pythorix/bin/python TesouroDireto_Dia_v3.py

# Adicione alterações ao staging
git add .

# Faça o commit com uma mensagem
git commit -m "Atualização automatica de tesouro_direto.json"

# Faça o push para o repositório remoto
git push origin main
