from fastapi import FastAPI
from database import engine, Base

from routes.campaigns import router as campaigns_router
from routes.tracking import router as tracking_router
from routes.reports import router as reports_router

app = FastAPI(title="Phishing Awareness Backend")

# create tables automatically
Base.metadata.create_all(bind=engine)

app.include_router(campaigns_router)
app.include_router(tracking_router)
app.include_router(reports_router)


@app.get("/")
def home():
    return {"status": "Backend running 🚀"}
