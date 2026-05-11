# chap26b - Step-by-step recap: the MLflow CLI (`mlflow doctor`, `mlflow artifacts`, `mlflow experiments`, `mlflow runs`, `mlflow db upgrade`)

The full lesson lives at [`../26b-mlflow-step-by-step-recap-mlflow-cli-doctor-artifacts-experiments-runs.md`](../26b-mlflow-step-by-step-recap-mlflow-cli-doctor-artifacts-experiments-runs.md).

> **In one line.** This chapter is about how to **drive every MLflow administrative task from a dedicated `cli` Docker service** instead of opening Python: `mlflow doctor`, `mlflow experiments create/rename/delete/restore/search/csv`, `mlflow runs list/describe/delete/restore`, `mlflow artifacts list/download/log-artifacts`, `mlflow db upgrade`.

## What is new vs chap26

- A third service `cli` (image `mlops/mlflow-cli`) with **only** `mlflow` installed and `MLFLOW_TRACKING_URI=http://mlflow:5000` baked in via env var.
- No `ENTRYPOINT` on the `cli` image -- you spawn arbitrary CLI commands with `docker compose run --rm cli mlflow ...` (or open a shell with `docker compose run --rm --entrypoint sh cli`).
- A `./cli_artifact:/artifacts` host bind mount on the `cli` service -- the natural target for `mlflow artifacts download` outputs and `mlflow experiments csv --filename /artifacts/...`.
- The `trainer` is unchanged from chap25's idiomatic context-manager style (`with mlflow.start_run(...)` inside a `main()`), used here only to **seed** a couple of runs so the CLI demos have something to inspect.

## Project structure

```text
chap26b-.../
+- README.md                 <- this file
+- docker-compose.yml        <- mlflow + trainer + cli
+- data/
|  +- red-wine-quality.csv
+- mlflow/
|  +- Dockerfile             <- mlflow tracking server image
+- trainer/                  <- seeds 1-2 runs so we have something to inspect
|  +- Dockerfile
|  +- requirements.txt
|  +- train.py
+- cli/                      <- the CLI sandbox
|  +- Dockerfile
|  +- requirements.txt
+- cli_artifact/             <- host bind-mount for download/csv outputs (created on first use)
```

## Run it (100% Docker, no Python on the host)

### 1. Move into the chapter

```bash
cd chap26b-mlflow-step-by-step-recap-mlflow-cli-doctor-artifacts-experiments-runs
```

### 2. Build everything and start the MLflow server in the background

```bash
docker compose up -d --build mlflow
```

Verify with:

```bash
docker compose ps
# mlflow-recap-26b    Up X seconds (healthy)
```

