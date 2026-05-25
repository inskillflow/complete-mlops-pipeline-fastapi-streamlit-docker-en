# chap06 - Step-by-step recap: `create_experiment` with tags and a custom artifact location

The full lesson lives at [`../06-practical-work-mlflow-step-by-step-recap-create-experiment-with-tags-and-artifact-location.md`](../06-practical-work-mlflow-step-by-step-recap-create-experiment-with-tags-and-artifact-location.md).

> [!TIP]
> **Objectif du chap06 — Créer des expériences MLflow _programmatiquement_, avec tags et emplacement d'artefacts personnalisé.**
>
> Tu vas :
> 1. Remplacer le `mlflow.set_experiment("experiment_1")` implicite par un appel explicite à `mlflow.create_experiment(name, tags, artifact_location)`.
> 2. Attacher des **tags** (`version=v1`, `priority=p1`) à l'expérience dès sa création — utiles pour filtrer, organiser, faire du reporting.
> 3. Rediriger les artefacts vers un **nouveau volume nommé `myartifacts`** (au lieu du `/mlflow/mlruns` par défaut), monté sur **les deux services** pour que l'UI puisse les afficher.
> 4. Ajouter un flag CLI `--exp-name` qui te permet de **créer une nouvelle expérience par commande** : `docker compose run --rm trainer ... --exp-name demo_06_alt`.
> 5. Gérer proprement le cas "l'expérience existe déjà" avec un `try/except MlflowException` qui retombe sur `set_experiment` — le script reste **idempotent**.
>
> À la fin, tu sais structurer tes expériences MLflow comme un vrai projet (noms parlants, tags filtrables, artefacts au bon endroit), et tu comprends le mécanisme du **volume Docker partagé** indispensable pour que l'URI `file:///mlflow/myartifacts` reste résolvable côté UI.


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
This lab is where the trainer **stops relying on the default experiment** (`experiment_1` in chap05) and starts **creating its own experiments** -- with tags (`version`, `priority`) and a **custom artifact location** stored in a dedicated Docker volume (`myartifacts`). The first run of each new experiment goes through `mlflow.create_experiment(...)`; subsequent runs fall back to `mlflow.set_experiment(...)` thanks to a try/except.


## What's new vs chap05 - Programmatic experiment creation + tags + artifact_location

- `train.py` now uses `mlflow.create_experiment(name, tags, artifact_location)` instead of the implicit `set_experiment`
- New CLI flag `--exp-name` -> you can pick the experiment from the command line:
  ```bash
  docker compose run --rm trainer --alpha 0.4 --l1_ratio 0.4 --exp-name demo_06
  ```
- Tags `{"version": "v1", "priority": "p1"}` are attached to the experiment at creation time
- Artifacts of this experiment land in `/mlflow/myartifacts/` (a brand-new named volume) instead of `/mlflow/mlruns/`
- `myartifacts` is mounted on **both** services so the trainer can write and the MLflow server can read
- A try/except catches `MlflowException` (the experiment already exists) and falls back to `set_experiment(...)` -> the script stays idempotent

> ⚠️ **Chapter quirk.** The `artifact_location` URI points to a directory **inside the container** (`file:///mlflow/myartifacts`). That path is valid only because `myartifacts` is the same named volume on both services. If you ran the trainer outside Compose without that volume, the location would not resolve from the MLflow side.

---

# 1. Clone the project

```bash
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git
```

```bash
cd mlops-beginner-level-01-en/chap05-mlflow-step-by-step-recap-passing-tracking-uri-via-env-var
# done

cd ../chap06-mlflow-step-by-step-recap-create-experiment-with-tags-and-artifact-location
# start project #6
```

---

# 2. Stop any running containers first

## Method 1 — Stop containers from another project

```bash
cd other-project
docker compose down
```

## Method 2 — Use Docker Desktop

```text
1. Go to Containers
2. Find the running container (e.g. mlflow-recap-05)
3. Stop it
4. Delete it if necessary
```

---

# 3. Start project #6

You should now be inside:

```bash
chap06-mlflow-step-by-step-recap-create-experiment-with-tags-and-artifact-location
```

