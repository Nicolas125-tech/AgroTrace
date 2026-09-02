# AgroTrace

O AgroTrace é um sistema de rastreamento logístico e monitoramento de temperatura para o transporte agropecuário. O foco do projeto é ter boa performance no banco de dados, permitir acesso de múltiplas empresas com segurança, e funcionar bem mesmo quando o celular do motorista perde o sinal de internet (offline-first).

---

## Como a arquitetura funciona

### 1. Ingestão e Processamento de Dados
No transporte refrigerado, são gerados muitos dados de temperatura e localização. Bancos relacionais normais podem sofrer com isso.
- **TimescaleDB (PostgreSQL)**: Usamos uma Hypertable com o SQLAlchemy para salvar a telemetria.
- **Consultas Rápidas**: A API em FastAPI resume os dados rapidamente usando as funções do TimescaleDB, para não travar o frontend em React.
- **Alertas (MQTT Mosquitto)**: Um worker verifica alertas críticos (como mudança de temperatura) e valida as regras de negócio em tempo real.

### 2. Multi-Tenant (Múltiplas Empresas)
Como várias transportadoras usam o mesmo banco sem ver os dados umas das outras?
- **Row-Level Security (RLS)**: A segurança de dados é feita direto no PostgreSQL.
- **ContextVars**: A API FastAPI usa `SET LOCAL app.current_tenant` a cada transação, isolando os dados de cada empresa no banco.

### 3. Funcionamento Offline (Mobile)
Nas estradas, muitas vezes não há sinal de internet.
- **Links com Assinatura**: O motorista não precisa fazer login. Ele escaneia um QR Code com um token HMAC-SHA256 seguro.
- **Fila Offline com Zustand**: Se não houver internet, o aplicativo salva o momento exato em que a carga foi aceita no celular.
- **Sincronização**: Quando o sinal volta, o app envia os dados para o backend em segundo plano, mantendo o horário correto do aceite.

---

## Stack
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic, uv, paho-mqtt
- **Infra/Dados**: TimescaleDB (PostgreSQL), Eclipse Mosquitto (MQTT), Docker
- **Frontend Web**: Next.js, React Query, Tailwind CSS, Recharts, MapLibre
- **Mobile**: React Native (Expo), Zustand, AsyncStorage, expo-camera

## Como rodar o projeto localmente

### O que você precisa ter instalado
- Docker e Docker Compose
- uv (Gerenciador de pacotes Python)
- Node.js (versão 20+)

### 1. Configurando o ambiente
Clone o repositório e crie o `.env`:
```bash
cp .env.example .env
```
Exemplo de configuração para o `.env`:
```env
POSTGRES_USER=agrotrace
POSTGRES_PASSWORD=agrotrace_dev
POSTGRES_DB=agrotrace
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
MQTT_BROKER=localhost
SECRET_KEY=sua_chave_secreta_aqui
```

### 2. Rodando com Docker
Para subir o banco, broker MQTT, API e o Frontend juntos:
```bash
docker-compose up --build
```
- A API ficará em: `http://localhost:8000`
- O Dashboard ficará em: `http://localhost:3000`

### 3. Rodando sem Docker
**Backend (API):**
```bash
uv sync
uv run uvicorn main:app --reload
```

**Frontend (Web Dashboard):**
```bash
cd frontend
npm install
npm run dev
```

## Deploy em Produção (Render)

O repositório já está configurado para deploy no Render.com.
- `render.yaml`: Configuração do web service FastAPI.
- `Dockerfile`: Imagem de produção do Backend.
- `Dockerfile.mosquitto`: Configuração do proxy e broker MQTT.
- `scripts/render_deploy.py`: Script para deploy.

Conecte o repositório ao Render e use o `render.yaml`. Lembre-se de configurar a variável `SECRET_KEY`!
