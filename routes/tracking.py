from fastapi import APIRouter, Depends
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session
import base64

from database import get_db
from models import Campaign

router = APIRouter(prefix="/track", tags=["Tracking"])

# 1x1 transparent PNG pixel
PIXEL_DATA = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)

# =========================
# OPEN TRACK
# =========================
@router.get("/open/{cid}/{email}")
def track_open(cid: int, email: str, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if campaign:
        campaign.opened += 1
        db.commit()

    return Response(content=PIXEL_DATA, media_type="image/png")


# =========================
# CLICK TRACK
# =========================
@router.get("/click/{cid}/{email}")
def track_click(cid: int, email: str, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if campaign:
        campaign.clicked += 1
        db.commit()

    return RedirectResponse("https://google.com")
