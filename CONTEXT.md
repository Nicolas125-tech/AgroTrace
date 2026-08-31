# AgroTrace

Sistema de rastreamento de cadeia de frio para remessas agropecuárias com sensores de borda e validação de custódia.

## Language

**Remessa**:
Uma carga física (grão, proteína, café) monitorada através da cadeia de suprimentos. Após uma ruptura confirmada, seu ciclo de vida é encerrado e não pode ser reutilizada.
_Avoid_: Carga, Lote, Shipment

**CargoProfile**:
Perfil de tolerância da remessa que define limites máximo/mínimo de temperatura e o tempo contínuo de exposição permitido.
_Avoid_: Regra de Temperatura, Configuração

**Ruptura**:
Um estado crítico irreversível onde a remessa violou o tempo contínuo de exposição do seu CargoProfile. Resulta no encerramento da remessa (status `Breached`).
_Avoid_: Violação, Alarme, Breach

**Handshake de Custódia**:
O processo de transferência de responsabilidade. Inicia com um escaneamento físico (QR Code) e é validado pelo Fast-Path (imediato) ou Slow-Path.

**Pending Sync**:
Estado temporário de custódia onde a carga foi recebida fisicamente, mas aguarda o payload MQTT (Fast-Path) para validar se houve Ruptura.
_Avoid_: Recebido, Aguardando

**Quarantined**:
Estado de bloqueio digital acionado quando o descarregamento (Pending Sync) estoura o tempo limite (ex: 24h) por falha no hardware. Exige auditoria e resolução manual (forçando Accepted ou Rejected).
_Avoid_: Disputed, Perdido

**Fast-Path Validation**:
Validação imediata de custódia baseada em um booleano de ruptura pré-calculado pela máquina de estados (FSM) da borda, enviado no primeiro pulso MQTT.

**Slow-Path Validation**:
Conciliação assíncrona feita em background pelo backend, ingerindo o histórico completo de telemetria no TimescaleDB para bater com a flag antifraude do Fast-Path.

**Grace Period**:
Tempo de tolerância esperado sem conexão de rede, definido pela rota ou meio de transporte da remessa.

**In Transit - Offline**:
Status da remessa quando perde o sinal dentro do Grace Period. É um estado normal e não gera alertas críticos no painel.
_Avoid_: Desconectado, Sinal Perdido

**Tenant (Inquilino)**:
A entidade formal e faturável do sistema (Produtor, Transportadora Logix, Comprador) que possui login e cujos dados são isolados no banco de dados via RLS.
_Avoid_: Usuário, Empresa

**Motorista Efêmero**:
O motorista autônomo subcontratado. Ele age com a posse física provisória em nome de uma Transportadora formal, interagindo com o sistema apenas via Portal Público (sem possuir uma conta própria).
_Avoid_: Sub-contratado, Motorista Terceiro

**Signed URL**:
Link temporário e criptográfico embutido no QR Code da remessa. Permite acesso ao Portal Público para realização do Handshake por motoristas efêmeros, bloqueando acesso ao histórico de telemetria.
_Avoid_: Link Público, Token URL

**Mutation Queue Persistente**:
Fila local no dispositivo móvel (app) que armazena intenções de mudança de estado (ex: Handshake) com o timestamp exato em que a ação ocorreu (offline_timestamp), sincronizando automaticamente quando a conectividade é restabelecida.

**Cloud-Only App**:
Abordagem onde o aplicativo interage com o ecossistema estritamente através das APIs em nuvem, não estabelecendo conexões diretas (ex: BLE/Bluetooth) com o hardware embarcado na remessa. Em áreas sem conexão, o usuário deve confiar nos alertas físicos (LEDs/Buzzers) do próprio dispositivo da carga.

**Rastreio em Eventos Discretos (GPS Discreto)**:
Captura de localização do aplicativo móvel realizada apenas durante interações pontuais do motorista (ex: escaneamento de QR Code), deixando a coleta contínua de GPS para o hardware logístico. Preserva a bateria do smartphone e simplifica o gerenciamento de permissões (Foreground apenas).
