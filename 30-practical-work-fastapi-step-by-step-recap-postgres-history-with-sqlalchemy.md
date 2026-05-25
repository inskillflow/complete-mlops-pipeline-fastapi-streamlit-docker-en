# chap30 - Step-by-step recap: PostgreSQL history with SQLAlchemy

> [!TIP]
> **Objectif du chap30 — Persister l'historique des calculs dans une vraie base PostgreSQL.**
>
> Tu vas :
> 1. Ajouter un **3ème service** dans `docker-compose.yml` : `postgres:16-alpine` avec un bind mount `./pgdata` pour que les données survivent à `docker compose down`.
> 2. Brancher FastAPI à PostgreSQL via **SQLAlchemy 2.0** (avec le driver moderne `psycopg[binary]`).
> 3. Définir un model ORM `Calculation` (`id`, `operation`, `a`, `b`, `result`, `created_at`) et le créer automatiquement au démarrage avec `Base.metadata.create_all()`.
> 4. À chaque `POST /calculate`, **insérer une ligne en base** et la renvoyer dans la réponse (avec son `id` auto-généré et son `created_at`).
> 5. Ajouter `GET /history?limit=N` qui renvoie les N derniers calculs, et `DELETE /history` pour vider la table.
> 6. Côté Streamlit : un nouvel onglet **"Historique"** qui affiche le tableau (via `pandas.DataFrame` + `st.dataframe`) et un bouton "Vider".
>
> À la fin, tu sais brancher une API FastAPI à une vraie BDD relationnelle, gérer la session DB avec `Depends(get_db)`, et chaîner 3 services Docker (`postgres → fastapi → streamlit`) avec `depends_on` + `healthcheck`.

## Structure du projet

```
chap30-fastapi-step-by-step-recap-postgres-history-with-sqlalchemy/
├── fastapi/
│   ├── Dockerfile              <- python:3.12 + fastapi + sqlalchemy + psycopg
│   └── requirements.txt
├── streamlit/
│   ├── Dockerfile              <- python:3.12 + streamlit + requests + pandas
│   └── requirements.txt
├── docker-compose.yml          <- 3 services (postgres + fastapi + streamlit)
├── main.py                     <- backend + ORM Calculation + /calculate + /history
├── app.py                      <- front Streamlit avec 2 onglets (Calculer / Historique)
├── pgdata/                     <- bind mount Postgres (cree au 1er run)
└── README.md
```

## Diagramme — qui parle à qui

```
       Toi (navigateur)
              |
              | http://localhost:8501
              v
   +----------------------+    http://fastapi:8000     +-----------------------+   postgres://...   +-------------------+
   |  streamlit (app.py)  | -------------------------> |   fastapi (main.py)   | ---------------->  |  postgres:5432    |
   |   port 8501          |                            |   port 8000           |                    |   table:           |
   |                      |                            |   SQLAlchemy ORM      |                    |   calculations     |
   +----------------------+                            +-----------------------+                    +-------------------+
                                                       <-- reseau Docker calc-net (DNS interne) --->
```

## What's new vs chap29

| | chap29 | chap30 |
|---|---|---|
| Services | `fastapi` + `streamlit` | **`postgres`** + `fastapi` + `streamlit` |
| Persistance | aucune (RAM) | **PostgreSQL** + bind mount `./pgdata` |
| ORM | aucun | **SQLAlchemy 2.0** (`DeclarativeBase`, `Mapped[...]`) |
| Driver | n/a | `psycopg[binary]` (psycopg 3 moderne) |
| Endpoints en plus | — | `GET /history`, `DELETE /history` |
| Front | 1 page | **2 onglets** : Calculer / Historique |
| Affichage tableau | — | **`pandas.DataFrame` + `st.dataframe`** |

## Le concept clé : SQLAlchemy 2.0 + Depends(get_db)

```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://calc:calc@postgres:5432/calc",  # postgres = nom du service Docker
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Calculation(Base):
    __tablename__ = "calculations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation: Mapped[str] = mapped_column(String(16))
    a: Mapped[float] = mapped_column(Float)
    b: Mapped[float] = mapped_column(Float)
    result: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/calculate", response_model=CalculationResponse)
def calculate(payload: CalculationRequest, db: Session = Depends(get_db)):
    record = Calculation(operation=..., a=..., b=..., result=...)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
```

> [!IMPORTANT]
> **Pourquoi `postgres` dans l'URL ?**
>
> Pareil qu'au chap28 pour FastAPI : sur le réseau Docker `calc-net`, le **nom de service** est résolu en DNS interne. Ton `DATABASE_URL` pointe donc vers `postgres:5432`, le nom du conteneur Postgres défini dans `docker-compose.yml`. Si tu utilises l'app **depuis ton hôte** (dehors de Docker), tu utiliserais `localhost:5432` à la place.

