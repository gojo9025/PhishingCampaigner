from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import smtplib
from email.message import EmailMessage
import os
import urllib.parse
from dotenv import load_dotenv

from database import get_db
from models import Campaign, EmailOpen, EmailClick

load_dotenv()

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
BASE_URL = os.getenv("BASE_URL")


# =========================
# EMAIL SENDER
# =========================
def send_email(to_email: str, subject: str, html_body: str):

    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.set_content("Please open this email in HTML supported client.")
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)


# =========================
# REQUEST MODEL
# =========================
class CampaignCreate(BaseModel):
    name: str
    subject: str
    template: str
    employees: list[str]


# =========================
# CREATE CAMPAIGN
# =========================
@router.post("")
def create_campaign(data: CampaignCreate, db: Session = Depends(get_db)):

    campaign = Campaign(
        name=data.name,
        subject=data.subject,
        template=data.template,
        employees=",".join(data.employees),
        status="created",
        opened=0,
        clicked=0
    )

    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    return {"campaign_id": campaign.id}


# =========================
# START CAMPAIGN
# =========================
@router.post("/{cid}/start")
def start_campaign(cid: int, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if not campaign:
        raise HTTPException(404)

    campaign.status = "running"

    employees = campaign.employees.split(",")

    for email in employees:
        email = email.strip()
        encoded_email = urllib.parse.quote(email)

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Security Awareness Training</h2>
            <p>{campaign.template}</p>

            <p>
                <a href="{BASE_URL}/track/click/{cid}/{encoded_email}"
                   style="background:#0078d4;color:white;padding:12px 20px;
                          text-decoration:none;border-radius:6px;font-weight:bold;">
                   Start Training
                </a>
            </p>

            <img src="{BASE_URL}/track/open/{cid}/{encoded_email}"
                 width="1" height="1"/>
        </body>
        </html>
        """

        send_email(email, campaign.subject, body)

    db.commit()

    return {"message": "Campaign started and emails sent"}


# =========================
# STATUS WITH DETAILS
# =========================
@router.get("/{cid}")
def get_status(cid: int, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if not campaign:
        raise HTTPException(404)

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
