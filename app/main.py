import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from db.funcs import DataBase as db

from shapes.user import UserRequest
from routes import trans


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trans.router, prefix="/api", tags=["transactions"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True
    )


@app.post("/user")
def create_user(user: UserRequest):
    logging.info(f"start creating user: {user.model_dump()}")
    user_id = db.create_user(user.name)
    return {"id": user_id}