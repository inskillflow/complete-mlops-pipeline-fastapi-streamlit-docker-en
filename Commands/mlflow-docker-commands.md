# Docker + MLflow Training Commands

> [!IMPORTANT]
> Before starting, make sure Docker Desktop is already running.

---

## COMMANDS

### 01 — Clone the repository

```bash
git clone https://github.com/inskillflow/complete-mlops-pipeline-fastapi-streamlit-docker-en.git
```

### 02 — Go inside the project folder

```bash
cd .\complete-mlops-pipeline-fastapi-streamlit-docker-en\
```

### 03 — Go inside the training folder

```bash
cd .\part-04-mlflow-step-by-step-recap-running-the-training-in-docker\
```

### 04 — Check your current directory

```bash
pwd
```

> [!TIP]
> This command helps you verify that you are inside the correct project folder.

---

## Step 1 — Verify Docker

### 05 — Instruction 1

> [!IMPORTANT]
> Please be sure that you've started your docker Desktop.
>  
> This is not a command.

### 06 — Check Docker version

```bash
docker --version
```

### 07 — Check Docker Compose version

```bash
docker compose version
```

### 08 — Check running containers

```bash
docker ps
```

---

## Step 2 — Start MLflow

### 09 — Start the MLflow service

```bash
docker compose up -d --build mlflow
```

### 10 — Verify running containers

```bash
docker ps
```

---

## Step 3 — Run training experiments

### 11 — Run experiment 1

```bash
docker compose run --rm trainer --alpha 0.1 --l1_ratio 0.1
```

### 11 — Run experiment 2

```bash
docker compose run --rm trainer --alpha 0.5 --l1_ratio 0.5
```

### 12 — Run experiment 3

```bash
docker compose run --rm trainer --alpha 0.9 --l1_ratio 0.1
```

---

## Step 4 — Observe MLflow

### 13 — Instruction 2

> [!TIP]
> Obeserve the result in:
>
> http://localhost:5000/

### 14 — Instruction 3

> [!WARNING]
> The experiments are not showing.
>
> Explain why.
>
> You may have a look on `docker-compose-option2.yml_`

---

## Step 5 — Stop and clean Docker containers

### 15 — Stop Docker Compose services

```bash
docker compose down
```

### 16 — Stop all Docker containers

```bash
docker stop $(docker ps -a -q)
```

### 17 — Remove all Docker containers

```bash
docker rm $(docker ps -a -q)
```

> [!CAUTION]
> These commands stop and remove all containers on your machine.
>
> Use them carefully if you have other Docker projects running.

---

## Step 6 — Run the second Docker Compose configuration

### 18 — Start services with `docker-compose-option2.yml`

```bash
docker compose -f docker-compose-option2.yml up -d --build
```

### 19 — Run experiment 1

```bash
docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.1 --l1_ratio 0.1
```

### 20 — Run experiment 2

```bash
docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.5 --l1_ratio 0.5
```

### 21 — Run experiment 3

```bash
docker compose -f docker-compose-option2.yml run --rm trainer --alpha 0.9 --l1_ratio 0.1
```

---

## Step 7 — Observe MLflow again

### 22 — Instruction 4

> [!TIP]
> Obeserve the result in:
>
> http://localhost:5000/

### 23 — Instruction 5

> [!IMPORTANT]
> Are the experiments showing now?
>
> What was the error in `docker-compose.yml`?

---

## Step 8 — Stop the second Docker Compose configuration

```bash
docker compose -f docker-compose-option2.yml down
```

---

# USEFUL COMMANDS FOR TROUBELSHOOTING

> [!TIP]
> Use these commands when Docker containers are not behaving as expected.

## Stop Docker Compose services

```bash
docker compose down
```

## Show all containers

```bash
docker ps -a
```

## Stop all containers

```bash
docker stop $(docker ps -a -q)
```

## Remove all containers

```bash
docker rm $(docker ps -a -q)
```

## Verify containers again

```bash
docker ps -a
```

## Restart MLflow

```bash
docker compose up -d --build mlflow
```

> [!CAUTION]
> `docker stop $(docker ps -a -q)` and `docker rm $(docker ps -a -q)` affect all containers.
>
> Do not run them if you want to keep other Docker projects active.
