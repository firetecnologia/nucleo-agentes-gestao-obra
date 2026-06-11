# Demo do MVP - Nucleo 377

Este roteiro permite demonstrar o MVP localmente, em modo seguro. Todos os comandos usam `dry-run`, nao conectam Asana real, nao usam token real, nao enviam mensagem ao cliente e nao acionam email, WhatsApp ou qualquer canal externo.

## 1. Preparar ambiente local

Requisitos:

- Python 3.11 ou superior.
- Nenhuma dependencia externa obrigatoria.

Opcionalmente crie o `.env` a partir do exemplo, sem tokens reais:

```bash
cp .env.example .env
```

Instalacao:

```bash
python -m pip install -r requirements.txt
```

O `requirements.txt` nao instala bibliotecas externas nesta fase.

## 2. Rodar testes

```bash
python -m unittest discover
```

A demo deve seguir apenas se os testes passarem.

## 3. Analise de tarefa

```bash
python -m src.workflows.analyze_task --input sample_task_payload.json --dry-run
```

Mostre a decisao do agente, risco, evidencias ausentes, proxima acao e operacoes planejadas.

## 4. Processamento de evento

```bash
python -m src.workflows.process_event --input samples/asana_event_task_ready.json --dry-run
```

Explique que o evento e simulado e que nenhuma chamada real ao Asana acontece.

## 5. Relatorio semanal

```bash
python -m src.workflows.generate_report --input samples/report_input_weekly.json --type weekly_management --dry-run
```

Mostre resumo executivo, riscos, decisoes pendentes e acoes recomendadas.

## 6. Dashboard da obra

```bash
python -m src.workflows.generate_dashboard --input samples/dashboard_input_obra.json --dry-run
```

Destaque metricas, saude da obra, gargalos por departamento e historico de decisoes.

## 7. Simulacao ponta a ponta da obra piloto

```bash
python -m src.workflows.run_simulation --input samples/obra_piloto_scenario.json --dry-run
```

Use esta etapa para mostrar o fluxo completo:

- tarefa de Engenharia pronta para analise;
- falta de evidencia de campo;
- correcao solicitada;
- impacto financeiro detectado;
- decisao escalada para gestao;
- relatorio semanal gerado;
- dashboard atualizado;
- historico local salvo e consultavel.

Confirme na saida:

```json
{
  "dry_run": true,
  "external_operations": []
}
```

## 8. Template de obra piloto Nucleo

Use os arquivos abaixo para apresentar a estrutura operacional de uma obra piloto sem dados reais de cliente:

- `samples/nucleo_obra_piloto_template.json`
- `samples/nucleo_obra_piloto_seed.json`

O template mostra etapas, departamentos, tarefas padrao, evidencias obrigatorias, riscos comuns e pontos de aprovacao. O seed pode alimentar analise de tarefa, simulacao, relatorio, dashboard e fila de revisao em dry-run.

## 9. Revisao humana e auditoria

Para listar a fila local:

```bash
python -m src.workflows.list_reviews --dry-run
```

Para atualizar um item ja criado localmente:

```bash
python -m src.workflows.review_decision --review-id REV-001 --status approved --reviewer Gestao --dry-run
```

Explique que aprovar na fila altera apenas o status local e registra auditoria. Isso nao aprova impacto financeiro no Asana e nao executa nenhuma acao externa.

## 10. Interface web local

```bash
python -m src.web.app
```

Acesse no navegador:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/dashboard`
- `http://127.0.0.1:8000/historico-decisoes`
- `http://127.0.0.1:8000/relatorio-semanal`
- `http://127.0.0.1:8000/rascunho-cliente`

O rascunho para cliente e apenas uma previa interna, com revisao humana obrigatoria.

## Sequencia recomendada para diretoria e equipe

1. Abrir com as regras de seguranca: dry-run, sem tokens, sem envio externo.
2. Rodar os testes para provar estabilidade.
3. Demonstrar a analise de uma tarefa individual.
4. Demonstrar um evento simulado do Asana.
5. Gerar o relatorio semanal executivo.
6. Gerar o dashboard JSON.
7. Rodar a simulacao ponta a ponta da obra piloto.
8. Mostrar o template e o seed da obra piloto Nucleo.
9. Mostrar a fila de revisao humana e a trilha de auditoria.
10. Abrir a interface web local para visualizacao executiva.

## Pontos de controle

- Nenhum token real deve ser usado.
- `ASANA_ENABLE_REAL_ACTIONS` deve permanecer `false`.
- Nenhum comentario real no Asana deve ser publicado.
- Nenhuma tarefa real deve ser criada.
- Nenhuma mensagem ao cliente deve ser enviada.
- Impacto financeiro medio, alto ou critico deve passar por revisao humana.
