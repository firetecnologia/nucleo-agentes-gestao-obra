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
- Mapeia decisoes internas para operacoes planejadas do Asana em sandbox dry-run.
- Renderiza interface web local para dashboard, historico, relatorio semanal e rascunho de cliente.
- Executa simulacao ponta a ponta da obra piloto, com relatorio, dashboard e historico local.
- Mantem fila de revisao humana e trilha de auditoria local para decisoes sensiveis.
- Gera comentario interno para Asana em portugues do Brasil.
- Sugere proximas tarefas apenas como dry-run.
- Exige revisao humana para impacto financeiro sensivel, gestao, bloqueios e comunicacao com cliente.

## Requisitos

- Python 3.11 ou superior.
- Nenhuma dependencia externa obrigatoria.

O arquivo `requirements.txt` documenta que o MVP usa apenas a biblioteca padrao do Python.

## Comandos principais

```bash
python -m unittest discover
python -m src.workflows.analyze_task --input sample_task_payload.json --dry-run
python -m src.workflows.process_event --input samples/asana_event_task_ready.json --dry-run
python -m src.workflows.generate_report --input samples/report_input_weekly.json --type weekly_management --dry-run
python -m src.workflows.generate_dashboard --input samples/dashboard_input_obra.json --dry-run
python -m src.workflows.export_html --type dashboard --input samples/dashboard_input_obra.json --dry-run
python -m src.workflows.export_html --type weekly_report --input samples/report_input_weekly.json --dry-run
python -m src.workflows.run_simulation --input samples/obra_piloto_scenario.json --dry-run
python -m src.workflows.list_reviews --dry-run
python -m src.workflows.review_decision --review-id REV-001 --status approved --reviewer Gestao --dry-run
python -m src.web.app
```

O roteiro completo para demonstracao esta em `DEMO.md`.

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

## Simular obra piloto em dry-run

```bash
python -m src.workflows.run_simulation --input samples/obra_piloto_scenario.json --dry-run
```

A simulacao encadeia analise de tarefa, processamento de evento, operacoes planejadas, relatorio semanal, dashboard, interface web local e historico em `local_data/`. A saida consolida:

- `analyses`;
- `events_processed`;
- `planned_operations`;
- `weekly_report`;
- `dashboard`;
- `saved_records`;
- `storage_query`;
- `web_preview`;
- `dry_run=true`;
- `external_operations=[]`.

## Revisao humana e auditoria local

```bash
python -m src.workflows.list_reviews --dry-run
python -m src.workflows.review_decision --review-id REV-001 --status approved --reviewer Gestao --dry-run
```

A fila de revisao e local e serve para governanca antes de qualquer decisao sensivel. Decisoes com cliente, bloqueio, escalonamento para gestao, impacto financeiro medio/alto/critico ou risco alto/critico exigem revisao humana. Aprovar na fila altera apenas o JSON local, registra auditoria e nunca executa acao externa.

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

## Mapeamentos Asana em sandbox dry-run

A camada de mapeamento transforma decisoes internas em operacoes planejadas, sem executar chamada externa:

- comentario interno planejado;
- tarefa interna planejada;
- atualizacao planejada de campo;
- vinculo planejado entre obra, departamento e tarefa;
- registro planejado de revisao humana.

Todas as operacoes retornam `dry_run=true`, `external_call=false` e `real_action=false`.

## Interface web local em dry-run

A interface web local usa apenas biblioteca padrao e dados de samples. Ela renderiza:

- `/`: pagina inicial da obra;
- `/dashboard`: dashboard executivo;
- `/historico-decisoes`: historico de decisoes;
- `/relatorio-semanal`: relatorio semanal;
- `/rascunho-cliente`: rascunho para cliente com aviso de revisao humana.

Para subir localmente:

```bash
python -m src.web.app
```

O servidor usa `127.0.0.1:8000` por padrao e nao conecta nenhum sistema externo.

## Exportar HTML premium em dry-run

