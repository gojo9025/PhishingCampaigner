from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    subject = Column(String)
    template = Column(String)
    employees = Column(String)

    status = Column(String, default="created")

    # 🔥 tracking counters
    opened = Column(Integer, default=0)
    clicked = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
