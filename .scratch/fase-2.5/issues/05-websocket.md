# 05: Canal de tempo real (WebSocket)

**What to build:** Conexão em tempo real (via WebSocket ou SSE) estabelecida entre o backend e a página de detalhes da remessa no frontend (já existente), permitindo atualizações ao vivo (ex: nova telemetria).

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Adicionar suporte a WebSocket ou SSE no FastAPI para transmitir eventos de uma remessa específica.
- [ ] Atualizar o frontend na página `shipments/[id]` para conectar no canal de tempo real e atualizar a UI em caso de novos dados de telemetria.
