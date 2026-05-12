# Évolution du cours — de `chap01` à `chap26b`

> Ce document est la **carte du voyage MLflow**. Il décrit, chapitre par chapitre, ce qui change vs le chapitre précédent (code, `docker-compose.yml`, image Docker, dépendances) et regroupe les chapitres en **9 phases pédagogiques**. Tous les diagrammes sont en Mermaid (rendus nativement par GitHub).

---

## Vue d'ensemble — la trajectoire complète en un seul diagramme

```mermaid
flowchart TB
    subgraph P1["Phase 1 — Fondations"]
        direction LR
        c01[chap01<br/>Hello MLflow] --> c02[chap02<br/>set_tracking_uri] --> c03[chap03<br/>ElasticNet pipeline]
    end

    subgraph P2["Phase 2 — Docker multi-services"]
        direction LR
        c04[chap04<br/>+ trainer service<br/>BUG-BY-DESIGN] --> c05[chap05<br/>+ MLFLOW_TRACKING_URI<br/>env var fix]
    end

    subgraph P3["Phase 3 — Logging avancé"]
        direction LR
        c06[chap06<br/>create_experiment<br/>+ tags + artifact_loc] --> c07[chap07<br/>start_run / end_run<br/>active_run] --> c08[chap08<br/>log_artifacts<br/>+ bulk log_*] --> c09[chap09<br/>set_tags metadata]
    end

    subgraph P4["Phase 4 — Multi-runs / multi-experiments"]
        direction LR
        c10[chap10<br/>helper + for loop<br/>3 runs / 1 exp] --> c11[chap11<br/>ElasticNet/Ridge/Lasso<br/>3 expériences] --> c12[chap12<br/>autolog]
    end

    subgraph P5["Phase 5 — Production"]
        direction LR
        c13[chap13<br/>Postgres backend<br/>+ S3 artifacts]
    end

    subgraph P6["Phase 6 — Model packaging"]
        direction LR
        c14[chap14<br/>infer_signature] --> c15[chap15<br/>Schema + ColSpec] --> c16[chap16<br/>PyFunc wrapper<br/>+ conda env] --> c17[chap17<br/>load_model<br/>+ predict]
    end

    subgraph P7["Phase 7 — Évaluation"]
        direction LR
        c18[chap18<br/>mlflow.evaluate] --> c19[chap19<br/>custom metrics<br/>+ scatter artifact] --> c20[chap20<br/>thresholds<br/>+ DummyRegressor]
    end

    subgraph P8["Phase 8 — Model Registry"]
        direction LR
        c21[chap21<br/>registered_model_name] --> c22[chap22<br/>log_model + pickle.dump] --> c23[chap23<br/>register_model post-hoc<br/>+ load by version] --> c24[chap24<br/>pretrainer + registrar<br/>cloudpickle import]
    end

    subgraph P9["Phase 9 — MLflow Projects / CLI"]
        direction LR
        c25[chap25<br/>with start_run<br/>+ main] --> c26[chap26<br/>MLproject<br/>+ entry_points] --> c26b[chap26b<br/>MLflow CLI<br/>doctor/artifacts/exp/runs]
    end

    P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> P7 --> P8 --> P9

    style c04 fill:#ffd4d4
    style c05 fill:#d4ffd4
    style c13 fill:#fff4d4
    style c16 fill:#d4e4ff
    style c24 fill:#fff4d4
```

**Légende des couleurs :** rouge = bug pédagogique ; vert = fix officiel ; jaune = topologie de production / cas industriel ; bleu = packaging avancé.

---

## Évolution de l'architecture Docker

Voici comment la pile Docker grossit au fil des chapitres :

