# Quiz - chap01 to chap05 - MLflow concepts (MCQ) - **ANSWER KEY**

Companion answer key for [`quiz-chap01-chap05-mlflow-concepts-en-mcq.md`](./quiz-chap01-chap05-mlflow-concepts-en-mcq.md).

Each answer includes:
- The correct option (A / B / C / D)
- A justification of **at least 4 sentences** explaining **why** the correct answer is right, **why the other options are wrong**, the **underlying concept**, and (when relevant) a **reference to the chapter** in the recap series.

> [!IMPORTANT]
> Do not share this file with students before they have submitted their answers. The justifications are written to be used in a **debrief session**, not as a cheat sheet.

---

## Section 1 - What is MLflow and why does it exist?

### Question 1 - **Answer: B**
MLflow is an open-source platform created by Databricks in 2018 and donated to the LF AI & Data Foundation in 2020 — it manages the **end-to-end ML lifecycle** through four pillars: Tracking, Projects, Models, and Model Registry. **A** is wrong because MLflow is not primarily a web framework; the Flask-based UI is a thin layer on top, not the core product. **C** is wrong because MLflow OSS is free under Apache 2.0 (Databricks sells a managed hosted version, but the open-source core has no license fee). **D** is wrong because MLflow does not train models itself — it **instruments** your existing training code, regardless of the ML framework you use.

### Question 2 - **Answer: D**
The four official MLflow components are **Tracking**, **Projects**, **Models**, and **Model Registry**. "Inference Gateway" does not exist in MLflow's vocabulary; the closest concept would be `mlflow models serve`, but that is part of the Models component, not a separate pillar. **A**, **B**, and **C** are all genuine MLflow pillars. The Tracking component (option A) is precisely what chap01-05 of this course focuses on.

### Question 3 - **Answer: A**
After Tracking, Projects, and Models, the fourth pillar is the **Model Registry**, which was introduced in MLflow 1.4. It manages model versions, stages (None → Staging → Production → Archived), and approval workflows on top of the Tracking server. **B**, **C**, and **D** are plausible-sounding but made-up names that do not exist anywhere in the MLflow documentation. The Model Registry is covered in detail starting from chap21 of this course.

### Question 4 - **Answer: C**
All five chapters chap01 → chap05 focus exclusively on **Tracking**: starting an MLflow server, logging params, metrics, models, and tags, then comparing runs in the UI. **A** (Projects) is introduced only in chap25+ when the course shows MLproject YAML files. **B** (Model Registry) is covered from chap21 onwards. **D** (Models) appears implicitly in chap03 via `mlflow.sklearn.log_model`, but it is a side-effect, not the focus of the chapter.

### Question 5 - **Answer: B**
MLflow ships built-in "flavors" for scikit-learn, PyTorch, TensorFlow/Keras, XGBoost, LightGBM, ONNX, Spark MLlib, statsmodels, fastai, and more — plus the generic `mlflow.pyfunc` flavor to wrap **any** Python callable. **A** is wrong because TF is just one of many supported frameworks. **C** is wrong because MLflow offers a Java client, an R client, and a language-agnostic REST API. **D** is wrong because MLflow is independent of any cloud provider — it works on AWS, GCP, Azure, on-prem, or on your laptop.

### Question 6 - **Answer: B**
MLflow's killer feature is exactly this: making the link between **params** (alpha=0.5), **code** (commit abc123), **dataset** (red-wine-quality.csv), **metrics** (rmse=0.74), and **artifact** (mymodel.pkl) PERSISTENT and SEARCHABLE. **A** is wrong because MLflow does not do distributed training (you would use Spark, Ray, or Horovod for that). **C** is wrong because MLflow does not write your training code — you do. **D** is wrong because MLflow uses scikit-learn (or any other library); it complements them rather than replacing them.

