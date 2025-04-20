from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from bot.db import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    full_name = Column(String)
    phone = Column(String)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