```mermaid
flowchart TB
    subgraph A["chap01-03 — 1 service"]
        direction LR
        A1["mlflow<br/>(server + script local)"]
    end

    subgraph B["chap04-12 — 2 services"]
        direction LR
        B1[mlflow] -- recap-net --> B2[trainer]
    end

    subgraph C["chap13 — 3 services (production)"]
        direction LR
        C1[mlflow] -- recap-net --> C2[trainer]
        C1 -- recap-net --> C3[(postgres<br/>backend store)]
    end

    subgraph D["chap24 — pretrainer + registrar"]
        direction LR
        D1[mlflow] -- recap-net --> D3[registrar]
        D2[pretrainer] -. shared volume .-> D3
    end

    subgraph E["chap26 — projets MLflow (sans trainer Docker)"]
        direction LR
        E1[mlflow server] -.->|CLI mlflow run| E2["host Python<br/>(MLproject + conda)"]
    end

    subgraph F["chap26b — + service cli"]
        direction LR
        F1[mlflow] -- recap-net --> F2[trainer]
        F1 -- recap-net --> F3["cli<br/>(mlflow doctor/artifacts/...)"]
    end

    A --> B --> C
    B --> D
    B --> E
    B --> F
```

---

## Phase 1 — Fondations (chap01 → chap03)

> **Objectif de la phase.** Installer MLflow, comprendre la notion de **tracking URI**, et écrire un premier vrai pipeline ML (ElasticNet sur le red wine quality dataset).

```mermaid
flowchart LR
    c01["chap01<br/><b>Hello MLflow</b><br/>print + serveur"] -->|"+ set_tracking_uri()<br/>+ get_tracking_uri()"| c02["chap02<br/><b>Print tracking URI</b>"]
    c02 -->|"+ pandas/sklearn<br/>+ ElasticNet<br/>+ log_param/metric/model<br/>+ argparse alpha/l1_ratio"| c03["chap03<br/><b>ElasticNet pipeline</b>"]
```

| Chapitre  | Ce qui est nouveau                                                                                              |
| --------- | --------------------------------------------------------------------------------------------------------------- |
| `chap01`  | `mlflow server` lancé dans Docker ; un script `hello_mlflow.py` imprime « Hello, MLflow! »                       |
| `chap02`  | `mlflow.set_tracking_uri("http://localhost:5000")` puis `print(mlflow.get_tracking_uri())` — premier vrai contact avec le serveur |
| `chap03`  | Premier ML pipeline complet : `pandas` charge le dataset, `train_test_split`, `ElasticNet(...)`, `log_param/log_metric/sklearn.log_model`, CLI args via `argparse` |

---

## Phase 2 — Docker multi-services (chap04 → chap05)

> **Objectif de la phase.** Séparer le **serveur MLflow** du **script d'entraînement** en deux conteneurs distincts ; comprendre pourquoi MLflow doit savoir explicitement où écrire (config par variable d'environnement = pattern 12-factor).

```mermaid
flowchart LR
    c03["chap03<br/>Un seul conteneur"] -->|"+ trainer/ folder<br/>+ Dockerfile trainer<br/>+ ENTRYPOINT python train.py<br/>+ recap-net network<br/>- set_tracking_uri (volontairement!)"| c04["chap04<br/>+ trainer service<br/><b>BUG-BY-DESIGN</b>"]
    c04 -->|"+ MLFLOW_TRACKING_URI on trainer<br/>+ os.getenv(MLFLOW_TRACKING_URI)<br/>+ mlflow.set_tracking_uri(...)"| c05["chap05<br/>ENV var fix<br/><b>les runs apparaissent enfin</b>"]
```

| Chapitre  | Ce qui est nouveau                                                                                              |
| --------- | --------------------------------------------------------------------------------------------------------------- |
| `chap04`  | Service `trainer` séparé avec son `Dockerfile` + `requirements.txt`. Réseau Docker `recap-net`. **Volontairement** sans `set_tracking_uri()` → les runs disparaissent (bug pédagogique). Solution : `docker-compose-option2.yml` ou `docker compose exec -e MLFLOW_TRACKING_URI=http://localhost:5000 mlflow python trainer/train.py ...` |
| `chap05`  | Variable d'env `MLFLOW_TRACKING_URI: http://mlflow:5000` ajoutée au service `trainer`. Le script lit `os.getenv(...)` puis appelle `set_tracking_uri(...)`. Pattern 12-factor verrouillé pour le reste du cours |

---

## Phase 3 — Logging avancé (chap06 → chap09)

> **Objectif de la phase.** Maîtriser l'API de tracking de MLflow : créer des expériences nommées, gérer le cycle de vie des runs explicitement, logger des artefacts arbitraires et attacher de la metadata.

