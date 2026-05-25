# chap04 - Step-by-step recap: running the training inside a second Docker service (with `requirements.txt`)

The full lesson lives at [`../04-practical-work-mlflow-step-by-step-recap-running-the-training-in-a-second-docker-service-with-requirements-txt.md`](../04-practical-work-mlflow-step-by-step-recap-running-the-training-in-a-second-docker-service-with-requirements-txt.md).

> [!TIP]
> **Objectif du chap04 — Séparer le code d'entraînement du serveur MLflow.**
>
> Tu vas :
> 1. Créer un **deuxième service Docker** (`trainer`) avec son propre `Dockerfile` et son propre `requirements.txt` (`scikit-learn`, `pandas`, `numpy`, `mlflow`).
> 2. Connecter les deux services (`mlflow` et `trainer`) via un réseau Docker partagé `recap-net`.
> 3. Remplacer les bind mounts `./database/` et `./mlruns/` par des **volumes Docker nommés** (`mlflow-db`, `mlflow-artifacts`) — plus besoin de `mkdir` avant de démarrer.
> 4. Lancer l'entraînement avec `docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1` au lieu de `docker compose exec mlflow python ...`.
> 5. **Observer un bug volontaire** : sans `set_tracking_uri`, les runs disparaissent dans le conteneur et **n'apparaissent pas dans l'UI**.
>
> À la fin, tu comprends le pattern multi-services `mlflow + trainer`, la différence entre `exec` (attacher) et `run --rm` (one-shot), et tu vois _pourquoi_ MLflow a besoin qu'on lui dise explicitement où écrire — ce que chap05 va corriger avec une variable d'environnement.

## Before you start — Create the host folders!

> [!IMPORTANT]
> **You MUST create the local folders `database/` and `mlruns/` BEFORE the first `docker compose up`.**
>
> This chapter's `docker-compose.yml` uses **bind mounts** (host folders mapped INTO the container), not anonymous Docker volumes. If the host folders don't exist, Docker will silently create them as **empty root-owned directories** that are hard to inspect or clean up from your editor on Windows.
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
> The third mount (`.:/work`) plus `working_dir: /work` is what makes **Docker Desktop → Containers → `mlflow-recap-04` → Exec → `ls`** show all your project files. Without it, `exec` would drop you in `/mlflow/` and you'd see nothing useful. `working_dir:` is a Docker Compose directive that sets the default cwd for `RUN`, `CMD` and any `docker compose exec` — think of it as `cd /work` baked into the container.

## chap04 = bug-by-design! Read this BEFORE running anything

> [!WARNING]
> **This chapter intentionally has a bug.** `train.py` does NOT call `mlflow.set_tracking_uri(...)`, so by default runs are written to `file:///code/mlruns` INSIDE the `trainer` container, then wiped by `--rm`. **chap05 fixes this** properly with the `MLFLOW_TRACKING_URI` env var. To deal with this RIGHT NOW you have **two options**: stick with the default `docker-compose.yml` and use the workaround command, OR switch to `docker-compose-option2.yml` where the env var is already wired.

## Option 1 — default `docker-compose.yml` (the bug stays)

> [!IMPORTANT]
> With the default `docker-compose.yml` of this chapter, **the standard `docker compose run --rm trainer ...` will NOT put your runs in the UI**. Only ONE command actually pushes runs to the MLflow server — the one that injects the env var on the fly:
>
> ### ✅ ONLY this command works with the default `docker-compose.yml`
> ```bash
> docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1
> ```
> Why it works: MLflow's Python client automatically reads the `MLFLOW_TRACKING_URI` environment variable. We're running INSIDE the `mlflow` container, so `localhost:5000` is the server itself. The runs land in `mlflow.db` + `./mlruns/` and show up in the UI.
>
> ### ❌ These two will silently fail (no run in the UI)
> ```bash
> docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1          # writes to /code/mlruns inside trainer, then --rm wipes it
> docker compose exec mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1   # writes to /work/mlruns, UI still has no clue
> ```
> They fail because the trainer image has no `MLFLOW_TRACKING_URI` set, and `train.py` does not call `set_tracking_uri()`. The client falls back to `file:///...` and the MLflow server never sees the runs.

