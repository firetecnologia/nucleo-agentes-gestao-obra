# Qualidade e validacao do MVP

Este checklist deve ser executado antes de qualquer apresentacao interna, demo para diretoria ou evolucao de integracao. Tudo permanece em `dry-run`.

## Comando principal

```bash
python -m unittest discover
```

## O que a suite valida

- Smoke tests dos fluxos principais: analise de tarefa, evento, relatorio, dashboard, simulacao, fila de revisao, interface web local e mapeamentos Asana sandbox.
- Contratos JSON dos retornos principais para evitar quebra silenciosa.
- Garantias de seguranca: `dry_run=true`, `external_operations=[]`, sem chamada real e sem envio ao cliente.
- Rascunho de cliente continua como `draft_only_no_external_send`.

## Checklist antes da demo

1. Confirmar que `.env` nao contem token real.
2. Confirmar que `ASANA_ENABLE_REAL_ACTIONS` permanece `false`.
3. Rodar `python -m unittest discover`.
4. Rodar a simulacao ponta a ponta:

```bash
python -m src.workflows.run_simulation --input samples/obra_piloto_scenario.json --dry-run
```

5. Conferir na saida:

```json
{
  "dry_run": true,
  "external_operations": []
}
```

6. Abrir a interface web local apenas se necessario:

```bash
python -m src.web.app
```

## Pontos que nao podem regredir

- Nenhum workflow pode depender de credenciais.
- Nenhuma mensagem pode ser enviada automaticamente ao cliente.
- Nenhuma tarefa real pode ser criada no Asana.
- Nenhum comentario real pode ser postado no Asana.
- Impacto financeiro alto continua exigindo revisao humana.
- Decisoes de cliente continuam exigindo revisao humana.
