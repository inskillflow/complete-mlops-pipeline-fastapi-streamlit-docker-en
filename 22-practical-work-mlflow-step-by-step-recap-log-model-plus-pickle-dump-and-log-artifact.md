# chap22 - Step-by-step recap: `log_model` + side-car `pickle.dump` + `log_artifact` (dual-format logging)

The full lesson lives at [../22-practical-work-mlflow-step-by-step-recap-log-model-plus-pickle-dump-and-log-artifact.md](../22-practical-work-mlflow-step-by-step-recap-log-model-plus-pickle-dump-and-log-artifact.md).

> **In one line.** This chapter is about how to **log the model **the canonical MLflow way** (`mlflow.sklearn.log_model`) AND save a side-car `pickle` of it (`pickle.dump` + `mlflow.log_artifact("elastic-net-regression.pkl")`) -- useful when a downstream consumer wants the raw `.pkl` (older code, custom loader, notebook)**.


## Before you start — Create the host folders!

> [!IMPORTANT]
> **You MUST create the local folders `database/` and `mlruns/` BEFORE the first `docker compose up`.**
>
> This chapter's `docker-compose.yml` uses **bind mounts** (host folders mapped INTO the container), not anonymous Docker volumes. If the host folders don't exist, Docker will silently create them as **empty root-owned directories** that are hard to inspect or clean up from your editor on Windows, and you'll wonder why `mlflow.db` "disappears" when you run `docker compose down -v`.
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
> | Host (your laptop, this chapter folder) | Container path (`mlflow` service)   | What lives there                                |
> | --------------------------------------- | ----------------------------------- | ----------------------------------------------- |
> | `./database/`                           | `/mlflow/database/`                 | `mlflow.db` — the SQLite tracking store         |
> | `./mlruns/`                             | `/mlflow/mlruns/`                   | Artifacts: models, plots, metric files          |
> | `.` (the entire chapter folder)         | `/work/`  ←  this is `working_dir:` | The full project tree: `trainer/`, `data/`, ... |
>
> The third mount (`.:/work`) plus `working_dir: /work` is what makes **Docker Desktop → Containers → `mlflow-recap-XX` → Exec → `ls`** show all your project files. Without it, `exec` would drop you in `/mlflow/` and you'd see nothing useful. `working_dir:` is a Docker Compose directive that sets the default cwd for `RUN`, `CMD` and any `docker compose exec` — think of it as `cd /work` baked into the container.

## Two ways to launch the training

> [!NOTE]
> **Way A — canonical (one-shot `trainer` container, recommended for the lesson):**
> ```bash
> docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
> ```
>
> **Way B — via `docker compose exec` inside the running `mlflow` container (Docker Desktop friendly):**
> ```bash
> docker compose exec mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1
> ```
>
> Both run the same `train.py`. Way B works because `mlflow==2.16.2` brings `scikit-learn`, `pandas` and `numpy` as transitive deps. From chap05 onwards, the `MLFLOW_TRACKING_URI` env var is set on the `trainer` service in `docker-compose.yml` and `train.py` reads it via `os.getenv(...)`, so both Way A and Way B "just work" and the runs appear in the MLflow UI under the correct experiment. If a run does NOT appear in the UI, force the URI with: `docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py ...`

## What is new vs chap21

- `mlflow.sklearn.log_model(lr, "model")` -> canonical flavour artifact (`MLmodel`, `conda.yaml`, `model.pkl`, signature)
- `pickle.dump(lr, open("elastic-net-regression.pkl", "wb"))` -> raw `.pkl` on disk
- `mlflow.log_artifact("elastic-net-regression.pkl")` -> upload alongside the canonical model
- Drop the `registered_model_name=` kwarg from chap21 -- this is pure logging, registration is a separate concern


## Project structure

The project follows the canonical recap layout (see [section 8 of the root README](../README.md#section-8) for the full reference):

```text
chap22-.../
+- README.md                 <- this file
+- docker-compose.yml        <- mlflow + trainer
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
cd chap22-mlflow-step-by-step-recap...
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
# mlflow-recap-22    Up X seconds (healthy)
```

Open [http://localhost:5000](http://localhost:5000). The UI is empty for now (only `Default`) unless you have persistent volumes from a previous chapter.

### 3. Run the trainer (with CLI args)

```bash
docker compose run --rm trainer --alpha 0.4 --l1_ratio 0.4
```

### 4. Refresh the MLflow UI

Open / refresh [http://localhost:5000](http://localhost:5000). Expected:

- Experiment: `experiment_dual_format`
- 1 run with BOTH `model/` (canonical MLflow flavour) AND `elastic-net-regression.pkl` (raw pickle) under **Artifacts**.

> **Chapter quirk.** `pickle` is the lingua franca, but it breaks across major Python or sklearn versions. The MLflow flavour pins the env via `conda.yaml`; the raw `.pkl` does not. Document the Python + sklearn version anywhere you publish the side-car.

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


Inspect them with:

```bash
docker volume ls | grep recap
docker volume inspect <volume_name>
```

These volumes survive `docker compose down`. Only `docker compose down -v` wipes them.

## Recap (bash, one-shot)

```bash
cd chap22-mlflow-step-by-step-recap...

docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.4 --l1_ratio 0.4

# Open http://localhost:5000 and inspect the runs in experiment 'experiment_dual_format'.

docker compose down
```

## Recap (Windows PowerShell)

```powershell
cd chap22-mlflow-step-by-step-recap...

docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.4 --l1_ratio 0.4

# Open http://localhost:5000 and inspect the runs in experiment 'experiment_dual_format'.

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
3. The MLflow service is healthy: `docker compose ps` -> `mlflow-recap-22 ... healthy`.

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

**Next**: [chap23](../23-practical-work-mlflow-step-by-step-recap-mlflow-register-model-post-hoc-and-load-by-version.md) -- register an existing run's model **after the fact** with `mlflow.register_model(model_uri, name)` (so you don't have to decide at training time), then load it back deterministically by version with `mlflow.pyfunc.load_model(f"models:/<name>/<version>")`.