## Option 2 — alternative `docker-compose-option2.yml` (the standard command works)

> [!NOTE]
> If you want `docker compose run --rm trainer ...` to **just work** in chap04 without modifying `train.py`, use the alternative compose file shipped in this chapter: `docker-compose-option2.yml`. The only difference vs the default file is one line:
> ```yaml
> trainer:
>   environment:
>     MLFLOW_TRACKING_URI: "http://mlflow:5000"   # <-- the ONLY difference
> ```
> Same idea as before: MLflow's client picks up the env var automatically, so we don't need to touch `train.py`.
>
> ### Tear down the default stack first (so the same container names get freed)
> ```bash
> docker compose down
> ```
>
> ### Then bring up the Option 2 stack with the `-f` flag
> ```bash
> docker compose -f docker-compose-option2.yml up -d --build
> docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.1 --l1_ratio 0.1
> docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.5 --l1_ratio 0.5
> docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.9 --l1_ratio 0.1
> docker compose -f docker-compose-option2.yml down
> ```
> All three runs now appear in the UI at <http://localhost:5000>. The `docker compose exec mlflow python trainer/train.py ...` command also works without the `-e` flag here, because the env var is already on the trainer service (but `exec` is on the `mlflow` service, so for `exec` you still need to pass `-e` — see Option 1).

## TL;DR which command should I use?

| If you are running...                                                                 | Use this command                                                                                                                          | Runs in the UI? |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| default `docker-compose.yml`                                                           | `docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1`              | ✅ yes          |
| default `docker-compose.yml`                                                           | `docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1`                                                                              | ❌ no (bug)     |
| default `docker-compose.yml`                                                           | `docker compose exec mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1`                                                           | ❌ no (bug)     |
| `docker-compose-option2.yml` (`-f` flag!)                                              | `docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.1 --l1_ratio 0.1`                                                | ✅ yes          |
| `docker-compose-option2.yml` (`-f` flag!)                                              | `docker compose -f docker-compose-option2.yml exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py ...`       | ✅ yes          |


This lab shows how to move the training script **out of the MLflow container** and into its own dedicated `trainer` service. From now on every chapter uses the same two-service skeleton: `mlflow` (the tracking server) + `trainer` (the one-shot Python image that runs `train.py`).


## What's new vs chap03 - Containerised trainer with its own `requirements.txt`

- New `trainer/` folder with its **own** `Dockerfile`, `requirements.txt`, and `train.py` (separate from the MLflow server image)
- `docker-compose.yml` gains a second service `trainer` on a shared `recap-net` network
- `ENTRYPOINT ["python", "train.py"]` in the trainer image -> CLI args flow through `docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1`
- `./data:/code/data` bind mount so you can edit the CSV without rebuilding
- Same host bind mounts as chap01-03 (`./database`, `./mlruns`, `.:/work`) so you can still `docker compose exec mlflow ls` from Docker Desktop and see the whole project

> ⚠️ **Chapter quirk.** `train.py` deliberately does NOT call `mlflow.set_tracking_uri(...)`. The runs end up in `file:///code/mlruns` **inside the trainer container** and are wiped by `--rm`. This is the "bug-by-design" that **chap05** fixes via the `MLFLOW_TRACKING_URI` environment variable.

---

# 1. Clone the project

```bash
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git
```

Then enter the project folders in order:

```bash
cd mlops-beginner-level-01-en/chap01-mlflow-step-by-step-recap-hello-mlflow-basics
# done

cd ../chap02-mlflow-step-by-step-recap-printing-the-tracking-uri
# done

cd ../chap03-mlflow-step-by-step-recap-elasticnet-on-red-wine-quality
# done

cd ../chap04-mlflow-step-by-step-recap-running-the-training-in-docker
# start project #4
```

---

# 2. Stop any running containers first

Before starting this lab, make sure that no other MLflow container is already running on port `5000`.

## Method 1 — Stop containers from another project

Go to the other project folder:

```bash
cd other-project
docker compose down
```

This stops and removes the containers created by that project.

---

## Method 2 — Use Docker Desktop

You can also open **Docker Desktop** and manually:

