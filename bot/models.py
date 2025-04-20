from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from bot.db import Base

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    full_name = Column(String)
    phone = Column(String)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