```bash
python -m src.workflows.export_html --type dashboard --input samples/dashboard_input_obra.json --dry-run
python -m src.workflows.export_html --type weekly_report --input samples/report_input_weekly.json --dry-run
python -m src.workflows.export_html --type client_draft --input samples/report_input_weekly.json --dry-run
python -m src.workflows.export_html --type simulation_summary --input samples/obra_piloto_scenario.json --dry-run
```

A exportacao gera arquivos `.html` locais em `exports/` e retorna o caminho gerado. Ela nao gera PDF, nao envia arquivo, nao conecta Asana real e nao aciona nenhum canal externo.

## Rodar testes

```bash
python -m unittest discover
```

Os testes cobrem a matriz de decisao, evidencias ausentes, configuracao segura, stubs do Asana, automacao de eventos, agentes especialistas, relatorios, dashboard, metricas, historico de decisoes, storage local, rotas internas da API, mapeamentos Asana sandbox, interface web local, simulacao ponta a ponta, fila de revisao humana e auditoria.

A Fase 14 adiciona smoke tests e testes de regressao em:

- `tests/test_smoke_workflows.py`;
- `tests/test_regression_contracts.py`;
- `tests/test_security_dry_run.py`.

Use `QUALITY.md` como checklist antes de apresentar o MVP.

## Estrutura

- `src/domain/`: modelos, validacao de evidencias, classificacao de risco e motor de decisao.
- `src/agents/`: agente orquestrador e agentes especialistas por departamento.
- `src/integrations/`: stub seguro para integracao com Asana e mapeamentos sandbox.
- `src/events/`: modelos, roteador, processador e log estruturado de eventos.
- `src/reports/`: modelos e builders de relatorios em dry-run.
- `src/dashboard/`: modelos, metricas, historico de decisoes e builder de dashboard por obra.
- `src/storage/`: armazenamento local em JSON para historico dry-run.
- `src/api/`: camada API-like local em dry-run.
- `src/web/`: interface web local para demonstracao interna.
- `src/simulation/`: simulacao ponta a ponta da obra piloto.
- `src/review/`: fila de revisao humana, regras de aprovacao local e auditoria.
- `src/templates/`: template operacional e seed sintetico da obra piloto Nucleo.
- `src/export/`: exportadores HTML locais para relatorios, dashboard, rascunho de cliente e simulacao.
- `src/workflows/`: CLIs de analise de tarefa, processamento de evento, geracao de relatorio, dashboard, exportacao HTML, storage, simulacao e revisao.
- `tests/`: testes unitarios.
- `samples/`: eventos simulados do Asana para dry-run.
- `samples/nucleo_obra_piloto_template.json`: template sintetico de obra real da Nucleo.
- `samples/nucleo_obra_piloto_seed.json`: seed inicial para analise, simulacao, relatorio, dashboard e fila de revisao.
- `sample_task_payload.json`: payload de exemplo.
- `DEMO.md`: roteiro de demonstracao do MVP.
- `AGENTS.md` e arquivos numerados: planejamento e regras do produto.

## Regras de seguranca do MVP

- Dry-run permanece como padrao.
- Nenhum token real deve ser versionado.
- Nenhuma mensagem e enviada automaticamente ao cliente.
- Nenhum comentario ou tarefa e criado no Asana nesta fase.
- Nenhum relatorio e enviado por email, WhatsApp, Asana real ou qualquer canal externo.
- Nenhum dashboard executa operacao externa; ele apenas imprime JSON local.
- Nenhuma exportacao HTML envia arquivo ou gera PDF; tudo fica local em `exports/`.
- O historico local usa `local_data/`, sem banco externo e sem credenciais.
- A API interna nao exige token e nao executa operacao externa.
- Os mapeamentos Asana geram apenas operacoes planejadas em memoria.
- A interface web local usa samples/storage e nao envia dados para fora.
- A simulacao e local, salva historico em `local_data/` e nao chama servicos externos.
- A revisao humana altera apenas status local e registra auditoria em dry-run.
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

## Fase 9 - Mapeamentos Asana em sandbox dry-run

A Fase 9 prepara a traducao entre decisoes internas dos agentes e a estrutura futura do Asana, mantendo tudo em memoria e sandbox.

