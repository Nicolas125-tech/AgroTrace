# 0008. Motorista Efêmero para Posse Física

## Date
2026-08-31

## Context
Na logística do agronegócio, as transportadoras frequentemente terceirizam a viagem (perna) para motoristas autônomos. Precisávamos definir como esse ator entraria no nosso Role-Based Access Control (RBAC).

## Decision
Não criar a role "Sub-contratado". O motorista atuará como um **Motorista Efêmero**, identificando-se através de chaves únicas (documento/CPF ou placa) no momento do escaneamento, mas sempre agindo **em nome** da Transportadora legalmente responsável (o Tenant real).

## Consequences
- **Adoção Fluida**: Zero atrito nas estradas. O motorista autônomo não precisa baixar aplicativo, se cadastrar ou gerenciar senhas.
- **Simplificação de DB**: Reduz a complexidade da modelagem e a fatura de infraestrutura ao não inflar o banco de usuários com identidades que serão usadas apenas uma vez na vida.
- O Handshake fica dependente do modelo de posse efêmera vinculada a um tenant.
