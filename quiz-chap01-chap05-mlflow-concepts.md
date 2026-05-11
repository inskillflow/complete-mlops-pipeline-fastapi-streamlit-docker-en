# Quiz - chap01 à chap05 - Pourquoi MLflow, concepts fondamentaux et premier pipeline

50 questions sans réponses, à compléter individuellement ou en classe.

Les questions couvrent :

- chap01 - Hello MLflow basics
- chap02 - Print the tracking URI
- chap03 - ElasticNet sur red-wine-quality
- chap04 - Le trainer dans un deuxième service Docker
- chap05 - Passer le tracking URI via une variable d'environnement

Les thèmes sont organisés en 6 sections : **pourquoi MLflow**, **concepts MLflow fondamentaux**, **tracking URI & backend**, **Docker & Docker Compose**, **pipeline ML ElasticNet**, **variables d'environnement & 12-factor**.

> [!TIP]
> Format : réponds dans tes propres mots, sans copier-coller le code. Pour les questions "VRAI / FAUX", justifie ta réponse en une phrase. Pour les questions à choix multiples, encercle la bonne réponse **et** explique pourquoi les autres sont fausses.

---

## Section 1 - Pourquoi MLflow ? (intérêt, motivation, contexte MLOps)

### Question 1
En une ou deux phrases, explique ce qu'est MLflow et le problème **principal** qu'il vient résoudre dans un projet de machine learning.

### Question 2
Cite **trois douleurs concrètes** qu'un data scientist rencontre **sans** MLflow (par exemple : "j'ai oublié quels hyperparamètres ont produit mon meilleur modèle de la semaine dernière"). Donne pour chacune une phrase courte décrivant le problème.

### Question 3
MLflow se décompose en plusieurs composants : **Tracking**, **Projects**, **Models**, **Model Registry**. Sur lequel de ces quatre composants se concentrent les chapitres 01 à 05 du cours ? Justifie en une phrase.

### Question 4
**VRAI / FAUX** : MLflow est une bibliothèque uniquement Python.
Justifie ta réponse en une phrase (pense aux langages supportés et au protocole de communication).

### Question 5
Pourquoi est-il important de pouvoir **comparer plusieurs runs côte à côte** dans une UI plutôt que de simplement imprimer les métriques dans la console ? Donne au moins deux raisons concrètes.

### Question 6
**Question piège** : un collègue te dit "moi je n'ai pas besoin de MLflow, je mets tout dans un Excel avec date, alpha, l1_ratio et rmse". Cite **trois choses** que cette approche Excel **ne peut pas** faire et que MLflow fait par défaut.

### Question 7
À quoi sert le concept d'**expérience** (`experiment`) dans MLflow ? En quoi est-ce différent d'un **run** ?

### Question 8
Dans la philosophie MLOps, on parle souvent de **reproductibilité**. Cite **deux mécanismes** vus dans les chapitres 01 à 05 qui contribuent directement à la reproductibilité d'un résultat ML.

### Question 9
Pourquoi le cours impose-t-il dès chap01 de faire tourner MLflow **dans Docker** plutôt que de faire `pip install mlflow` directement sur la machine de l'étudiant ? Donne au moins deux raisons.

---

## Section 2 - Concepts MLflow fondamentaux

### Question 10
À quoi sert l'appel `mlflow.start_run()` ? Que se passe-t-il si on appelle `mlflow.log_param("alpha", 0.5)` **sans** avoir ouvert un run avant ?

### Question 11
Quelle est la différence entre `mlflow.log_param(...)` et `mlflow.log_metric(...)` ? Donne un exemple de chacune dans le contexte d'ElasticNet.

### Question 12
**VRAI / FAUX** : on peut logger plusieurs valeurs successives pour la **même** métrique dans **un seul run** (par exemple `rmse` au fil des époques).
Justifie ta réponse.

### Question 13
Dans le code du chap03, on appelle `mlflow.sklearn.log_model(lr, "mymodel")`. Que produit cet appel sur disque ? Cite au moins **deux fichiers ou dossiers** que tu verras dans le dossier `artifacts/mymodel/` du run dans l'UI.

### Question 14
Cite **trois informations** que MLflow capture **automatiquement** pour chaque run (sans que tu aies besoin de les logger explicitement).

### Question 15
Quel est le rôle du `run_id` ? Pourquoi est-ce un UUID et pas un entier auto-incrémenté simple ?

### Question 16
À quoi servent les **tags** sur un run ou sur une expérience ? Cite deux exemples concrets de tags utiles (ex. : `git_commit=...`).

### Question 17
Dans la console du chap03, après chaque run on voit `RMSE`, `MAE` et `R²`. Pour chacune de ces métriques, indique :
- ce qu'elle mesure,
- si on veut la **maximiser** ou la **minimiser**.

