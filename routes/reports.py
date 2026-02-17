from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Campaign

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{cid}")
def get_report(cid: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if not campaign:
        raise HTTPException(404)

    success_rate = 0
    if campaign.opened:
        success_rate = (campaign.clicked / campaign.opened) * 100

    return {
        "campaign": campaign.name,
        "opened": campaign.opened,
        "clicked": campaign.clicked,
        "success_rate": f"{success_rate:.2f}%"
    }