```mermaid
flowchart LR
    c05 -->|"+ mlflow.create_experiment(name, tags, artifact_location)<br/>+ mlflow.set_experiment(name)"| c06["chap06<br/>experiments + tags<br/>+ artifact_location"]
    c06 -->|"+ mlflow.start_run() / end_run() impératif<br/>+ active_run()<br/>+ last_active_run()"| c07["chap07<br/>start_run/end_run<br/>+ active_run"]
    c07 -->|"+ log_artifacts(dir)<br/>+ log_params(dict)<br/>+ log_metrics(dict)"| c08["chap08<br/>bulk logging"]
    c08 -->|"+ set_tags({k: v, ...}) metadata"| c09["chap09<br/>set_tags metadata"]
```

| Chapitre  | Concept clé                              | Code phare                                              |
| --------- | ---------------------------------------- | ------------------------------------------------------- |
| `chap06`  | Expérience nommée + tags + chemin custom | `mlflow.create_experiment("experiment_2", tags={...}, artifact_location="...")` |
| `chap07`  | Style impératif (vs context manager)     | `run = mlflow.start_run(); ... mlflow.end_run()` + `mlflow.active_run()` + `mlflow.last_active_run()` |
| `chap08`  | Logging en masse                          | `mlflow.log_artifacts("plots/")` + `log_params({"a": 1, "b": 2})` + `log_metrics({"rmse": 0.4, "mae": 0.3})` |
| `chap09`  | Metadata textuelle                        | `mlflow.set_tags({"author": "alice", "dataset_version": "v3", "purpose": "weekly retraining"})` |

---

## Phase 4 — Multi-runs et multi-experiments (chap10 → chap12)

> **Objectif de la phase.** Passer de « 1 commande = 1 run » à « 1 commande = N runs comparables », et automatiser le logging.

```mermaid
flowchart LR
    c09 -->|"+ train_one_run() helper<br/>+ CONFIGS list<br/>+ for cfg in CONFIGS"| c10["chap10<br/>3 runs / 1 expérience"]
    c10 -->|"+ 3 modèles distincts (EN/Ridge/Lasso)<br/>+ mlflow.set_experiment(name) par modèle"| c11["chap11<br/>3 expériences séparées"]
    c11 -->|"+ mlflow.autolog()<br/>- log_param/log_metric/log_model manuels"| c12["chap12<br/>autolog magique"]
```

| Chapitre  | Concept clé                                                                                                                 |
| --------- | --------------------------------------------------------------------------------------------------------------------------- |
| `chap10`  | Helper function `train_one_run(name, alpha, l1_ratio, ...)` + liste `CONFIGS` + boucle `for` → 3 runs avec `run_name` propres dans la même expérience → cliquer **Compare** dans l'UI |
| `chap11`  | Trois expériences nommées (`exp_elasticnet`, `exp_ridge`, `exp_lasso`), une par algorithme. `mlflow.set_experiment(name)` change d'expérience à la volée |
| `chap12`  | Un seul appel : `mlflow.autolog()` → params, metrics, modèle et signature loggés automatiquement par MLflow pour sklearn (fini les `log_param/log_metric` manuels) |

---

## Phase 5 — Production topology (chap13)

> **Objectif de la phase.** Remplacer la stack SQLite + filesystem local par la stack canonique de prod : **Postgres** comme backend store et **S3** (ou MinIO) comme artifact store.

```mermaid
flowchart LR
    subgraph chap12["chap12 (avant)"]
        direction TB
        m1[mlflow<br/>backend = sqlite:///database/mlflow.db<br/>artifacts = /mlflow/mlruns]
        m1 --- t1[trainer]
    end

    subgraph chap13["chap13 (après)"]
        direction TB
        m2[mlflow<br/>backend = postgresql://...<br/>artifacts = /mlflow/mlruns or s3://bucket]
        m2 --- t2[trainer]
        m2 -. depends_on healthy .-> pg[(postgres<br/>image: postgres:16-alpine)]
    end

    chap12 -->|"+ service postgres<br/>+ psycopg2-binary<br/>+ POSTGRES_DB/USER/PASSWORD<br/>+ --backend-store-uri postgresql://...<br/>+ healthcheck pg_isready"| chap13
```

