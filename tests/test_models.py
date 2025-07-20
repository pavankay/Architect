import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import Base, Project
from backend.database import get_db

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_create_project(db):
    """Test creating a new project"""
    project = Project(
        name="Test Project",
        description="This is a test project"
    )
    db.add(project)
    db.commit()
    
    assert project.id is not None
    assert project.name == "Test Project"
    assert project.description == "This is a test project"
    assert project.created_at is not None
    assert project.site_maps == []
    assert project.mermaid_diagrams == []
    assert project.backend_diagrams == []
    assert project.ratings == {}

def test_project_with_artifacts(db):
    """Test project with AI-generated artifacts"""
    project = Project(
        name="AI Project",
        description="Project with artifacts",
        site_maps=[{"pages": [{"name": "Home", "path": "/"}]}],
        mermaid_diagrams=["graph TD\nA-->B"],
        backend_diagrams=["flowchart TD\nAPI-->DB"],
        ratings={"site_maps": [{"overall_score": 8.5}]}
    )
    db.add(project)
    db.commit()
    
    # Retrieve and verify
    saved_project = db.query(Project).filter_by(id=project.id).first()
    assert saved_project is not None
    assert len(saved_project.site_maps) == 1
    assert saved_project.site_maps[0]["pages"][0]["name"] == "Home"
    assert len(saved_project.mermaid_diagrams) == 1
    assert "graph TD" in saved_project.mermaid_diagrams[0]
    assert len(saved_project.backend_diagrams) == 1
    assert saved_project.ratings["site_maps"][0]["overall_score"] == 8.5

def test_update_project(db):
    """Test updating project artifacts"""
    project = Project(name="Update Test", description="Original description")
    db.add(project)
    db.commit()
    
    # Update project
    project.description = "Updated description"
    project.site_maps = [{"pages": [{"name": "Updated"}]}]
    db.commit()
    
    # Verify update
    updated = db.query(Project).filter_by(id=project.id).first()
    assert updated.description == "Updated description"
    assert updated.site_maps[0]["pages"][0]["name"] == "Updated"

def test_delete_project(db):
    """Test deleting a project"""
    project = Project(name="Delete Test", description="To be deleted")
    db.add(project)
    db.commit()
    project_id = project.id
    
    # Delete project
    db.delete(project)
    db.commit()
    
    # Verify deletion
    deleted = db.query(Project).filter_by(id=project_id).first()
    assert deleted is None