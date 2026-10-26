from fastapi import FastAPI
from modules.models.config import settings


app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Go to '/docs' to explore opportunities"}


