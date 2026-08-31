# Transferência de Custódia Assíncrona (Pending Sync)

Decidimos que a transferência de custódia (ex: do motorista para o armazém) em áreas sem cobertura de rede mudará o estado da carga para "Pending Sync" após o escaneamento do QR Code. A custódia legal (Accepted) só é efetivada após o dispositivo de borda sincronizar o histórico via MQTT no backend e o sistema validar a ausência de Rupturas. Se houver ruptura prévia no histórico, a transferência é rejeitada. Isso evita que o recebedor assuma a responsabilidade financeira "no escuro" por uma carga já danificada.
