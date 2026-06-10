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

O MVP usa `unittest` e não exige dependências externas:

```bash
python -m unittest discover
```

## Observações

- A primeira versão não altera o Asana.
- O dry-run é o padrão do MVP.
- A integração com Asana está preparada apenas como simulação.
- Nunca versionar tokens reais.
- Mensagens ao cliente exigem revisão humana.
- Impacto financeiro alto exige revisão humana.
