# 09: Endpoint de listagem de remessas

**What to build:** Um novo endpoint `GET /api/shipments` que retorna as remessas de forma paginada e filtrável por status, com os resultados restritos apenas aos dados pertencentes ao tenant autenticado.

**Blocked by:** 08: Aplicar autenticação nos endpoints existentes

**Status:** ready-for-agent

- [ ] Criar rota `GET /api/shipments` exigindo tenant autenticado.
- [ ] Implementar paginação básica (limit/offset ou cursor).
- [ ] Implementar suporte a filtragem pelo campo de status da remessa.
