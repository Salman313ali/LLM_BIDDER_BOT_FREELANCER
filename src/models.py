"""
Database models for the Freelancer Bot
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True)
    project_title = Column(String)
    project_description = Column(Text)
    owner_id = Column(String)
    minimum_budget = Column(Float)
    maximum_budget = Column(Float)
    currency = Column(String)
    project_type = Column(String)  # fixed or hourly
    exchange_rate = Column(Float)
    submitdate = Column(DateTime)
    seo_url = Column(String)
    status = Column(String, default="active")  # active, bid_placed, won, lost
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, index=True)
    project_title = Column(String)
    bid_amount = Column(Float)
    bid_period = Column(Integer)
    bid_content = Column(Text)
    currency_code = Column(String)
    status = Column(String, default="placed")  # placed, won, lost, withdrawn
    bid_date = Column(DateTime, default=func.now())
    project_link = Column(String)
    session_id = Column(String, index=True)  # Link to session
    
    # Foreign key relationship
    project = Column(String, index=True)

class BotSession(Base):
    __tablename__ = "bot_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)
    status = Column(String, default="running")  # running, stopped, error
    total_projects_found = Column(Integer, default=0)
    total_projects_filtered = Column(Integer, default=0)
    total_bids_placed = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    configuration = Column(JSON)  # Store bot configuration as JSON

class BotLog(Base):
    __tablename__ = "bot_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime, default=func.now())
    level = Column(String)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text)
    project_id = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)

