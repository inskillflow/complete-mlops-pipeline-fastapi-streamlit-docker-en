# chap13 - Step-by-step recap: PostgreSQL backend store and S3 artifacts (production topology)

The full lesson lives at [../13-practical-work-mlflow-step-by-step-recap-postgresql-backend-store-and-s3-artifacts.md](../13-practical-work-mlflow-step-by-step-recap-postgresql-backend-store-and-s3-artifacts.md).

> **In one line.** This chapter is about how to **replace SQLite with PostgreSQL for the backend store, and outline how to plug an S3 (or MinIO) bucket as the artifact store -- the canonical production deployment of MLflow**.

## What is new vs chap12

- Third service: `postgres` (image `postgres:16-alpine`) with `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` env vars
- `mlflow/Dockerfile` adds `psycopg2-binary`; the `CMD` uses `--backend-store-uri postgresql://mlflowuser:...@postgres:5432/mlflowdb`
- `depends_on: postgres: condition: service_healthy` -> MLflow only starts once the DB accepts connections
- Artifacts can stay on a local named volume OR move to S3/MinIO with `--default-artifact-root s3://...` + AWS creds env vars

This chapter adds extra service(s) on top of the standard mlflow + trainer pair: **postgres**. See the lesson .md for the rationale.


## Project structure

