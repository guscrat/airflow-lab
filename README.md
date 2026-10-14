# airflow-lab

Projeto de estudos de Apache Airflow, usado para orquestrar o pipeline do
projeto [`jaffle-shop-analytics-bigquery`](https://github.com/guscrat/jaffle-shop-analytics-bigquery)
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

O ambiente roda **exclusivamente via Docker Compose** — não há mais execução
direta na máquina (standalone). Isso mantém o setup igual em qualquer SO
(Windows, Linux ou macOS), que foi o motivo da migração: o fluxo antigo
dependia de shell POSIX e do Airflow instalado localmente e quebrava no
Windows.

Pré-requisito: Docker Desktop (ou Docker Engine + Compose) instalado e com
pelo menos ~4 GB de memória disponíveis para o Docker.

### 1. Subir o ambiente

A partir da raiz deste repositório:

```bash
docker compose up -d
```

O `docker-compose.yaml` é a configuração oficial do Apache Airflow
(CeleryExecutor + PostgreSQL + Redis). Na primeira vez, o serviço
`airflow-init` roda a migração do banco de metadados e cria o usuário admin
antes dos demais serviços subirem.

### 2. Acessar a UI

A UI web fica em **`http://localhost:8081`** (o compose mapeia a porta interna
`8080` para `8081` no host). Usuário e senha padrão são `airflow` / `airflow`.

### 3. Rodar o DAG

Pela UI, ative o DAG desejado (`jaffle_shop_pipeline` ou `jaffle_shop_cosmos`)
e dispare uma execução manual, ou via CLI dentro do container:

```bash
docker compose run --rm airflow-cli dags trigger jaffle_shop_pipeline
# ou
docker compose run --rm airflow-cli dags trigger jaffle_shop_cosmos
```

### 4. Derrubar o ambiente

```bash
docker compose down
# para apagar também o banco de metadados (volume do Postgres):
docker compose down -v
```

## ⚠️ Pendências para o pipeline rodar de ponta a ponta

O Compose já sobe o Airflow e carrega os DAGs deste repositório, **mas o
pipeline ainda não executa de ponta a ponta** — o `docker-compose.yaml` é o
oficial da Apache, sem as customizações específicas deste projeto. Falta
configurar:

1. **Montar o projeto dbt no container.** O caminho em `DBT_PROJECT_DIR` aponta
   para uma pasta *fora* deste repositório; dentro do container esse caminho
   não existe. É preciso adicionar um volume (ex.: via `AIRFLOW_PROJ_DIR` ou um
   mount dedicado) expondo o projeto dbt para os serviços.
2. **Instalar as dependências do pipeline.** A imagem `apache/airflow` não traz
   o [Astronomer Cosmos](https://astronomer.github.io/astronomer-cosmos/) nem o
   `dbt-bigquery`. Usar `_PIP_ADDITIONAL_REQUIREMENTS` (apenas para testes
   rápidos) ou estender a imagem via `build:` (recomendado).
3. **Prover as credenciais do GCP.** Montar a service account e apontar
   `GOOGLE_APPLICATION_CREDENTIALS` (ou o `profiles.yml` do dbt) para dentro do
   container, de modo que as tasks consigam acessar o BigQuery.
4. **Desligar os DAGs de exemplo.** Trocar
   `AIRFLOW__CORE__LOAD_EXAMPLES` para `'false'` para não poluir a UI com os
   DAGs de demonstração do Airflow.

Esses ajustes serão feitos conforme o projeto dbt for validado.

## Estrutura

- `docker-compose.yaml` — ambiente do Airflow (CeleryExecutor + PostgreSQL +
  Redis), base oficial da Apache.
- `dags/jaffle_shop_pipeline.py` — DAG sequencial (`BashOperator` chamando
  `dbt run`/`dbt test`).
- `dags/jaffle_shop_cosmos.py` — DAG com Cosmos, paralelizando as tasks de
  transformação do dbt.
- `config/`, `plugins/` — montados nos containers (`/opt/airflow/config` e
  `/opt/airflow/plugins`).
- `logs/` — logs de execução das tasks, montado nos containers (não
  versionado).

## Resources

- [Documentação do Airflow](https://airflow.apache.org/docs/)
- Projeto dbt orquestrado: [`jaffle-shop-analytics-bigquery`](https://github.com/guscrat/jaffle-shop-analytics-bigquery)
