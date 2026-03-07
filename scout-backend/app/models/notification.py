"""Notification log model."""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    alert_id = Column(Integer, nullable=True, index=True)
    channel = Column(String, nullable=False)  # sms, whatsapp
    phone = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    status = Column(String, default="sent")  # sent, failed, delivered
    twilio_sid = Column(String, nullable=True)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
