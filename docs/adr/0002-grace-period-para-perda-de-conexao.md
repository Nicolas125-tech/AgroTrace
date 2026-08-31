# Grace Period para Perda de Conexão em Trânsito

Decidimos usar um "Grace Period" atrelado à Rota ou Meio de Transporte para classificar quedas de rede. Quando o sinal cai, o status muda para "In Transit - Offline" (estado normal). Alertas críticos de desconexão só disparam no painel web se o dispositivo não voltar a se comunicar após a expiração desse período. Isso evita a fadiga de alarmes (um problema comum em roteamentos agro/marítimos) enquanto mantém o fail-safe local (buzzer/LED) rodando de forma autônoma no hardware da borda.
