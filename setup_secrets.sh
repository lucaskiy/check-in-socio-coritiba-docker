#!/bin/bash
# Cria os secrets no Secret Manager.
# Execute este script UMA VEZ antes de rodar o deploy.sh.
# Edite os valores abaixo com suas credenciais reais antes de executar.

set -e

PROJECT_ID="coxa-checkin"

# =============================================
# EDITE OS VALORES ABAIXO COM SUAS CREDENCIAIS
# =============================================
COXA_CPF="SEU_CPF_AQUI"             # Somente números, ex: 12345678901
COXA_PASSWORD="SUA_SENHA_AQUI"
COXA_SECTOR="arquibancada"           # arquibancada ou maua
TWILIO_ACCOUNT_SID="SEU_ACCOUNT_SID"
TWILIO_AUTH_TOKEN="SEU_AUTH_TOKEN"
TWILIO_FROM_NUMBER="+1415XXXXXXX"    # Número Twilio gerado (ex: +1415XXXXXXX)
TWILIO_TO_NUMBER="+5541XXXXXXXXX"    # Seu número verificado (ex: +5541XXXXXXXXX)
# =============================================

gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

create_or_update_secret() {
  local name=$1
  local value=$2
  if gcloud secrets describe "$name" --project=$PROJECT_ID &>/dev/null; then
    echo "Atualizando secret: $name"
    echo -n "$value" | gcloud secrets versions add "$name" --data-file=- --project=$PROJECT_ID
  else
    echo "Criando secret: $name"
    echo -n "$value" | gcloud secrets create "$name" --data-file=- --project=$PROJECT_ID
  fi
}

create_or_update_secret "COXA_CPF"           "$COXA_CPF"
create_or_update_secret "COXA_PASSWORD"      "$COXA_PASSWORD"
create_or_update_secret "COXA_SECTOR"        "$COXA_SECTOR"
create_or_update_secret "TWILIO_ACCOUNT_SID" "$TWILIO_ACCOUNT_SID"
create_or_update_secret "TWILIO_AUTH_TOKEN"  "$TWILIO_AUTH_TOKEN"
create_or_update_secret "TWILIO_FROM_NUMBER" "$TWILIO_FROM_NUMBER"
create_or_update_secret "TWILIO_TO_NUMBER"   "$TWILIO_TO_NUMBER"

echo ""
echo "Secrets criados/atualizados com sucesso no projeto $PROJECT_ID!"
