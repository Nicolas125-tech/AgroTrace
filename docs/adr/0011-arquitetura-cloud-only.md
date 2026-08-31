# 0011. Arquitetura Cloud-Only (Sem BLE) para Alertas do Mobile

## Date
2026-08-31

## Context
Quando há uma ruptura da cadeia de frio no ambiente de carga isolada (sem 4G), o sensor físico atua ativando um Fail-safe (alarme local em LED/Buzzer). Havia o dilema de fazer o App mobile parear fisicamente com esse hardware por Bluetooth (BLE) para exibir o alerta no celular do motorista na cabine do caminhão, mesmo sem internet.

## Decision
Adotaremos uma arquitetura **Cloud-Only App** para a comunicação de alertas e telemetria no mobile. O aplicativo não fará pareamento ou escaneamento local de Bluetooth. Qualquer comunicação com as Remessas se dará exclusivamente consumindo as APIs REST/WebSockets em nuvem (FastAPI). Em caso de isolamento total de rede, a responsabilidade do aviso de ruptura passa a ser puramente visual/sonora diretamente no hardware físico.

## Consequences
- **Velocidade de Iteração Máxima**: Permaneceremos na stack gerenciada do Expo Go. Sem precisar ejetar para builds nativos de bibliotecas pesadas de Bluetooth.
- **Risco Minimizado de Fragmentação**: Não precisaremos lidar com as instabilidades agressivas da stack Bluetooth de diversos aparelhos Android de baixo custo utilizados por motoristas terceirizados.
