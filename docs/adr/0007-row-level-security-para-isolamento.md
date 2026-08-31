# 0007. Row-Level Security para Isolamento de Tenants

## Date
2026-08-31

## Context
A infraestrutura do AgroTrace rastreia cargas valiosas de múltiplos clientes. Precisávamos decidir onde a barreira de isolamento de dados seria implementada: na camada de aplicação (SQLAlchemy `where` clauses e mixins) ou diretamente no banco de dados (Row-Level Security - RLS).

## Decision
Adotar **Row-Level Security (RLS)** nativo do PostgreSQL/TimescaleDB. 

Utilizaremos Event Listeners no pool do SQLAlchemy para executar `SET LOCAL tenant_id = X` assim que uma sessão for instanciada pelo middleware de autenticação do FastAPI.

## Consequences
- **Segurança Blindada**: Erros de desenvolvedores (como esquecer um `.filter_by(tenant_id=X)`) não vazarão rotas e dados milionários entre transportadoras concorrentes. O banco de dados simplesmente ocultará as linhas indesejadas.
- **Complexidade de Migrations**: O Alembic terá que gerenciar as políticas RLS para novas tabelas explicitamente.
- **Performance**: O RLS tem um pequeno overhead no PostgreSQL, mas compensado de sobra pelo TimescaleDB e índices apropriados.
