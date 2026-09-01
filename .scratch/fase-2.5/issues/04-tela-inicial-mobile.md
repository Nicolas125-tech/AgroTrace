# 04: Tela inicial + histórico no mobile

**What to build:** O app mobile ganha uma tela inicial amigável e um histórico local dos handshakes realizados pelo motorista. Suposição: o histórico será lido apenas localmente (do Zustand/AsyncStorage já existente). Se no futuro exigirmos histórico validado no servidor, este ticket passaria a depender da autenticação de tenant.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Criar uma nova tela inicial no app mobile separada do scanner direto.
- [ ] Implementar visualização do histórico de handshakes baseada nos dados salvos localmente via Zustand/AsyncStorage.
- [ ] Refinar o fluxo de navegação entre Home e o Scanner de QR code.
