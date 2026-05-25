# chap27 - Step-by-step recap: Hello FastAPI (Calculatrice)

> [!TIP]
> **Objectif du chap27 — Faire tourner FastAPI pour la toute première fois.**
>
> Tu vas :
> 1. Construire et démarrer un serveur **FastAPI 100 % dans Docker** (aucun Python sur l'hôte).
> 2. Ouvrir la documentation interactive Swagger sur `http://localhost:8000/docs`.
> 3. Appeler **une petite API calculatrice** (`/add`, `/subtract`, `/multiply`, `/divide`) directement depuis ton navigateur ou avec `curl`.
> 4. Modifier `main.py` à chaud (hot reload via `uvicorn --reload`) sans rebuild de l'image, grâce au bind mount `.:/app`.
>
> À la fin, tu sais démarrer un FastAPI propre, l'arrêter avec `docker compose down`, et tu reconnais la pile `fastapi + uvicorn + bind mount` qui sert de base à tous les chapitres FastAPI suivants.

## Structure du projet

```
chap27-fastapi-step-by-step-recap-hello-fastapi-calculator/
├── fastapi/
│   └── Dockerfile              <- image Python 3.12 + fastapi + uvicorn
├── docker-compose.yml          <- service "fastapi" sur le port 8000
├── main.py                     <- l'API calculatrice (4 endpoints)
└── README.md
```

## Run it (100% Docker, no Python on the host)

```bash
# 1. Lis le Dockerfile et le docker-compose.yml pour comprendre comment
#    le serveur FastAPI est configuré (uvicorn écoute sur 0.0.0.0:8000,
#    bind mount .:/app pour voir main.py et activer le hot reload).

cd chap27-fastapi-step-by-step-recap-hello-fastapi-calculator

# 2. Démarre le serveur FastAPI en mode détaché.
docker compose up -d --build
# Vérifie ces URLs :
#   http://localhost:8000          -> message d'accueil JSON
#   http://localhost:8000/docs     -> Swagger UI (documentation interactive)
#   http://localhost:8000/redoc    -> ReDoc (documentation alternative)

# 3. Teste les endpoints depuis ton navigateur ou en ligne de commande :
curl http://localhost:8000/add/2/3
# {"operation":"addition","a":2.0,"b":3.0,"result":5.0}

curl http://localhost:8000/subtract/10/4
# {"operation":"subtraction","a":10.0,"b":4.0,"result":6.0}

curl http://localhost:8000/multiply/6/7
# {"operation":"multiplication","a":6.0,"b":7.0,"result":42.0}

curl http://localhost:8000/divide/10/2
# {"operation":"division","a":10.0,"b":2.0,"result":5.0}

curl http://localhost:8000/divide/10/0
# {"detail":"Division par zéro impossible"}

# 4. Stoppe le serveur quand tu as fini.
docker compose down
```

## Pourquoi `uvicorn --reload` ?

Le `Dockerfile` lance uvicorn avec l'option `--reload` :

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Combiné au bind mount `.:/app` du `docker-compose.yml`, **chaque modification de `main.py` sur ton hôte est détectée et le serveur redémarre automatiquement** — pas besoin de rebuild de l'image pour tester un changement.

## Tester le hot reload

1. Garde le conteneur en marche (`docker compose up -d`).
2. Ouvre `http://localhost:8000` -> tu vois `"Bienvenue sur la calculatrice FastAPI"`.
3. Édite `main.py` et change le message d'accueil, par exemple :

```python
@app.get("/")
def read_root():
    return {"message": "Salut, ça marche !"}
```

4. Sauvegarde, rafraîchis la page -> le nouveau message s'affiche **sans rebuild ni restart manuel**.

Tu peux suivre le redémarrage dans les logs :

```bash
docker compose logs -f fastapi
```

## Recap

```bash
cd chap27-fastapi-step-by-step-recap-hello-fastapi-calculator
docker compose up -d --build
# -> http://localhost:8000/docs
docker compose down
```

## Recap +

```bash
cd chap27-fastapi-step-by-step-recap-hello-fastapi-calculator
docker compose up -d --build

# Tester quelques endpoints :
curl http://localhost:8000/
curl http://localhost:8000/add/40/2
curl http://localhost:8000/divide/1/0   # erreur 400 contrôlée

# Entrer dans le conteneur (équivalent docker exec) :
# docker exec -it <id> bash
# ls
# Pour récupérer le <id> -> docker ps
# exit

docker compose down
```

# Troubleshooting - killing the zombies

<details>
   <summary> Troubleshooting </summary>

> Sur Windows, pour tuer le processus qui occupe le port **8000** :

```bat
netstat -ano | findstr :8000
```

Tu verras quelque chose comme :

```bat
TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    12345
```

Le dernier nombre est le **PID**. Tue-le :

```bat
taskkill /PID 12345 /F
```

Séquence complète :

```bat
netstat -ano | findstr :8000
taskkill /PID 12345 /F
```

Pour vérifier quelle application c'est avant de la tuer :

```bat
tasklist | findstr 12345
```

> Version PowerShell :

```powershell
Get-NetTCPConnection -LocalPort 8000
Stop-Process -Id 12345 -Force
```

> Le port **8000** est comme une porte utilisée par une application. Si une autre instance d'uvicorn, Flask, Django ou un autre serveur l'utilise déjà, FastAPI ne pourra pas démarrer dessus. `netstat` trouve qui occupe la porte, et `taskkill` arrête ce processus.

</details>