No `mkdir` needed -- everything lives in three named volumes: `mlflow-db`, `mlflow-artifacts`, `myartifacts`.

Start MLflow:

```bash
docker compose up -d --build mlflow
```

Verify:

```bash
docker compose ps
# mlflow-recap-06    Up X seconds (healthy)
```

Open:

```text
http://localhost:5000
```

The list of experiments may show `Default` only -- that is fine.

---

# 4. Run experiment 1

Use the chapter's default experiment name (`exp_create_exp_artifact`) and:

```text
alpha    = 0.1
l1_ratio = 0.1
```

Command:

```bash
docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
```

Expected console output (the **first** time):

```text
Tracking URI: http://mlflow:5000
Artifact location URI: file:///mlflow/myartifacts
Created experiment 'exp_create_exp_artifact' with id=1
Name              : exp_create_exp_artifact
Experiment_id     : 1
Artifact Location : file:///mlflow/myartifacts
Tags              : {'version': 'v1', 'priority': 'p1'}
Lifecycle_stage   : active
Creation timestamp: 17XXXXXXXXXXX
Elasticnet (alpha=0.100000, l1_ratio=0.100000):
  RMSE: 0.7460807474738669
  MAE:  0.5762786116981458
  R2:   0.2018715961101284
```

Refresh `http://localhost:5000`:

- Experiment `exp_create_exp_artifact` is now in the sidebar
- Its **Description** tab shows tags `version=v1`, `priority=p1`
- The run's **Artifacts** tab shows `model/` (the pickled ElasticNet)
- The run's **Overview** -> `Artifact Location` is `file:///mlflow/myartifacts/...` -> not the default `/mlflow/mlruns/`

---

# 5. Run experiment 2

Same experiment, different hyperparams:

```text
alpha    = 0.5
l1_ratio = 0.5
```

```bash
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
```

Expected console output (now the experiment already exists):

```text
Tracking URI: http://mlflow:5000
Artifact location URI: file:///mlflow/myartifacts
Experiment already exists: id=1 (RESOURCE_ALREADY_EXISTS)
Name              : exp_create_exp_artifact
...
```

The try/except in `train.py` made the script idempotent -- it falls back to `set_experiment` and reuses the existing experiment id.

---

# 6. Run experiment 3 in a brand new experiment

Use `--exp-name` to spawn a separate experiment with the same tags:

```bash
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1 --exp-name demo_06_alt
```

In the UI you now have **two** experiments side by side:

```text
exp_create_exp_artifact   (3 runs)
demo_06_alt               (1 run)
```

Both share the same `artifact_location` URI (the `myartifacts` volume).

---

# 7. Verify the artifact_location on disk

Enter the MLflow container:

```bash
docker compose exec mlflow bash
ls /mlflow/myartifacts/      # one folder per experiment: 1/, 2/, ...
ls /mlflow/myartifacts/1/    # one folder per run, each contains model/MLmodel + model.pkl
exit
```

Compare with the default location used by chap05:

```bash
docker compose exec mlflow bash
ls /mlflow/mlruns/           # the Default experiment lives here, but exp_create_exp_artifact does NOT
exit
```

This proves that `artifact_location` is honored: artifacts ended up where we asked, not in the default tree.

---

# 8. Stop the containers

```bash
docker compose down       # keep all three volumes
docker compose down -v    # wipe DB + mlflow-artifacts + myartifacts
```


## What ends up on your host

Three named Docker volumes are created the first time:

```text
mlflow-db          <- SQLite DB:        experiments, runs, registered models
mlflow-artifacts   <- default artifact root (the Default experiment lives here)
myartifacts        <- THIS chapter's custom artifact_location
```

Only the wine-quality CSV is mounted from the host (`./data:/code/data`).

---

## Why does the artifact_location URI work across containers?

The trick is the **shared named volume**:

```text
docker-compose.yml
    └─ volumes:
        myartifacts:                 <- declared once at the top
    └─ services.mlflow.volumes:
        - myartifacts:/mlflow/myartifacts   <- mounted on the MLflow server
    └─ services.trainer.volumes:
        - myartifacts:/mlflow/myartifacts   <- mounted on the trainer too

So when train.py writes to file:///mlflow/myartifacts, the file lands
in the named volume `myartifacts`, which is the same on disk for both
containers. The MLflow UI (running in the mlflow container) reads back
from the same path -> the link in the UI works.
```

