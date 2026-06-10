# Matriz de Decisão dos Agentes

## Decisões principais

| Condição | Decisão | Ação |
|---|---|---|
| Evidência completa, sem risco relevante | approved | Aprovar e liberar próxima etapa |
| Evidência incompleta | request_correction | Solicitar complemento |
| Falta aprovação do cliente | ask_client | Acionar atendimento |
| Falta decisão interna | escalate_management | Acionar gestão |
| Impacto financeiro médio/alto | escalate_management | Acionar gestão e financeiro |
| Impacto prazo alto/crítico | escalate_management | Acionar gestão e planejamento |
| Falta projeto ou conflito técnico | request_correction | Acionar projetos |
| Falta material crítico | create_next_tasks | Acionar compras |
| Tarefa depende de outra não concluída | blocked | Bloquear e apontar dependência |
| Cliente precisa ser comunicado | ask_client | Criar rascunho de mensagem |

## Classificação de risco

### Baixo

- Sem impacto direto em prazo, custo ou cliente.
- Correção simples.
- Não bloqueia próxima etapa.

### Médio

- Pode gerar atraso pontual.
- Pode gerar retrabalho limitado.
- Pode exigir alinhamento entre departamentos.

### Alto

- Pode afetar cronograma macro.
- Pode gerar custo adicional.
- Pode afetar percepção do cliente.
- Pode bloquear execução.

### Crítico

- Pode gerar prejuízo relevante.
- Pode gerar conflito contratual.
- Pode gerar paralisação da obra.
- Pode comprometer entrega ao cliente.

## Regras rígidas

1. Se `impacto_financeiro` for alto, decisão deve exigir gestão.
2. Se `impacto_cliente` for alto, atendimento deve ser acionado.
3. Se `evidencias_faltantes` não estiver vazio, não aprovar completamente.
4. Se tarefa estiver no caminho crítico e atrasada, escalar para gestão.
5. Se houver alteração de escopo, escalar para gestão.
6. Se houver decisão do cliente pendente, criar tarefa para atendimento.
7. Se material crítico não foi comprado, acionar compras e planejamento.
8. Se projeto estiver incompleto, bloquear execução relacionada.
