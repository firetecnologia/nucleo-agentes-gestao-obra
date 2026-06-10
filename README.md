# Nucleo 377 - Agentes de Gestao Premium de Obra

MVP em Python para analisar tarefas de obra vindas do Asana, validar evidencias, classificar risco, aplicar uma matriz de decisao e preparar acoes operacionais em modo seguro.

O sistema nao executa chamadas reais ao Asana nesta fase. O `dry_run` e o comportamento padrao e a saida mostra apenas decisoes e operacoes planejadas.

## O que o MVP faz

- Recebe um payload JSON de tarefa.
- Identifica obra, departamento, etapa, status, evidencias, riscos e proximo departamento.
- Valida evidencias obrigatorias em anexos, comentarios e descricao.
- Classifica risco como `low`, `medium`, `high` ou `critical`.
- Decide entre `approved`, `request_correction`, `escalate_management`, `ask_client`, `create_next_tasks`, `blocked` ou `monitor`.
- Roteia a analise para um agente especialista quando o departamento e reconhecido.
- Gera relatorios diarios internos, semanais de gestao e rascunhos seguros para cliente.
- Gera dashboard JSON por obra com metricas, historico de decisoes, riscos e saude da obra.
- Guarda e consulta historico local em JSON para desenvolvimento, sem banco externo.
- Expoe rotas internas API-like em dry-run para analise, eventos, relatorios e dashboard.
- Gera comentario interno para Asana em portugues do Brasil.
- Sugere proximas tarefas apenas como dry-run.
- Exige revisao humana para impacto financeiro sensivel, gestao, bloqueios e comunicacao com cliente.

## Requisitos

- Python 3.11 ou superior.
- Nenhuma dependencia externa obrigatoria.

O arquivo `requirements.txt` documenta que o MVP usa apenas a biblioteca padrao do Python.

## Configuracao

Crie um arquivo `.env` local a partir do exemplo, se for preparar a proxima fase:

```bash
cp .env.example .env
```

Nao coloque tokens reais no repositorio. Mesmo com variaveis configuradas, o cliente Asana permanece bloqueado para chamadas reais.

Variaveis lidas por `src.config`:

- `DRY_RUN`: mantem o comportamento seguro quando `true`.
- `ASANA_ACCESS_TOKEN`: token futuro do Asana, nunca versionado.
- `ASANA_WORKSPACE_GID`: workspace futuro.
- `ASANA_PROJECT_GID`: projeto futuro.
- `ASANA_ENABLE_REAL_ACTIONS`: deve permanecer `false` ate a integracao real ser aprovada.

## Rodar analise em dry-run

```bash
python -m src.workflows.analyze_task --input sample_task_payload.json --dry-run
```

A saida sera um JSON com a decisao do agente e as operacoes planejadas:

```json
{
  "decision": "request_correction",
  "risk_level": "medium",
  "asana_comment": "...",
  "specialist_agent": "EngineeringAgent",
  "specialist_analysis": {},
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

O workflow de eventos recebe um JSON simulado, roteia pelo tipo de evento, roda o agente quando ha payload da tarefa e devolve:

```json
{
  "event_type": "task_ready_for_agent_review",
  "processed": true,
  "dry_run": true,
  "decision": "request_correction",
  "specialist_agent": "EngineeringAgent",
  "specialist_analysis": {},
  "planned_operations": [],
  "log_entry": {}
}
```

## Gerar relatorios em dry-run

```bash
python -m src.workflows.generate_report --input samples/report_input_daily.json --type internal_daily --dry-run
python -m src.workflows.generate_report --input samples/report_input_weekly.json --type weekly_management --dry-run
python -m src.workflows.generate_report --input samples/report_input_weekly.json --type client_draft --dry-run
```

A CLI de relatorios apenas imprime JSON local. Ela nao envia email, WhatsApp, comentario no Asana, mensagem ao cliente ou qualquer outra operacao externa.

## Gerar dashboard da obra em dry-run

```bash
python -m src.workflows.generate_dashboard --input samples/dashboard_input_obra.json --dry-run
```

A CLI de dashboard consolida analises, eventos e relatorios simulados em uma visao JSON por obra. Ela calcula metricas, gargalos por departamento, historico de decisoes, riscos ativos, decisoes pendentes, acoes recomendadas de gestao e saude da obra.

O dashboard nao conecta Asana real, email, WhatsApp ou qualquer canal externo. A saida sempre mantem:

```json
{
  "dry_run": true,
  "external_operations": []
}
```

## Guardar e consultar historico local em dry-run

```bash
python -m src.workflows.store_record --input samples/storage_record_analysis.json --dry-run
python -m src.workflows.query_records --obra "Obra Piloto Nucleo" --record-type analysis --dry-run
```

A camada de storage usa apenas arquivos JSON locais em `local_data/`. Essa pasta e ignorada pelo Git e serve para desenvolvimento, testes e demonstracoes internas. Nenhum banco externo, Asana real ou canal de envio e acionado.

## API interna em dry-run

Nesta fase, a API e uma camada local testavel em memoria, sem dependencia externa. Os endpoints internos disponiveis sao:

- `GET /health`
- `POST /analyze-task`
- `POST /process-event`
- `POST /generate-report`
- `POST /generate-dashboard`

Exemplo de uso em Python:

```python
from src.api import create_app