### Question 7 - **Answer: C**
Without MLflow, the typical workflow is "edit alpha in train.py, run, write the RMSE on a Post-it, repeat". After 20 models, you cannot reproduce a specific result, you cannot compare them objectively, and you cannot identify the best one with confidence. **A** is unrelated (MLflow does not provide GPUs). **B** is unrelated (offline / online is a deployment concern, not a tracking one). **D** is wrong because MLflow does not speed up training — it just records what happened during training.

### Question 8 - **Answer: D**
MLflow is a pure Python package distributed via PyPI; it runs on any OS with Python 3.9+, including Linux, Windows, and macOS. The Docker images used in chap01-05 run on Docker Desktop (Windows, macOS) or Docker Engine (Linux). **A**, **B**, **C** are all too restrictive. The very reason chap01 starts with "100% Docker, no Python on the host" is to keep the setup **OS-agnostic**.

### Question 9 - **Answer: B**
MLflow OSS is Apache 2.0 licensed and runs locally without internet access — the entire chap01-05 stack proves this works on a laptop. **A** is wrong because Databricks Managed MLflow is just one optional deployment; the OSS version is free and complete. **C** is wrong because there is no SaaS hosted by an MLflow Inc. (MLflow is governed by the LF AI & Data Foundation). **D** is wrong because MLflow runs perfectly fine without Kubernetes — in fact, the simplest deployment is a single container.

### Question 10 - **Answer: C**
This is MLflow's fundamental contract: params/metrics/tags go in a metadata DB (SQLite or Postgres), and artifacts (including the trained model itself) go in a separate artifact store (filesystem, S3, Azure Blob...). Without **both**, you cannot reproduce results. **A** is wrong because `mlflow.sklearn.log_model` exists and is used in chap03. **B** is wrong because `mlflow.log_param` and `log_metric` are the two most common MLflow calls. **D** is wrong because everything is persisted on disk in `./database/mlflow.db` and `./mlruns/`.

---

## Section 2 - The objective of each chapter file

### Question 11 - **Answer: B**
chap01 is intentionally the simplest chapter in the entire recap series: boot the MLflow server in Docker, open the UI at `http://localhost:5000`, and create one trivial run with `mlflow.start_run()` + `mlflow.log_metric("foo", 1)`. **A** is the objective of chap03, not chap01 — at this point there is no model, no dataset, no hyperparameters. **C** belongs to chap03 once multiple runs exist. **D** is far beyond chap01; model serving is covered only in chap20+. The pedagogical goal of chap01 is simply "I have a working MLflow stack and I can see a run in the UI".

### Question 12 - **Answer: C**
chap02 adds nothing but a single `print("Tracking URI:", mlflow.get_tracking_uri())` line — but conceptually it teaches **the** most important lesson of the entire series: MLflow has ONE active tracking URI at any time, and you must know what it is BEFORE logging anything. **A** is wrong because no refactoring happens in chap02. **B** is wrong because S3 comes much later. **D** is wrong because run_id is unrelated to chap02's lesson; the chapter is about backend awareness, not run identification.

### Question 13 - **Answer: B**
Literally the only difference between chap01 and chap02 is one Python line and the corresponding markdown explanation in the lesson file. The Docker setup, the bind mounts (`./database`, `./mlruns`), the SQLite DB, and the requirements file are all identical. **A** is wrong because no new service is added (still single-service `mlflow`). **C** is wrong because SQLite stays as the metadata backend. **D** is wrong because the Model Registry only comes into play in chap21+.

### Question 14 - **Answer: A**
chap03 teaches the canonical MLflow workflow: take a model (ElasticNet on red-wine-quality), VARY the hyperparameters, log everything, and COMPARE in the UI. The three specific runs in the README use `(alpha, l1_ratio)` = `(0.1, 0.1)`, `(0.5, 0.5)`, `(0.9, 0.1)`. **B** is wrong (deployment is chap20+). **C** is wrong (ElasticNet stays throughout the dataset chapters). **D** is wrong (CI/CD is not covered in the recap series).

