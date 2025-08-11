import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from db.funcs import DataBase as db

from shapes.user import UserRequest
from routes import trans, groups, trips, debts, bank_accounts

app = FastAPI(
    title="Koin - Финансовое приложение",
    description="Приложение для учета личных и общих финансов с поддержкой поездок и групп",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(trans.router, prefix="/api", tags=["transactions"])
app.include_router(groups.router, prefix="/api", tags=["groups"])
app.include_router(trips.router, prefix="/api", tags=["trips"])
app.include_router(debts.router, prefix="/api", tags=["debts"])
app.include_router(bank_accounts.router, prefix="/api", tags=["bank-accounts"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True
    )

@app.post("/user")
def create_user(user: UserRequest):
    logging.info(f"start creating user: {user.model_dump()}")
    user_id = db.create_user(user.name)
    return {"id": user_id}

@app.get("/")
def root():
    return {
        "message": "Добро пожаловать в Koin - Финансовое приложение!",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}