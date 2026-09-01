# 02: CI básico

**What to build:** Toda PR e push na `main` passa a rodar lint e testes (pytest) via GitHub Actions, com branch protection ativada garantindo que código quebrado não seja mesclado.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] Criar arquivo de workflow `.github/workflows/ci.yml`.
- [x] Configurar job para rodar linter na base de código.
- [x] Configurar job para executar a suíte de testes com `pytest`.
- [ ] (Manual/Admin) Ativar ruleset / branch protection no GitHub exigindo que este workflow passe antes de merge na `main`.
