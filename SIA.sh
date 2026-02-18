#!/bin/bash

# Inicie o ssh-agent
eval "$(ssh-agent -s)"

# Adicione a chave ao agente
ssh-add /home/yair/.ssh/id_rsa

# Navegue até o diretório do repositório
cd /home/yair/GHub/TD/

# Ative o ambiente Python pythorix
source ~/bin/pythorix/bin/activate

DISPLAY=:0 /home/yair/bin/pythorix/bin/python3 SIA.py

# Adicione alterações ao staging
git add .

# Faça o commit com uma mensagem
git commit -m "Atualização automatica"

# Faça o push para o repositório remoto
git push origin main