### Question 15 - **Answer: B**
chap01-02 used only `start_run` plus `log_metric("foo", 1)`. chap03 introduces the FULL triple: `log_param` for hyperparams, `log_metric` for RMSE/MAE/R², and `mlflow.sklearn.log_model` for the trained ElasticNet object. **A** is incomplete because `log_metric` already existed in chap01. **C** is wrong because `log_artifact` is introduced later (chap07+). **D** is wrong because `set_experiment` is implicit in chap03 and only made explicit in chap05 onwards.

### Question 16 - **Answer: B**
Until chap03, `train.py` ran INSIDE the MLflow server container via `docker compose exec mlflow python train.py`. chap04 creates a brand-new `trainer` service with its own Dockerfile and its own `requirements.txt`. This forces the student to think about networking, image scoping, and one-shot execution patterns. **A** is wrong (no replacement of MLflow happens anywhere). **C** is wrong (Kubernetes is not covered). **D** is wrong (no encryption is added).

### Question 17 - **Answer: C**
chap04's `train.py` DELIBERATELY does NOT call `mlflow.set_tracking_uri(...)`. MLflow falls back to its default `file:./mlruns/` — which means inside the `trainer` container at `/code/mlruns`. The `--rm` flag then deletes the container after the run, wiping the directory. **A** is wrong (the server starts fine). **B** is wrong (the Python script runs to completion with no error). **D** is wrong (both Docker images build successfully). The pedagogical point is to make the student **feel** the bug before learning the fix in chap05.

### Question 18 - **Answer: B**
chap05 reads `os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")` and passes it to `mlflow.set_tracking_uri(...)`. The `docker-compose.yml` declares this env var on the `trainer` service. This is exactly the cleanup pass that follows chap04's deliberate breakage. **A** is the antipattern that chap05 explicitly avoids. **C** is part of chap21+. **D** (multi-user auth) is way beyond this course's scope.

### Question 19 - **Answer: B**
The **12-factor app** methodology says "store config in the environment", separating CODE (which is the same in dev/staging/prod) from CONFIGURATION (which differs per environment). The same `train.py` can then point at `http://mlflow:5000` in dev and `http://prod-mlflow.company.com` in prod without modifying any source file. **A** is wrong: `os.getenv` is actually slower than a Python literal (negligible, but still). **C** is wrong: MLflow has had `set_tracking_uri` since v0.1. **D** is wrong: Docker has no opinion on hardcoded URLs.

### Question 20 - **Answer: B**
This is a classic pedagogical pattern: experience the broken state, understand the symptom, THEN learn the fix. If chap04 and chap05 were merged, the student would see env vars from the start and never grasp WHY they matter. The "aha moment" comes from running chap04 three times, opening the UI, seeing zero runs, and then opening chap05 to fix it. **A**, **C**, **D** are technically conceivable but miss the pedagogical intent.

### Question 21 - **Answer: B**
chap01 adds the MLflow server, chap02 adds awareness of the tracking URI, chap03 adds the ML pipeline (ElasticNet + log_param/metric/model), chap04 adds a second Docker service (trainer), chap05 adds the env var injection pattern. Each chapter adds EXACTLY one new concept on top of the previous one. **A** is the anti-pattern the course explicitly avoids. **C** is wrong (the course is bottom-up, not top-down). **D** is wrong (the registry comes later, after this 5-chapter foundation).

### Question 22 - **Answer: A**
The endpoint of chap01 → chap05 is exactly: a `mlflow` service + a `trainer` service connected via the `recap-net` bridge network, with `MLFLOW_TRACKING_URI` injected via `docker-compose.yml`. This is the **canonical pattern** that all subsequent chapters (chap06+) extend with new features. **B** describes chap01-03 (single container). **C** and **D** are far beyond the recap series.