Arquivos principais:

- `src/integrations/asana_payloads.py`: modelos de referencia e operacao planejada.
- `src/integrations/asana_operations.py`: builders de operacoes planejadas.
- `src/integrations/asana_mapping.py`: mapeamento de decisoes para operacoes.

Mapeamentos principais:

- `request_correction`: comentario interno planejado e atualizacao planejada de campos.
- `ask_client`: tarefa interna para Atendimento/Gestao revisar comunicacao; nenhuma mensagem ao cliente.
- `escalate_management`: tarefa interna para Gestao e revisao humana.
- `create_next_tasks`: tarefa planejada para o proximo departamento.
- `blocked`: comentario interno e revisao humana.

Regras de seguranca da Fase 9:

- tudo permanece em `dry_run`;
- nenhuma chamada externa e executada;
- nenhum token real e usado;
- nenhuma producao e ativada;
- nenhuma mensagem e enviada ao cliente;
- toda operacao planejada retorna `external_call=false` e `real_action=false`.

## Fase 10 - Interface web local para dashboard e relatorios

A Fase 10 cria uma interface web local para demonstracao interna da diretoria/equipe, usando os dados de samples e os modulos internos ja existentes.

Arquivos principais:

- `src/web/app.py`: aplicacao web local e servidor HTTP simples.
- `src/web/templates/`: templates HTML das telas.
- `src/web/static/`: CSS e ativo visual local.

Telas disponiveis:

- pagina inicial da obra;
- dashboard executivo;
- historico de decisoes;
- relatorio semanal;
- rascunho para cliente com aviso de revisao humana.

Regras de seguranca da Fase 10:

- sem login nesta fase;
- tudo local e em `dry_run`;
- nenhuma chamada real ao Asana e executada;
- nenhum email, WhatsApp ou canal externo e acionado;
- nenhum dado e enviado ao cliente;
- a interface consome apenas samples e modulos internos.

## Fase 11 - Simulacao ponta a ponta da obra piloto

A Fase 11 cria um cenario completo da obra piloto para demonstrar o MVP funcionando como um fluxo integrado.

Arquivos principais:

- `src/simulation/obra_piloto.py`: caminhos padrao da obra piloto.
- `src/simulation/scenario_builder.py`: carregamento e montagem de entradas para relatorio, dashboard e historico.
- `src/simulation/scenario_runner.py`: executor da simulacao completa.
- `src/workflows/run_simulation.py`: CLI da simulacao.
- `samples/obra_piloto_scenario.json`: cenario da obra piloto.

O ciclo demonstrado inclui:

- tarefa de Engenharia pronta para analise;
- falta de evidencia de campo;
- correcao solicitada;
- impacto financeiro detectado;
- decisao escalada para gestao;
- relatorio semanal gerado;
- dashboard atualizado;
- historico local salvo e consultavel.

Regras de seguranca da Fase 11:

- tudo permanece em `dry_run`;
- nenhuma chamada real ao Asana e executada;
- nenhuma tarefa real e criada;
- nenhuma mensagem e enviada ao cliente;
- `external_operations` permanece vazio.

## Fase 12 - Revisao humana, aprovacoes locais e auditoria

A Fase 12 cria uma fila local para diretoria/gestao revisar decisoes sensiveis antes de qualquer avanco operacional.

Arquivos principais:

- `src/review/review_models.py`: modelo de item de revisao.
- `src/review/approval_rules.py`: regras que determinam quando uma decisao exige revisao humana.
- `src/review/review_queue.py`: fila local de revisoes.
- `src/review/audit_trail.py`: trilha de auditoria.
- `src/workflows/list_reviews.py`: CLI para listar revisoes.
- `src/workflows/review_decision.py`: CLI para atualizar status local.

Status suportados:

- `pending`;
- `approved`;
- `rejected`;
- `changes_requested`.

Regras de seguranca da Fase 12:

- aprovar na fila nao executa acao externa;
- aprovacao altera apenas status local em dry-run;
- decisoes de cliente sempre exigem revisao humana;
- impacto financeiro medio, alto ou critico exige revisao humana;
- risco alto ou critico exige revisao humana;
- toda mudanca de status registra auditoria;
- nenhuma mensagem e enviada ao cliente.

