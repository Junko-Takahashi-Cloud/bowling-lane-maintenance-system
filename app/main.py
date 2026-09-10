from fastapi import FastAPI
from app.routers import rental_items, maintenance_log

app = FastAPI()

app.include_router(rental_items.router)
app.include_router(maintenance_log.router)


@app.get("/")
def root():
    return {"message": "OK"}