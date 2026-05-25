# chap24 - Step-by-step recap: registering a model trained OUTSIDE MLflow (cloudpickle import)

The full lesson lives at [../24-practical-work-mlflow-step-by-step-recap-registering-a-model-trained-outside-mlflow-with-cloudpickle.md](../24-practical-work-mlflow-step-by-step-recap-registering-a-model-trained-outside-mlflow-with-cloudpickle.md).

> **In one line.** This chapter is about how to **split the workflow into two one-shot Docker services: a `pretrainer` that trains a model WITHOUT touching MLflow (`pickle.dump` + done) and a `registrar` that **imports** that pickle, loads it, and pushes it into the registry with `mlflow.sklearn.log_model(..., serialization_format="cloudpickle", registered_model_name=...)`**.

## Before you start — Create the host folders!

> [!IMPORTANT]
> **You MUST create the local folders `database/` and `mlruns/` BEFORE the first `docker compose up`.**
>
> This chapter's `docker-compose.yml` uses **bind mounts** (host folders mapped INTO the `mlflow` container) for the tracking DB and artifacts, plus a separate **named volume `shared:`** that the `pretrainer` and `registrar` services share for the pickle handover. If the host folders don't exist, Docker will silently create them as **empty root-owned directories**.
>
> ### Create them now
> ```bash
> mkdir database mlruns       # bash / Git Bash / macOS / Linux / WSL
> ```
> ```powershell
> New-Item -ItemType Directory database, mlruns -Force | Out-Null   # PowerShell
> ```
>
> ### What ends up in those folders — and what `working_dir` is for
>
> | Host (your laptop, this chapter folder) | Container path                                | What lives there                                          |
> | --------------------------------------- | --------------------------------------------- | --------------------------------------------------------- |
> | `./database/`                           | `/mlflow/database/` (in `mlflow`)             | `mlflow.db` — the SQLite tracking store                   |
> | `./mlruns/`                             | `/mlflow/mlruns/`  (in `mlflow`)              | Artifacts + the registered `external-elasticnet` model    |
> | `.` (the entire chapter folder)         | `/work/`  ←  this is `working_dir:` in mlflow | The full project tree: `pretrainer/`, `registrar/`, ...   |
> | (named volume `shared:`)                | `/shared/` (in `pretrainer` and `registrar`)  | `external_model.pkl` produced by `pretrainer`             |
>
> The `.:/work` mount plus `working_dir: /work` is what makes **Docker Desktop → Containers → `mlflow-recap-24` → Exec → `ls`** show all your project files (so you can run `python registrar/register_external.py` from there). `working_dir:` is a Compose directive that sets the default cwd for `RUN`, `CMD` and any `docker compose exec`.

## Two ways to launch the workflow

> [!NOTE]
> **Way A — canonical (run the two one-shot containers in order, recommended for the lesson):**
> ```bash
> docker compose run --rm pretrainer        # writes /shared/external_model.pkl (no MLflow)
> docker compose run --rm registrar         # loads pickle, registers it in MLflow
> ```
>
> **Way B — via `docker compose exec` inside the running `mlflow` container (Docker Desktop friendly):**
> ```bash
> docker compose run --rm pretrainer        # still needed: produces /shared/external_model.pkl
> docker compose exec mlflow python registrar/register_external.py
> ```
>
> The `pretrainer` MUST be a one-shot container — it has no MLflow client and writes the pickle to the `shared` named volume; you cannot run it from the `mlflow` container because the `mlflow` container has no access to `shared/`. The `registrar` script CAN run either as its own container OR directly inside `mlflow` (the `mlflow` image has `mlflow.sklearn.log_model`, and since `.:/work` is mounted, the script file is visible — BUT the `mlflow` container has no `/shared/` mount, so Way B reads the pickle from `./shared` only if you tweak the mount. In practice, prefer Way A.). Both paths produce the same registered model `external-elasticnet` in the MLflow Registry. If a run does NOT appear in the UI, force the URI with: `docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python registrar/register_external.py`.

## What is new vs chap23

