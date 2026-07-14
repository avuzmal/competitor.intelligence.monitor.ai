from datetime import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email_address = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(sqlalchemy.Boolean, default=True, nullable=False)
    stripe_customer_id = Column(String, index=True, nullable=True)
    slack_webhook_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    competitors = relationship("Competitor", back_populates="client", cascade="all, delete-orphan")
    briefing_histories = relationship("BriefingHistory", back_populates="client", cascade="all, delete-orphan")
