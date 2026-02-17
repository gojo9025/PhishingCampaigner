from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import Campaign

import requests
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


# =================================================
# ENV CONFIG
# =================================================

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
BASE_URL = os.getenv("BASE_URL")


# =================================================
# MICROSOFT GRAPH AUTH
# =================================================

def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default"
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    return response.json()["access_token"]


# =================================================
# EMAIL SENDER (GRAPH API VERSION)
# =================================================

def send_email(to_email: str, subject: str, html_body: str):

    token = get_access_token()

    url = f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail"

    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": html_body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email
                    }
                }
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    res = requests.post(url, headers=headers, json=payload)

    if res.status_code >= 300:
        raise Exception(f"Graph sendMail failed: {res.text}")


# =================================================
# REQUEST MODEL
# =================================================

class CampaignCreate(BaseModel):
    name: str
    subject: str
    template: str
    employees: list[str]


# =================================================
# CREATE CAMPAIGN
# =================================================

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


# =================================================
# START CAMPAIGN + SEND EMAILS
# =================================================

@router.post("/{cid}/start")
def start_campaign(cid: int, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if not campaign:
        raise HTTPException(404, "Campaign not found")

    campaign.status = "running"

    employees = campaign.employees.split(",")

    for email in employees:
        email = email.strip()

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">

            <h2>Security Awareness Training</h2>

            <p>{campaign.template}</p>

            <p>
                <a href="{BASE_URL}/track/click/{cid}/{email}"
                   style="
                       background:#0078d4;
                       color:white;
                       padding:12px 20px;
                       text-decoration:none;
                       border-radius:6px;
                       font-weight:bold;
                   ">
                   Start Training
                </a>
            </p>

            <img src="{BASE_URL}/track/open/{cid}/{email}" width="1" height="1"/>

        </body>
        </html>
        """

        send_email(email, campaign.subject, body)

    db.commit()

    return {"message": "Campaign started and emails sent"}


# =================================================
# STATUS
# =================================================

@router.get("/{cid}")
def get_status(cid: int, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if not campaign:
        raise HTTPException(404)

    return {
        "id": campaign.id,
        "name": campaign.name,
        "status": campaign.status,
        "opened": campaign.opened,
        "clicked": campaign.clicked
    }


# =================================================
# REPORT
# =================================================

@router.get("/{cid}/report")
def report(cid: int, db: Session = Depends(get_db)):

    campaign = db.query(Campaign).filter(Campaign.id == cid).first()

    if not campaign:
        raise HTTPException(404)

    opened = campaign.opened
    clicked = campaign.clicked

    rate = 0
    if opened:
        rate = (clicked / opened) * 100

    return {
        "opened": opened,
        "clicked": clicked,
        "click_rate": f"{rate:.2f}%"
    }
