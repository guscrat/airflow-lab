# airflow-lab

Projeto de estudos de Apache Airflow, usado para orquestrar o pipeline do
projeto [`DBT-Fundamentals---Jaffle-Shop`](https://github.com/guscrat/DBT-Fundamentals---Jaffle-Shop)
(dbt + BigQuery). Aqui o foco é aprender Airflow em si — os DAGs apenas chamam
os mesmos comandos que já são rodados manualmente naquele projeto dbt.

O projeto migrou de DuckDB para BigQuery por razões didáticas: com um
warehouse remoto dá pra explorar paralelismo real entre execuções de modelos
dbt (via Cosmos) sem esbarrar nas limitações de concorrência de um arquivo
local do DuckDB.

## Como os dois projetos se conversam

Este repositório não contém lógica de transformação de dados — isso mora no
projeto dbt. Existem dois DAGs, ambos encadeando, dentro do diretório do
projeto dbt, os mesmos passos de fundo (carga + transformação):

- **`dags/jaffle_shop_pipeline.py`** — versão simples, com `BashOperator`
  chamando `dbt run` e `dbt test` sequencialmente:

  ```
  load_raw (load_raw.py) >> dbt_run (dbt run) >> dbt_test (dbt test)
  ```

- **`dags/jaffle_shop_cosmos.py`** — versão com
  [Astronomer Cosmos](https://astronomer.github.io/astronomer-cosmos/),
  que converte cada model/test do dbt em uma task própria do Airflow
  (`DbtTaskGroup`), permitindo paralelismo real entre models sem
  dependência entre si — o principal motivo de usar BigQuery aqui:

  ```
  load_raw (load_raw.py) >> dbt_transform (DbtTaskGroup via Cosmos)
  ```

O caminho do projeto dbt está hardcoded na constante `DBT_PROJECT_DIR` de
cada DAG e aponta para uma pasta fora deste repositório. Se você clonar este
projeto em outra máquina, precisa ajustar esse caminho (e ter o projeto dbt
já configurado, com `uv sync`, `profiles.yml` apontando para o profile
`jaffle_shop`/BigQuery e credenciais do GCP configuradas — veja o README
dele).

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

Pela UI, ative o DAG desejado (`jaffle_shop_pipeline` ou `jaffle_shop_cosmos`)
e dispare uma execução manual, ou via CLI:

```bash
uv run airflow dags trigger jaffle_shop_pipeline
# ou
uv run airflow dags trigger jaffle_shop_cosmos
```

## Estrutura

- `dags/jaffle_shop_pipeline.py` — DAG sequencial (`BashOperator` chamando
  `dbt run`/`dbt test`).
- `dags/jaffle_shop_cosmos.py` — DAG com Cosmos, paralelizando as tasks de
  transformação do dbt.
- `airflow.cfg`, `airflow.db*` — configuração e metadados locais do Airflow
  (não versionados).
- `logs/` — logs de execução das tasks (não versionado).

## Resources

- [Documentação do Airflow](https://airflow.apache.org/docs/)
- Projeto dbt orquestrado: [`DBT-Fundamentals---Jaffle-Shop`](https://github.com/guscrat/DBT-Fundamentals---Jaffle-Shop)