```text
1. Go to Containers
2. Find the running container
3. Stop it
4. Delete it if necessary
```

This is useful if you do not remember which folder started the container.

---

# 3. Start project #4

You should now be inside this folder:

```bash
chap04-mlflow-step-by-step-recap-running-the-training-in-docker
```

This chapter uses **bind mounts** to host folders (same pattern as chap01-03), so the MLflow server can read/write to your local `./database/` and `./mlruns/` -> you can see everything from your file explorer AND from Docker Desktop -> Exec -> `ls`.

If the two folders do not exist yet, create them first:

```bash
mkdir database mlruns       # bash / Git Bash / WSL
```

```powershell
New-Item -ItemType Directory database, mlruns -Force | Out-Null   # PowerShell
```

> [!IMPORTANT]
> Without these two folders on the host **before** `docker compose up`, Docker creates them as **root-owned** empty folders inside the container and writes the SQLite DB there -> permission errors on Linux/WSL. On Windows Docker Desktop it usually works but creates `database` and `mlruns` automatically with possibly weird permissions.

Start the MLflow server in the background:

```bash
docker compose up -d --build mlflow
```

- `-d` runs the server detached so this terminal stays free for the trainer.
- `--build` forces a rebuild if any `Dockerfile` or `requirements.txt` changed.
- `mlflow` (the last word) is the service name -> we start ONLY the MLflow server, not the trainer (the trainer is a one-shot service).

Verify it is healthy:

```bash
docker compose ps
# mlflow-recap-04    Up X seconds (healthy)
```

Open the MLflow UI:

```text
http://localhost:5000
```

At this point, the UI may be empty or may only show the default experiment. This is normal.

---

# 4. Run experiment 1

Run the model with:

```text
alpha    = 0.1
l1_ratio = 0.1
```

You can launch the training **two equivalent ways**:

### Way A -- canonical chap04 (one-shot `trainer` container)

```bash
docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
```

| Token | Meaning |
|---|---|
| `docker compose run` | Spawn a one-off container of the requested service. |
| `--rm` | Delete the container as soon as the script returns (no zombie containers). |
| `trainer` | Which service to run. |
| `--alpha 0.1 --l1_ratio 0.1` | These tokens are appended to the `ENTRYPOINT`, so the container actually runs `python train.py --alpha 0.1 --l1_ratio 0.1`. |

### Way B -- via `docker compose exec` inside the running `mlflow` container

```bash
docker compose exec mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1
```

Same script, but launched **inside the mlflow server container** (which has `scikit-learn`, `pandas`, `numpy` installed as transitive deps of `mlflow==2.16.2`).

Then check:

```text
http://localhost:5000
```

> ⚠️ **Surprise:** the UI is still empty whichever way you launched it. The script does NOT call `set_tracking_uri(...)` and no `MLFLOW_TRACKING_URI` env var is set, so MLflow falls back to `file:///...mlruns` inside whichever container ran it. **chap05 fixes this for Way A; the `-e MLFLOW_TRACKING_URI=...` flag below fixes it for Way B.**

### Way B-fixed -- with the env var override

```bash
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow \
  python trainer/train.py --alpha 0.1 --l1_ratio 0.1
```

This time the run appears in the UI under `experiment_1`.

---

# 5. Run experiment 2

Run the model with:

```text
alpha    = 0.5
l1_ratio = 0.5
```

```bash
# Way A (chap04 canonical, bug-by-design):
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5

# Way B (run via exec, bug too):
docker compose exec mlflow python trainer/train.py --alpha 0.5 --l1_ratio 0.5

# Way B-fixed (run in UI):
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow \
  python trainer/train.py --alpha 0.5 --l1_ratio 0.5
```

---

# 6. Run experiment 3

Run the model with:

```text
alpha    = 0.9
l1_ratio = 0.1
```

```bash
# Way A:
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1

# Way B-fixed:
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow \
  python trainer/train.py --alpha 0.9 --l1_ratio 0.1
```

---

# 7. Where did my runs go?

To convince yourself the runs really exist (just in the wrong place), run **without** `--rm` once and look inside the stopped container:

