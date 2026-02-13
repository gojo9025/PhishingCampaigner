from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.sql import func
from database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    subject = Column(String)
    template = Column(String)
    employees = Column(String)

    status = Column(String, default="created")

    opened = Column(Integer, default=0)
    clicked = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# 🔥 NEW TABLE — OPEN TRACKING DETAILS
class EmailOpen(Base):
    __tablename__ = "email_opens"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    email = Column(String)
    opened_at = Column(DateTime, server_default=func.now())


# 🔥 NEW TABLE — CLICK TRACKING DETAILS
class EmailClick(Base):
    __tablename__ = "email_clicks"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    email = Column(String)
    clicked_at = Column(DateTime, server_default=func.now())
