# AgroTrace

Sistema para rastreamento de temperatura de cargas agropecuárias. O sistema monitora sensores IoT e valida a transferência da carga entre os responsáveis.

## Termos do Projeto

**Remessa**:
A carga física (grão, carne, etc) que estamos monitorando. Se o limite de temperatura for ultrapassado (ruptura), o ciclo dela acaba e não dá para reutilizar.

**CargoProfile**:
Regras que definem os limites de temperatura (máximo e mínimo) e por quanto tempo a carga pode ficar fora dessa faixa.

**Ruptura**:
Quando a temperatura da carga sai dos limites por muito tempo, violando o CargoProfile. Isso encerra a remessa (status `Breached`).

**Handshake de Custódia**:
É a transferência de responsabilidade da carga de uma pessoa para outra. Começa lendo um QR Code e é validado na hora (Fast-Path) ou depois (Slow-Path).

**Pending Sync**:
Quando a carga foi escaneada e recebida, mas o sistema ainda está esperando os dados dos sensores chegarem via MQTT para confirmar se houve alguma ruptura de temperatura.

**Quarantined**:
Se uma carga fica presa no status "Pending Sync" por muito tempo (ex: mais de 24h) por problema no sensor, ela entra em quarentena. Alguém precisa entrar no sistema e aprovar ou rejeitar manualmente.

**Fast-Path Validation**:
Validação rápida. O primeiro dado enviado pelo sensor já diz se houve ruptura ou não, para agilizar a resposta.

**Slow-Path Validation**:
Validação que roda em background. O sistema analisa todo o histórico de dados no banco (TimescaleDB) para conferir se a resposta rápida (Fast-Path) estava certa.

**Grace Period**:
Tempo limite que o sistema aceita que a carga fique sem enviar dados porque perdeu o sinal de internet no caminho.

**In Transit - Offline**:
Status de quando a carga perde o sinal de internet, mas ainda está dentro do tempo limite (Grace Period). É normal e não gera alertas.

**Tenant**:
A empresa que paga pelo sistema e tem login (como uma transportadora ou produtor). Os dados de um tenant não se misturam com os dos outros no banco.

**Motorista Temporário (Efêmero)**:
O motorista que faz o frete, mas não tem conta no sistema. Ele só acessa um link temporário para registrar a carga e pronto.

**Signed URL**:
O link seguro que vem no QR Code da carga. Deixa o motorista temporário registrar que pegou a carga sem precisar de login, mas não deixa ele ver o histórico de temperatura.

**Fila Local de Sincronização**:
Como nem sempre tem internet na estrada, o aplicativo salva quando o motorista escaneia a carga e guarda o horário certo. Quando a internet volta, o app envia os dados para o servidor.

**App Baseado em Nuvem (Cloud-Only)**:
O aplicativo de celular não conecta direto no sensor da carga por Bluetooth. Tudo vai pra nuvem primeiro. Se estiver sem sinal, o motorista tem que olhar os LEDs do próprio sensor para ver se está tudo bem.

**Rastreio Simples de GPS**:
O app só pega a localização do motorista quando ele faz alguma ação (tipo escanear o QR Code). O rastreio contínuo do trajeto fica por conta do sensor logístico, para não gastar a bateria do celular do motorista.
