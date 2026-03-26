import uuid
import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Initialize database engine
engine = create_engine("sqlite:///./agrisight.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_chat_id = Column(String, unique=True)
    email = Column(String, nullable=True)
    email_reports = Column(Boolean, default=False)
    sms_alerts = Column(Boolean, default=False)
    weekly_summary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship to ScanLog
    scan_logs = relationship("ScanLog", back_populates="user")

class ScanLog(Base):
    __tablename__ = "scan_logs"
    scan_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"))
    image_path = Column(String)
    inference_time_ms = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scan_logs")
    detections = relationship("Detection", back_populates="scan_log")

class Detection(Base):
    __tablename__ = "detections"
    detection_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("scan_logs.scan_id"))
    class_label = Column(String)
    confidence_score = Column(Float)
    severity_grade = Column(String)
    bbox_coordinates = Column(String) # Store JSON formatted coordinates
    
    # Relationship to ScanLog
    scan_log = relationship("ScanLog", back_populates="detections")

def init_db():
    Base.metadata.create_all(bind=engine)