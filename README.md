# AgroTrace 🚜🌍

AgroTrace é um ecossistema full-stack de rastreamento logístico e monitoramento térmico de ponta a ponta (IoT ao Mobile), desenhado para resolver as dores reais do transporte agropecuário de alto valor.

Diferente de sistemas de prateleira engessados, o AgroTrace foi moldado em torno de três princípios inegociáveis: **Desempenho Massivo em Time-Series, Segurança B2B Inflexível e Tolerância Bruta a Zonas Mortas (Offline-First).**

---

## 🏗️ O Pitch Arquitetural (Tech Stack & Soluções)

### 1. Ingestão e Processamento (O Gargalo de Dados Resolvido)
No transporte refrigerado, os caminhões disparam rajadas de telemetria térmica e coordenadas espaciais via satélite. Bancos relacionais comuns travam quando o volume chega aos milhões.
- **TimescaleDB Nativo (PostgreSQL)**: Tratamos o *Slow-Path* transformando a tabela de `Telemetry` diretamente em uma Hypertable com DDL hooks do SQLAlchemy. 
- **Downsampling Espacial**: No FastAPI (Dashboard API), nós agregamos e sumarizamos gigabytes de pontos em frações de segundo usando as funções nativas de `time_bucket` do TimescaleDB, garantindo que o front-end em React (Next.js/Recharts/MapLibre) nunca trave.
- **Fast-Path (MQTT Mosquitto)**: Um worker leve intercepta os alertas críticos (como as rupturas da cadeia de frio), validando via Pydantic e acionando nossa FSM (Máquina de Estados Finita) no mesmo segundo.

### 2. Multi-Tenant Criptográfico (A Blindagem B2B)
Como Transportadoras concorrentes dividem o mesmo banco de dados sem que a Empresa A veja a rota da Empresa B?
- **Row-Level Security (RLS)**: Substituímos o risco humano do programador esquecer cláusulas `WHERE tenant_id=X` nas APIs. Empurramos a barreira criptográfica para as entranhas do motor PostgreSQL.
- **ContextVars no Connection Pool**: A API FastAPI orquestra o acesso injetando `SET LOCAL app.current_tenant` a cada transação assíncrona, barrando fisicamente o vazamento de dados corporativos no nível do kernel do banco de dados.

### 3. Logística de Guerrilha (Mobile Offline-First)
Nas estradas rurais do agronegócio não há sinal 4G. Exigir que o motorista faça logins demorados e possua internet para assumir a custódia da carga é pedir para o sistema ser odiado e boicotado.
- **Signed URLs vs Logins (Custódia Efêmera)**: Caminhoneiros não fazem cadastro formal. Eles apontam o celular para a carga. O aplicativo (React Native/Expo) decodifica um token HMAC-SHA256 (itsdangerous) nativamente seguro contra falsificações (IDOR).
- **Zustand Mutation Queue (Offline)**: Se não houver internet na fazenda, o aplicativo não bloqueia a viagem. O "Aceite" é cravado na memória Flash (AsyncStorage) junto com a variável `offline_timestamp` (capturando o momento legal e exato do aperto de mão na vida real).
- **Network Hooks Silent-Sync**: Assim que o caminhão retorna à pista e encontra sinal (NetInfo listener), a fila dispara em background. O Backend FastAPI sabe aceitar esse relógio "atrasado" para refazer a linha do tempo da auditoria. Sem botão de "sincronizar", sem dor de cabeça.

---

## 🛠️ Stack Tecnológica
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, uv (Packaging), paho-mqtt
- **Infra/Dados**: TimescaleDB (PostgreSQL), Eclipse Mosquitto (Broker MQTT), Docker
- **Web Frontend**: Next.js (App Router), React Query, Tailwind CSS, Recharts, MapLibre
- **Mobile**: React Native (Expo), Zustand, AsyncStorage, expo-camera

## 🚀 Como Rodar o MVP (Desenvolvimento Local)

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- [uv](https://github.com/astral-sh/uv) (Gerenciador de pacotes e dependências Python)
- Node.js (versão 20+)

### 1. Configurando o Ambiente
Clone o repositório e crie o arquivo `.env` baseado no `.env.example`:
```bash
cp .env.example .env
```
O `.env` precisa de algumas chaves. Para desenvolvimento, você pode preenchê-las assim:
```env
# Banco de Dados
POSTGRES_USER=agrotrace
POSTGRES_PASSWORD=agrotrace_dev
POSTGRES_DB=agrotrace
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Mensageria
MQTT_BROKER=localhost

# Segurança
SECRET_KEY=uma_chave_secreta_aleatoria_aqui
```

### 2. Subindo a Infraestrutura Completa (Docker Compose)
Para facilitar o desenvolvimento, você pode subir o banco de dados (TimescaleDB), o broker de mensageria (Mosquitto), a API Backend e o Frontend simultaneamente:
```bash
docker-compose up --build
```
- A **API Backend** ficará disponível em: `http://localhost:8000`
- O **Frontend Dashboard** ficará disponível em: `http://localhost:3000`

### 3. Rodando Manualmente (Sem Docker)
Caso queira rodar os componentes fora do Docker para debug:

**Backend (API):**
```bash
# Instala as dependências usando uv
uv sync

# Sobe o servidor FastAPI
uv run uvicorn main:app --reload
```

**Frontend (Web Dashboard):**
```bash
cd frontend
npm install
npm run dev
```

## ☁️ Deploy em Produção (Render)

A infraestrutura foi preparada para ser facilmente hospedada no [Render.com](https://render.com/).

O repositório já contém as definições de infraestrutura como código (IaC):
- `render.yaml`: Define o web service do FastAPI e os scripts de build.
- `Dockerfile` (na raiz): Imagem de produção do Backend (FastAPI).
- `Dockerfile.mosquitto`: Configuração de proxy e broker do MQTT caso precise hospedar o seu próprio mosquitto lá.
- `scripts/render_deploy.py`: Script para automação do deploy que empacota o ambiente via `uv`.

Para fazer o deploy, conecte o repositório ao Render e crie o serviço utilizando o `render.yaml` como Blueprint. Lembre-se de preencher a variável `SECRET_KEY` no painel do Render!

---

*(Consulte os arquivos na pasta `docs/` e `docs/adr/` para um mergulho detalhado nas decisões arquiteturais e design do Domínio.)*
