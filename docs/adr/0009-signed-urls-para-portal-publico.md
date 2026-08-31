# 0009. Signed URLs para Portal Público

## Date
2026-08-31

## Context
O Motorista Efêmero (sem login) fará o Handshake escaneando o QR Code físico na remessa. A URL do QR não poderia usar apenas IDs de banco de dados (`/scan/123`), pois seria previsível e permitiria scraping de status logístico de todas as cargas. Além disso, a telemetria não pode ficar exposta.

## Decision
O QR Code gerará uma **Signed URL** contendo um token criptográfico hash/JWT com validade ou vinculação estrita à Remessa (ex: `?token=eyJhb...`). 

O acesso sem autenticação tradicional baterá num portal Frontend isolado (Portal Público), que consumirá um endpoint do Backend exclusivo para Handshakes. 

## Consequences
- **Segurança via Ofuscação e Assinatura**: O acesso só é possível pra quem estiver segurando o papel/documento com o QR Code. 
- **Privacidade da Telemetria**: A rota FastAPI atrelada a este token público omitirá integralmente a série temporal e os mapas de GPS, expondo estritamente o Status da Remessa, Destino e a tela para aceitar Custódia.
