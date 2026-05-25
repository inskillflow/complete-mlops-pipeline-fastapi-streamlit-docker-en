# chap05 - Step-by-step recap: passing the tracking URI via an environment variable

The full lesson lives at [`../05-practical-work-mlflow-step-by-step-recap-passing-tracking-uri-via-env-var.md`](../05-practical-work-mlflow-step-by-step-recap-passing-tracking-uri-via-env-var.md).

> [!TIP]
> **Objectif du chap05 — Réparer le bug de chap04 proprement, avec une variable d'environnement.**
>
> Tu vas :
> 1. Ajouter `MLFLOW_TRACKING_URI: "http://mlflow:5000"` dans le bloc `environment:` du service `trainer` dans `docker-compose.yml`.
> 2. Lire cette variable dans `train.py` avec `os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")` puis appeler `mlflow.set_tracking_uri(...)`.
> 3. Imprimer l'URI courante (`print("Tracking URI:", mlflow.get_tracking_uri())`) pour vérifier que la chaîne `compose → Docker → os.getenv → MLflow` fonctionne.
> 4. Relancer les trois runs (`0.1/0.1`, `0.5/0.5`, `0.9/0.1`) et **enfin les voir apparaître dans l'UI** sous l'expérience `experiment_1`.
> 5. Apprendre à **surcharger l'URI à la volée** : `docker compose run --rm -e MLFLOW_TRACKING_URI=... trainer ...`.
>
> À la fin, tu maîtrises le pattern de configuration **12-factor** (config via env vars, jamais en dur dans le code) — c'est la base de tout MLOps en production. C'est aussi le pattern utilisé partout dans la suite du cours (Postgres, S3, registry, etc.).


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
This lab is the **fix for chap04**. In chap04 the runs vanished because the trainer wrote them to `file:///code/mlruns` inside the container. Here we point the trainer at the MLflow server in a clean, repeatable way: via the `MLFLOW_TRACKING_URI` environment variable, set in `docker-compose.yml` and read in `train.py` with `os.getenv(...)`.


## What's new vs chap04 - The trainer now talks to the MLflow server

- `train.py` now contains:
  - `tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")`
  - `mlflow.set_tracking_uri(tracking_uri)`
  - `print("Tracking URI:", mlflow.get_tracking_uri())` -> visible in the trainer log
- `docker-compose.yml` declares the variable on the `trainer` service:
  ```yaml
  trainer:
    environment:
      MLFLOW_TRACKING_URI: "http://mlflow:5000"
  ```
- The runs finally appear in the MLflow UI at `http://localhost:5000`

> ⚠️ **Chapter quirk.** All runs land in a single experiment named `experiment_1` (created on the fly via `mlflow.set_experiment("experiment_1")`). chap06 introduces a CLI flag to choose the experiment name dynamically.

---

# 1. Clone the project

```bash
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git
```

Then enter the folders in order:

```bash
cd mlops-beginner-level-01-en/chap01-mlflow-step-by-step-recap-hello-mlflow-basics
# done
cd ../chap02-mlflow-step-by-step-recap-printing-the-tracking-uri
# done
cd ../chap03-mlflow-step-by-step-recap-elasticnet-on-red-wine-quality
# done
cd ../chap04-mlflow-step-by-step-recap-running-the-training-in-docker
# done

cd ../chap05-mlflow-step-by-step-recap-passing-tracking-uri-via-env-var
# start project #5
```

---

# 2. Stop any running containers first

Make sure that no other MLflow container holds port `5000`.

## Method 1 — Stop containers from another project

```bash
cd other-project
docker compose down
```

## Method 2 — Use Docker Desktop

```text
1. Go to Containers
2. Find the running container (e.g. mlflow-recap-04)
3. Stop it
4. Delete it if necessary
```

---

# 3. Start project #5

You should now be inside:

```bash
chap05-mlflow-step-by-step-recap-passing-tracking-uri-via-env-var
```

No `mkdir` needed -- MLflow data lives in named Docker volumes (`mlflow-db`, `mlflow-artifacts`).

Start MLflow:

```bash
docker compose up -d --build mlflow
```

- `-d` -> detached
- `--build` -> force rebuild if the Dockerfile or `requirements.txt` changed
- `mlflow` -> only the server (the trainer is launched on demand)

Verify:

```bash
docker compose ps
# mlflow-recap-05    Up X seconds (healthy)
```

Open:

```text
http://localhost:5000
```

---

# 4. Run experiment 1

Run the model with:

```text
alpha    = 0.1
l1_ratio = 0.1
```

Command:

```bash
docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
```

Expected console output (the **important** line is the first one):

```text
Tracking URI: http://mlflow:5000
Elasticnet model (alpha=0.100000, l1_ratio=0.100000):
  RMSE: 0.7460807474738669
  MAE:  0.5762786116981458
  R2:   0.2018715961101284
```

Now refresh:

```text
http://localhost:5000
```

You should see:

- Experiment `experiment_1`
- 1 run with params (`alpha=0.1`, `l1_ratio=0.1`), metrics (`rmse`, `mae`, `r2`) and an artifact `mymodel/`

If you still see the URI `file:///code/mlruns` -> see Troubleshooting 3.

---

# 5. Run experiment 2

Run the model with:

```text
alpha    = 0.5
l1_ratio = 0.5
```

```bash
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
```

The new run lands in the **same** experiment `experiment_1` (chap06 will fix that).

---

# 6. Run experiment 3

Run the model with:

```text
alpha    = 0.9
l1_ratio = 0.1
```

```bash
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1
```

