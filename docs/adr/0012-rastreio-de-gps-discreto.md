# 0012. Rastreio de GPS Exclusivamente em Eventos Discretos

## Date
2026-08-31

## Context
Precisávamos decidir se o smartphone do motorista funcionaria como um rastreador veicular redundante, enviando coletas de localização de 5 em 5 minutos em background para complementar o sensor de GPS do hardware da carreta.

## Decision
Optamos pelo **Rastreio de GPS Discreto**. O aplicativo não solicitará e não usará permissões de "Background Location". O rastreio temporal contínuo (Slow-path GPS) continuará sendo monopólio exclusivo do hardware alimentado pela bateria do veículo. O App mobile só coletará as coordenadas pontuais em primeiro plano (Foreground) quando ocorrer um evento logístico manual (ex: Scans de QR Code, Pausas, Handshakes).

## Consequences
- **Economia Drástica de Bateria**: Sem serviços rodando em background 24h, garantimos que o app será amado e não desinstalado/forçado a fechar pelo motorista autônomo.
- **Privacidade Assegurada**: O Motorista Efêmero sabe que não estamos rastreando sua vida em segundo plano.
- **Simplificação das Lojas (App Store/Play Store)**: Escapamos das severas e burocráticas revisões do Google e da Apple sobre o uso não razoável de localização em background.
