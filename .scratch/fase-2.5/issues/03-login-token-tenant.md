# 03: Login e emissão de token para Tenant

**What to build:** Modelo de credenciais para Tenant (Produtor/Transportadora/Comprador) e endpoint de login que emite um token de sessão válido. Testável isolado: tenant existente faz login e recebe token; token inválido/expirado é rejeitado.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Definir o modelo e tabela/schema para as credenciais de Tenant (se não existirem).
- [ ] Criar o endpoint de autenticação (ex: `POST /api/auth/login`) que verifica as credenciais.
- [ ] Emitir JWT (ou token opaco) contendo a identificação do Tenant e os papéis associados.