### Question 23 - **Answer: B**
In chap01-03, the MLflow image happened to have scikit-learn installed (a side-effect of how it was built). chap04 makes the MLflow image MINIMAL (only `mlflow`) and the trainer image have its own sklearn/pandas/numpy. `docker compose run --rm trainer` is then the right tool to invoke that one-shot service. **A** is wrong (`exec` is not deprecated). **C** is wrong (no root privileges required). **D** is wrong (`run` is not "mathematically faster" than `exec` — they just do different things).

---

## Section 3 - Experiments, runs, params, metrics, artifacts, tags

### Question 24 - **Answer: B**
An MLflow **experiment** is a named namespace that groups related runs together — examples: `wine_quality_elasticnet`, `text_classifier_v2`, `recommendation_engine_AB_test`. Each experiment has many runs but only one name and one experiment_id. **A** confuses experiment with run (a run is a single execution; an experiment groups many runs). **C** is wrong because an experiment is a logical entity in the metadata DB, not "just a folder". **D** is wrong (an experiment is not a config file).

### Question 25 - **Answer: B**
A **run** is the unit of execution in MLflow: one `mlflow.start_run() ... mlflow.end_run()` block (or the equivalent `with` context manager). Each run has its own UUID, params, metrics, tags, and artifacts. **A** confuses run with experiment (the run belongs to an experiment, not the other way around). **C** is wrong (a run is metadata-rich, not just a folder). **D** is wrong (a run is a logical entity, not an API call).

### Question 26 - **Answer: B**
**Params** are values that are KNOWN BEFORE training starts and DO NOT change during training: hyperparameters, dataset version, random seed, model architecture choices, etc. `alpha=0.5` is the textbook example. **A** (training time) is a METRIC computed AFTER training. **C** (the trained model) is an ARTIFACT. **D** (validation RMSE) is also a METRIC computed AFTER training.

### Question 27 - **Answer: B**
**Metrics** are numerical quantities computed DURING or AFTER training: loss, accuracy, AUC, RMSE, MAE, R². They can be logged multiple times to form a time series (one value per epoch). **A** (git commit) is typically logged as a TAG (or auto-captured). **C** (alpha) is a PARAM, not a metric. **D** (sklearn version) is captured automatically as part of the run metadata, not as a metric.

### Question 28 - **Answer: C**
**Tags** are arbitrary string key-value labels attached to a run or experiment: owner, environment, git branch, model version, etc. They are great for filtering and organising. **A** (RMSE) is a numerical METRIC. **B** (the trained model) is an ARTIFACT. **D** (the dataset CSV) is also an ARTIFACT, logged via `log_artifact`.

### Question 29 - **Answer: C**
`mlflow.sklearn.log_model(lr, "mymodel")` serialises the trained sklearn estimator (via cloudpickle) plus the MLmodel YAML descriptor and a `conda.yaml` env spec. This creates a directory `mymodel/` under the run's artifacts. **A** (RMSE) is a METRIC. **B** (alpha) is a PARAM. **D** (the dataset) would be logged via `mlflow.log_artifact("data/red-wine-quality.csv")`, a different API.

### Question 30 - **Answer: B**
MLflow run IDs are UUIDv4-style strings like `0123456789abcdef0123456789abcdef`. They are globally unique with negligible collision probability (the chance of two UUIDv4 values colliding is roughly 1 in 10^36). **A** is wrong because incremental ids would force a single source of truth (the DB) for every new run. **C** is wrong because Unix timestamps can collide when two runs start in the same millisecond. **D** is wrong (no hash relation to model weights — the run_id is generated at run START, before any weight exists).

### Question 31 - **Answer: B**
With incremental IDs, every new run requires a round-trip to the DB to allocate the next number, which SERIALISES all writes. With UUIDs, each client generates its own id locally (`uuid.uuid4()`) with no coordination, supporting massively parallel logging. **A** is wrong (UUIDs are LARGER, 16 bytes vs 4–8 bytes for an int). **C** is wrong (UUIDs sort fine as strings, but "faster to sort" is not the reason). **D** is wrong (MLflow does use UUIDs internally — you can see them in the URL of every run page).

