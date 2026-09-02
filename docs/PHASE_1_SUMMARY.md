# AgroTrace - Resumo da Fase 1

## Visão Geral
Concluímos a Fase 1 do backend do MVP do AgroTrace. Criamos a base de um sistema de logística preparado para lidar com quedas de conexão, resolver a transferência de responsabilidade das cargas e processar dados dos sensores rapidamente.

## Entregas Principais

### 1. Regras de Negócio e Arquitetura
- **Documentação de Decisões (ADRs)**: Definimos:
  - Como calcular se a carga saiu da temperatura certa usando o `CargoProfile`.
  - Como o motorista assume a carga mesmo sem internet.
  - As regras de quarentena caso o sensor quebre ou fique offline por mais de 24h.
  - O tempo limite de tolerância (Grace Period) para ficar offline sem gerar alertas.
  - A divisão entre validação rápida (Fast-Path) e validação completa do histórico (Slow-Path).

### 2. Infraestrutura
- O projeto usa `uv` para gerenciar as dependências Python.
- API criada em FastAPI.
- Usamos **TimescaleDB** (PostgreSQL) para lidar com a quantidade grande de dados gerados pelos sensores.
- Broker MQTT (Mosquitto) para receber os dados.

### 3. Recebimento de Dados (MQTT)
- **Fast-Path**: Uma rotina no tópico `agrotrace/handshake` valida os dados importantes na hora, para avisar logo se a carga foi comprometida.
- **Slow-Path**: Uma rotina no tópico `agrotrace/telemetry` pega o histórico completo de temperatura e salva em lotes no banco de dados.

### 4. API do Dashboard
- Para não sobrecarregar a tela do usuário com milhares de pontos de temperatura, agregamos os dados no próprio banco:
  - Juntamos as temperaturas em blocos (usando `time_bucket`) para gerar médias.
  - Filtramos os dados do GPS para simplificar a renderização do mapa no frontend.

### 5. Qualidade
- Criamos testes de integração integrados ao banco de dados rodando no Docker.
- Script para simular dados falsos de sensores, para testarmos como o sistema se comporta sob carga.

## Conclusão
O núcleo do backend já está pronto e lidando bem com falhas de rede. O próximo passo é integrar com o Frontend!
