from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import router

app = FastAPI(title="Second Opinion MVP")
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")