```bash
docker compose run trainer --alpha 0.5 --l1_ratio 0.5
docker ps -a | grep trainer-recap-04   # find the stopped container id
docker exec -it <container_id> ls /code/mlruns/   # -> meta.yaml, 0/, 1/, ...
```

The runs are there -- but inside a dead container that nobody is reading.

---

# 8. Stop the containers

When you are finished:

```bash
docker compose down       # keep volumes (DB + artifacts survive)
docker compose down -v    # wipe everything (DB + artifacts + named volumes)
```


## What ends up on your host

This chapter populates **host folders** (bind mounts, same as chap01-03):

```text
chap04-mlflow-step-by-step-recap-running-the-training-in-docker/
├── database/
│   └── mlflow.db          <- SQLite metadata DB (created when the server starts)
├── mlruns/                <- empty until a run actually reaches the server
│   └── (no runs yet -- this is the chap04 bug-by-design, see section "Where did my runs go?")
├── data/
│   └── red-wine-quality.csv
├── mlflow/                <- Dockerfile for the MLflow server image
├── trainer/               <- Dockerfile + requirements.txt + train.py for the trainer image
├── docker-compose.yml
└── README.md
```

Inspect from your host with `ls -la database/ mlruns/` (bash) or `dir database, mlruns` (PowerShell).

Wipe with `rm -rf database/* mlruns/*` (bash) — `database/.gitkeep` and `mlruns/.gitkeep` keep the folders in git.

---

## ⚠️ Important warning — the runs are NOT in the MLflow UI

⚠️ Be careful: with this chapter's `train.py` (no `set_tracking_uri`, no `MLFLOW_TRACKING_URI` env var), MLflow falls back to the default `file:./mlruns/` **inside the trainer container**.

You may open the MLflow UI at:

```text
http://localhost:5000
````

but you will **NOT** see your runs, metrics, parameters, or artifacts.

Three ways to fix this -- the lesson explains all three, and **chap05 implements the production one**:

1. Add `mlflow.set_tracking_uri("http://mlflow:5000")` in `train.py` (works but hard-codes a hostname).
2. Read the URI from `os.getenv("MLFLOW_TRACKING_URI", "...")` and pass it via Docker (the **clean** way -> chap05).
3. Set `MLFLOW_TRACKING_URI` directly in `docker-compose.yml` so MLflow picks it up automatically (no `set_tracking_uri` line needed at all).

---

# Final command recap

### Way A -- chap04 canonical (one-shot `trainer`, demonstrates the bug)

```bash
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git

cd mlops-beginner-level-01-en/chap04-mlflow-step-by-step-recap-running-the-training-in-docker

mkdir database mlruns                               # bash / Git Bash / WSL
docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1

docker compose down
```

PowerShell version:

```powershell
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git

cd mlops-beginner-level-01-en/chap04-mlflow-step-by-step-recap-running-the-training-in-docker

New-Item -ItemType Directory database, mlruns -Force | Out-Null
docker compose up -d --build mlflow

docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1

docker compose down
```

### Way B -- via `docker compose exec` inside the mlflow container (Docker Desktop friendly)

```bash
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git

cd mlops-beginner-level-01-en/chap04-mlflow-step-by-step-recap-running-the-training-in-docker

mkdir database mlruns
docker compose up -d --build mlflow

# Without the env var override -> bug (run vanishes from UI):
docker compose exec mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1

# With the env var override -> run appears in UI:
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.5 --l1_ratio 0.5
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.9 --l1_ratio 0.1

docker compose down
```

PowerShell version (one line each):

```powershell
git clone https://github.com/inskillflow/mlops-beginner-level-01-en.git

cd mlops-beginner-level-01-en/chap04-mlflow-step-by-step-recap-running-the-training-in-docker

New-Item -ItemType Directory database, mlruns -Force | Out-Null
docker compose up -d --build mlflow

docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.5 --l1_ratio 0.5
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.9 --l1_ratio 0.1