### Question 32 - **Answer: B**
Calling `log_param("alpha", 0.5)` followed by `log_param("alpha", 0.6)` raises an `mlflow.exceptions.MlflowException` with code `INVALID_PARAMETER_VALUE`. Params describe the INITIAL state of the run, so they are intentionally immutable — this prevents the antipattern of "rewriting history". **A** is wrong (no silent overwrite; an exception is raised). **C** is wrong (no admin role exists). **D** is wrong (no license gating; MLflow OSS has the same behaviour as MLflow on Databricks).

### Question 33 - **Answer: B**
Metrics support multiple log calls per run — each call adds a `(step, value, timestamp)` tuple. The UI then shows a line chart automatically. This is the STANDARD pattern for logging loss per epoch in deep learning. **A** is wrong (the chap03 example uses one value but the general rule is multi-value). **C** is wrong (you keep the same metric name; the step changes). **D** is wrong (no exception is raised; this is a designed feature).

### Question 34 - **Answer: B**
The `MLmodel` file is a small YAML manifest specifying flavors (`sklearn`, `pyfunc`, `pytorch`, ...), the python_function entry point, the conda environment, the signature, and metadata. This descriptor is what makes MLflow framework-agnostic at load time. **A** is a Keras-specific format. **C** is a PyTorch-specific format. **D** is an industry-standard cross-framework format, but more restricted than MLmodel; MLflow can wrap all of them under MLmodel.

### Question 35 - **Answer: B**
MLflow records `start_time`, `end_time`, `status` (RUNNING / FINISHED / FAILED), `user`, `source_name` (script path), `source_type`, and a few more pieces of metadata automatically. **A** is wrong: git DIFF is not captured (but git COMMIT can be added manually via `mlflow.set_tag("mlflow.source.git.commit", ...)`). **C** is wrong (no RAM dump is ever taken — that would be a security and performance disaster). **D** is wrong (no screenshots are taken; MLflow is privacy-friendly).

### Question 36 - **Answer: B**
Metadata (params, metrics, tags) is **small** and **structured** — perfect for a SQL database that can index and query it in microseconds. Artifacts (pickled models, plots, datasets) are **large** **binary blobs** — perfect for object storage that is cheap, durable, and content-addressable. Querying `WHERE metrics.rmse < 0.7` in SQLite/Postgres is fast; downloading a 200-MB model from S3 is the right tool for that job. **A** is wrong (artifacts are usually MUCH larger than metadata, not smaller). **C** is wrong (the MLflow license is silent on this). **D** is wrong (separation is real and visible in `./database` vs `./mlruns`).

---

## Section 4 - Comparing experiments (the heart of MLflow)

### Question 37 - **Answer: B**
The MLflow UI lets you click any column header to sort runs. For ElasticNet on red-wine-quality, lower RMSE = better regression model, so sorting `rmse` ascending puts your best run at the top. This is a 2-click operation. **A** is the pre-MLflow "Post-it" workflow that the entire course argues against. **C** works but is unnecessary when the UI offers the same view in one click. **D** is wrong — comparison IS the central feature of MLflow Tracking.

### Question 38 - **Answer: B**
RMSE = root mean squared error and MAE = mean absolute error are both **error** metrics measuring the average distance between predicted and actual values. A perfect model has RMSE = MAE = 0; the worse the predictions, the higher these numbers. **A** is the inverse (a common student trap — error is not a score). **C** is wrong (these metrics have no theoretical upper bound). **D** is wrong (0.5 has no special meaning for these metrics).

### Question 39 - **Answer: C**
R² = 1 means the model explains 100% of the variance in the target; R² = 0 means the model is no better than predicting the dataset mean; R² < 0 means the model is worse than predicting the mean (a non-trivial case for very bad models). Higher R² is always better. **A** is the inverse. **B** is the "no skill" baseline, not a target. **D** is the failure case, definitely not "good".

