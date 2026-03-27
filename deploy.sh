#!/bin/bash
# Deploy completo do coxa-checkin na GCP.
# Pré-requisitos:
#   - gcloud CLI instalado e autenticado (gcloud auth login)
#   - setup_secrets.sh já executado com suas credenciais reais
#   - Projeto GCP "coxa-checkin" criado e billing habilitado

set -e

PROJECT_ID="coxa-checkin"
REGION="southamerica-east1"
REPO_NAME="coxa-checkin"
IMAGE_NAME="coxa-checkin"
JOB_NAME="coxa-checkin-job"
SA_NAME="coxa-checkin-sa"
SCHEDULER_NAME="coxa-checkin-scheduler"
IMAGE_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

echo "=== [1/6] Habilitando APIs necessárias ==="
gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  --project=$PROJECT_ID

echo ""
echo "=== [2/6] Criando repositório no Artifact Registry ==="
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="Imagens do coxa check-in" \
  --project=$PROJECT_ID 2>/dev/null || echo "Repositório já existe, continuando..."

echo ""
echo "=== [3/6] Build e push da imagem via Cloud Build ==="
gcloud builds submit \
  --tag=$IMAGE_URL \
  --project=$PROJECT_ID

echo ""
echo "=== [4/6] Criando Service Account e permissões ==="
gcloud iam service-accounts create $SA_NAME \
  --display-name="Coxa Check-in Service Account" \
  --project=$PROJECT_ID 2>/dev/null || echo "Service account já existe, continuando..."

# Permissão para disparar Cloud Run Jobs (usado pelo Cloud Scheduler)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/run.invoker" \
  --condition=None

# Permissão para ler os secrets em tempo de execução
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor" \
  --condition=None

echo ""
echo "=== [5/6] Criando/atualizando Cloud Run Job ==="
gcloud run jobs deploy $JOB_NAME \
  --image=$IMAGE_URL \
  --region=$REGION \
  --service-account=$SA_EMAIL \
  --set-secrets=COXA_CPF=COXA_CPF:latest,COXA_PASSWORD=COXA_PASSWORD:latest,COXA_SECTOR=COXA_SECTOR:latest,TWILIO_ACCOUNT_SID=TWILIO_ACCOUNT_SID:latest,TWILIO_AUTH_TOKEN=TWILIO_AUTH_TOKEN:latest,TWILIO_FROM_NUMBER=TWILIO_FROM_NUMBER:latest,TWILIO_TO_NUMBER=TWILIO_TO_NUMBER:latest \
  --memory=2Gi \
  --cpu=1 \
  --max-retries=0 \
  --task-timeout=300 \
  --project=$PROJECT_ID

echo ""
echo "=== [6/6] Criando/atualizando Cloud Scheduler (18h horário de Brasília) ==="
if gcloud scheduler jobs describe $SCHEDULER_NAME --location=$REGION --project=$PROJECT_ID &>/dev/null; then
  echo "Atualizando scheduler existente..."
  gcloud scheduler jobs update http $SCHEDULER_NAME \
    --schedule="0 18 * * *" \
    --time-zone="America/Sao_Paulo" \
    --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" \
    --http-method=POST \
    --oauth-service-account-email=$SA_EMAIL \
    --location=$REGION \
    --project=$PROJECT_ID
else
  echo "Criando novo scheduler..."
  gcloud scheduler jobs create http $SCHEDULER_NAME \
    --schedule="0 18 * * *" \
    --time-zone="America/Sao_Paulo" \
    --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" \
    --http-method=POST \
    --oauth-service-account-email=$SA_EMAIL \
    --location=$REGION \
    --project=$PROJECT_ID
fi

echo ""
echo "======================================================"
echo "Deploy concluído com sucesso!"
echo "  Projeto:       $PROJECT_ID"
echo "  Região:        $REGION"
echo "  Job:           $JOB_NAME"
echo "  Imagem:        $IMAGE_URL"
echo "  Agendamento:   todos os dias às 18h (América/São_Paulo)"
echo ""
echo "Para executar manualmente:"
echo "  gcloud run jobs execute $JOB_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
echo "Para ver os logs:"
echo "  gcloud logging read 'resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME' --project=$PROJECT_ID --limit=50"
echo "======================================================"