docker compose down
```

---

# To enter the trainer container manually

The `ENTRYPOINT ["python", "train.py"]` runs the script immediately. To get a shell instead (for `ls`, `env | grep MLFLOW`, manual `python` calls), override the entrypoint:

```bash
docker compose run --rm --entrypoint bash trainer
```

Inside the container:

```bash
ls
cat train.py
env | grep MLFLOW
python train.py --alpha 0.5 --l1_ratio 0.5
exit
```

To enter the MLflow server container instead:

```bash
docker compose exec mlflow bash
# inside:
ls /mlflow
ls /mlflow/mlruns
exit
```

`exec` (not `run`) is the right tool here because the MLflow server is already running -- you attach to it instead of spawning a new container.

---

# From Docker Desktop -> Exec, what can I see and what can I run? ⚠️

Open Docker Desktop -> Containers -> `mlflow-recap-04` -> Exec tab. Type:

```bash
ls          # -> database  mlruns  trainer  mlflow  data  docker-compose.yml  README.md ...
pwd         # -> /work     (because of working_dir: /work in docker-compose.yml)
```

You can:

- Browse the whole project (everything under `/work` is the host folder of this chapter)
- `cd /mlflow && ls database/` to see the SQLite DB and confirm where the server writes
- Run `mlflow experiments search` (since the `mlflow` CLI is installed in this image)
- Run **any** training script — the `mlflow==2.16.2` install brings `scikit-learn`, `pandas` and `numpy` as transitive deps, so `import sklearn`, `import pandas`, `import numpy` all work in the `mlflow` container too

---

# Running the training via `docker compose exec` (alternative to `docker compose run --rm trainer`)

Two ways to launch a training in chap04:

## Way 1 -- the chap04 canonical command (one-shot `trainer` container)

```bash
docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1
```

> [!WARNING]
> The `trainer` service has **no `MLFLOW_TRACKING_URI`** environment variable in chap04 (this is the bug-by-design). Runs end up in `file:///code/mlruns` inside the trainer container and are wiped by `--rm`. You will see **nothing** in the MLflow UI. chap05 fixes this.

## Way 2 -- run the same script via `docker compose exec mlflow` (Docker Desktop friendly)

The `mlflow` server container also has `scikit-learn` + `pandas` + `numpy` installed (transitive deps of `mlflow`). So you can run the trainer script **directly inside the mlflow container**, as long as you tell it where the server is via the `-e` flag:

```bash
# Same chap04 bug -- run vanishes from the UI:
docker compose exec mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1

# Fixed version -- inject MLFLOW_TRACKING_URI=http://localhost:5000 at exec time:
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow \
  python trainer/train.py --alpha 0.1 --l1_ratio 0.1

docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow \
  python trainer/train.py --alpha 0.5 --l1_ratio 0.5

docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow \
  python trainer/train.py --alpha 0.9 --l1_ratio 0.1
```

PowerShell version (one line each):

```powershell
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.1 --l1_ratio 0.1
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.5 --l1_ratio 0.5
docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.9 --l1_ratio 0.1
```

Why `http://localhost:5000` and not `http://mlflow:5000`? Because **`docker compose exec mlflow ...` runs INSIDE the mlflow container**, so the MLflow server is reachable on `localhost` (same container) -- you do NOT need the Docker DNS hostname.

> [!NOTE]
> `-e MLFLOW_TRACKING_URI=http://localhost:5000` for the exec is functionally the same fix that chap05 will apply permanently to the `trainer` service (via `docker-compose.yml`).

## Side-by-side comparison

| Command | Where does Python run? | URI used | Run in UI? |
|---|---|---|---|
| `docker compose run --rm trainer --alpha 0.1` | inside `trainer` container | `file:///code/mlruns` (default) | ❌ no -- bug-by-design |
| `docker compose exec mlflow python trainer/train.py --alpha 0.1` | inside `mlflow` container | `file:///work/mlruns` (default) | ❌ no -- same bug, different path |
| `docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py --alpha 0.1` | inside `mlflow` container | `http://localhost:5000` | ✅ YES |
| `docker compose run --rm -e MLFLOW_TRACKING_URI=http://mlflow:5000 trainer --alpha 0.1` | inside `trainer` container | `http://mlflow:5000` | ✅ YES |

---

# Why `docker compose run --rm` and not `docker compose exec`?

You may see this command in older docs:

```bash
docker compose exec mlflow python train.py --alpha 0.1 --l1_ratio 0.1
```

