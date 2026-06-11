# Próximos passos Codex — Automação dos Agentes de Gestão de Obra

Este arquivo orienta a próxima sequência de desenvolvimento do projeto `nucleo-agentes-gestao-obra`.

## Objetivo estratégico

Sair do MVP simulado em `dry-run` para uma operação progressivamente automatizada, conectada a dados reais, mas com segurança.

A regra principal é:

> Primeiro ler dados reais. Depois analisar. Depois propor ação. Só depois escrever no Asana com travas explícitas.

## Estado atual do MVP

O projeto já possui:

- agente orquestrador;
- agentes especialistas por departamento;
- matriz de decisão;
- validação de evidências;
- classificação de risco;
- eventos simulados do Asana;
- relatórios;
- dashboard;
- interface web local;
- simulação ponta a ponta;
- fila de revisão humana;
- trilha de auditoria;
- integração Asana ainda bloqueada em stubs seguros;
- CI com `python -m unittest discover`.

## Ordem obrigatória das próximas fases

### Fase 15 — Validação técnica do MVP e CI verde

Issue: https://github.com/firetecnologia/nucleo-agentes-gestao-obra/issues/22

Entregar antes de qualquer integração real:

1. Rodar `python -m unittest discover`.
2. Garantir que a suíte passa localmente.
3. Garantir que o GitHub Actions roda em push e pull request.
4. Corrigir imports, paths, samples ou contratos quebrados.
5. Documentar como interpretar o resultado da suíte.

Critério de aceite:

- CI verde.
- Nenhum teste depende de token real.
- `dry_run=true` permanece padrão.

---

### Fase 16 — Leitura real do Asana em modo seguro

Issue: https://github.com/firetecnologia/nucleo-agentes-gestao-obra/issues/23

Objetivo:

Buscar tarefas reais do Asana e converter em `TaskPayload`, sem escrever nada.

Entregar:

1. Cliente read-only do Asana.
2. CLI:

```bash
python -m src.workflows.fetch_asana_task --task-id <TASK_GID> --dry-run
```

3. Conversor de tarefa real para `TaskPayload`.
4. Leitura de:
   - nome;
   - descrição;
   - responsável;
   - data;
   - seção/projeto;
   - custom fields;
   - anexos;
   - comentários, se disponível.
5. Testes com mocks.

Critério de aceite:

- Uma tarefa real pode ser lida.
- A tarefa real pode ser analisada pelo agente.
- Nenhuma ação real é executada.

---

### Fase 17 — Integração com planilhas de obra e mão de obra

Issue: https://github.com/firetecnologia/nucleo-agentes-gestao-obra/issues/24

Objetivo:

Ler planilhas reais de obra e localizar informações de mão de obra, como grupo, prestador e valor pago.

Entregar:

1. Módulo `src/integrations/spreadsheet_reader.py`.
2. CLI:

```bash
python -m src.workflows.read_labor_costs --input <arquivo.xlsx> --grupo pintura --prestador jeferson --dry-run
```

3. Identificação flexível de abas:
   - `CONTROLE DE M.O.`;
   - `Controle M.O`;
   - `M.O.`;
   - `Mão de Obra`.
4. Normalização de texto sem acento e caixa baixa.
5. Soma de múltiplas linhas compatíveis.
6. Resultado JSON com achados e ação planejada.

Critério de aceite:

- Encontrar prestador por nome parcial.
- Encontrar grupo por nome parcial.
- Somar valores quando houver múltiplas linhas.
- Informar ambiguidade quando houver dúvida.

---

### Fase 18 — Escrita controlada no Asana com aprovação humana

Objetivo:

Permitir que o agente crie comentário ou subtarefa real no Asana apenas quando houver aprovação explícita.

Entregar:

1. Novo modo `approval_required`.
2. Ações reais bloqueadas por padrão.
3. Uma fila local ou arquivo de aprovação com status:
   - pending;
   - approved;
   - rejected;
   - changes_requested.
4. CLI para preparar ação:

```bash
python -m src.workflows.prepare_asana_action --input planned_action.json --dry-run
```

5. CLI para executar ação aprovada:

```bash
python -m src.workflows.execute_approved_asana_action --review-id <ID> --confirm-real-action
```

6. Escrita permitida inicialmente apenas para:
   - comentário interno;
   - subtarefa interna;
   - atualização de campo não sensível.

Travas obrigatórias:

- Nunca enviar mensagem ao cliente automaticamente.
- Nunca aprovar impacto financeiro alto automaticamente.
- Nunca alterar tarefa concluída sem revisão humana.
- Nunca rodar se `ASANA_ENABLE_REAL_ACTIONS` estiver `false`.
- Nunca rodar sem `confirm_real_action=True`.
- Toda ação real deve gerar auditoria.

Critério de aceite:

- Ação planejada fica pendente.
- Ação pendente pode ser aprovada localmente.
- Só ação aprovada executa escrita real.
- Testes provam que ação não aprovada não escreve.

---

### Fase 19 — Automação operacional recorrente

Objetivo:

Criar um robô operacional que rode periodicamente, leia tarefas reais, analise e gere fila de ações.

Entregar:

1. CLI:

```bash
python -m src.workflows.run_daily_agent_check --project-id <ASANA_PROJECT_GID> --dry-run
```

2. Leitura de tarefas por projeto/seção.
3. Filtros mínimos:
   - tarefas vencidas;
   - tarefas com status pronto para agente;
   - tarefas sem evidência obrigatória;
   - tarefas com impacto financeiro/prazo/cliente.
4. Geração de relatório diário interno.
5. Geração de fila de revisão.
6. Nenhuma escrita real por padrão.

Critério de aceite:

- O comando roda sem token em modo sample.
- O comando roda com token em modo read-only.
- O comando gera fila de ações planejadas.

---

### Fase 20 — Automação via GitHub Actions ou servidor local

Objetivo:

Preparar a automação para rodar em rotina, inicialmente com GitHub Actions manual/scheduled ou servidor local.

Entregar:

1. Workflow manual `workflow_dispatch` para rodar smoke test.
2. Workflow manual para rodar simulação.
3. Workflow opcional scheduled em dry-run.
4. Logs exportáveis como artifact.
5. Sem tokens reais obrigatórios no CI público.

Critério de aceite:

- Rodada manual de simulação funciona.
- Artifact de relatório é gerado.
- Sem chamada real ao Asana no CI.

## Prioridade brutalmente honesta

A prioridade não é criar mais telas nem mais documentação. A prioridade agora é:

1. provar que os testes passam;
2. ler uma tarefa real do Asana;
3. analisar essa tarefa;
4. ler uma planilha real;
5. gerar ação planejada;
6. colocar ação em revisão humana;
7. só então escrever no Asana.

## Não fazer agora

- Não integrar WhatsApp.
- Não enviar mensagem ao cliente.
- Não liberar escrita automática irrestrita.
- Não criar banco externo antes de validar o fluxo.
- Não colocar token real no repositório.
- Não transformar dry-run em falso padrão.

## Demonstração esperada ao fim da Fase 17

Rodar:

```bash
python -m unittest discover
python -m src.workflows.fetch_asana_task --task-id <TASK_GID> --dry-run
python -m src.workflows.analyze_task --input output/asana_task_payload.json --dry-run
python -m src.workflows.read_labor_costs --input "PLANILHA OBRA_ JAIRO.xlsx" --grupo pintura --prestador jeferson --dry-run
```

Resultado esperado:

- tarefa real lida;
- payload convertido;
- análise do agente gerada;
- custo de mão de obra localizado;
- subtarefa planejada em dry-run;
- nenhuma ação externa executada.
