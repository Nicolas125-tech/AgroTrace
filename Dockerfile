FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema (para compilar o psycopg e dependências C)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Instalar o gerenciador uv
RUN pip install uv

# Copiar os arquivos de lock e projeto
COPY pyproject.toml uv.lock ./

# Instalar dependências globais na imagem
RUN uv sync --no-dev --system

# Copiar a aplicação
COPY src/ ./src/
COPY main.py ./

# Porta que o Render mapeia automaticamente
EXPOSE 8000

# Script de boot (utilizamos as variáveis de ambiente diretamente)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