app = create_app()
response = app.get("/health")
print(response.to_dict())
```

FastAPI e `uvicorn src.api.app:app --reload` ficam documentados como evolucao futura quando dependencias externas forem aprovadas. A fase atual mantem apenas biblioteca padrao para preservar testes locais e seguranca.

## Rodar testes

```bash
python -m unittest discover
```

Os testes cobrem a matriz de decisao, evidencias ausentes, configuracao segura, stubs do Asana, automacao de eventos, agentes especialistas, relatorios, dashboard, metricas, historico de decisoes, storage local e rotas internas da API.

## Estrutura

- `src/domain/`: modelos, validacao de evidencias, classificacao de risco e motor de decisao.
- `src/agents/`: agente orquestrador e agentes especialistas por departamento.
- `src/integrations/`: stub seguro para integracao com Asana.
- `src/events/`: modelos, roteador, processador e log estruturado de eventos.
- `src/reports/`: modelos e builders de relatorios em dry-run.
- `src/dashboard/`: modelos, metricas, historico de decisoes e builder de dashboard por obra.
- `src/storage/`: armazenamento local em JSON para historico dry-run.
- `src/api/`: camada API-like local em dry-run.
- `src/workflows/`: CLIs de analise de tarefa, processamento de evento, geracao de relatorio, dashboard e storage.
- `tests/`: testes unitarios.
- `samples/`: eventos simulados do Asana para dry-run.
- `sample_task_payload.json`: payload de exemplo.
- `AGENTS.md` e arquivos numerados: planejamento e regras do produto.

## Regras de seguranca do MVP

- Dry-run permanece como padrao.
- Nenhum token real deve ser versionado.
- Nenhuma mensagem e enviada automaticamente ao cliente.
- Nenhum comentario ou tarefa e criado no Asana nesta fase.
- Nenhum relatorio e enviado por email, WhatsApp, Asana real ou qualquer canal externo.
- Nenhum dashboard executa operacao externa; ele apenas imprime JSON local.
- O historico local usa `local_data/`, sem banco externo e sem credenciais.
- A API interna nao exige token e nao executa operacao externa.
- Impacto financeiro alto nunca e aprovado sem revisao humana.
- Impacto financeiro medio, alto ou critico em Financeiro escala para gestao.
- Arquivos de planejamento nao devem ser apagados.

## Fase 2 - Integracao Asana segura

A Fase 2 prepara a integracao sem executar chamadas reais. O modulo `src.integrations.asana_client` expoe stubs para:

- buscar tarefa por ID;
- postar comentario;
- criar tarefa;
- atualizar campos.

Todas essas operacoes retornam uma operacao planejada quando `dry_run=True`. Para qualquer chamada real ser considerada, o codigo exige simultaneamente:

- `dry_run=False`;
- `ASANA_ENABLE_REAL_ACTIONS=true`;
- `ASANA_ACCESS_TOKEN` configurado;
- confirmacao explicita no codigo por `confirm_real_action=True`.

Mesmo com todos os portoes abertos, a integracao ainda interrompe a execucao em um stub seguro com `NotImplementedError`, sem enviar nada ao Asana.

## Fase 3 - Automacao segura de eventos Asana

A Fase 3 prepara o motor interno para receber eventos do Asana, ainda sem webhook real. Eventos suportados:

- `task_ready_for_agent_review`: tarefa pronta para analise do agente.
- `task_overdue`: tarefa vencida e nao concluida.
- `new_attachment_added`: novo anexo recebido para revalidacao de evidencias.
- `client_decision_required`: decisao de cliente exigida, com tarefa interna para Atendimento.
- `financial_impact_detected`: impacto financeiro medio, alto ou critico, sempre com revisao humana.

Regras da Fase 3:

- `dry_run=True` e forcado pelo processador de eventos.
- Nenhuma chamada real ao Asana e executada.
- Nenhuma mensagem e enviada ao cliente.
- Nenhuma tarefa real e criada.
- Toda acao externa vira `planned_operation`.
- Todo evento processado gera `log_entry` estruturado.
- Evento desconhecido retorna erro controlado.

## Fase 4 - Agentes especialistas por departamento

A Fase 4 adiciona agentes especialistas em `src/agents/` para refinar a matriz geral sem sair do modo seguro:

- `PlanningAgent`: avalia prazo, caminho critico, dependencias e impacto no cronograma.
- `ProjectsAgent`: avalia pendencias de projeto, compatibilizacao, versao, detalhe executivo, RFI e conflitos.
- `EngineeringAgent`: avalia evidencias de campo, fotos, diario de obra, vistoria, divergencias e retrabalho.
- `PurchasingAgent`: avalia especificacao, quantidade, cotacao, prazo de entrega, fornecedor e aprovacao de compra.
- `FinanceAgent`: avalia nota fiscal, boleto, medicao, previsto x realizado e desvio financeiro.
- `ClientServiceAgent`: prepara apenas rascunho interno para revisao humana quando houver assunto de cliente.
- `QualityAgent`: avalia checklist, evidencias minimas, liberacao de etapa e pendencias de qualidade.

Contrato comum de saida dos especialistas:

```json
{
  "agent_name": "EngineeringAgent",
  "department": "Engenharia",
  "decision": "request_correction",
  "risk_level": "medium",
  "analysis": "...",
  "validated_evidence": [],
  "missing_evidence": ["Foto"],
  "recommended_actions": [],
  "next_tasks": [],
  "requires_human_review": true
}
```

O `OrchestratorAgent` identifica o departamento, chama o especialista correspondente e combina a decisao especialista com a matriz geral. A decisao final sempre prioriza o caminho mais conservador.

Se qualquer especialista retornar `blocked`, `escalate_management` ou `ask_client`, o orquestrador nao aprova automaticamente.

Eventos processados por `src.workflows.process_event` tambem podem incluir:

```json
{
  "specialist_agent": "EngineeringAgent",
  "specialist_analysis": {}
}
```

Regras de seguranca mantidas na Fase 4:

- tudo permanece em `dry_run`;
- nenhuma conexao real com Asana e ativada;
- nenhum token real e necessario ou usado;
- nenhuma mensagem e enviada automaticamente ao cliente;
- nenhuma tarefa real e criada;
- bloqueios, comunicacao com cliente e correcoes impedem aprovacao automatica.

## Fase 5 - Relatorios operacionais, executivos e rascunhos para cliente

A Fase 5 transforma os resultados de analises e eventos em relatorios uteis para gestao, equipe interna e cliente, mantendo tudo em dry-run.

Arquivos principais:

- `src/reports/report_models.py`: modelos serializaveis de entrada, itens, periodo, rascunho de cliente e saida.
- `src/reports/report_builder.py`: builder central, classificacao de saude da obra e consolidadores.
- `src/reports/internal_daily_report.py`: relatorio diario interno para orientar a equipe.
- `src/reports/weekly_management_report.py`: relatorio semanal executivo para lideranca.
- `src/reports/client_report_draft.py`: rascunho seguro para cliente, sempre com revisao humana.
- `src/workflows/generate_report.py`: CLI para gerar relatorios em JSON.

Tipos suportados:

- `internal_daily`: tarefas analisadas, aprovadas, correcoes, bloqueios, riscos ativos, pendencias por departamento, proximas acoes e decisoes de gestao.
- `weekly_management`: resumo executivo, saude da obra, avancos, riscos, impactos de prazo, impactos financeiros, gargalos, decisoes pendentes e recomendacoes.
- `client_draft`: comunicacao profissional em rascunho, sem envio automatico, sem expor conflito interno ou linguagem alarmista.

Indicador de saude da obra:

- `on_track`: maioria aprovada e sem riscos relevantes.
- `attention`: correcoes, riscos medios, aprovacoes pendentes ou gargalo de departamento.
- `at_risk`: multiplos riscos altos, impacto financeiro alto ou prazo critico.
- `critical`: risco critico ou tarefa bloqueada relevante.

Regras de seguranca da Fase 5:

- tudo permanece em `dry_run`;
- a CLI nao conecta canal externo;
- o rascunho para cliente sempre retorna `requires_human_review=true`;
- `external_operations` permanece vazio;
- nenhum relatorio e enviado automaticamente;
- nenhum token real e usado.

## Fase 6 - Dashboard, historico e indicadores por obra

A Fase 6 cria a camada de estado da obra para consolidar analises, eventos simulados e relatorios em uma saida JSON preparada para uma futura interface web.

Arquivos principais:

- `src/dashboard/dashboard_models.py`: modelos serializaveis de entrada, metricas, historico e saida do dashboard.
- `src/dashboard/decision_history.py`: historico de decisoes com ordenacao por data, filtros por departamento, risco e decisao, e consolidacao de pendencias.
- `src/dashboard/metrics.py`: indicadores de tarefas analisadas, aprovadas, correcoes, bloqueios, revisao humana, riscos, decisoes de cliente, impactos financeiros, gargalos, taxa de aprovacao, taxa de retrabalho/pendencia e indice de saude.
- `src/dashboard/work_health.py`: regra unica para classificar a saude da obra como `on_track`, `attention`, `at_risk` ou `critical`.
- `src/dashboard/dashboard_builder.py`: builder central do dashboard por obra.
- `src/workflows/generate_dashboard.py`: CLI para gerar o dashboard em JSON.

Exemplo de entrada:

```json
{
  "obra": "Obra Piloto Nucleo",
  "cliente": "Cliente Exemplo",
  "periodo": {
    "inicio": "2026-06-01",
    "fim": "2026-06-30"
  },
  "analyses": [],
  "events": [],
  "reports": []
}
```

Regras de saude da obra:

- `critical`: risco critico, bloqueio relevante ou muitos bloqueios.
- `at_risk`: multiplos riscos altos, impacto financeiro relevante ou gargalos recorrentes.
- `attention`: correcoes, revisao humana, decisoes de cliente, riscos medios ou ausencia de dados.
- `on_track`: maioria aprovada e sem gargalos relevantes.

Regras de seguranca da Fase 6:

- tudo permanece em `dry_run`;
- a CLI nao conecta Asana real;
- nenhum email, WhatsApp ou canal externo e acionado;
- `external_operations` permanece vazio;
- nenhum token real e usado;
- historico e metricas sao apenas dados locais serializaveis em JSON.

## Fase 7 - Storage local e consultas por obra

A Fase 7 adiciona uma camada local para guardar saidas JSON do sistema durante desenvolvimento. O objetivo e formar historico consultavel por obra sem usar banco externo.

Arquivos principais:

- `src/storage/storage_models.py`: modelo `StorageRecord` e consulta `StorageQuery`.
- `src/storage/json_store.py`: persistencia local em arquivos JSON.
- `src/storage/repositories.py`: repositorio para salvar e consultar registros por obra e tipo.
- `src/workflows/store_record.py`: CLI para salvar registro local.
- `src/workflows/query_records.py`: CLI para consultar historico local.

Estrutura local criada automaticamente:

```txt
local_data/
  analyses/
  events/
  reports/
  dashboards/
  decision_history/
