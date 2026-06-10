# Como rodar o MVP localmente

## 1. Clonar o repositório

```bash
git clone https://github.com/firetecnologia/nucleo-agentes-gestao-obra.git
cd nucleo-agentes-gestao-obra
```

## 2. Rodar análise em modo dry-run

```bash
python -m src.workflows.analyze_task --input sample_task_payload.json --dry-run
```

## 3. Rodar testes

Instale pytest no seu ambiente Python e execute:

```bash
python -m pytest
```

## Observações

- A primeira versão não altera o Asana.
- A integração com Asana está em modo placeholder.
- O foco desta entrega é validar a lógica de análise, risco e decisão.
- Tokens reais devem ser configurados apenas em etapa posterior.
