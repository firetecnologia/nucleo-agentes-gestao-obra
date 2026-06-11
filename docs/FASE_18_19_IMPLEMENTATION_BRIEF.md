# Briefing de Implementação — Fases 18 e 19

## Fase 18 — Escrita controlada no Asana com aprovação humana

### Objetivo

Permitir que ações planejadas pelo agente sejam executadas no Asana somente após aprovação humana explícita.

### Arquitetura sugerida

Criar os módulos:

- `src/actions/action_models.py`
- `src/actions/action_queue.py`
- `src/actions/action_executor.py`
- `src/actions/action_audit.py`
- `src/workflows/prepare_asana_action.py`
- `src/workflows/execute_approved_asana_action.py`

### Modelo mínimo da ação

Campos sugeridos:

- `review_id`
- `source`
- `obra`
- `action_type`
- `status`
- `requires_human_review`
- `parent_task_gid`
- `planned_task`
- `planned_comment`
- `planned_fields`
- `safety`
- `created_at`
- `approved_at`
- `executed_at`
- `executed_by`

### Tipos de ação permitidos inicialmente

- `post_internal_comment`
- `create_internal_subtask`
- `update_operational_field`

### Tipos proibidos inicialmente

- `send_client_message`
- `approve_financial_change`
- `delete_task`
- `close_critical_task`
- `bulk_create_tasks`

### CLI esperada

Preparar ação:

```bash
python -m src.workflows.prepare_asana_action --input samples/planned_action_example.json --dry-run
```

Executar ação aprovada:

```bash
python -m src.workflows.execute_approved_asana_action --review-id REV-ASANA-001 --confirm-real-action
```

### Testes mínimos

- ação pendente não executa;
- ação sem `confirm_real_action` não executa;
- ação sem `ASANA_ENABLE_REAL_ACTIONS=true` não executa;
- ação aprovada em dry-run gera apenas operação planejada;
- ação sensível exige revisão humana;
- auditoria é gravada.

---

## Fase 19 — Automação operacional recorrente

### Objetivo

Criar uma rotina que lê tarefas reais ou samples, analisa automaticamente e gera fila de ações planejadas.

### Arquitetura sugerida

Criar os módulos:

- `src/automation/daily_check.py`
- `src/automation/task_filters.py`
- `src/automation/automation_report.py`
- `src/workflows/run_daily_agent_check.py`

### CLI esperada

```bash
python -m src.workflows.run_daily_agent_check --project-id <ASANA_PROJECT_GID> --dry-run
```

### Modo sample

Quando não houver token ou projeto configurado, o comando deve rodar sobre samples locais.

### Modo read-only real

Quando houver token, o comando deve apenas ler tarefas reais. Nenhuma escrita real pode ocorrer nessa fase.

### Filtros mínimos

- tarefas vencidas;
- tarefas próximas do vencimento;
- tarefas com status pronto para análise;
- tarefas com evidência obrigatória ausente;
- tarefas com impacto financeiro;
- tarefas com impacto de prazo;
- tarefas com pendência de cliente;
- tarefas bloqueadas.

### Saída esperada

JSON contendo:

- `dry_run`
- `project_id`
- `tasks_scanned`
- `tasks_analyzed`
- `planned_actions`
- `human_reviews_created`
- `risks_found`
- `summary`
- `external_operations`

### Testes mínimos

- roda sem token em modo sample;
- roda com mock read-only;
- não escreve no Asana;
- cria ações planejadas;
- cria fila de revisão;
- gera resumo diário.

## Observação final

Não avance para automação de cliente, WhatsApp ou e-mail antes da Fase 19 estar estável.
