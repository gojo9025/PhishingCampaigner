# from fastapi import FastAPI
# from dotenv import load_dotenv

# # load .env variables (EMAIL_USER, EMAIL_PASS etc.)
# # load .env variables (EMAIL_USER, EMAIL_PASS etc.)
# load_dotenv()

# from database import engine, Base
# import models

# Base.metadata.create_all(bind=engine)

# # -------------------------
# # Create FastAPI app
# # -------------------------
# app = FastAPI(
#     title="Phishing Awareness Simulation API",
#     description="Internal phishing awareness training backend",
#     version="1.0.0"
# )


# # -------------------------
# # Routers
# # -------------------------
# from routes.campaigns import router as campaigns_router
# from routes.reports import router as reports_router
# from routes.tracking import router as tracking_router

# app.include_router(campaigns_router)
# app.include_router(reports_router)
# app.include_router(tracking_router)


# # -------------------------
# # Health Check
# # -------------------------
# @app.get("/")
# def health():
#     return {"status": "Phishing Awareness API running"}
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
