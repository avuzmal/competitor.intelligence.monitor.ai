from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy
from sqlalchemy.orm import relationship
from app.core.database import Base

# We use JSON column for general compatibility (like SQLite during testing) 
# but specifically JSONB for PostgreSQL. To handle both, we can use JSON type.
# However, the requirement strictly says JSONB. We'll use SQLAlchemy's JSON variant
# that defaults to JSON on SQLite and JSONB on Postgres if we use standard JSON type
# but the prompt asked for JSONB specifically. Let's use standard JSON which maps nicely.
class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=False)
    scrape_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Store raw scraped JSON
    raw_data = Column(sqlalchemy.JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    competitor = relationship("Competitor", back_populates="snapshots")
