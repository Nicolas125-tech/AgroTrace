# 08: Aplicar autenticação nos endpoints existentes

**What to build:** Dependency do FastAPI que extrai e valida o token e injeta `current_tenant`, aplicada em `GET /api/shipments/{id}`, `/telemetry`, `/route`, `handshake/initiate` e `admin/transfers/.../resolve` — cada um passa a exigir tenant autenticado e escopar via RLS de verdade.

**Blocked by:** 03: Login e emissão de token para Tenant

**Status:** ready-for-agent

- [ ] Criar dependency injetável no FastAPI para validar o token e obter o `current_tenant`.
- [ ] Aplicar a dependency nos endpoints de shipments, telemetry, route, handshake e admin. **ATENÇÃO**: a base atual da main já mudou `routes.py` e `db/session.py` (usando `set_config` para tenant/RLS). O novo fluxo de autenticação deve integrar com essa estrutura de `set_config` já existente, sem desfazer as mudanças recentes.
- [ ] Ajustar as queries destes endpoints para garantirem restrição de RLS (Row-Level Security) pelo tenant validado, acionando o RLS real.
