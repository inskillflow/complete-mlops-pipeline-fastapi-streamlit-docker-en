import os
from datetime import datetime
from enum import Enum

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://calc:calc@postgres:5432/calc",
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation: Mapped[str] = mapped_column(String(16), nullable=False)
    a: Mapped[float] = mapped_column(Float, nullable=False)
    b: Mapped[float] = mapped_column(Float, nullable=False)
    result: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


class Operation(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"


class CalculationRequest(BaseModel):
    a: float = Field(..., examples=[10])
    b: float = Field(..., examples=[2])
    operation: Operation


class CalculationResponse(BaseModel):
    id: int
    operation: Operation
    a: float
    b: float
    result: float
    created_at: datetime

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    title="FastAPI Calculatrice - PostgreSQL history (chap30)",
    description="Persistance de l'historique des calculs dans PostgreSQL via SQLAlchemy.",
    version="0.4.0",
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur la calculatrice FastAPI (chap30 - PostgreSQL)",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "POST /calculate": "calcul + insertion en base",
            "GET /history": "lister tous les calculs (les plus recents d'abord)",
            "DELETE /history": "vider l'historique",
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
def calculate(payload: CalculationRequest, db: Session = Depends(get_db)):
    result = _compute(payload.a, payload.b, payload.operation)
    record = Calculation(
        operation=payload.operation.value,
        a=payload.a,
        b=payload.b,
        result=result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/history", response_model=list[CalculationResponse])
def get_history(limit: int = 50, db: Session = Depends(get_db)):
    stmt = select(Calculation).order_by(Calculation.created_at.desc()).limit(limit)
    return list(db.execute(stmt).scalars())


@app.delete("/history")
def clear_history(db: Session = Depends(get_db)):
    deleted = db.query(Calculation).delete()
    db.commit()
    return {"deleted": deleted}
