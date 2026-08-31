# Definição de Ruptura por Tempo Contínuo e CargoProfile

Decidimos que as regras de "Ruptura de Cadeia Fria" serão definidas por um `CargoProfile` (ex: Proteína, Café) que estipula não apenas o limite de temperatura, mas também o tempo contínuo de exposição. Picos curtos que não estouram essa janela de tempo geram apenas eventos de Warning. A Ruptura (estado crítico) só é consolidada se o limite for ultrapassado pelo tempo contínuo estipulado, aproveitando os time-buckets nativos do TimescaleDB para a validação no backend.