The project follows the canonical recap layout (see [section 8 of the root README](../README.md#section-8) for the full reference):

```text
chap13-.../
+- README.md                 <- this file
+- docker-compose.yml        <- mlflow + trainer + postgres
+- mlflow/
|  +- Dockerfile             <- mlflow tracking server image
+- data/
|  +- red-wine-quality.csv
+- trainer/                  <- training service
   +- Dockerfile
   +- requirements.txt
   +- train.py
```

## Run it (100% Docker, no Python on the host)

This is the **canonical run sequence** for the recap series. It is the same for every chapter from 04 onward; only the trainer arguments change.

### 1. Move into the chapter

```bash
cd chap13-mlflow-step-by-step-recap...
```

### 2. Build everything and start the MLflow server in the background

```bash
docker compose up -d --build mlflow postgres
```

- `-d` runs the server detached so this terminal stays free for the trainer.
- `--build` forces a rebuild if any `Dockerfile` or `requirements.txt` changed.

Verify with:

```bash
docker compose ps
# mlflow-recap-13    Up X seconds (healthy)
```

Open [http://localhost:5000](http://localhost:5000). The UI is empty for now (only `Default`) unless you have persistent volumes from a previous chapter.

### 3. Run the trainer (with CLI args)

```bash
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
```

### 4. Refresh the MLflow UI

Open / refresh [http://localhost:5000](http://localhost:5000). Expected:

- Experiment: `experiment_pg`
- 1 run; UI on [http://localhost:5000](http://localhost:5000) is identical to chap12 but the data now lives in PostgreSQL.

> **Chapter quirk.** Use `docker compose exec postgres psql -U mlflowuser -d mlflowdb -c "\dt"` to confirm MLflow's schema was created (you should see `experiments`, `runs`, `metrics`, `params`, ...). If the tables are missing, `mlflow db upgrade postgresql://...` is the fix.

### 5. Tear down

```bash
docker compose down       # keep volumes (DB + artifacts survive)
docker compose down -v    # wipe everything (DB + artifacts + this chapter's named volumes)
```

## What ends up on your host

This chapter uses **named Docker volumes** rather than host-side bind mounts for the MLflow data:

| Volume | Contents |
|---|---|
| `mlflow-db` *(unused -- DB lives in `postgres-data` now)* | SQLite metadata DB (experiments, runs, registered models) *(unused, see `postgres-data`)* |
| `mlflow-artifacts` | Pickled models, signatures, plots, CSVs |
| `postgres-data` | PostgreSQL data directory |

Inspect them with:

```bash
docker volume ls | grep recap
docker volume inspect <volume_name>
```

These volumes survive `docker compose down`. Only `docker compose down -v` wipes them.

## Recap (bash, one-shot)

```bash
cd chap13-mlflow-step-by-step-recap...

docker compose up -d --build mlflow postgres

docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5

# Open http://localhost:5000 and inspect the runs in experiment 'experiment_pg'.

docker compose down
```

## Recap (Windows PowerShell)

```powershell
cd chap13-mlflow-step-by-step-recap...

docker compose up -d --build mlflow postgres

docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5

# Open http://localhost:5000 and inspect the runs in experiment 'experiment_pg'.

docker compose down
```

## Enter the trainer container manually (debugging)

Sometimes you want a shell inside the trainer to inspect the filesystem, the env, or to step through the script line by line:

```bash
docker compose run --rm --entrypoint bash trainer
# inside:
#   cat train.py
#   ls /code/data
#   env | grep MLFLOW
#   python train.py --alpha 0.5 --l1_ratio 0.5
#   exit
```

The `--entrypoint bash` flag overrides the image's `ENTRYPOINT ["python", "train.py"]` and drops you into a shell instead.

## Troubleshooting

<details>
<summary><strong>Port 5000 already in use on Windows</strong></summary>

The MLflow server publishes `5000:5000`. If something else is already on port 5000 the container fails to start.

CMD:

```bat
netstat -ano | findstr :5000
:: Last column is the PID. Then:
tasklist | findstr 12345
taskkill /PID 12345 /F
```

PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 5000
Stop-Process -Id 12345 -Force
```

Port 5000 is the most common collision (Flask dev servers, AirPlay on macOS, `Hyper-V`, `IIS`, `netbios`, a previous MLflow chapter you forgot to `docker compose down`).

</details>

<details>
<summary><strong>Docker Desktop frozen / containers stuck in `Created`</strong></summary>

Open **PowerShell as Administrator**:

```powershell
# 1. Stop Docker Desktop processes
Get-Process *docker* -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Stop the Docker service
Stop-Service com.docker.service -Force -ErrorAction SilentlyContinue

# 3. Force-stop the WSL backend
wsl --shutdown
```

Wait 10-15 seconds, then:

```powershell
Start-Service com.docker.service
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

If still frozen:

```powershell
taskkill /F /IM "Docker Desktop.exe"
taskkill /F /IM "com.docker.backend.exe"
taskkill /F /IM "com.docker.service.exe"
taskkill /F /IM "dockerd.exe"
wsl --shutdown
```

Then restart Docker Desktop from the Start menu.

</details>

<details>
<summary><strong>Trainer says `Tracking URI: file:///code/mlruns`</strong></summary>

That means the trainer did NOT see `MLFLOW_TRACKING_URI`. Three places to check:

1. `docker-compose.yml` -> trainer -> `environment: MLFLOW_TRACKING_URI:` is present.
2. You launched via `docker compose run --rm trainer ...` (not `docker run` directly).
3. The MLflow service is healthy: `docker compose ps` -> `mlflow-recap-13 ... healthy`.

Override at runtime if needed:

```bash
docker compose run --rm -e MLFLOW_TRACKING_URI=http://mlflow:5000 trainer --alpha 0.4 --l1_ratio 0.4
```

</details>

<details>
<summary><strong>Trainer fails immediately with `Image not found` / `manifest unknown`</strong></summary>

You forgot `--build` or the trainer image is stale.

```bash
docker compose down
docker compose up -d --build mlflow
docker compose run --rm trainer --alpha 0.4 --l1_ratio 0.4
```

If `--build` itself fails, prune and retry:

```bash
docker compose down -v
docker builder prune -af
docker compose up -d --build mlflow
```

</details>

## Next chapter

**Next**: [chap14](../14-practical-work-mlflow-step-by-step-recap-model-signature-manual-and-infer-signature.md) -- attach a **model signature** so MLflow knows the exact data types and shapes your model expects. Two approaches: manual (`ModelSignature` + `Schema` + `ColSpec`) and automatic (`infer_signature`).