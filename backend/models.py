from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    site_maps = Column(JSON, default=list)  # List of AI-generated site maps
    mermaid_diagrams = Column(JSON, default=list)  # List of AI-generated diagrams
    backend_diagrams = Column(JSON, default=list)  # List of backend architecture diagrams
    ratings = Column(JSON, default=dict)  # Ratings for each generated artifact
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())