```

Tipos suportados:

- `analysis`
- `event`
- `report`
- `dashboard`
- `decision_history`

Regras de seguranca da Fase 7:

- `local_data/` fica fora do Git;
- tudo permanece em `dry_run`;
- nenhuma chamada real ao Asana e executada;
- nenhum banco externo e usado;
- nenhum token real e necessario;
- `external_operations` permanece vazio.

## Fase 8 - API interna local em dry-run

A Fase 8 cria uma camada API-like para expor os recursos ja construidos sem adicionar dependencia externa. Isso permite testar os contratos de rota antes de acoplar FastAPI em uma fase posterior.

Arquivos principais:

- `src/api/app.py`: aplicacao local com roteamento em memoria.
- `src/api/routes_analysis.py`: rota `POST /analyze-task`.
- `src/api/routes_events.py`: rota `POST /process-event`.
- `src/api/routes_reports.py`: rota `POST /generate-report`.
- `src/api/routes_dashboard.py`: rota `POST /generate-dashboard`.
- `src/api/schemas.py`: respostas e definicoes serializaveis.

Rotas disponiveis:

```txt
GET  /health
POST /analyze-task
POST /process-event
POST /generate-report
POST /generate-dashboard
```

Regras de seguranca da Fase 8:

- tudo permanece em `dry_run`;
- nenhuma dependencia externa obrigatoria foi adicionada;
- FastAPI/uvicorn ficam para a etapa em que dependencias forem aprovadas;
- nenhuma chamada real ao Asana e executada;
- nenhuma mensagem e enviada ao cliente;
- nenhum token real e necessario;
- `external_operations` permanece vazio.

## CI

O GitHub Actions roda a suite padrao em pushes e pull requests:

```bash
python -m unittest discover
```
