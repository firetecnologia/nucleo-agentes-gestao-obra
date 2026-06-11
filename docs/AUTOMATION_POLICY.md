# Política de Automação Segura — Núcleo 377

Esta política define o que os agentes podem e não podem fazer quando evoluírem do MVP dry-run para operação real.

## Princípio central

Automação deve reduzir trabalho operacional, mas não pode retirar controle humano de decisões sensíveis.

## Níveis de automação

### Nível 0 — Dry-run total

- Lê dados de samples.
- Analisa tarefas simuladas.
- Gera ações planejadas.
- Não lê Asana real.
- Não escreve no Asana.
- Não envia mensagens.

### Nível 1 — Leitura real segura

- Pode ler tarefas reais do Asana.
- Pode ler planilhas locais.
- Pode converter dados reais em payloads internos.
- Pode analisar e gerar decisão.
- Não pode escrever no Asana.

### Nível 2 — Escrita com aprovação humana

- Pode criar comentário interno no Asana depois de aprovação.
- Pode criar subtarefa interna depois de aprovação.
- Pode atualizar campo operacional depois de aprovação.
- Toda ação real precisa de auditoria.

### Nível 3 — Automação assistida recorrente

- Pode rodar diariamente ou semanalmente.
- Pode gerar fila de ações.
- Pode gerar relatório interno.
- Pode sugerir prioridades.
- Não pode comunicar cliente sem revisão humana.

### Nível 4 — Automação avançada futura

Só poderá ser considerada depois de validação operacional prolongada.

## Ações permitidas no início da operação real

- Ler tarefa do Asana.
- Ler comentário/anexo/campo de tarefa.
- Gerar análise.
- Criar fila de revisão.
- Criar comentário interno aprovado.
- Criar subtarefa interna aprovada.
- Atualizar campo operacional aprovado.

## Ações proibidas sem autorização explícita

- Enviar mensagem ao cliente.
- Alterar escopo contratado.
- Aprovar custo adicional.
- Aprovar medição financeira.
- Fechar tarefa crítica automaticamente.
- Alterar tarefa concluída.
- Criar tarefa em massa sem revisão.
- Apagar tarefas, comentários ou evidências.

## Travas obrigatórias

Uma ação real só pode acontecer se todas as condições forem verdadeiras:

- `dry_run` é falso somente no workflow específico de execução aprovada.
- `ASANA_ENABLE_REAL_ACTIONS=true`.
- `ASANA_ACCESS_TOKEN` está configurado no ambiente seguro.
- `confirm_real_action=True` foi passado explicitamente.
- A ação possui `review_id`.
- A ação está com status `approved`.
- A auditoria será gravada antes/depois da tentativa.

## Decisões sempre humanas

- Comunicação com cliente.
- Impacto financeiro médio, alto ou crítico.
- Impacto em prazo alto ou crítico.
- Mudança de escopo.
- Bloqueio de obra.
- Conflito entre projeto e campo.
- Encerramento de etapa crítica.

## Regra de ouro

O agente pode acelerar o processo, mas a gestão continua dona da decisão.
