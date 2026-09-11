# airflow-lab

Projeto de estudos de Apache Airflow, usado para orquestrar o pipeline do
projeto [`DBT-Fundamentals---Jaffle-Shop`](https://github.com/guscrat/DBT-Fundamentals---Jaffle-Shop)
(dbt + DuckDB). Aqui o foco é aprender Airflow em si — o DAG apenas chama, via
`BashOperator`, os mesmos comandos que já são rodados manualmente naquele
projeto dbt.

## Como os dois projetos se conversam

Este repositório não contém lógica de transformação de dados — isso mora no
projeto dbt. O único DAG existente (`dags/jaffle_shop_pipeline.py`) apenas
encadeia, dentro do diretório do projeto dbt, os passos:

```
load_raw (load_raw.py) >> dbt_run (dbt run) >> dbt_test (dbt test)
```

O caminho do projeto dbt está hardcoded na constante `DBT_DIR` do DAG e
aponta para uma pasta fora deste repositório. Se você clonar este projeto em
outra máquina, precisa ajustar esse caminho (e ter o projeto dbt já
configurado, com `uv sync` e `profiles.yml` feitos — veja o README dele).

## Setup

### 1. Instalar as dependências

```bash
uv sync
```

### 2. Ajustar o `AIRFLOW_HOME`

O Airflow usa o diretório atual como `AIRFLOW_HOME` por padrão (`airflow.cfg`,
`airflow.db`, `logs/` já estão aqui). Rode os comandos sempre a partir da raiz
deste repositório, ou exporte:

```bash
export AIRFLOW_HOME=$(pwd)
```

### 3. Subir o Airflow (standalone)

```bash
uv run airflow standalone
```

Isso inicializa o banco de metadados, cria um usuário admin e sobe o
scheduler + a UI web (por padrão em `http://localhost:8080`). O usuário e
senha gerados aparecem no log de saída (também salvos em
`simple_auth_manager_passwords.json.generated`).

### 4. Rodar o DAG

Pela UI, ative o DAG `jaffle_shop_pipeline` e dispare uma execução manual, ou
via CLI:

```bash
uv run airflow dags trigger jaffle_shop_pipeline
```

## Estrutura

- `dags/jaffle_shop_pipeline.py` — DAG único do projeto.
- `airflow.cfg`, `airflow.db*` — configuração e metadados locais do Airflow
  (não versionados).
- `logs/` — logs de execução das tasks (não versionado).

## Resources

- [Documentação do Airflow](https://airflow.apache.org/docs/)
- Projeto dbt orquestrado: [`DBT-Fundamentals---Jaffle-Shop`](https://github.com/guscrat/DBT-Fundamentals---Jaffle-Shop)
