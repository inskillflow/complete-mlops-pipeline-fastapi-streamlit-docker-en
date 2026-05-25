from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Hello FastAPI - Calculatrice",
    description="Premier projet FastAPI : une calculatrice simple pour apprendre les bases.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur la calculatrice FastAPI",
        "docs": "http://localhost:8000/docs",
        "endpoints": ["/add", "/subtract", "/multiply", "/divide"],
    }


@app.get("/add/{a}/{b}")
def add(a: float, b: float):
    return {"operation": "addition", "a": a, "b": b, "result": a + b}


@app.get("/subtract/{a}/{b}")
def subtract(a: float, b: float):
    return {"operation": "subtraction", "a": a, "b": b, "result": a - b}


@app.get("/multiply/{a}/{b}")
def multiply(a: float, b: float):
    return {"operation": "multiplication", "a": a, "b": b, "result": a * b}


@app.get("/divide/{a}/{b}")
def divide(a: float, b: float):
    if b == 0:
        raise HTTPException(status_code=400, detail="Division par zéro impossible")
    return {"operation": "division", "a": a, "b": b, "result": a / b}