### Question 40 - **Answer: C**
The mathematical definition is R² = 1 - (SS_res / SS_tot). When predictions are perfect, SS_res = 0 and R² = 1. R² can be negative for very bad models but cannot exceed 1. **A** is the "no skill" baseline (predict the mean). **B** is somewhere between random and perfect. **D** is wrong because R² is bounded above by 1.

### Question 41 - **Answer: B**
When you select multiple runs and click "Compare", MLflow shows: (1) a flat table with one column per run for params and metrics, (2) scatter plots between any pair of params/metrics, (3) a parallel coordinates plot for high-dimensional views, and (4) a contour plot. **A** is wrong (source diff is not a Compare feature). **C** is wrong (artifacts are not auto-loaded in Compare). **D** is wrong (Compare does not show stdout logs).

### Question 42 - **Answer: B**
A parallel coordinates plot has one VERTICAL axis per hyperparameter and per metric, with one POLYLINE per run connecting its values across all axes. It is the canonical way to spot patterns like "low alpha + high l1_ratio always gives low RMSE" when you have, say, 5 hyperparameters and 50 runs. **A** is degenerate (one point cannot make a line). **C** has nothing to draw. **D** is wrong (parallel coordinates handle both categorical and numerical values).

### Question 43 - **Answer: B**
One run alone gives an RMSE but no context — is 0.74 good or bad? Three runs let you ORDER them and start building intuition about the hyperparameter space (e.g. "alpha is the dominant variable, l1_ratio matters less"). **A** is wrong (MLflow has no minimum run count). **C** is wrong (the dataset's column count is unrelated). **D** is wrong (3 has no statistical significance — for stats you would need many more samples).

### Question 44 - **Answer: A**
The MLflow UI exposes a search bar at the top of the experiment view, accepting an SQL-like syntax: `params.alpha < 0.3 and metrics.rmse < 0.7`. This is the same syntax accepted by the Python API `mlflow.search_runs(filter_string=...)`. **B** is the pre-MLflow workflow. **C** bypasses MLflow's API and is brittle (the DB schema can change). **D** is overkill for a built-in feature.

### Question 45 - **Answer: B**
The Compare feature works on the selected runs, regardless of which experiment they belong to. You go to the experiment list view, multi-select experiments (Shift+click), then multi-select runs, then click Compare. **A** is a common misconception — comparison is run-level, not experiment-level. **C** is wrong (no license gate on this feature). **D** is wrong (the experiments can have any names).

### Question 46 - **Answer: B**
ML training is sensitive to randomness at many levels: weight initialisation, train/test split, shuffle order, dropout masks, etc. Without fixing `np.random.seed(40)` AND `random_state=42` for both the split and the model (as chap03's `train.py` does), two runs with identical hyperparams can produce different metrics. **A** is wrong (MLflow records exactly what you log, no perturbation). **C** is wrong (MLflow's recording IS deterministic — only your code's training is not). **D** is wrong — non-determinism is exactly why setting seeds is a best practice.

### Question 47 - **Answer: B**
The whole purpose of training many models is to find the best one — which only makes sense if you can COMPARE them objectively. Without MLflow, the comparison happens in a developer's head or on a Post-it, and is lost the moment they close their laptop. MLflow makes comparison PERSISTENT (it survives reboots), SEARCHABLE (filter by `metrics.rmse < 0.7`), and SHAREABLE (your team can see the same UI). **A** misses the point (comparison speed vs training speed is irrelevant). **C** is wrong (MLflow does much more). **D** is wrong (GPU spending is unrelated).

---

## Section 5 - Tracking URI, hosts and config precedence

### Question 48 - **Answer: B**
When neither `mlflow.set_tracking_uri(...)` nor the env var `MLFLOW_TRACKING_URI` is set, MLflow defaults to `file:./mlruns` resolved against the current working directory. This is precisely why chap04's trainer writes to `/code/mlruns` inside the container (its WORKDIR is `/code`). **A** is wrong (no auto-server; MLflow does not magically start a server). **C** is wrong (sqlite is a metadata backend, not a default tracking URI). **D** is wrong (`databricks` is the default only when you `pip install databricks-cli` and authenticate).

### Question 49 - **Answer: C**
Docker Compose creates a bridge network (in our case `recap-net`) declared at the bottom of `docker-compose.yml`. For each service, Compose registers the SERVICE NAME as a DNS A-record on that network. So inside the `trainer` container, `mlflow` resolves to the IP address of the `mlflow` service container. **A** is wrong (no public DNS lookup happens). **B** is wrong (no manual `/etc/hosts` edit is done). **D** is wrong (MLflow has no hardcoded hostname; you can call your service `foo` and it would still work as long as the URI matches).

### Question 50 - **Answer: B**
When `mlflow.set_tracking_uri(...)` is called explicitly in Python, that value takes priority for the rest of the process (it overrides any env var). If `set_tracking_uri` is not called, MLflow reads `MLFLOW_TRACKING_URI`. If that env var is also unset, MLflow falls back to `file:./mlruns`. **A** is the exact reverse (default → env → code is wrong). **C** swaps default and code (also wrong). **D** is wrong because the precedence is deterministic and well-documented, not random.

---

## Appendix - Look-ahead questions

### Question B1 - **Answer: B**
A **model signature** in MLflow is a schema that describes the input columns and output columns the model expects, with their dtypes (`integer`, `double`, `string`, `boolean`, `binary`). At serving time, MLflow validates incoming requests against this schema and rejects malformed payloads with a clear error. **A** is wrong (no cryptographic signing is involved). **C** is wrong (author info goes in tags, not in the signature). **D** is wrong (git commit goes in tags via `mlflow.set_tag`). Signatures are covered in detail in chap14+.

### Question B2 - **Answer: B**
`mlflow.sklearn.log_model(...)` is a **framework-specific flavor** that knows how to (de)serialise sklearn estimators via cloudpickle and to reconstruct them at load time. `mlflow.pyfunc.log_model(...)` is the **universal flavor**: you provide a Python class implementing `predict(self, context, model_input)`, and MLflow wraps it generically — perfect for custom preprocessing pipelines, ensembles, or non-sklearn models. **A** is wrong (different APIs and different use cases). **C** is wrong (pyfunc is framework-agnostic, not TF-specific). **D** is wrong (sklearn flavor is the recommended path for sklearn models). Pyfunc is covered in detail in chap16+.

### Question B3 - **Answer: A**
The **Model Registry** is built on top of Tracking but adds versioning (v1, v2, v3, ...), stages (None, Staging, Production, Archived), aliases, descriptions, and webhooks for CI/CD pipelines. A registered model is a stable handle that your serving infrastructure can subscribe to, decoupled from the raw run that produced it. **B** is wrong (Registry and Tracking are distinct components with different APIs). **C** is wrong (Registry is part of MLflow OSS, Apache 2.0). **D** is wrong (Registry works with any backend the Tracking server supports). The Registry is covered in chap21+.

---

# How to use this answer key in class

1. Hand out the **questions-only** file (`...mcq.md`) to students.
2. Give them 30-45 minutes to answer individually or in pairs.
3. Run a debrief session: for each question, ask **one student** to defend their answer using the 4-sentence template (correct option + concept + why others are wrong + chapter reference).
4. Use the justifications in this file as the gold standard for the debrief.

**Recommended grading**:
- Correct option: **1 point**
- Correct option + correct justification of "why the other options are wrong": **2 points**
- Wrong option: **0 points**

Maximum score: 100 points across the 50 questions.

---

**End of answer key - 50 questions + 3 bonus, chapters 01 to 05.**
