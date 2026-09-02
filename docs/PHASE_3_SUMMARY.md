# AgroTrace - Resumo da Fase 3 (Mobile e Offline)

## Visão Geral
A Fase 3 foca no aplicativo mobile (React Native / Expo) que será usado pelos motoristas. O principal desafio aqui é que as estradas e fazendas muitas vezes não têm sinal de internet, então o app precisa funcionar offline e não pode travar.

## Entregas Principais

### 1. Funcionamento Offline (Fila de Sincronização)
- **Zustand + AsyncStorage**: Quando o motorista assume uma carga sem internet, o aplicativo salva as informações direto no armazenamento do celular.
- **Horário Exato**: O app guarda o horário local exato em que o QR Code foi lido (`offline_timestamp`). Isso é importante para fins legais e de seguro, garantindo que o horário registrado seja o da leitura, e não o de quando o celular reconectou na internet.

### 2. Sincronização Automática
- O aplicativo monitora o sinal de celular em segundo plano.
- Assim que detecta conexão com a internet, o app envia automaticamente os dados salvos para a API. O motorista não precisa lembrar de apertar nenhum botão de "sincronizar".

### 3. Interface e Uso da Câmera
- **Câmera**: Configuramos a câmera para ler o QR Code e parar imediatamente, evitando que o app fique tentando ler várias vezes seguidas e trave.
- **Design para a Estrada**: Usamos botões grandes e um modo escuro (Dark Mode) com alto contraste para facilitar a leitura no sol e o toque na tela com o celular no suporte do painel.
- **Foco na Bateria**: O celular não fica rastreando a localização do motorista o tempo todo, e nem se conecta ao sensor via Bluetooth. O rastreamento pesado fica por conta do sensor da carga, poupando a bateria do telefone.

## Conclusão
Com o aplicativo finalizado, o sistema consegue ligar as pontas entre a logística física e o monitoramento em nuvem. O motorista consegue trabalhar tranquilamente mesmo sem internet, e o servidor arruma o histórico assim que os dados chegam.
