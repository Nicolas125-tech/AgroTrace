# Imutabilidade da Remessa Pós-Ruptura

Decidimos que a entidade Remessa (Shipment) é imutável em sua essência logística. Uma ruptura confirmada marcará a remessa como `Breached` e o seu ciclo de vida será permanentemente encerrado, revertendo a custódia para o detentor anterior. Caso a carga física seja reaproveitada, leiloada ou vendida como produto rebaixado, o sistema exigirá a criação de uma nova Remessa com um novo `CargoProfile`, evitando assim contaminação de histórico e simplificando a modelagem DDD.
