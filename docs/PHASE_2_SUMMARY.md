# AgroTrace - Resumo da Fase 2 (Segurança e Múltiplos Clientes)

## Visão Geral
Na Fase 2 do backend do AgroTrace, focamos na segurança do acesso e em garantir que diferentes empresas possam usar o mesmo sistema sem acessar os dados umas das outras. 

## Entregas Principais

### 1. Isolamento de Dados (Múltiplas Empresas)
- **Segurança no Banco (RLS)**: Usamos as políticas do PostgreSQL (Row-Level Security) para separar os dados de cada empresa. Assim, se alguém esquecer de colocar um `WHERE tenant_id=X` na query, o banco de dados mesmo assim barra o acesso.
- **Injeção de Contexto**: A API manda um `SET LOCAL app.current_tenant` pro banco de dados em cada request. Isso ajuda a evitar o vazamento de informações.

### 2. URLs Seguras para o Motorista
- Quando o motorista vai pegar a carga, ele lê um QR Code com um link. Esse link usa uma assinatura (HMAC-SHA256) pra garantir que não foi alterado.
- Se o link for válido, o sistema libera só as informações necessárias para ele, escondendo dados sensíveis de trajeto ou temperatura da carga.

### 3. Cadastro Temporário de Motoristas
- Como os motoristas geralmente são terceirizados, seria muito ruim pedir para eles criarem uma conta no sistema só para transportar a carga.
- Então, eles usam a URL segura do QR Code e digitam CPF, Nome e Placa. Esses dados ficam atrelados ao registro da carga da empresa, mantendo o controle da viagem sem encher o banco de usuários.

### 4. Testes de Segurança
- Criamos testes para ter certeza que as regras de isolamento de dados e os links seguros estavam funcionando:
  - Tentamos acessar dados de outra empresa e conferimos se o sistema bloqueou (retornando lista vazia).
  - Tentamos alterar o link (URL Segura) para ver se ele era negado com erro 403.
  - Simulamos a expiração dos links alterando o relógio do sistema, para ver se links velhos não eram aceitos.

## Conclusão
O sistema agora está mais seguro. Várias empresas podem dividir o mesmo banco de dados sem que uma veja os dados da outra, e o app ficou muito mais fácil pro motorista usar, já que ele não precisa de login e senha para trabalhar.
