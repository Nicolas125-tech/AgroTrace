# 01: Remover secret hardcoded

**What to build:** A aplicação passa a exigir a variável de ambiente `SECRET_KEY` em produção, e utiliza um gerador aleatório seguro para ambientes de desenvolvimento ao invés de um valor hardcoded no repositório.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Remover o valor literal do `SECRET_KEY` no `src/core/security.py`.
- [x] Exigir que a variável de ambiente seja fornecida para iniciar fora de ambiente de testes.
- [x] Implementar geração de valor aleatório seguro como fallback exclusivo para modo de desenvolvimento/testes.

*Closed in PR #3 / commit c72a235.*
