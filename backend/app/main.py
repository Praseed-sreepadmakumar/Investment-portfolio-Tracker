from fastapi import FastAPI
from app.database.database import Base, engine
from app.routes.auth import router 

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="Investment Portfolio Tracker",
)
app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "Investment Portfolio Tracker API!"
    }