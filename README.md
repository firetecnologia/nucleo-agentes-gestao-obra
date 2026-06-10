# Núcleo 377 — Agentes de Gestão Premium de Obra

Este pacote contém a base operacional para desenvolver um sistema de agentes para gestão de obras da Núcleo 377.

## Objetivo

Criar um sistema onde agentes digitais acompanham o planejamento de cada obra, analisam entregas dos departamentos, cobram evidências, geram próximas tarefas e notificam a equipe via Asana ou outro canal configurado.

## Estrutura sugerida

- `AGENTS.md` — instruções gerais para o Codex trabalhar neste projeto.
- `01_prompt_codex_inicial.md` — prompt inicial para iniciar o desenvolvimento no Codex.
- `02_agente_orquestrador.md` — prompt mestre do Agente Orquestrador da Obra.
- `03_agentes_especialistas.md` — prompts dos agentes por departamento.
- `04_matriz_decisao.md` — regras de aprovação, devolução, escalação e acionamento.
- `05_campos_asana.yaml` — campos personalizados sugeridos para o Asana.
- `06_fluxo_operacional.yaml` — fluxo entre departamentos.
- `07_modelo_eventos_asana.yaml` — eventos que devem disparar análise dos agentes.
- `08_backlog_desenvolvimento.md` — etapas de desenvolvimento do sistema.
- `09_modelo_payload_tarefa.json` — estrutura base de dados para análise de uma tarefa.
- `10_exemplo_saida_agente.json` — exemplo de resposta do agente.

## Visão do sistema

O Asana deve ser a fonte da verdade operacional.  
O Agente Orquestrador deve ser o cérebro do fluxo.  
Os agentes especialistas devem analisar entregas específicas por departamento.  
A automação deve transformar eventos do Asana em análises, comentários, alertas e criação de novas tarefas.
