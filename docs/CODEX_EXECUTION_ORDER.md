# Ordem de Execução para Codex

Execute nesta ordem, sem pular fases.

## 1. Fase 15 — Validação técnica

Issue: #22

Prioridade máxima.

Não implemente integração real antes de o CI ficar verde.

## 2. Fase 16 — Leitura real do Asana

Issue: #23

Apenas leitura. Nenhuma escrita real.

## 3. Fase 17 — Leitura de planilhas de obra

Issue: #24

Ler XLSX local, encontrar grupo/prestador/valor e gerar ação planejada.

## 4. Fase 18 — Escrita controlada

Use `docs/FASE_18_19_IMPLEMENTATION_BRIEF.md`.

A escrita real só pode acontecer com aprovação humana e travas de segurança.

## 5. Fase 19 — Automação recorrente

Use `docs/OPERACAO_AUTOMATIZADA_ROTEIRO.md`.

O robô deve varrer tarefas, analisar e gerar fila de revisão.

## 6. Fase 20 — Rotina de execução no GitHub Actions ou servidor local

Use `.github/workflows/manual-dry-run-demo.yml` como base.

## Critérios gerais

- Toda fase deve ter testes.
- Todo workflow deve preservar `dry_run` como padrão.
- Nenhum token real no repositório.
- Nenhum envio externo automático.
- Nenhuma comunicação com cliente sem revisão humana.
- Nenhuma ação financeira sensível sem revisão humana.