After the three runs, the UI shows three rows under `experiment_1`, sortable by `rmse` / `r2` / `mae`. Click a row -> click **Artifacts** -> the `mymodel/` folder is browsable (this is the artifact the chapter delivers).

---

# 7. Override the URI at the command line (optional)

The env var on the compose service is the **default**. You can override it for one run:

```bash
docker compose run --rm \
  -e MLFLOW_TRACKING_URI=http://mlflow:5000 \
  trainer --alpha 0.3 --l1_ratio 0.7
```

PowerShell version (one line):

```powershell
docker compose run --rm -e MLFLOW_TRACKING_URI=http://mlflow:5000 trainer --alpha 0.3 --l1_ratio 0.7
```

`-e` injects the variable for **this** one-shot container only, overriding what is in `docker-compose.yml`.

---

# 8. Stop the containers

```bash
docker compose down       # keep the volumes (DB + artifacts survive)
docker compose down -v    # wipe everything (DB + artifacts + named volumes)
```


## What ends up on your host

Named Docker volumes (auto-created the first time you `up`):

```text
mlflow-db          <- SQLite DB:        experiments, runs, registered models
mlflow-artifacts   <- pickled models, signatures, plots
```

Inspect:

```bash
docker volume ls | grep recap
docker volume inspect mlflow-db
docker volume inspect mlflow-artifacts
```

The only host bind mount is `./data:/code/data` (the wine-quality CSV).

---

## Why does `os.getenv(...)` + `mlflow.set_tracking_uri(...)` work?

The chain looks like this:

```text
docker-compose.yml
    └─ trainer.environment.MLFLOW_TRACKING_URI = "http://mlflow:5000"
        └─ Docker injects it into the trainer container at boot
            └─ os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
                └─ mlflow.set_tracking_uri(...)
                    └─ all subsequent mlflow.log_param/metric/model calls
                       go to http://mlflow:5000 inside the recap-net network
```

- `mlflow` (the hostname) resolves on the `recap-net` bridge network because both services declare `networks: [recap-net]` in compose.
- The fallback `"http://mlflow:5000"` in `os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")` is there so the script also works when launched **outside** Compose with the right `--network` flag.

---

# Final command recap

```bash
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git

cd mlops-beginner-level-01-en/chap05-mlflow-step-by-step-recap-passing-tracking-uri-via-env-var

docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1

docker compose down
```

PowerShell version:

```powershell
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git

cd mlops-beginner-level-01-en/chap05-mlflow-step-by-step-recap-passing-tracking-uri-via-env-var

docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1

docker compose down
```

---

# To enter the trainer container manually

```bash
docker compose run --rm --entrypoint bash trainer
```

Inside:

```bash
env | grep MLFLOW            # MLFLOW_TRACKING_URI=http://mlflow:5000
python -c "import mlflow; print(mlflow.get_tracking_uri())"  # http://mlflow:5000
python train.py --alpha 0.5 --l1_ratio 0.5
exit
```

Quickly check connectivity from the trainer to the MLflow server:

```bash
docker compose run --rm --entrypoint bash trainer
python -c "import urllib.request; print(urllib.request.urlopen('http://mlflow:5000').status)"  # 200
exit
```

To enter the MLflow server container:

```bash
docker compose exec mlflow bash
ls /mlflow/database     # mlflow.db
ls /mlflow/mlruns       # 1/, 2/, ...   <- one folder per experiment
exit
```

---

# What happens if I forgot to set the env var?

If you delete the `MLFLOW_TRACKING_URI:` line from `docker-compose.yml` AND remove the fallback in `os.getenv("...", "http://mlflow:5000")`, the run falls back to `file:///code/mlruns` inside the container -- exactly the chap04 bug.

Diagnose by re-running with the `-e` override:

```bash
docker compose run --rm -e MLFLOW_TRACKING_URI=http://mlflow:5000 trainer --alpha 0.1 --l1_ratio 0.1
```

If that single run shows up in the UI but the normal one does not, the env var was missing.

---

# How to fix it

## Step 1 — Stop the containers

```bash
docker compose down
```

## Step 2 — Verify the env var is in `docker-compose.yml`

The trainer service must contain:

```yaml
trainer:
  environment:
    MLFLOW_TRACKING_URI: "http://mlflow:5000"
```

## Step 3 — Rebuild and retry

```bash
docker compose up -d --build mlflow
docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
```

The first line printed by the trainer should be:

```text
Tracking URI: http://mlflow:5000
```

If you see `file:///code/mlruns` -> the env var did not make it through Compose. Re-check indentation in `docker-compose.yml` (YAML is whitespace-sensitive).

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

# Troubleshooting 3 : trainer still says `Tracking URI: file:///code/mlruns` ⚠️

This is the chap04 bug coming back. Three checks:

1. **Compose injection** -> the trainer log first line must be `Tracking URI: http://mlflow:5000`. If it says `file:///code/mlruns`, the env var is not making it in:
   ```bash
   docker compose run --rm --entrypoint bash trainer
   env | grep MLFLOW
   exit
   ```
   If `env | grep MLFLOW` is empty, the `environment:` block in `docker-compose.yml` is missing or mis-indented.

2. **MLflow service is up and healthy** -> in chap05 the trainer depends on `mlflow` being `service_healthy`, so this should be enforced, but verify:
   ```bash
   docker compose ps
   # mlflow-recap-05    Up X seconds (healthy)
   ```

3. **Manual override** -> bypass compose injection to confirm:
   ```bash
   docker compose run --rm -e MLFLOW_TRACKING_URI=http://mlflow:5000 trainer --alpha 0.4 --l1_ratio 0.4
   ```
   If that one run lands in the UI, the env var system works -- the problem is your `docker-compose.yml`, not the code.
