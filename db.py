from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./uaal_v2.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class ActionRecord(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String, unique=True, index=True)
    actor_id = Column(String, index=True)
    actor_type = Column(String)
    verb = Column(String, index=True)
    object_type = Column(String)
    object_id = Column(String)
    parameters = Column(JSON)
    confidence = Column(Float)
    reasoning = Column(Text)
    state = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    delivered = Column(Boolean, default=False)
    deliveries = Column(JSON, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String, index=True)
    user = Column(String)
    event = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    display_name = Column(String)
    role = Column(String)  # admin, approver, agent, viewer
    spending_limit = Column(Float, default=0.0)

class Watchlist(Base):
    __tablename__ = "watchlists"
    id = Column(Integer, primary_key=True)
    type = Column(String)  # whitelist / blacklist
    field = Column(String)
    value = Column(String)

Base.metadata.create_all(bind=engine)