Open [http://localhost:5000](http://localhost:5000). Empty UI at this stage (only `Default`).

### 3. Seed two runs for the CLI demos

```bash
docker compose run --rm trainer --alpha 0.4 --l1_ratio 0.4
docker compose run --rm trainer --alpha 0.6 --l1_ratio 0.6
```

Refresh the UI -> experiment `experiment_cli_demo` with 2 runs, each containing a `model/` artifact. Note one of the run ids; the lesson refers to it as `<RUN_ID>`.

### 4. Drive the CLI from the `cli` service

```bash
# Installation health check
docker compose run --rm cli mlflow doctor

# Experiments
docker compose run --rm cli mlflow experiments search --view all
docker compose run --rm cli mlflow experiments create --experiment-name cli_experiment
docker compose run --rm cli mlflow experiments rename --experiment-id 2 --new-name test1
docker compose run --rm cli mlflow experiments delete  --experiment-id 2
docker compose run --rm cli mlflow experiments restore --experiment-id 2
docker compose run --rm cli mlflow experiments csv \
  --experiment-id 1 --filename /artifacts/test.csv

# Runs
docker compose run --rm cli mlflow runs list --experiment-id 1 --view all
docker compose run --rm cli mlflow runs describe --run-id <RUN_ID>
docker compose run --rm cli mlflow runs delete  --run-id <RUN_ID>
docker compose run --rm cli mlflow runs restore --run-id <RUN_ID>

# Artifacts
docker compose run --rm cli mlflow artifacts list     --run-id <RUN_ID>
docker compose run --rm cli mlflow artifacts download --run-id <RUN_ID> \
  --artifact-path model --dst-path /artifacts
docker compose run --rm cli mlflow artifacts log-artifacts \
  --local-dir /artifacts/notes --run-id <RUN_ID>
```

After `download` / `csv`, look on the host: the outputs land in `./cli_artifact/...` thanks to the bind mount.

### 5. Open a long-running shell inside the CLI sandbox

When you want to chain many commands without paying the container start-up over and over:

```bash
docker compose run --rm --entrypoint sh cli
# inside:
#   mlflow doctor
#   mlflow experiments search --view all
#   mlflow runs list --experiment-id 1 --view all
#   mlflow artifacts download --run-id <RUN_ID> --artifact-path model --dst-path /artifacts
#   exit
```

### 6. Tear down

```bash
docker compose down       # keep volumes (DB + artifacts survive)
docker compose down -v    # wipe everything
```

## What ends up on your host

| Path / Volume | Contents |
|---|---|
| `mlflow-db` (Docker volume) | SQLite metadata DB |
| `mlflow-artifacts` (Docker volume) | Pickled models, signatures |
| `./cli_artifact/` (host bind mount) | `mlflow artifacts download` outputs + `mlflow experiments csv` exports |

Inspect the named volumes with:

```bash
docker volume ls | grep recap
docker volume inspect mlflow-artifacts
```

## Recap (bash, one-shot)

```bash
cd chap26b-mlflow-step-by-step-recap-mlflow-cli-doctor-artifacts-experiments-runs

docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.4 --l1_ratio 0.4
docker compose run --rm trainer --alpha 0.6 --l1_ratio 0.6

docker compose run --rm cli mlflow doctor
docker compose run --rm cli mlflow experiments search --view all
docker compose run --rm cli mlflow runs list --experiment-id 1 --view all

docker compose down
```

## Recap (Windows PowerShell)

```powershell
cd chap26b-mlflow-step-by-step-recap-mlflow-cli-doctor-artifacts-experiments-runs

docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.4 --l1_ratio 0.4
docker compose run --rm trainer --alpha 0.6 --l1_ratio 0.6

docker compose run --rm cli mlflow doctor
docker compose run --rm cli mlflow experiments search --view all
docker compose run --rm cli mlflow runs list --experiment-id 1 --view all

docker compose down
```

## Troubleshooting

<details>
<summary><strong>Port 5000 already in use on Windows</strong></summary>

CMD:

```bat
netstat -ano | findstr :5000
tasklist | findstr 12345
taskkill /PID 12345 /F
```

PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 5000
Stop-Process -Id 12345 -Force
```

</details>

<details>
<summary><strong>Docker Desktop frozen</strong></summary>

Open **PowerShell as Administrator**:

```powershell
Get-Process *docker* -ErrorAction SilentlyContinue | Stop-Process -Force
Stop-Service com.docker.service -Force -ErrorAction SilentlyContinue
wsl --shutdown
```

Then:

```powershell
Start-Service com.docker.service
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

</details>

<details>
<summary><strong>`mlflow doctor` shows the wrong tracking URI</strong></summary>

The `cli` image bakes `MLFLOW_TRACKING_URI=http://mlflow:5000`. If `mlflow doctor` shows something else, check:

1. `docker-compose.yml` -> `cli` service -> the `environment:` block.
2. You launched via `docker compose run --rm cli ...` (the `cli` service inherits the network + env).
3. The MLflow service is healthy: `docker compose ps` -> `mlflow-recap-26b ... healthy`.

Override at runtime if needed:

```bash
docker compose run --rm -e MLFLOW_TRACKING_URI=http://other:5000 cli mlflow doctor
```

</details>

<details>
<summary><strong>`mlflow artifacts download` cannot find my output</strong></summary>

The `cli` service mounts `./cli_artifact:/artifacts`. Always pass `--dst-path /artifacts/...` (inside the container) so the file lands in `./cli_artifact/...` on the host. If you `--dst-path /tmp/foo`, the file lives only inside the (`--rm`-removed) container and is lost the moment the command returns.

</details>

## Final wrap-up

You've now closed the **complete recap series**: chap01 -> 26b. The trainer side is fully covered (basics, Docker plumbing, experiments, runs, artifacts, tags, autolog, signatures, pyfunc, evaluation, validation, registry, projects, CLI). The next major step of the course is **deployment**: serving the registered model through FastAPI and consuming it from a Streamlit frontend (chapters 21+ of the original course track).
