# Phase 3 Mobile App Specification

## Problem Statement
O motorista na estrada frequentemente se depara com a falta de sinal de celular (Offline). Sem um aplicativo preparado (Offline-First), ele não consegue realizar o Handshake escaneando o QR Code da remessa. Além disso, se a sincronização ocorrer horas depois e o sistema registrar a hora atual do upload em vez da hora exata do escaneamento, a Transportadora perderá respaldo legal em caso de sinistro e seguros de cargas. O aplicativo também não pode drenar a bateria rodando GPS em background o tempo todo, e não pode travar a UX forçando integrações complexas por Bluetooth para alertas locais.

## Solution
Criaremos um App Mobile em React Native/Expo que atua de forma discreta, puramente na camada de nuvem (Cloud-Only). O Handshake usará uma fila local (Zustand) que grava o `offline_timestamp` com exatidão legal e sincroniza em background quando a rede retornar. O GPS será coletado exclusivamente em primeiro plano (Foreground) durante eventos de mutação, deixando o rastreamento pesado a cargo do próprio veículo.

## User Stories
1. As a Motorista Efêmero, I want to scan a shipment's QR code without an internet connection, so that I don't get blocked at a remote farm.
2. As a Transportadora, I want the system to record the exact offline timestamp of the physical handover, so that legal and insurance liabilities are accurately audited.
3. As a Motorista Efêmero, I want the app to sync my pending handshakes automatically when 4G returns, so that I don't have to remember to click "sync".
4. As a Motorista Efêmero, I want the app to only track my location when I actively interact with it, so that my personal phone's battery isn't drained during a 48-hour trip.
5. As a Motorista Efêmero, I want to view my current shipment's status based strictly on the cloud data, so that I don't need complex Bluetooth pairing steps with the physical cargo sensor.

## Implementation Decisions
- **Fila Offline**: Utilizaremos Zustand + AsyncStorage para enfileirar as ações de Handshake.
- **Backend Schema Change**: O payload Pydantic `EphemeralDriverPayload` aceitará a variável `offline_timestamp`.
- **FSM Timestamp**: A máquina de estados registrará o campo `initiated_at` usando o `offline_timestamp` recebido; se nulo, usará `datetime.utcnow()`.
- **Nenhum BLE**: Todo alerta virá da API FastAPI (Polling ou Websocket ativo quando em tela). Se offline, o motorista confiará nas luzes físicas da carreta.
- **Localização Discreta**: Usaremos `expo-location` apenas em Foreground, disparando junto aos eventos manuais do motorista.

## Testing Decisions
- **Seam 1 (Backend Auditoria Retroativa)**: Testaremos o endpoint `/api/public/handshake` enviando um payload com `offline_timestamp` forjado 2 horas no passado. O banco de dados deve aprovar e a query de validação deve cravar que `initiated_at` respeitou retroativamente o timestamp, e não o relógio atual do servidor.
- **Seam 2 (Mobile Queue Sync)**: (A ser implementado no front) Simularemos falta de rede no celular, adicionaremos o Handshake, restauraremos a rede e validaremos se o Request final foi enviado.

## Out of Scope
- Rastreamento contínuo de background location no celular.
- Integração Bluetooth com o sensor físico da carga.
- Cadastro/Login de motoristas no aplicativo (será sempre via QR Code).

## Further Notes
O sucesso desta arquitetura reside em manter a UX a mais indolor possível para caminhoneiros. Bateria duradoura e fluidez offline são as métricas de sucesso.