This **runs the script INSIDE the MLflow server container**, which works in chap01-03 because the MLflow image happens to have `scikit-learn` installed by accident. From chap04 onward, the MLflow image is intentionally minimal (only `mlflow`), and the heavy training deps live in the `trainer` image. So:

## Recommended version ⚠️⚠️ :

```bash
docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
```

This:

1. Uses the **right image** (trainer, with `scikit-learn` + `pandas` + `numpy`).
2. Forwards CLI args through `ENTRYPOINT` -> clean.
3. `--rm` deletes the one-shot container -> no garbage piling up.

If something goes wrong, the error appears immediately in the console !!!!

---

# What happens if I forgot `--build`?

If you skip `--build` the first time, Docker tries to use a cached image that may not exist yet, and the build fails. Symptoms:

```text
Error response from daemon: pull access denied for mlops/trainer-recap, repository does not exist
Image not found locally
manifest unknown
```

In simple words:

```text
Docker tried to pull mlops/trainer-recap:latest from a public registry,
but that image only exists locally -- we are about to build it ourselves.
The fix is to ask Docker to build it: docker compose up -d --build mlflow
                                                                ^^^^^^^
```

---

# How to fix it

## Step 1 — Stop the containers

```bash
docker compose down
```

## Step 2 — Force a rebuild of both images

```bash
docker compose up -d --build mlflow
```

The `--build` option forces Docker to rebuild the image.

This is useful when:

```text
the Dockerfile changed
dependencies changed (requirements.txt)
the environment needs to be refreshed
the previous container was created incorrectly
```

## Step 3 — Run the trainer again

```bash
docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
```

If the build still fails, prune Docker's build cache and retry:

```bash
docker compose down -v
docker builder prune -af
docker compose up -d --build mlflow
```

---

# Troubleshooting 1 : port 5000 already used ⚠️

On Windows CMD:

```bat
netstat -ano | findstr :5000
tasklist | findstr 12345
taskkill /PID 12345 /F
```

On PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 5000
Stop-Process -Id 12345 -Force
```

Replace `12345` with the PID shown by the command.

Simple explanation:

Port `5000` is like a door. If another application is already using this door, MLflow cannot start on the same port. You must either stop the other application or change the port used by MLflow.

The most common culprit in this course is a **previous chapter** you forgot to tear down. Always run `docker compose down` in the previous chapter folder before starting a new one.

---

# Troubleshooting 2 : docker Desktop not starting ⚠️

Open **PowerShell as Administrator**, then run this:

```powershell
# 1. Stop Docker Desktop processes
Get-Process *docker* -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Stop Docker Desktop service
Stop-Service com.docker.service -Force -ErrorAction SilentlyContinue

# 3. Force-stop WSL backend used by Docker
wsl --shutdown
```

Then wait **10–15 seconds**.

To restart Docker Desktop:

```powershell
Start-Service com.docker.service
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

If it is still frozen, use the stronger version:

```powershell
taskkill /F /IM "Docker Desktop.exe"
taskkill /F /IM "com.docker.backend.exe"
taskkill /F /IM "com.docker.service.exe"
taskkill /F /IM "dockerd.exe"
wsl --shutdown
```

Then restart Docker Desktop manually from the Start menu.

Do **not** delete Docker folders yet. First try force stop + `wsl --shutdown`.

---

# Troubleshooting 3 : trainer says `Tracking URI: file:///code/mlruns` ⚠️

That message is **expected** in chap04 -- it is the very bug we leave on purpose. From chap05 onward, the `MLFLOW_TRACKING_URI` env var on the trainer service fixes it.

If you still see it from chap05 onward, three places to check:

1. `docker-compose.yml` -> trainer -> `environment: MLFLOW_TRACKING_URI:` is present.
2. You launched via `docker compose run --rm trainer ...` (not `docker run` directly, which bypasses Compose env injection).
3. The MLflow service is healthy: `docker compose ps` -> `mlflow-recap-04 ... healthy`.

Override at runtime if needed:

```bash
docker compose run --rm -e MLFLOW_TRACKING_URI=http://mlflow:5000 trainer --alpha 0.4 --l1_ratio 0.4
```
