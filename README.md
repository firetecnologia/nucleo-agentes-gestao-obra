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

## Rodar testes

```bash
python -m unittest discover
```

Os testes cobrem a matriz de decisão, evidências ausentes, impacto financeiro alto, aprovação com baixo risco, aprovação do cliente com revisão humana e criação sugerida de próxima tarefa.

## Estrutura

- `src/domain/`: modelos, validação de evidências, classificação de risco e motor de decisão.
- `src/agents/`: agente orquestrador.
- `src/integrations/`: stub seguro para integração com Asana.
- `src/workflows/`: CLI de análise de tarefa.
- `tests/`: testes unitários.
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
