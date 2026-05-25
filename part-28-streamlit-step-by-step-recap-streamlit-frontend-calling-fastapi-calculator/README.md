# chap28 - Step-by-step recap: Streamlit frontend calling FastAPI calculator

> [!TIP]
> **Objectif du chap28 — Faire dialoguer DEUX conteneurs : un front Streamlit qui appelle le backend FastAPI du chap27.**
>
> Tu vas :
> 1. Réutiliser exactement la calculatrice FastAPI du chap27 (`main.py`, port 8000).
> 2. Ajouter un **second service** dans `docker-compose.yml` : un front Streamlit (`app.py`, port 8501).
> 3. Mettre les deux services sur **le même réseau Docker** (`calc-net`) pour que Streamlit puisse appeler FastAPI par le nom de service `http://fastapi:8000` (et NON `http://localhost:8000`).
> 4. Utiliser `depends_on` + `healthcheck` pour que Streamlit ne démarre **qu'après** que FastAPI soit prêt à répondre.
> 5. Saisir deux nombres dans Streamlit, choisir une opération, cliquer sur **Calculer**, et voir Streamlit appeler FastAPI puis afficher le résultat.
>
> À la fin, tu sais brancher un front sur un backend dans une stack Docker Compose multi-services — c'est la base de toute application web moderne.

## Structure du projet

```
chap28-streamlit-step-by-step-recap-streamlit-frontend-calling-fastapi-calculator/
├── fastapi/
│   └── Dockerfile              <- python:3.12-slim + fastapi + uvicorn
├── streamlit/
│   ├── Dockerfile              <- python:3.12-slim + streamlit + requests
│   └── requirements.txt
├── docker-compose.yml          <- 2 services + réseau partagé "calc-net"
├── main.py                     <- backend FastAPI (4 endpoints calculatrice)
├── app.py                      <- front Streamlit qui appelle le backend
└── README.md
```

## Diagramme — qui parle à qui

```
       Toi (navigateur)
              |
              | http://localhost:8501
              v
   +----------------------+         http://fastapi:8000        +-----------------------+
   |  streamlit (app.py)  | ------------------------------->   |   fastapi (main.py)   |
   |   port 8501          |   <reseau Docker "calc-net">       |   port 8000           |
   +----------------------+         (resolution DNS)            +-----------------------+
```

> [!IMPORTANT]
> **Pourquoi `http://fastapi:8000` et pas `http://localhost:8000` ?**
>
> Dans Docker Compose, **`localhost` à l'intérieur d'un conteneur = ce conteneur lui-même**. Si Streamlit appelle `http://localhost:8000`, il parle à lui-même (port 8000 inexistant dans le conteneur Streamlit) → erreur de connexion.
>
> Sur un même réseau Docker (`calc-net`), chaque service est joignable par **son nom de service** (`fastapi`) qui est résolu en DNS interne. C'est la même idée que `mlflow` + `trainer` dans le `chap04`.

## What's new vs chap27

| | chap27 | chap28 |
|---|---|---|
| Services | `fastapi` seul | `fastapi` + `streamlit` |
| Réseau | défaut | `calc-net` (bridge dédié) |
| `depends_on` | ❌ | ✅ avec `condition: service_healthy` |
| `healthcheck` FastAPI | ❌ | ✅ |
| Variable d'env | ❌ | `API_URL=http://fastapi:8000` |
| Front | aucun | Streamlit (`app.py`) |

## Run it (100% Docker, no Python on the host)

```bash
# 1. Lis les fichiers Dockerfile, docker-compose.yml, main.py, app.py
#    pour comprendre comment les deux services sont configures et comment
#    Streamlit appelle FastAPI via le reseau Docker interne.

cd chap28-streamlit-step-by-step-recap-streamlit-frontend-calling-fastapi-calculator

# 2. Demarre les DEUX services en mode detache (build + up).
docker compose up -d --build
# Streamlit attend que FastAPI soit "healthy" grace au depends_on.
# Surveille les logs si besoin :
#   docker compose logs -f

# 3. Verifie les deux URLs :
#   Backend FastAPI Swagger UI  : http://localhost:8000/docs
#   Frontend Streamlit          : http://localhost:8501

# 4. Sur l'UI Streamlit :
#    - Clique sur "Tester la connexion" (sidebar) -> doit afficher le JSON
#      de bienvenue du backend.
#    - Saisis deux nombres, choisis une operation, clique sur "Calculer".
#    - Le resultat s'affiche, calcule par FastAPI.

# 5. Stoppe les deux services quand tu as fini.
docker compose down
```

## Tester en ligne de commande (sans Streamlit)

Tu peux aussi prouver que les deux conteneurs partagent bien un réseau en exécutant `curl` depuis le conteneur Streamlit vers le conteneur FastAPI :

```bash
docker compose exec streamlit python -c "import requests; print(requests.get('http://fastapi:8000/add/40/2').json())"
# {'operation': 'addition', 'a': 40.0, 'b': 2.0, 'result': 42.0}
```

## Hot reload

- **FastAPI** : `uvicorn --reload` + bind mount `.:/app` -> modifie `main.py`, le serveur redémarre seul.
- **Streamlit** : bind mount `.:/front` -> modifie `app.py`, l'UI propose un bouton "Rerun" (ou actualise toute seule selon la config).

## Recap

```bash
cd chap28-streamlit-step-by-step-recap-streamlit-frontend-calling-fastapi-calculator
docker compose up -d --build
# -> http://localhost:8501  (front)
# -> http://localhost:8000/docs  (backend Swagger)
docker compose down
```

## Recap +

```bash
cd chap28-streamlit-step-by-step-recap-streamlit-frontend-calling-fastapi-calculator
docker compose up -d --build

# Verifier que les 2 conteneurs tournent :
docker compose ps

# Suivre les logs des deux en parallele :
docker compose logs -f

# Verifier que streamlit "voit" fastapi par son nom de service :
docker compose exec streamlit python -c "import requests; print(requests.get('http://fastapi:8000/').status_code)"
# 200

# Entrer dans un conteneur pour explorer (equivalent docker exec) :
# docker exec -it <id> bash
# ls
# Pour recuperer le <id> -> docker ps
# exit

docker compose down
```

# Troubleshooting - killing the zombies

<details>
   <summary> Troubleshooting </summary>

> Sur Windows, pour tuer le processus qui occupe le port **8000** ou **8501** :

```bat
netstat -ano | findstr :8000
netstat -ano | findstr :8501
```

Tu verras quelque chose comme :

```bat
TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    12345
```

Le dernier nombre est le **PID**. Tue-le :

```bat
taskkill /PID 12345 /F
```

> Version PowerShell :

```powershell
Get-NetTCPConnection -LocalPort 8000
Get-NetTCPConnection -LocalPort 8501
Stop-Process -Id 12345 -Force
```

> **Erreur "Connection refused" depuis Streamlit ?**
>
> Vérifie ces points dans l'ordre :
> 1. Les deux services sont sur le même réseau (`calc-net`) ?
> 2. La variable `API_URL` côté Streamlit vaut bien `http://fastapi:8000` (pas `localhost`) ?
> 3. Le service backend s'appelle bien `fastapi` dans `docker-compose.yml` (le nom est utilisé comme hostname) ?
> 4. Le `healthcheck` du service `fastapi` passe-t-il ? (`docker compose ps` doit afficher `healthy`)

</details>
