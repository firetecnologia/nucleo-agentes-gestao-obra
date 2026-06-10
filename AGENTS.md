# AGENTS.md — Núcleo 377 / Sistema de Agentes de Gestão de Obra

## Contexto do projeto

Este projeto pertence à Núcleo 377, empresa de engenharia que está estruturando um produto premium de planejamento e gestão de obras.

O sistema deve ajudar a equipe a controlar obras com previsibilidade, qualidade, comunicação clara, redução de retrabalho e integração entre departamentos.

## Objetivo técnico

Construir uma aplicação/automação que integre:

- Asana como fonte da verdade das tarefas;
- Agente Orquestrador para analisar andamento da obra;
- Agentes especialistas por departamento;
- Regras de validação de evidências;
- Criação de novas tarefas;
- Comentários automáticos no Asana;
- Alertas antecipados de prazo, risco, custo e cliente;
- Relatórios executivos da obra.

## Linguagem e estilo

- O sistema, comentários e mensagens para equipe devem estar em português do Brasil.
- A comunicação deve ser objetiva, profissional e clara.
- Evitar linguagem excessivamente técnica quando a mensagem for para cliente.
- Para equipe interna, usar linguagem direta e operacional.

## Princípios do produto

1. O agente não substitui a equipe.
2. O agente reduz esquecimento, retrabalho e improviso.
3. Toda tarefa precisa ter responsável, prazo, evidência e próximo passo.
4. Nenhuma etapa crítica deve avançar sem validação.
5. O cliente deve sentir previsibilidade, controle e segurança.
6. O Asana deve ser a fonte da verdade.
7. O histórico da obra deve ficar registrado.

## Regras de desenvolvimento

- Separar lógica de agentes, integração com Asana e camada de notificações.
- Criar funções pequenas e testáveis.
- Evitar hardcode de IDs de projetos, seções e campos.
- Usar variáveis de ambiente para tokens e chaves.
- Criar logs de todas as decisões automáticas.
- Nunca apagar tarefas automaticamente.
- Nunca aprovar impacto financeiro alto sem revisão humana.
- Nunca enviar mensagem ao cliente sem permitir revisão humana na primeira versão.
- Criar modo `dry_run` para simular ações sem alterar o Asana.

## Arquitetura sugerida

Pastas sugeridas:

```txt
src/
  agents/
    orchestrator.py
    planning_agent.py
    engineering_agent.py
    purchasing_agent.py
    projects_agent.py
    finance_agent.py
    client_service_agent.py
    quality_agent.py
  integrations/
    asana_client.py
    notifications.py
  domain/
    task_payload.py
    decision_engine.py
    risk_classifier.py
    evidence_validator.py
  workflows/
    analyze_task.py
    daily_scan.py
    weekly_report.py
  prompts/
    orchestrator.md
    specialists.md
  tests/
```

## Primeira entrega esperada

Criar um MVP que:

1. Receba um payload de tarefa do Asana.
2. Identifique departamento, etapa, status e evidências.
3. Classifique a tarefa como:
   - aprovada;
   - correção solicitada;
   - precisa de gestão;
   - precisa de cliente;
   - criar próxima tarefa.
4. Gere uma resposta estruturada.
5. Em modo `dry_run`, apenas exiba o resultado.
6. Em modo real, publique comentário no Asana e, quando aplicável, crie nova tarefa.
