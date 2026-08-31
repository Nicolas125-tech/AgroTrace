# Timeout de Pending Sync resulta em Quarentena

Decidimos que se uma transferência de custódia permanecer no estado `Pending Sync` além de um limite aceitável (ex: 24 horas), o sistema (via um worker em background) transicionará a Remessa para o status de `Quarantined`. A ausência de dados, que pode ocorrer por destruição física do sensor, não configurará aceite tácito nem devolução automática. A resolução desse estado será estritamente manual, requerendo auditoria física e intervenção de um administrador.
