# 06: Docker-compose completo

**What to build:** O comando `docker-compose up` passa a subir toda a stack do projeto simultaneamente (TimescaleDB, Mosquitto, API FastAPI e Frontend web), facilitando o desenvolvimento local.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Revisar os arquivos recém-criados `Dockerfile` e `Dockerfile.mosquitto` (voltados para deploy no Render) e garantir que o compose se beneficie ou interaja bem com eles localmente.
- [ ] Adicionar o serviço da API backend no `docker-compose.yml`.
- [ ] Adicionar o serviço do frontend web.
- [ ] Configurar redes e variáveis de ambiente no compose para que backend comunique com DB/MQTT, e frontend comunique com backend.