## Run it (100% Docker, no Python on the host)

```bash
cd chap30-fastapi-step-by-step-recap-postgres-history-with-sqlalchemy

# 1. Build + up des 3 services. L'ordre est garanti par depends_on :
#    postgres -> fastapi (quand healthy) -> streamlit (quand fastapi healthy).
docker compose up -d --build

# 2. Verifier les URLs :
#    Swagger UI                     : http://localhost:8000/docs
#    Streamlit (onglets)            : http://localhost:8501
#    Postgres (avec un client SQL)  : localhost:5432  (user/pass/db = calc/calc/calc)

# 3. Faire 3 calculs depuis Streamlit ou via curl :
curl -X POST http://localhost:8000/calculate -H "Content-Type: application/json" -d '{"a":10,"b":2,"operation":"add"}'
curl -X POST http://localhost:8000/calculate -H "Content-Type: application/json" -d '{"a":7,"b":6,"operation":"multiply"}'
curl -X POST http://localhost:8000/calculate -H "Content-Type: application/json" -d '{"a":1,"b":4,"operation":"subtract"}'

# 4. Lister l'historique :
curl http://localhost:8000/history
# [{"id":3,"operation":"subtract","a":1.0,"b":4.0,"result":-3.0,"created_at":"..."}, ...]

# 5. Stop. Les donnees Postgres SURVIVENT dans ./pgdata.
docker compose down

# 6. Relancer -> l'historique est toujours la, prouvant la persistance disque :
docker compose up -d
curl http://localhost:8000/history     # mêmes lignes qu'avant

# 7. Tout nettoyer (DESTRUCTIF) :
docker compose down
rm -rf pgdata
```

## Ouvrir la base avec psql (sans installer psql sur l'hote)

```bash
docker compose exec postgres psql -U calc -d calc
\dt                       -- liste les tables
SELECT * FROM calculations ORDER BY id DESC LIMIT 5;
\q
```

## Tester via le conteneur Streamlit (prouver le DNS Docker)

```bash
docker compose exec streamlit python -c "import requests; print(requests.get('http://fastapi:8000/history').json())"
```

## Recap

```bash
cd chap30-fastapi-step-by-step-recap-postgres-history-with-sqlalchemy
docker compose up -d --build
# -> http://localhost:8501          (front avec onglets Calculer / Historique)
# -> http://localhost:8000/docs     (Swagger : /calculate /history /history DELETE)
docker compose down
# Donnees toujours sur le disque dans ./pgdata
```

## Recap +

```bash
cd chap30-fastapi-step-by-step-recap-postgres-history-with-sqlalchemy
docker compose up -d --build

# Verifier que les 3 conteneurs tournent et sont healthy :
docker compose ps

# Logs en parallele :
docker compose logs -f

# Faire un calcul et le voir directement en SQL :
curl -X POST http://localhost:8000/calculate -H "Content-Type: application/json" -d '{"a":42,"b":1,"operation":"add"}'
docker compose exec postgres psql -U calc -d calc -c "SELECT * FROM calculations;"

# Persistance : redemarrer toute la stack et verifier que l'historique survit :
docker compose down
docker compose up -d
curl http://localhost:8000/history

docker compose down
```

# Troubleshooting - killing the zombies

<details>
   <summary> Troubleshooting </summary>

> Sur Windows, pour tuer les processus qui occupent les ports **8000**, **8501** ou **5432** :

```bat
netstat -ano | findstr :8000
netstat -ano | findstr :8501
netstat -ano | findstr :5432
taskkill /PID 12345 /F
```

> Version PowerShell :

```powershell
Get-NetTCPConnection -LocalPort 8000
Get-NetTCPConnection -LocalPort 8501
Get-NetTCPConnection -LocalPort 5432
Stop-Process -Id 12345 -Force
```

> **Le conteneur fastapi crash au démarrage avec une erreur de connexion DB ?**
>
> 1. Vérifie que `postgres` est bien `healthy` (`docker compose ps`).
> 2. Le `depends_on: postgres: condition: service_healthy` doit être présent dans `docker-compose.yml` côté `fastapi`.
> 3. La `DATABASE_URL` côté FastAPI doit pointer vers `postgres` (le nom du service), pas `localhost`.
> 4. Si `./pgdata` a été créé avec un mauvais owner (Linux), supprime-le et relance.

> **Le port 5432 est déjà pris ?** Tu as probablement un Postgres local qui tourne sur ton hôte. Soit tu l'arrêtes, soit tu changes le mapping dans `docker-compose.yml` :
> ```yaml
> ports:
>   - "5433:5432"   # 5433 cote hote -> 5432 cote conteneur
> ```
> (le service interne `postgres` continue d'écouter sur 5432, donc l'URL côté FastAPI ne change pas).

</details>
