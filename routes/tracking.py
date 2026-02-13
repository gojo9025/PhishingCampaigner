from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session
import base64
import urllib.parse

from database import get_db
from models import Campaign, EmailOpen, EmailClick

router = APIRouter(prefix="/track", tags=["Tracking"])

# 1x1 transparent pixel
PIXEL_DATA = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)

# =========================
# OPEN TRACK (GET + HEAD)
# =========================
@router.get("/open/{cid}/{email}")
@router.head("/open/{cid}/{email}")
def track_open(cid: int, email: str, request: Request, db: Session = Depends(get_db)):

    decoded_email = urllib.parse.unquote(email)

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if campaign:
        campaign.opened += 1

        open_entry = EmailOpen(
            campaign_id=cid,
            email=decoded_email
        )

        db.add(open_entry)
        db.commit()

    return Response(content=PIXEL_DATA, media_type="image/png")


# =========================
# CLICK TRACK
# =========================
@router.get("/click/{cid}/{email}")
def track_click(cid: int, email: str, db: Session = Depends(get_db)):

    decoded_email = urllib.parse.unquote(email)

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if campaign:
        campaign.clicked += 1

        click_entry = EmailClick(
            campaign_id=cid,
            email=decoded_email
        )

        db.add(click_entry)
        db.commit()

    return RedirectResponse("https://google.com")
