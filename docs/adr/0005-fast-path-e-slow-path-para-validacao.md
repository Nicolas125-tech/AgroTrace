# Fast-Path e Slow-Path para Validação de Custódia

Decidimos separar a validação de custódia em duas vias após um período offline prolongado:
1. **Fast-Path**: O handshake MQTT trará apenas o ID da remessa e uma flag booleana calculada pela Máquina de Estados da borda. Isso destrava ou rejeita a custódia instantaneamente para não parar a operação logística (ex: liberação no porto).
2. **Slow-Path**: O histórico completo de telemetria será ingerido de forma assíncrona no TimescaleDB, permitindo conciliação posterior (auditoria antifraude) para garantir que a telemetria bruta confirma a flag do handshake.