- Two trainer services: `pretrainer/` (pure sklearn, no MLflow) and `registrar/` (MLflow-aware import job)
- `pretrainer/train_outside_mlflow.py` -> writes `/shared/external_model.pkl`
- `registrar/register_external.py` -> `pickle.load(...)` then `mlflow.sklearn.log_model(loaded, "model", serialization_format="cloudpickle", registered_model_name="external-elasticnet")`
- Named volume `shared:/shared` mounted on BOTH services for the handover
- `cloudpickle` (instead of vanilla `pickle`) -> robust for sklearn objects with closures, lambdas, custom transformers

This chapter adds extra service(s) on top of the standard mlflow + trainer pair: **pretrainer, registrar**. See the lesson .md for the rationale.


## Project structure

The project follows the canonical recap layout (see [section 8 of the root README](../README.md#section-8) for the full reference):

```text
chap24-.../
+- README.md                 <- this file
+- docker-compose.yml        <- mlflow + trainer + pretrainer + registrar
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
cd chap24-mlflow-step-by-step-recap...
```

### 2. Build everything and start the MLflow server in the background

```bash
docker compose up -d --build mlflow
```

- `-d` runs the server detached so this terminal stays free for the trainer.
- `--build` forces a rebuild if any `Dockerfile` or `requirements.txt` changed.

Verify with:

```bash
docker compose ps
# mlflow-recap-24    Up X seconds (healthy)
```

Open [http://localhost:5000](http://localhost:5000). The UI is empty for now (only `Default`) unless you have persistent volumes from a previous chapter.

### 3. Run the trainer (with CLI args)

```bash
docker compose run --rm pretrainer --alpha 0.4 --l1_ratio 0.4
docker compose run --rm registrar
```

### 4. Refresh the MLflow UI

Open / refresh [http://localhost:5000](http://localhost:5000). Expected:

- Experiment: `external_models`
- 1 run in `external_models` + an `external-elasticnet` entry in the **Models** tab. The model never saw `mlflow.start_run()` during training -- only during the import.

> **Chapter quirk.** `cloudpickle` serializes things `pickle` cannot (closures, lambdas, dynamic classes). It is a strict superset for sklearn objects. Use it whenever you are importing a model produced by code you don't fully control.

### 5. Tear down

```bash
docker compose down       # keep volumes (DB + artifacts survive)
docker compose down -v    # wipe everything (DB + artifacts + this chapter's named volumes)
```

## What ends up on your host

This chapter uses **named Docker volumes** rather than host-side bind mounts for the MLflow data:

| Volume | Contents |
|---|---|
| `mlflow-db`  | SQLite metadata DB (experiments, runs, registered models) |
| `mlflow-artifacts` | Pickled models, signatures, plots, CSVs |
| `shared` | Handover folder between `pretrainer` and `registrar` |

Inspect them with:

```bash
docker volume ls | grep recap
docker volume inspect <volume_name>
```

These volumes survive `docker compose down`. Only `docker compose down -v` wipes them.

## Recap (bash, one-shot)

```bash
cd chap24-mlflow-step-by-step-recap...

docker compose up -d --build mlflow

docker compose run --rm pretrainer --alpha 0.4 --l1_ratio 0.4
docker compose run --rm registrar

# Open http://localhost:5000 and inspect the runs in experiment 'external_models'.

docker compose down
```

## Recap (Windows PowerShell)

```powershell
cd chap24-mlflow-step-by-step-recap...

docker compose up -d --build mlflow

docker compose run --rm pretrainer --alpha 0.4 --l1_ratio 0.4
docker compose run --rm registrar

# Open http://localhost:5000 and inspect the runs in experiment 'external_models'.

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
3. The MLflow service is healthy: `docker compose ps` -> `mlflow-recap-24 ... healthy`.

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

**Next**: [chap25](../25-practical-work-mlflow-step-by-step-recap-with-start-run-context-manager-and-main-function.md) -- replace the imperative `mlflow.start_run() / mlflow.end_run()` style with the idiomatic Pythonic context manager `with mlflow.start_run(experiment_id=exp.experiment_id):` wrapped in a clean `main()` function.