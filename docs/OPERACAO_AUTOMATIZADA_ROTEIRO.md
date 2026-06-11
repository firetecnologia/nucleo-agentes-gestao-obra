# Roteiro Operacional Automatizado — Agentes Núcleo 377

Este roteiro descreve como a operação deve funcionar quando as fases de integração estiverem prontas.

## Fluxo ideal

1. Agente lê tarefas reais do Asana.
2. Agente converte tarefas em `TaskPayload`.
3. Agente valida evidências.
4. Agente classifica risco.
5. Agente chama especialista por departamento.
6. Agente gera decisão.
7. Agente cria ação planejada.
8. Ação planejada entra em revisão humana.
9. Gestão aprova ou rejeita.
10. Apenas ações aprovadas podem escrever no Asana.
11. Toda ação gera auditoria.
12. Relatório diário consolida o que foi feito e o que está pendente.

## Rotina diária sugerida

### 07h00 — Varredura automática

Comando futuro:

```bash
python -m src.workflows.run_daily_agent_check --project-id <ASANA_PROJECT_GID> --dry-run
```

O agente deve verificar:

- tarefas vencidas;
- tarefas que vencem hoje;
- tarefas sem evidência;
- tarefas prontas para análise;
- tarefas bloqueadas;
- tarefas com impacto financeiro ou de prazo.

### 07h10 — Fila de revisão humana

O sistema deve gerar uma lista de itens que a gestão precisa olhar.

### 07h30 — Ações aprovadas

Somente depois da aprovação, o sistema poderá preparar escrita real no Asana.

### 17h30 — Fechamento diário

Gerar resumo interno:

- tarefas analisadas;
- riscos encontrados;
- pendências por departamento;
- ações planejadas;
- ações aprovadas;
- ações executadas;
- bloqueios para amanhã.

## Rotina semanal

Toda sexta-feira:

- consolidar relatório semanal;
- listar desvios de custo;
- listar desvios de prazo;
- listar decisões pendentes;
- listar comunicação necessária com cliente;
- gerar rascunho interno para revisão humana.

## Indicadores mínimos

- tarefas analisadas por dia;
- tarefas corrigidas;
- tarefas bloqueadas;
- evidências ausentes;
- riscos por departamento;
- tempo médio de resposta;
- valores financeiros identificados;
- ações aguardando aprovação;
- ações aprovadas;
- ações executadas.

## Regra operacional

Automação não substitui gestão. Automação antecipa, organiza, alerta e executa tarefas simples aprovadas.