| Chapitre  | Concept clé                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------------ |
| `chap13`  | 3 services au lieu de 2. Image MLflow custom (`mlops/mlflow-pg-recap`) qui installe `psycopg2-binary`. `--backend-store-uri postgresql://mlflowuser:mlflowpassword@postgres:5432/mlflowdb`. Discussion S3/MinIO en option |

---

## Phase 6 — Model packaging (chap14 → chap17)

> **Objectif de la phase.** Décrire le contrat du modèle (signature) puis l'emballer dans un format « universel » (PyFunc) que MLflow saura recharger plus tard.

```mermaid
flowchart LR
    c13 -->|"+ infer_signature(X_train, y_pred)<br/>+ signature=... in log_model"| c14["chap14<br/>infer_signature"]
    c14 -->|"+ Schema([ColSpec(...)])<br/>+ ModelSignature(inputs, outputs)"| c15["chap15<br/>Schema + ColSpec"]
    c15 -->|"+ class MyModel(PythonModel)<br/>+ load_context / predict<br/>+ joblib.dump<br/>+ conda_env"| c16["chap16<br/>PyFunc wrapper"]
    c16 -->|"+ mlflow.pyfunc.load_model('runs:/<id>/model')<br/>+ model.predict(X_test)"| c17["chap17<br/>load + predict"]
```

| Chapitre  | Concept clé                                                                                                       |
| --------- | ----------------------------------------------------------------------------------------------------------------- |
| `chap14`  | `from mlflow.models import infer_signature` → MLflow déduit automatiquement la signature à partir d'un échantillon |
| `chap15`  | Construction manuelle de la signature avec `Schema([ColSpec("double", "alcohol"), ...])` — contrôle précis        |
| `chap16`  | Wrapper PyFunc : sous-classe `mlflow.pyfunc.PythonModel`, `load_context(self, ctx)` charge le pickle joblib, `predict(self, ctx, X)` fait l'inférence. `conda.yaml` listé pour la repro |
| `chap17`  | `loaded = mlflow.pyfunc.load_model("runs:/<run_id>/model")` puis `loaded.predict(X_test)` — boucle complète : log → relire → prédire |

---

## Phase 7 — Évaluation (chap18 → chap20)

> **Objectif de la phase.** Automatiser le calcul de métriques d'évaluation et bloquer le déploiement d'un modèle qui n'atteint pas un seuil de qualité.

```mermaid
flowchart LR
    c17 -->|"+ mlflow.evaluate(model_uri, data=..., targets=..., model_type='regressor')"| c18["chap18<br/>evaluate default"]
    c18 -->|"+ custom_metric via make_metric(...)<br/>+ scatter plot artifact"| c19["chap19<br/>custom metrics"]
    c19 -->|"+ MetricThreshold(threshold=..., min_absolute_change=...)<br/>+ baseline DummyRegressor"| c20["chap20<br/>validation thresholds"]
```

| Chapitre  | Concept clé                                                                                                                 |
| --------- | --------------------------------------------------------------------------------------------------------------------------- |
| `chap18`  | `result = mlflow.evaluate("runs:/<id>/model", data=X_test, targets="quality", model_type="regressor")` → MAE/MSE/R² par défaut |
| `chap19`  | `make_metric(eval_fn=my_fn, greater_is_better=False)` pour ajouter des métriques custom + sauver un scatter `y_true vs y_pred` comme artefact |
| `chap20`  | `validation_thresholds={"rmse": MetricThreshold(threshold=0.8, higher_is_better=False)}` + `baseline_model = DummyRegressor(strategy="mean")` → MLflow lève une exception si le modèle n'est pas meilleur que la baseline |

---

## Phase 8 — Model Registry (chap21 → chap24)

> **Objectif de la phase.** Promouvoir un modèle de l'expérience vers le **Registry** (registre central versionné), avec différentes stratégies : auto à l'entraînement, post-hoc, ou import d'un modèle externe.

```mermaid
flowchart LR
    c20 -->|"+ registered_model_name='...' in log_model"| c21["chap21<br/>auto-register"]
    c21 -->|"+ pickle.dump + log_artifact (compare)"| c22["chap22<br/>log_model + pickle"]
    c22 -->|"+ mlflow.register_model(uri, name)<br/>+ load_model('models:/name/v')"| c23["chap23<br/>post-hoc + load by version"]
    c23 -->|"+ pretrainer service (no MLflow)<br/>+ registrar service<br/>+ cloudpickle handover"| c24["chap24<br/>external model import"]
```

