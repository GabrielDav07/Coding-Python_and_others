
<!-- Exercício 1.3 - Decisões de Arquitetura com CAP -->
<!--para rodar: ctrl + shift + V-->


# Decisão de Arquitetura - Teorema CAP

| Cenário | CP/AP | Justificativa |
| :--- | :--- | :--- |
| **1. Tabela de saldo bancário de clientes** | CP | Exige consistência forte para evitar divergências de saldo ou inconsistências financeiras entre nós, priorizando acurácia em vez de alta disponibilidade contínua durante partições. |
| **2. Ingestão de 500 mil eventos de firewall por minuto num SOC** | AP | Exige alta disponibilidade e vazão máxima para gravar volume massivo de logs sem perda ou travamento da rede, aceitando consistência eventual. |
| **3. Cache de tokens de sessão de usuários logados** | AP | Foca em baixa latência e alta disponibilidade na autenticação contínua; em caso de falha de partição, tokens podem ser revalidados no banco principal. |
| **4. Registro de quem autorizou cada transferência (auditoria)** | CP | Dados de auditoria não podem sofrer perda ou divergência temporal para fins de conformidade e não repúdio, exigindo consistência total no salvamento. |
| **5. Feed de indicadores de ameaça (IOCs) replicado em 5 regiões** | AP | Prioriza replicação distribuída e consulta rápida e disponível globalmente, tolerando pequeno atraso de sincronização entre regiões. |
