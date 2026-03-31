# Pokédex Analytics Pipeline

A modern data engineering pipeline that ingests Pokémon data from [PokéAPI](https://pokeapi.co), transforms it with **dbt + DuckDB**, and visualizes insights in a **Streamlit** dashboard, fully containerized with Docker.

## Architecture
```
PokéAPI → Python ingest → DuckDB (raw tables)
                               ↓
                    dbt (staging → marts)
                               ↓
                    Streamlit dashboard
```

## Data Model
```
raw_pokemon              ← ingested from PokéAPI (150 Gen I pokémon)
      ↓
stg_pokemon              ← cleaned, renamed, typed (view)
      ↓
fct_pokemon              ← fact table, one row per pokémon (table)
dim_type                 ← aggregated stats per type (table)
```

Staging models are materialized as **views** (no storage, always fresh). Mart models are materialized as **tables** (pre-computed, fast to query).

## Quickstart

**Requirements:** Docker
```bash
git clone git@github.com:anasiadan/duckdb-dbt-streamlit-project.git
cd duckdb-dbt-streamlit-project
docker-compose up
```

Open [http://localhost:8501](http://localhost:8501).

The pipeline runs automatically in order:
1. `ingest` — fetches data from PokéAPI → stores in DuckDB
2. `dbt` — runs transformations and tests
3. `streamlit` — serves the dashboard

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | Python + Requests |
| Storage | DuckDB |
| Transformation | dbt-duckdb |
| Visualization | Streamlit + Plotly |
| Containerization | Docker + Docker Compose |

## Proposed Next Steps

- **Incremental loads** : currently the ingest script drops and recreates the raw table on every run. In production this should be replaced with an upsert (INSERT OR REPLACE) to append new data and avoid reprocessing
- **Orchestration** : add Dagster or Airflow to schedule and monitor the pipeline
- **CI/CD** : GitHub Actions to run `dbt test` on every pull request
- **Cloud deployment** : move DuckDB to S3-backed storage (MotherDuck or LakeFS), deploy Streamlit to AWS/GCP