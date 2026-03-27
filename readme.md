# Coxa Doido — Check-in Automático

Script Python que realiza o check-in de sócio do Coritiba automaticamente, usando Selenium para navegar no site [sociocoxa.com.br](https://sociocoxa.com.br). Pode ser executado localmente via Docker ou agendado na Google Cloud Platform para rodar todo dia às 18h.

---

## Como funciona o script

O fluxo de execução segue as etapas abaixo:

```
Início
  │
  ├─► Login na página Coxa iD (CPF + senha)
  │       └─► Falha → encerra
  │
  ├─► Acessa a página de check-in
  │
  ├─► Busca jogos com "Check-in Aberto"
  │       ├─► Nenhum encontrado → encerra
  │       └─► Filtra apenas jogos do Brasileirão Série A
  │               └─► Ignora Copa do Brasil, amistosos, etc.
  │
  ├─► Verifica se o check-in do Série A já foi feito anteriormente
  │       └─► Se sim → loga e encerra (não faz duplo check-in)
  │
  ├─► Executa o check-in individual:
  │       ├─► Clica em "Check-in Aberto"
  │       ├─► Clica em "Check-in Individual"
  │       ├─► Clica em "Fazer Check-in"
  │       ├─► Clica em "Avançar"
  │       ├─► Seleciona o setor (Arquibancada ou Curva Mauá)
  │       └─► Seleciona "Biometria Facial"
  │
  └─► Envia SMS de confirmação via Twilio
```

### Regras e condições

| Situação | Comportamento |
|---|---|
| CPF ausente ou inválido (não numérico, ≠ 11 dígitos) | Encerra sem executar |
| Credenciais inválidas (login falhou) | Encerra sem executar |
| Nenhum jogo com check-in aberto | Encerra normalmente (sem erro) |
| Jogo disponível, mas não é Série A | Ignorado — continua buscando |
| Check-in do Série A já realizado | Loga a situação e encerra |
| Setor inválido (diferente de `arquibancada` ou `maua`) | Lança exceção e encerra |

---

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `COXA_CPF` | CPF de login (somente números, 11 dígitos) |
| `COXA_PASSWORD` | Senha da página Coxa iD |
| `COXA_SECTOR` | Setor do estádio: `arquibancada` ou `maua` |
| `TWILIO_ACCOUNT_SID` | Account SID da conta Twilio |
| `TWILIO_AUTH_TOKEN` | Auth Token da conta Twilio |
| `TWILIO_FROM_NUMBER` | Número Twilio para envio (ex: `+1415XXXXXXX`) |
| `TWILIO_TO_NUMBER` | Seu número para receber o SMS (ex: `+5541XXXXXXXXX`) |

---

## Execução local via Docker

### 1. Build da imagem

```bash
docker build -t coxa_checkin .
```

### 2. Executar o container

```bash
docker run \
  -e COXA_CPF=12345678901 \
  -e COXA_PASSWORD=suasenha \
  -e COXA_SECTOR=arquibancada \
  -e TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx \
  -e TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx \
  -e TWILIO_FROM_NUMBER=+1415XXXXXXX \
  -e TWILIO_TO_NUMBER=+5541XXXXXXXXX \
  coxa_checkin
```

> **Nota:** para testar com o browser visível (fora do Docker), comente a linha `chrome_options.add_argument("--headless")` no [main.py](main.py) e execute o script diretamente com `python3 main.py`.

---

## Execução automática na GCP (Cloud Run + Cloud Scheduler)

### Arquitetura

```
Cloud Scheduler (18h - horário de Brasília)
        │
        │  HTTP POST (OAuth)
        ▼
Cloud Run Jobs
        │  executa o container
        ▼
Docker Image (Artifact Registry)
        │
        ├─► Lê credenciais do Secret Manager
        └─► Roda main.py (Selenium + Chrome headless)
```

| Componente | Função |
|---|---|
| **Artifact Registry** | Repositório da imagem Docker (`southamerica-east1`) |
| **Cloud Build** | Faz o build e push da imagem no CI |
| **Cloud Run Jobs** | Executa o container como job de curta duração (sem porta HTTP) |
| **Cloud Scheduler** | Dispara o job todo dia às 18h (`America/Sao_Paulo`) |
| **Secret Manager** | Armazena todas as credenciais com segurança |
| **Service Account** | Identidade do job com permissões mínimas (secretAccessor + run.invoker) |

### Pré-requisitos

- [gcloud CLI](https://cloud.google.com/sdk/docs/install) instalado e autenticado
- Projeto GCP `coxa-checkin` criado com billing habilitado
- Conta Twilio configurada

### Deploy

**Passo 1 — Configurar os secrets**

Edite o [setup_secrets.sh](setup_secrets.sh) com suas credenciais reais e execute:

```bash
./setup_secrets.sh
```

**Passo 2 — Deploy completo**

```bash
./deploy.sh
```

O script habilita as APIs necessárias, faz o build da imagem, cria o Cloud Run Job e configura o agendamento automaticamente.

### Comandos úteis

```bash
# Executar o job manualmente
gcloud run jobs execute coxa-checkin-job --region=southamerica-east1 --project=coxa-checkin

# Ver logs da última execução
gcloud logging read \
  'resource.type=cloud_run_job AND resource.labels.job_name=coxa-checkin-job' \
  --project=coxa-checkin --limit=50 --format="value(textPayload)"

# Listar execuções do job
gcloud run jobs executions list --job=coxa-checkin-job --region=southamerica-east1 --project=coxa-checkin
```
