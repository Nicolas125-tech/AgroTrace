# 11: README com instruções reais de setup

**What to build:** A documentação do projeto passa a ter um passo a passo prático e funcional de como configurar as variáveis de ambiente e rodar o projeto do zero (docker, dependências e execução).

**Blocked by:** 06: Docker-compose completo

**Status:** ready-for-agent

- [ ] Adicionar lista de pré-requisitos no README.
- [ ] Documentar criação e preenchimento das variáveis de ambiente necessárias no `.env` (incluindo `SECRET_KEY`, `POSTGRES_PASSWORD`, etc).
- [ ] Incluir comandos explícitos de inicialização (ex: `docker-compose up`, `uv sync`, run scripts de front/mobile).
- [ ] Documentar o fluxo de deploy (arquivos `render.yaml` e `scripts/render_deploy.py` que já existem no repo).