## Fase 13 - Documentacao de demonstracao do MVP

A Fase 13 consolida a documentacao de demo para equipe e diretoria.

Arquivos principais:

- `DEMO.md`: roteiro recomendado de demonstracao local.
- `README.md`: comandos principais e resumo das fases.
- `requirements.txt`: declaracao de dependencias necessarias.

Regras de seguranca da Fase 13:

- documentacao reforca `dry_run` como padrao;
- nao inclui token real;
- nao instrui envio ao cliente;
- nao adiciona dependencias externas desnecessarias.

## Fase 14 - Qualidade, smoke tests e regressao

A Fase 14 endurece o MVP antes das proximas integracoes.

Arquivos principais:

- `QUALITY.md`: checklist de validacao antes de apresentar o MVP.
- `tests/test_smoke_workflows.py`: smoke tests dos fluxos principais.
- `tests/test_regression_contracts.py`: contratos JSON das saidas principais.
- `tests/test_security_dry_run.py`: garantias de dry-run, sem operacoes externas e sem envio ao cliente.

Regras de seguranca da Fase 14:

- todos os fluxos sensiveis mantem `dry_run=true`;
- `external_operations` permanece vazio nos contratos principais;
- comunicacao com cliente continua apenas como rascunho;
- nenhum teste depende de credenciais reais.

## Fase 15 - Template de obra piloto Nucleo

A Fase 15 cria um template operacional sintetico para demonstrar uma obra gerida pela Nucleo sem expor dados reais de cliente.

Arquivos principais:

- `src/templates/nucleo_work_template.py`: etapas, departamentos, tarefas padrao, evidencias, riscos e pontos de aprovacao.
- `src/templates/project_seed.py`: seed que alimenta analise, simulacao, relatorio, dashboard e fila de revisao.
- `samples/nucleo_obra_piloto_template.json`: snapshot do template piloto.
- `samples/nucleo_obra_piloto_seed.json`: JSON inicial seguro para demonstracao.
- `tests/test_nucleo_work_template.py`: validacao do template e do seed.

Etapas cobertas:

- Diagnostico inicial;
- Planejamento;
- Projetos e compatibilizacao;
- Compras;
- Execucao acompanhada;
- Medicoes;
- Qualidade;
- Entrega;
- Pos-obra.

Regras de seguranca da Fase 15:

- tudo permanece em `dry_run`;
- o template usa apenas dados sinteticos;
- nenhum servico externo e conectado;
- nenhuma mensagem ao cliente e enviada;
- impactos financeiros altos continuam exigindo revisao humana.

## Fase 16 - Exportacao premium em HTML

A Fase 16 adiciona exportadores HTML locais para apresentacao interna e futura evolucao para PDF, mantendo o MVP em modo seguro.

Arquivos principais:

- `src/export/html_exporter.py`: base visual, escrita local e resumo de simulacao.
- `src/export/report_exporter.py`: relatorio semanal executivo em HTML.
- `src/export/dashboard_exporter.py`: dashboard e historico de decisoes em HTML.
- `src/export/client_draft_exporter.py`: rascunho de cliente com aviso de revisao humana.
- `src/workflows/export_html.py`: CLI de exportacao HTML.
- `exports/.gitkeep`: pasta local de saida versionada sem artefatos gerados.
- `tests/test_html_exporter.py`: testes dos exportadores e da CLI.

Tipos suportados:

- `dashboard`;
- `weekly_report`;
- `client_draft`;
- `simulation_summary`.

Regras de seguranca da Fase 16:

- tudo permanece em `dry_run`;
- os arquivos sao gravados apenas localmente em `exports/`;
- nenhum email, WhatsApp, Asana real ou canal externo e acionado;
- nenhum PDF e gerado nesta fase;
- rascunhos de cliente sempre deixam clara a revisao humana obrigatoria.

## CI

O GitHub Actions roda a suite padrao em pushes e pull requests:

```bash
python -m unittest discover
```
