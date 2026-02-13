from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Campaign

from sqlalchemy import func
from models import EmailOpen, EmailClick

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{cid}")
def get_status(cid: int, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if not campaign:
        raise HTTPException(404)

    # 🔥 Detailed open stats
    open_stats = (
        db.query(
            EmailOpen.email,
            func.count(EmailOpen.id).label("opens")
        )
        .filter(EmailOpen.campaign_id == cid)
        .group_by(EmailOpen.email)
        .all()
    )

    click_stats = (
        db.query(
            EmailClick.email,
            func.count(EmailClick.id).label("clicks")
        )
        .filter(EmailClick.campaign_id == cid)
        .group_by(EmailClick.email)
        .all()
    )

    return {
        "campaign": campaign.name,
        "status": campaign.status,
        "total_opened": campaign.opened,
        "total_clicked": campaign.clicked,
        "opened_details": [
            {"email": o.email, "opens": o.opens}
            for o in open_stats
        ],
        "clicked_details": [
            {"email": c.email, "clicks": c.clicks}
            for c in click_stats
        ]
    }