Without this shared mount, the run would still be recorded in the DB but the **Artifacts** tab in the UI would 404 because the server cannot reach the file.

---

# Final command recap

```bash
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git

cd mlops-beginner-level-01-en/chap06-mlflow-step-by-step-recap-create-experiment-with-tags-and-artifact-location

docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1 --exp-name demo_06_alt

docker compose down
```

PowerShell version:

```powershell
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git

cd mlops-beginner-level-01-en/chap06-mlflow-step-by-step-recap-create-experiment-with-tags-and-artifact-location

docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1 --exp-name demo_06_alt

docker compose down
```

---

# To enter the trainer container manually

```bash
docker compose run --rm --entrypoint bash trainer
```

Inside:

```bash
env | grep MLFLOW
ls /mlflow/myartifacts          # writable from the trainer too
python train.py --alpha 0.3 --l1_ratio 0.3 --exp-name shell_test
exit
```

To enter the MLflow server container:

```bash
docker compose exec mlflow bash
ls /mlflow/database       # mlflow.db
ls /mlflow/mlruns         # default experiment data
ls /mlflow/myartifacts    # this chapter's artifact root
exit
```

---

# What happens if I forgot to mount `myartifacts` on the MLflow server?

If you removed this line from the `mlflow` service in `docker-compose.yml`:

```yaml
- myartifacts:/mlflow/myartifacts
```

The run still completes, the DB still records it, but in the UI the **Artifacts** tab is broken:

```text
Failed to list artifacts:
  file:///mlflow/myartifacts/1/<run_id>/artifacts not found
```

In simple words:

```text
The MLflow server received the artifact URI from the trainer,
but the directory does not exist on the server's filesystem
because the volume was mounted only on the trainer side.
The fix is to add the same line under the mlflow service.
```

---

# How to fix it

## Step 1 — Stop everything

```bash
docker compose down
```

## Step 2 — Add the volume on the MLflow service

Open `docker-compose.yml` and make sure the `mlflow` service has:

```yaml
volumes:
  - mlflow-db:/mlflow/database
  - mlflow-artifacts:/mlflow/mlruns
  - myartifacts:/mlflow/myartifacts   # this one is the new one
```

## Step 3 — Rebuild and rerun

```bash
docker compose up -d --build mlflow
docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
```

The **Artifacts** tab in the UI should now list `model/` and the `MLmodel` YAML file.

---

# Troubleshooting 1 : port 5000 already used ⚠️

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

Almost always: a previous chapter's `mlflow-recap-XX` container is still up. `cd` into that chapter and `docker compose down`.

---

# Troubleshooting 2 : docker Desktop not starting ⚠️

PowerShell **as Administrator**:

```powershell
Get-Process *docker* -ErrorAction SilentlyContinue | Stop-Process -Force
Stop-Service com.docker.service -Force -ErrorAction SilentlyContinue
wsl --shutdown
```

Wait **10–15 seconds**, then:

```powershell
Start-Service com.docker.service
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

Stronger version if it is still frozen:

```powershell
taskkill /F /IM "Docker Desktop.exe"
taskkill /F /IM "com.docker.backend.exe"
taskkill /F /IM "com.docker.service.exe"
taskkill /F /IM "dockerd.exe"
wsl --shutdown
```

---

# Troubleshooting 3 : `RESOURCE_ALREADY_EXISTS` on first run ⚠️

If the **first** run of a brand-new experiment prints:

```text
Experiment already exists: id=N (RESOURCE_ALREADY_EXISTS)
```

…it means the DB volume `mlflow-db` already contains that experiment name from a previous run of this chapter (the volume survives `docker compose down`). Two options:

1. Use a different `--exp-name`:
   ```bash
   docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1 --exp-name demo_06_fresh
   ```
2. Wipe the DB volume and start clean:
   ```bash
   docker compose down -v
   docker compose up -d --build mlflow
   docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
   ```
