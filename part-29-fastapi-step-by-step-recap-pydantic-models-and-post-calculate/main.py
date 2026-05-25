from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="FastAPI Calculatrice - Pydantic + POST (chap29)",
    description="Validation d'entrée stricte avec Pydantic et endpoint POST /calculate.",
    version="0.3.0",
)


class Operation(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"


class CalculationRequest(BaseModel):
    a: float = Field(..., description="Premier opérande", examples=[10])
    b: float = Field(..., description="Second opérande", examples=[2])
    operation: Operation = Field(..., description="Opération à effectuer")


class CalculationResponse(BaseModel):
    operation: Operation
    a: float
    b: float
    result: float


@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur la calculatrice FastAPI (chap29 - Pydantic + POST)",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "GET /": "ce message",
            "POST /calculate": "JSON body {a, b, operation}",
            "GET /add/{a}/{b}": "compat chap27/28",
            "GET /subtract/{a}/{b}": "compat chap27/28",
            "GET /multiply/{a}/{b}": "compat chap27/28",
            "GET /divide/{a}/{b}": "compat chap27/28",
        },
    }


def _compute(a: float, b: float, operation: Operation) -> float:
    if operation is Operation.add:
        return a + b
    if operation is Operation.subtract:
        return a - b
    if operation is Operation.multiply:
        return a * b
    if operation is Operation.divide:
        if b == 0:
            raise HTTPException(status_code=400, detail="Division par zéro impossible")
        return a / b
    raise HTTPException(status_code=400, detail=f"Opération inconnue : {operation}")


@app.post("/calculate", response_model=CalculationResponse)
def calculate(payload: CalculationRequest):
    result = _compute(payload.a, payload.b, payload.operation)
    return CalculationResponse(
        operation=payload.operation,
        a=payload.a,
        b=payload.b,
        result=result,
    )


@app.get("/add/{a}/{b}", response_model=CalculationResponse)
def add(a: float, b: float):
    return CalculationResponse(operation=Operation.add, a=a, b=b, result=_compute(a, b, Operation.add))


@app.get("/subtract/{a}/{b}", response_model=CalculationResponse)
def subtract(a: float, b: float):
    return CalculationResponse(operation=Operation.subtract, a=a, b=b, result=_compute(a, b, Operation.subtract))


@app.get("/multiply/{a}/{b}", response_model=CalculationResponse)
def multiply(a: float, b: float):
    return CalculationResponse(operation=Operation.multiply, a=a, b=b, result=_compute(a, b, Operation.multiply))


@app.get("/divide/{a}/{b}", response_model=CalculationResponse)
def divide(a: float, b: float):
    return CalculationResponse(operation=Operation.divide, a=a, b=b, result=_compute(a, b, Operation.divide))
