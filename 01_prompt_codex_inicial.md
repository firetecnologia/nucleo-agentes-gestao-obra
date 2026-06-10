# Prompt inicial para usar no Codex

Você está trabalhando no projeto "Núcleo 377 — Agentes de Gestão Premium de Obra".

Leia primeiro o arquivo `AGENTS.md` e siga todas as instruções.

## Contexto de negócio

A Núcleo 377 é uma empresa de engenharia que está estruturando um sistema premium de gestão de obras. A equipe trabalha com departamentos como Gestão, Planejamento, Engenharia, Projetos, Compras, Financeiro e Atendimento.

O objetivo é criar agentes que acompanhem as tarefas da obra no Asana, analisem entregas, cobrem evidências, identifiquem riscos e acionem o próximo departamento.

## Objetivo da primeira entrega

Crie um MVP em Python com arquitetura limpa para:

1. Receber um payload de tarefa vindo do Asana.
2. Identificar:
   - obra;
   - departamento responsável;
   - etapa da obra;
   - status atual;
   - evidências anexadas;
   - riscos informados;
   - prazo;
   - impacto no cliente;
   - impacto financeiro;
   - próximo departamento.
3. Analisar a tarefa usando uma matriz de decisão.
4. Gerar uma decisão estruturada:
   - `approved`;
   - `request_correction`;
   - `escalate_management`;
   - `ask_client`;
   - `create_next_tasks`;
   - `blocked`.
5. Gerar uma mensagem de comentário para o Asana.
6. Gerar tarefas sugeridas para o próximo departamento.
7. Rodar inicialmente em modo `dry_run`, sem alterar o Asana.

## Requisitos técnicos

- Use Python.
- Crie uma estrutura modular.
- Use dataclasses ou Pydantic para representar dados.
- Crie testes unitários para a matriz de decisão.
- Não use tokens reais.
- Configure `.env.example`.
- Crie um arquivo `sample_task_payload.json`.
- Crie README com instruções de execução.
- Crie logs claros.
- Mantenha todas as mensagens em português do Brasil.

## Entregáveis

Crie os arquivos necessários para um MVP funcional:

```txt
src/
  domain/
  agents/
  integrations/
  workflows/
tests/
README.md
.env.example
sample_task_payload.json
```

## Critérios de aceite

A primeira versão deve permitir rodar:

```bash
python -m src.workflows.analyze_task --input sample_task_payload.json --dry-run
```

E retornar uma saída JSON com:

```json
{
  "decision": "request_correction",
  "risk_level": "medium",
  "asana_comment": "...",
  "next_tasks": [],
  "requires_human_review": true
}
```

Comece criando a estrutura, os modelos de dados, a matriz de decisão e um teste simples.