### Question 18
**Question conceptuelle** : pourquoi MLflow sépare-t-il **clairement** la base de métadonnées (qui contient _alpha=0.5, rmse=0.74, run_id=abc..._) du stockage des artefacts (qui contient _le modèle pickle, les graphes, les CSV_) ? Cite au moins une raison technique.

---

## Section 3 - Tracking URI & backend de stockage

### Question 19
Que retourne `mlflow.get_tracking_uri()` dans le chap02 quand on n'a **rien** configuré ? Donne la valeur exacte que tu attends de voir imprimée.

### Question 20
Cite **trois schémas d'URI** valides pour `mlflow.set_tracking_uri(...)` et explique en une phrase à quoi chacun correspond (`file://`, `http://`, `https://`, `databricks`, etc.).

### Question 21
**VRAI / FAUX** : si je ne mets aucun `set_tracking_uri` et aucune variable d'environnement, MLflow refuse de tourner et lève une exception.
Justifie.

### Question 22
Dans chap04, le trainer écrit ses runs dans `file:///code/mlruns`. Pourquoi ces runs **n'apparaissent jamais** dans l'UI à `http://localhost:5000` ? Explique le mécanisme en 3 ou 4 phrases.

### Question 23
Quel est le rôle de l'option `--backend-store-uri` quand on démarre `mlflow server` ? Et de l'option `--default-artifact-root` ?

### Question 24
Pourquoi le cours utilise-t-il **SQLite** comme backend de métadonnées dans chap01-05 plutôt que **Postgres** ou **MySQL** ? Cite au moins deux avantages dans un contexte pédagogique.

### Question 25
**Scénario** : tu vois cette ligne dans la console du chap05 :

```text
Tracking URI: http://mlflow:5000
```

Pourquoi le nom d'hôte est **`mlflow`** et non pas **`localhost`** ou **`127.0.0.1`** ? Que se passerait-il si on essayait `http://localhost:5000` depuis le conteneur trainer ?

### Question 26
Cite l'**ordre de priorité** entre ces trois sources de configuration du tracking URI :
- variable d'environnement `MLFLOW_TRACKING_URI`,
- appel explicite à `mlflow.set_tracking_uri(...)` dans le code,
- valeur par défaut de MLflow.

---

## Section 4 - Docker, Docker Compose et architecture du cours

### Question 27
Quelle est la différence entre `docker compose up`, `docker compose up -d` et `docker compose up -d --build` ? Explique chaque variante en une ligne.

### Question 28
Dans `docker-compose.yml` du chap01, on a :

```yaml
volumes:
  - ./database:/mlflow/database
  - ./mlruns:/mlflow/mlruns
```

Quelle est la différence entre ce type de mount et les **volumes nommés** du chap04 (`mlflow-db:/mlflow/database`) ? Donne au moins deux différences concrètes.

### Question 29
Pourquoi le `Dockerfile` du serveur MLflow contient-il `EXPOSE 5000` ? Cela **ouvre-t-il vraiment** un port sur l'hôte ? Justifie.

### Question 30
À quoi sert le bloc `healthcheck` dans le service `mlflow` de `docker-compose.yml` ?

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "..."]
  interval: 10s
  retries: 5
```

Et pourquoi le service `trainer` (chap04+) a-t-il `depends_on: mlflow: { condition: service_healthy }` au lieu de simplement `depends_on: [mlflow]` ?

### Question 31
Différence entre `docker compose exec mlflow python train.py` (chap01-03) et `docker compose run --rm trainer --alpha 0.1` (chap04+). Pour chaque commande, indique :
- est-ce que le conteneur existait déjà avant la commande ?
- est-ce qu'il survit après la commande ?

### Question 32
Pourquoi utilise-t-on `--rm` avec `docker compose run` ? Que se passe-t-il sans `--rm` après 20 entraînements ?

### Question 33
Dans `docker-compose.yml` du chap04, on déclare un réseau `recap-net` partagé entre `mlflow` et `trainer`. Pourquoi est-ce **obligatoire** pour que le trainer puisse joindre le serveur via l'URL `http://mlflow:5000` ?

### Question 34
Pourquoi le serveur MLflow et le trainer ont chacun **leur propre `Dockerfile`** et **leur propre `requirements.txt`** à partir du chap04 ? Donne au moins deux avantages de cette séparation.

### Question 35
Que fait l'instruction `ENTRYPOINT ["python", "train.py"]` dans le `Dockerfile` du trainer ? Et que se passe-t-il quand on fait `docker compose run --rm trainer --alpha 0.4 --l1_ratio 0.6` ? Explique ce qui est concaténé.

### Question 36
**VRAI / FAUX** : sans `--build`, `docker compose up -d` ne reconstruit jamais l'image, même si tu as modifié le `Dockerfile`.
Justifie.

---

## Section 5 - Le pipeline ML ElasticNet (chap03 et au-delà)

