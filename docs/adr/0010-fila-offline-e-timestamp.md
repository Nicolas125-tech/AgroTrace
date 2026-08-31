# 0010. Fila Offline e Timestamp de Ação (Offline-First Handshake)

## Date
2026-08-31

## Context
Em estradas rurais, motoristas realizarão o escaneamento de QRs para assumir custódia de cargas valiosas em zonas sem cobertura celular (Offline). Se o aplicativo bloquear a transação por falta de conexão, a adoção no mundo real fracassará. Da mesma forma, registrar a hora de upload como a hora legal da custódia invalidará contratos de seguro de transporte em caso de sinistro.

## Decision
Adotaremos uma **Mutation Queue Persistente** baseada no armazenamento assíncrono local (AsyncStorage) orquestrada por bibliotecas de estado (ex: Zustand). As mutações (como o aceite da custódia) gerarão um payload que será salvo localmente incluindo a variável crítica `offline_timestamp`, que registra o relógio do celular exato do momento do aceite.

O App tentará sincronizar a fila silenciosamente em background quando detectar retorno de conectividade (`NetInfo`). 

## Consequences
- **UX de Fluxo Contínuo**: O motorista sempre vê a tela de sucesso, não importando a rede.
- **Backend Adaptado**: A API de Handshake (Fase 2) precisará aceitar o `offline_timestamp` no payload para garantir auditoria correta de quando a carga passou para a mão da Transportadora, e não quando a internet pegou na estrada.
- Dependência de confiança no relógio interno do dispositivo móvel do motorista para a marcação.
