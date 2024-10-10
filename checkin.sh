#!/bin/bash

# Digite seu CPF de login da página de login do sócio (somente os dígitos)
export COXA_CPF=

# Digite sua senha da página de login do sócio
export COXA_PASSWORD=

# Escolha o setor de check-in, opções: arquibancada ou maua (tudo minúsculo)
export COXA_SECTOR=

# Escolha o tipo de check-in, opções: fisica ou online (tudo minúsculo)
export CHECKIN_TYPE=

# Caso opte pela notificão de email, coloque abaixo o email que irá receber a notificação
export EMAIL=

# Senha de APP do email
export GMAIL_PASSWORD=


docker run -e EMAIL=$EMAIL -e COXA_CPF=$COXA_CPF -e COXA_PASSWORD=$COXA_PASSWORD -e COXA_SECTOR=$COXA_SECTOR -e CHECKIN_TYPE=$CHECKIN_TYPE -e GMAIL_PASSWORD=$GMAIL_PASSWORD coxa-checkin