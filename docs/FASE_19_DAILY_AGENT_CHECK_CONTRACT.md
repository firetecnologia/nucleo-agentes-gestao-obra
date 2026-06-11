# Contrato de Varredura Diária dos Agentes — Fase 19

Este contrato define a saída mínima esperada do workflow de varredura diária.

## Comando esperado

```bash
python -m src.workflows.run_daily_agent_check --project-id <ASANA_PROJECT_GID> --dry-run
```

## Entrada

- `project_id`: GID do projeto no Asana.
- `dry_run`: padrão `true`.
- `mode`: `sample`, `read_only` ou `approved_execution`.

## Filtros mínimos

O workflow deve analisar tarefas que atendam pelo menos um dos critérios:

- vencidas;
- vencem hoje;
- vencem amanhã;
- status pronto para análise;
- evidência obrigatória ausente;
- bloqueadas;
- impacto de prazo médio/alto/crítico;
- impacto financeiro médio/alto/crítico;
- impacto cliente médio/alto/crítico;
- aguardando aprovação.

## Saída JSON mínima

```json
{
  "dry_run": true,
  "mode": "sample",
  "project_id": "PROJECT_GID_EXEMPLO",
  "tasks_scanned": 0,
  "tasks_analyzed": 0,
  "planned_actions": [],
  "human_reviews_created": [],
  "risks_found": [],
  "summary": {
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "blocked": 0,
    "missing_evidence": 0
  },
  "external_operations": []
}
```

## Garantias obrigatórias

- `external_operations` deve ser vazio em dry-run.
- Nenhuma escrita real pode ocorrer na Fase 19.
- Cada ação planejada sensível deve gerar item de revisão humana.
- O relatório diário deve ser salvo localmente ou impresso como JSON.
- O workflow deve rodar sem token usando samples.

## Testes mínimos

- `test_daily_check_runs_in_sample_mode`
- `test_daily_check_does_not_write_to_asana`
- `test_daily_check_creates_review_for_high_financial_impact`
- `test_daily_check_flags_missing_evidence`
- `test_daily_check_summary_contract`