| Chapitre  | Concept clé                                                                                                                       |
| --------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `chap21`  | `mlflow.sklearn.log_model(model, "model", registered_model_name="elasticnet-recap")` → le modèle est enregistré ET versionné en une ligne |
| `chap22`  | Compare deux façons de persister un modèle dans MLflow : `mlflow.sklearn.log_model(...)` (canonique) vs `pickle.dump(model, f)` + `mlflow.log_artifact(...)` (« je l'ai sauvé moi-même ») |
| `chap23`  | Enregistrement post-hoc : on a déjà un run avec un modèle loggé → `mlflow.register_model("runs:/<run_id>/model", "name")` plus tard, puis `mlflow.sklearn.load_model("models:/name/<version>")` |
| `chap24`  | Cas réel : un modèle entraîné en dehors de MLflow (par exemple un héritage legacy). Deux services : `pretrainer` (sklearn pur, pickle.dump) → `registrar` (cloudpickle.load + log_model + registered_model_name) |

---

## Phase 9 — MLflow Projects + CLI (chap25 → chap26b)

> **Objectif de la phase.** Adopter les patterns réutilisables (context manager `with`, fonction `main`, MLproject reproductible, CLI MLflow pour l'inspection).

```mermaid
flowchart LR
    c24 -->|"+ with mlflow.start_run() as run:<br/>+ def main(): ..."| c25["chap25<br/>context manager + main"]
    c25 -->|"+ MLproject yaml<br/>+ entry_points main<br/>+ mlflow run . -P alpha=..."| c26["chap26<br/>MLflow Projects"]
    c26 -->|"+ service cli<br/>+ mlflow doctor / artifacts / experiments / runs"| c26b["chap26b<br/>MLflow CLI"]
```

| Chapitre  | Concept clé                                                                                                         |
| --------- | ------------------------------------------------------------------------------------------------------------------- |
| `chap25`  | Style Pythonique : `with mlflow.start_run(run_name="foo") as run: ...` (fermeture automatique du run même si exception) + organisation en `main()` + `if __name__ == "__main__":` |
| `chap26`  | Fichier `MLproject` (YAML) qui déclare entry_points + paramètres + `conda_env`. Lancement avec `mlflow run . -P alpha=0.1 -P l1_ratio=0.1` (au lieu de `docker compose run --rm trainer ...`) |
| `chap26b` | Service `cli` (image dédiée) qui expose les sous-commandes MLflow : `mlflow doctor` (diagnostic), `mlflow artifacts list` (lister), `mlflow experiments search`, `mlflow runs describe <id>` |

---

## Matrice des concepts (un seul tableau pour tout)

> Coche par chapitre des fonctionnalités MLflow / Docker utilisées. Lis-le verticalement pour voir où chaque concept apparaît pour la première fois.

| Concept                                  | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 26b |
| ---------------------------------------- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | --- |
| `mlflow server` dans Docker              | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ·  | ✓   |
| `set_tracking_uri()`                     | ·  | ✓  | ✓  | ✗  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓   |
| `log_param` / `log_metric`               | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓   |
| `sklearn.log_model`                      | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓   |
| Service `trainer` séparé                 | ·  | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓* | ✓  | ·  | ✓   |
| `MLFLOW_TRACKING_URI` env var            | ·  | ·  | ·  | ✗  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓   |
| `create_experiment` + tags               | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓   |
| `start_run / end_run` impératif          | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ·  | ·  | ✓   |
| `log_artifacts` + bulk `log_*`           | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓   |
| `set_tags`                               | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓   |
| Boucle multi-runs                        | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ·  | ✓  | ✓  | ✓   |
| Plusieurs expériences (3+)               | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·   |
| `mlflow.autolog()`                       | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·   |
| Backend = Postgres                       | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·   |
| Signature (`infer_signature` / Schema)   | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓  | ✓   |
| PyFunc wrapper + conda_env               | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·   |
| `pyfunc.load_model` + `predict`          | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ·  | ·  | ✓  | ·  | ·  | ·  | ·   |
| `mlflow.evaluate`                        | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓  | ·  | ·  | ·  | ·  | ·  | ·  | ·   |
| Custom metric + artefact                 | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ·  | ·  | ·  | ·  | ·  | ·  | ·   |
| Validation thresholds + baseline         | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ·  | ·  | ·  | ·  | ·  | ·  | ·   |
| `registered_model_name`                  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓  | ✓  | ·  | ·  | ·   |
| `pickle.dump` + `log_artifact`           | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ·  | ✓  | ·  | ·  | ·   |
| `register_model` post-hoc + load by ver. | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ·  | ·  | ·  | ·   |
| Service `pretrainer` (no MLflow)         | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ·  | ·  | ·   |
| Cloudpickle import (modèle externe)      | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ·  | ·  | ·   |
| `with start_run` (context manager)       | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓   |
| `def main()` + `if __name__`             | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ✓  | ✓   |
| `MLproject` yaml + `mlflow run`          | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓  | ·   |
| MLflow CLI (doctor / artifacts / ...)    | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ✓   |

**Légende :**
- ✓ = concept utilisé dans ce chapitre
- ✗ = bug-by-design (concept manquant intentionnellement)
- · = non utilisé
- ✓* = chap24 utilise `pretrainer` + `registrar` au lieu d'un simple `trainer`

---

## Évolution du `docker-compose.yml` au fil du cours

```mermaid
flowchart TB
    subgraph S1["chap01-03"]
        s1["services:<br/>&nbsp;&nbsp;mlflow:<br/>&nbsp;&nbsp;&nbsp;&nbsp;volumes: ./database, ./mlruns, .:/work<br/>&nbsp;&nbsp;&nbsp;&nbsp;working_dir: /work"]
    end

    subgraph S2["chap04"]
        s2["+ services:<br/>&nbsp;&nbsp;trainer:<br/>&nbsp;&nbsp;&nbsp;&nbsp;(no MLFLOW_TRACKING_URI = bug)<br/>+ networks: recap-net"]
    end

    subgraph S3["chap05-12"]
        s3["+ trainer.environment:<br/>&nbsp;&nbsp;&nbsp;&nbsp;MLFLOW_TRACKING_URI: http://mlflow:5000"]
    end

    subgraph S4["chap13"]
        s4["+ services:<br/>&nbsp;&nbsp;postgres: image postgres:16-alpine<br/>+ mlflow image custom (psycopg2-binary)<br/>+ --backend-store-uri postgresql://..."]
    end

    subgraph S5["chap14-23"]
        s5["(mêmes services que chap05-12,<br/>les changements sont dans le code Python)"]
    end

    subgraph S6["chap24"]
        s6["- trainer<br/>+ pretrainer (sklearn pur, no MLflow)<br/>+ registrar (MLflow-aware)<br/>+ volumes: shared (handover pickle)"]
    end

    subgraph S7["chap25"]
        s7["(idem chap05-12 + with start_run dans le code)"]
    end

    subgraph S8["chap26"]
        s8["+ MLproject yaml<br/>+ conda_env<br/>(lancement: mlflow run . -P alpha=...)"]
    end

    subgraph S9["chap26b"]
        s9["+ services:<br/>&nbsp;&nbsp;cli: image mlops/mlflow-cli<br/>+ subcommands doctor/artifacts/experiments/runs"]
    end

    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8 --> S9
```

---

## Évolution du `train.py` au fil du cours

```mermaid
flowchart TB
    t1["chap01: hello_mlflow.py<br/><i>juste un print</i>"]
    t2["chap02: + set_tracking_uri + get_tracking_uri"]
    t3["chap03: + pandas + ElasticNet + log_param/metric/sklearn.log_model + argparse"]
    t4["chap04: trainer/train.py (séparé) — NO set_tracking_uri (bug)"]
    t5["chap05: + os.getenv(MLFLOW_TRACKING_URI) + set_tracking_uri"]
    t6["chap06: + mlflow.create_experiment + set_experiment"]
    t7["chap07: + start_run/end_run impératif + active_run + last_active_run"]
    t8["chap08: + log_artifacts + log_params(dict) + log_metrics(dict)"]
    t9["chap09: + set_tags(metadata)"]
    t10["chap10: + train_one_run helper + CONFIGS + for loop"]
    t11["chap11: + 3 expériences (EN / Ridge / Lasso)"]
    t12["chap12: - log_param/metric manuels + mlflow.autolog()"]
    t13["chap13: même train.py — Postgres est côté serveur"]
    t14["chap14: + infer_signature + signature= in log_model"]
    t15["chap15: + Schema/ColSpec + ModelSignature manuel"]
    t16["chap16: + PyFunc wrapper class + joblib + conda.yaml"]
    t17["chap17: + pyfunc.load_model + predict roundtrip"]
    t18["chap18: + mlflow.evaluate(model_type=regressor)"]
    t19["chap19: + make_metric custom + scatter plot artifact"]
    t20["chap20: + MetricThreshold + DummyRegressor baseline"]
    t21["chap21: + registered_model_name= in log_model"]
    t22["chap22: + pickle.dump + log_artifact (comparaison)"]
    t23["chap23: + register_model post-hoc + load_model(models:/.../v)"]
    t24["chap24: pretrainer/train_outside_mlflow.py + registrar/register_external.py (cloudpickle)"]
    t25["chap25: + with start_run + def main"]
    t26["chap26: + MLproject + mlflow run . -P (plus de Docker trainer)"]
    t26b["chap26b: + cli/Dockerfile + entrypoint mlflow doctor/artifacts/experiments/runs"]

    t1 --> t2 --> t3 --> t4 --> t5 --> t6 --> t7 --> t8 --> t9 --> t10 --> t11 --> t12 --> t13 --> t14 --> t15 --> t16 --> t17 --> t18 --> t19 --> t20 --> t21 --> t22 --> t23 --> t24 --> t25 --> t26 --> t26b
```

---

## Cheat sheet — quel chapitre regarder pour quelle question ?

| Question que tu te poses                                                | Va voir              |
| ----------------------------------------------------------------------- | -------------------- |
| « Comment lancer un serveur MLflow ? »                                  | `chap01`             |
| « Comment dire à mon script où parler à MLflow ? »                      | `chap02`, `chap05`   |
| « Mon premier vrai pipeline ML, c'est où ? »                            | `chap03`             |
| « Pourquoi mes runs disparaissent dans le UI ? »                        | `chap04` (bug)       |
| « 12-factor app pour MLflow ? »                                         | `chap05`             |
| « Créer plusieurs expériences nommées ? »                               | `chap06`, `chap11`   |
| « `start_run` impératif vs context manager ? »                          | `chap07`, `chap25`   |
| « Logger plusieurs metrics d'un coup ? »                                | `chap08`             |
| « Attacher de la metadata à un run ? »                                  | `chap09`             |
| « 3 runs comparables en une commande ? »                                | `chap10`             |
| « Comparer ElasticNet vs Ridge vs Lasso ? »                             | `chap11`             |
| « Auto-loguer sans écrire `log_param` ? »                               | `chap12`             |
| « Stack de production : Postgres + S3 ? »                               | `chap13`             |
| « Signature du modèle (input/output schema) ? »                         | `chap14`, `chap15`   |
| « Emballer mon modèle en PyFunc + conda ? »                             | `chap16`             |
| « Recharger un modèle et faire predict() ? »                            | `chap17`             |
| « Évaluer automatiquement avec MAE/MSE/R² ? »                           | `chap18`             |
| « Ajouter ma propre metric + un scatter plot ? »                        | `chap19`             |
| « Bloquer la promo d'un modèle moins bon que la baseline ? »            | `chap20`             |
| « Enregistrer auto dans le Registry dès l'entraînement ? »              | `chap21`             |
| « `log_model` vs `pickle.dump` manuel ? »                               | `chap22`             |
| « Charger une version précise depuis le Registry ? »                    | `chap23`             |
| « Importer un modèle entraîné HORS MLflow ? »                           | `chap24`             |
| « Avec `with`, c'est plus propre, c'est où ? »                          | `chap25`             |
| « MLproject + `mlflow run .` à la place de Docker ? »                   | `chap26`             |
| « Inspecter le serveur avec la CLI MLflow ? »                           | `chap26b`            |
