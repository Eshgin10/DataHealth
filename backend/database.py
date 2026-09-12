import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

DATABASE_URL = "sqlite:///./data_health.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    status = Column(String) # uploading, profiling, validating, done, error
    row_count = Column(Integer, default=0)
    col_count = Column(Integer, default=0)
    health_score = Column(Float, default=0.0)
    completeness_score = Column(Float, default=0.0)
    validity_score = Column(Float, default=0.0)
    consistency_score = Column(Float, default=0.0)
    uniqueness_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ColumnProfile(Base):
    __tablename__ = "column_profiles"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String, index=True)
    name = Column(String)
    semantic_type = Column(String)
    null_count = Column(Integer)
    null_pct = Column(Float)
    unique_count = Column(Integer)
    unique_pct = Column(Float)
    min_val = Column(String, nullable=True)
    max_val = Column(String, nullable=True)
    mean_val = Column(Float, nullable=True)
    most_common = Column(String) # JSON encoded string

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(String, index=True)
    category = Column(String) # MISSING DATA, DUPLICATES, FORMAT ISSUES, etc.
    column_name = Column(String, nullable=True)
    issue_type = Column(String) # e.g. email malformed
    severity = Column(String) # high, medium, low
    affected_rows = Column(Integer)
    status = Column(String, default="open") # open, fixed

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
