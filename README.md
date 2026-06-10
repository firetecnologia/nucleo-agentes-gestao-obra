# Núcleo 377 - Agentes de Gestão Premium de Obra

MVP em Python para analisar tarefas de obra vindas do Asana, validar evidências, classificar risco, aplicar uma matriz de decisão e preparar ações operacionais em modo seguro.

Nesta fase o sistema **não executa chamadas reais ao Asana**. O dry-run é o comportamento padrão e a saída mostra apenas as operações planejadas.

## O que o MVP faz

- Recebe um payload JSON de tarefa.
- Identifica obra, departamento, etapa, status, evidências, riscos e próximo departamento.
- Valida evidências obrigatórias em anexos, comentários e descrição.
- Classifica risco como `low`, `medium`, `high` ou `critical`.
- Decide entre `approved`, `request_correction`, `escalate_management`, `ask_client`, `create_next_tasks` ou `blocked`.
- Gera comentário interno para Asana em português do Brasil.
- Sugere próximas tarefas sem criar nada em sistemas externos.
- Exige revisão humana para impacto financeiro alto, gestão, bloqueios e comunicação com cliente.

## Requisitos

- Python 3.11 ou superior.
- Nenhuma dependência externa obrigatória.

O arquivo `requirements.txt` existe para documentar que o MVP usa apenas a biblioteca padrão do Python.

## Configuração

Crie um arquivo `.env` local a partir do exemplo, se for preparar a próxima fase:

```bash
cp .env.example .env
```

Não coloque tokens reais no repositório. Nesta fase, mesmo com variáveis configuradas, o cliente Asana permanece bloqueado para chamadas reais.

Variáveis lidas pelo módulo `src.config`:

- `DRY_RUN`: mantém o comportamento seguro quando `true`.
- `ASANA_ACCESS_TOKEN`: token futuro do Asana, nunca versionado.
- `ASANA_WORKSPACE_GID`: workspace futuro.
- `ASANA_PROJECT_GID`: projeto futuro.
- `ASANA_ENABLE_REAL_ACTIONS`: deve permanecer `false` até a integração real ser aprovada.

## Rodar análise em dry-run

```bash
python -m src.workflows.analyze_task --input sample_task_payload.json --dry-run
```

A saída será um JSON com a decisão do agente e as operações planejadas:

```json
{
  "decision": "request_correction",
  "risk_level": "medium",
  "asana_comment": "...",
  "next_tasks": [],
  "requires_human_review": true,
  "dry_run": true,
  "planned_asana_operations": []
}
```

## Processar evento simulado em dry-run

```bash
python -m src.workflows.process_event --input samples/asana_event_task_ready.json --dry-run
```

O workflow de eventos recebe um JSON simulado, roteia pelo tipo de evento, roda o agente quando há payload da tarefa e devolve:

```json
{
  "event_type": "task_ready_for_agent_review",
  "processed": true,
  "dry_run": true,
  "decision": "request_correction",
  "planned_operations": [],
  "log_entry": {}
}
```

## Rodar testes

```bash
python -m unittest discover
```

Os testes cobrem a matriz de decisão, evidências ausentes, impacto financeiro alto, aprovação com baixo risco, aprovação do cliente com revisão humana e criação sugerida de próxima tarefa.

## Estrutura

- `src/domain/`: modelos, validação de evidências, classificação de risco e motor de decisão.
- `src/agents/`: agente orquestrador.
- `src/integrations/`: stub seguro para integração com Asana.
- `src/events/`: modelos, roteador, processador e log estruturado de eventos.
- `src/workflows/`: CLI de análise de tarefa.
- `tests/`: testes unitários.
- `samples/`: eventos simulados do Asana para dry-run.
- `sample_task_payload.json`: payload de exemplo.
- `AGENTS.md` e arquivos numerados: planejamento e regras do produto.

## Regras de segurança do MVP

- Dry-run permanece como padrão.
- Nenhum token real deve ser versionado.
- Nenhuma mensagem é enviada automaticamente ao cliente.
- Nenhum comentário ou tarefa é criado no Asana nesta fase.
- Impacto financeiro alto nunca é aprovado sem revisão humana.
- Arquivos de planejamento não devem ser apagados.

## Próxima fase: Asana

A integração real deve ser implementada apenas depois de validar:

- autenticação por variável de ambiente;
- IDs de workspace, projeto, seções e campos fora do código;
- logs das decisões automáticas;
- revisão humana antes de comunicação externa;
- flag explícita para liberar chamadas reais;
- testes com mocks para comentários e criação de tarefas.

## Fase 2 - Integração Asana segura

A Fase 2 prepara a integração sem executar chamadas reais. O módulo `src.integrations.asana_client` já expõe stubs para:

- buscar tarefa por ID;
- postar comentário;
- criar tarefa;
- atualizar campos.

Todas essas operações retornam uma operação planejada quando `dry_run=True`. Para qualquer chamada real ser considerada, o código exige simultaneamente:

- `dry_run=False`;
- `ASANA_ENABLE_REAL_ACTIONS=true`;
- `ASANA_ACCESS_TOKEN` configurado;
- confirmação explícita no código por `confirm_real_action=True`.

Mesmo com todos os portões abertos, a Fase 2 ainda interrompe a execução em um stub seguro com `NotImplementedError`, sem enviar nada ao Asana.

## CI

O GitHub Actions roda a suíte padrão em pushes e pull requests:

```bash
python -m unittest discover
```

## Fase 3 - Automação segura de eventos Asana

A Fase 3 prepara o motor interno para receber eventos do Asana, ainda sem webhook real. Eventos suportados:

- `task_ready_for_agent_review`: tarefa pronta para análise do agente.
- `task_overdue`: tarefa vencida e não concluída.
- `new_attachment_added`: novo anexo recebido para revalidação de evidências.
- `client_decision_required`: decisão de cliente exigida, com tarefa interna para Atendimento.
- `financial_impact_detected`: impacto financeiro médio, alto ou crítico, sempre com revisão humana.

Regras da Fase 3:

- `dry_run=True` é forçado pelo processador de eventos.
- Nenhuma chamada real ao Asana é executada.
- Nenhuma mensagem é enviada ao cliente.
- Nenhuma tarefa real é criada.
- Toda ação externa vira `planned_operation`.
- Todo evento processado gera `log_entry` estruturado.
- Evento desconhecido retorna erro controlado.