### Question 37
À quoi sert `train_test_split` ? Pourquoi est-il **dangereux** de ne pas le faire et de simplement entraîner sur tout le dataset ?

### Question 38
Que représentent les hyperparamètres `alpha` et `l1_ratio` dans `ElasticNet` ? Que se passe-t-il quand :
- `l1_ratio = 0` ?
- `l1_ratio = 1` ?

### Question 39
Pourquoi `np.random.seed(40)` et `random_state=42` apparaissent-ils dans `train.py` ? Quel concept MLOps cela renforce-t-il ?

### Question 40
Dans le chap03, on lance trois runs avec `(alpha, l1_ratio)` = `(0.1, 0.1)`, `(0.5, 0.5)` et `(0.9, 0.1)`. Selon toi, lequel des trois aura **le meilleur RMSE** sur le test set ? Justifie ton intuition **avant** d'aller voir le résultat dans l'UI.

### Question 41
Quelle est l'utilité d'`argparse` dans `train.py` ? Pourquoi est-ce **mieux** que de coder en dur `alpha = 0.5` au début du script ?

### Question 42
Quand on appelle `mlflow.sklearn.log_model(lr, "mymodel")`, MLflow sérialise le modèle. Cite la **bibliothèque de sérialisation** par défaut utilisée par MLflow pour les modèles sklearn, et explique en une phrase pourquoi elle est préférée à un simple `pickle.dump`.

### Question 43
Comment recharger un modèle MLflow déjà loggué pour faire des prédictions sur de nouvelles données ? Donne l'**appel d'API exact** (pseudo-code Python suffit).

---

## Section 6 - Variables d'environnement, 12-factor, et le pattern config

### Question 44
Que fait exactement l'appel `os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")` dans le chap05 ? Décris **le comportement dans les trois cas** :
- la variable est définie à `http://prod-mlflow:5000`,
- la variable est définie mais vide,
- la variable n'existe pas du tout.

### Question 45
Le pattern utilisé dans chap05 (config via variable d'environnement, jamais en dur dans le code) vient de la méthodologie **12-factor app**. Pourquoi est-ce une bonne idée en production ? Cite au moins deux raisons concrètes.

### Question 46
Dans `docker-compose.yml` du chap05, on a :

```yaml
trainer:
  environment:
    MLFLOW_TRACKING_URI: "http://mlflow:5000"
```

Cite **trois autres façons** d'injecter la même variable dans le conteneur trainer (sans modifier `docker-compose.yml`).

### Question 47
**Scénario** : tu lances `docker compose run --rm -e MLFLOW_TRACKING_URI=http://other-server:5000 trainer --alpha 0.4 --l1_ratio 0.4`. Quelle URI sera **effectivement** utilisée par le run ? Pourquoi ?

### Question 48
Pourquoi est-il préférable de mettre la valeur `http://mlflow:5000` dans `docker-compose.yml` plutôt que d'écrire `mlflow.set_tracking_uri("http://mlflow:5000")` directement dans `train.py` ? Cite au moins **deux scénarios** où la version "en dur dans le code" devient problématique.

### Question 49
Le serveur MLflow du chap05 utilise toujours **SQLite + bind/volume nommé** pour stocker les runs. **VRAI / FAUX** : si tu veux passer en Postgres, il suffit de changer la valeur de `MLFLOW_TRACKING_URI` côté trainer.
Justifie ta réponse (indice : pense à `--backend-store-uri` côté serveur).

### Question 50
**Question de synthèse** (longue réponse).
Imagine que tu doives présenter en 5 minutes à un nouveau collègue **pourquoi** ton équipe a choisi MLflow + Docker pour vos projets ML. Structure ta réponse autour des trois axes vus dans chap01-05 :
1. ce que MLflow apporte (traçabilité, comparaison, artefacts) ;
2. ce que Docker apporte (reproductibilité, isolation, déploiement) ;
3. ce que **le combo `MLflow + Docker + variable d'environnement`** apporte de plus (portabilité dev → staging → prod) ?

Conclus par **une limite ou un défi** de cette approche que tu vois venir (par exemple : multi-utilisateurs, sécurité, scalabilité, coût de stockage des artefacts, etc.).

---

# Annexe - Pour aller plus loin (questions bonus, hors-quiz)

- **B1.** Qu'est-ce qu'une **signature de modèle** dans MLflow ? À quoi ça sert ? (vu en détail au chap14+)
- **B2.** Quelle est la différence entre `mlflow.sklearn.log_model` et `mlflow.pyfunc.log_model` ? (vu au chap16+)
- **B3.** Qu'est-ce que le **Model Registry** de MLflow ? Pourquoi ce concept apparaît-il **après** le tracking ? (vu au chap21+)

---

**Fin du quiz - 50 questions, chapitres 01 à 05.**

Bonne révision !
