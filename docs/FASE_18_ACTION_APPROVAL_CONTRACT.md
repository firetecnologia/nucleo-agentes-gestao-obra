# Contrato de Aprovação de Ações Asana — Fase 18

Este contrato define o formato mínimo de uma ação planejada antes de qualquer escrita real no Asana.

## Estrutura JSON mínima

```json
{
  "review_id": "REV-ASANA-001",
  "source": "agent_analysis",
  "obra": "Obra Exemplo",
  "action_type": "create_internal_subtask",
  "status": "pending",
  "requires_human_review": true,
  "parent_task_gid": "TASK_GID_EXEMPLO",
  "planned_task": {
    "name": "Nome da subtarefa",
    "notes": "Descrição da subtarefa",
    "assignee_gid": "ASSIGNEE_GID_EXEMPLO",
    "due_on": "2026-06-12"
  },
  "planned_comment": null,
  "planned_fields": {},
  "safety": {
    "dry_run": true,
    "external_call": false,
    "real_action": false,
    "client_message": false,
    "financial_impact_reviewed": false
  }
}
```

## Status aceitos

- `pending`
- `approved`
- `rejected`
- `changes_requested`
- `executed`
- `failed`

## Ações aceitas inicialmente

- `post_internal_comment`
- `create_internal_subtask`
- `update_operational_field`

## Validações obrigatórias

Antes de executar ação real:

- `status == approved`
- `requires_human_review == true`
- `review_id` existe
- `action_type` está na lista permitida
- `safety.client_message == false`
- `safety.real_action == false` antes da execução
- ambiente com `ASANA_ENABLE_REAL_ACTIONS=true`
- chamada com `confirm_real_action=True`

## Resultado esperado após execução real

```json
{
  "review_id": "REV-ASANA-001",
  "executed": true,
  "real_action": true,
  "external_call": true,
  "asana_result": {},
  "audit_id": "AUDIT-001"
}
```

## Bloqueios obrigatórios

A execução deve falhar se:

- ação estiver pendente;
- ação estiver rejeitada;
- ação for comunicação com cliente;
- ação envolver decisão financeira sensível sem revisão;
- token não existir;
- confirmação explícita não existir;
- `ASANA_ENABLE_REAL_ACTIONS` não estiver ativo;
- `action_type` não estiver permitido.
