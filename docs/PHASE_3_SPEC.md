# Especificação do Aplicativo Mobile - Fase 3

## Problema
Motoristas na estrada frequentemente perdem o sinal de celular. Se o aplicativo não funcionar offline, eles não vão conseguir registrar o recebimento da carga (Handshake). Além disso, se o sistema só registrar o horário em que a internet voltou em vez do horário exato do recebimento, a transportadora pode ter problemas com a seguradora. Por fim, o aplicativo não pode gastar muita bateria com GPS nem exigir que o motorista faça pareamento Bluetooth com o sensor.

## Solução
Vamos criar um aplicativo em React Native/Expo focado apenas na comunicação com o servidor. O Handshake vai usar uma fila local no celular que salva o horário exato (`offline_timestamp`) e envia os dados assim que a internet voltar. O GPS só será usado rapidamente quando o motorista fizer alguma ação no app, deixando o rastreamento principal para o hardware da carreta.

## Histórias de Usuário
1. Como motorista, quero escanear o QR Code de uma carga mesmo sem internet, para não ficar travado na fazenda.
2. Como transportadora, quero que o sistema grave o horário exato da leitura offline, para auditorias e seguro.
3. Como motorista, quero que o app envie os dados sozinho quando o sinal voltar, para não ter que lembrar de clicar em sincronizar.
4. Como motorista, quero que o app pegue meu GPS apenas quando eu o uso, para não gastar toda a bateria do celular durante a viagem.
5. Como motorista, quero ver o status da carga pela nuvem, para não ter dor de cabeça conectando o celular no Bluetooth do sensor.

## Decisões Técnicas
- **Fila Offline**: Uso de Zustand e AsyncStorage para guardar os recebimentos.
- **Mudança na API**: O endpoint vai aceitar o parâmetro `offline_timestamp`.
- **Registro no Banco**: Se a API receber um `offline_timestamp`, vai usar ele. Se não, vai usar o horário atual do servidor.
- **Sem Bluetooth**: Os alertas vão vir da API (Polling ou Websocket) quando o app estiver aberto. Se não tiver internet, o motorista olha os LEDs do sensor na carreta.
- **GPS sob demanda**: O pacote `expo-location` só vai rodar no momento da leitura do QR Code.

## Como Testar
- **Teste de Auditoria (Backend)**: Enviar para a API um registro com o `offline_timestamp` apontando para 2 horas atrás. O banco deve aceitar e salvar esse horário antigo como a hora oficial do evento, ignorando o horário atual do servidor.
- **Teste de Sincronização (Mobile)**: Desligar a internet do celular, ler o QR Code, preencher os dados, religar a internet e verificar se o app mandou a requisição para o servidor automaticamente.

## Fora de Escopo
- Rastreamento contínuo de localização (background location) pelo celular.
- Conexão Bluetooth com o sensor da carga.
- Cadastro e login para motoristas (será tudo via QR Code com link temporário).
