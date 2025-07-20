import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from backend.main import app
from backend.database import get_db
from backend.models import Base, Project

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Site Helper API"}

def test_get_projects_empty():
    """Test getting projects when none exist"""
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json() == []

def test_get_projects_with_data():
    """Test getting projects with existing data"""
    # Add test project
    db = TestingSessionLocal()
    project = Project(
        name="Test Project",
        description="Test Description",
        site_maps=[{"pages": [{"name": "Home"}]}]
    )
    db.add(project)
    db.commit()
    db.close()
    
    response = client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Project"
    assert data[0]["description"] == "Test Description"

def test_get_project_by_id():
    """Test getting a specific project"""
    # Add test project
    db = TestingSessionLocal()
    project = Project(name="Specific Project", description="Specific Description")
    db.add(project)
    db.commit()
    project_id = project.id
    db.close()
    
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Specific Project"
    assert data["id"] == project_id

def test_get_project_not_found():
    """Test getting non-existent project"""
    response = client.get("/projects/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

@patch('backend.ai_agents.AIAgents.generate_site_maps')
@patch('backend.ai_agents.AIAgents.generate_mermaid_diagrams')
@patch('backend.ai_agents.AIAgents.generate_backend_diagrams')
@patch('backend.ai_agents.AIAgents.rate_artifacts')
def test_create_project(mock_rate, mock_backend, mock_mermaid, mock_site_maps):
    """Test creating a new project"""
    # Mock AI responses
    mock_site_maps.return_value = [{"pages": [{"name": "Home", "path": "/"}]}]
    mock_mermaid.return_value = ["graph TD\nA-->B"]
    mock_backend.return_value = ["flowchart TD\nAPI-->DB"]
    mock_rate.return_value = [{"index": 0, "overall_score": 8.5}]
    
    # Convert to async mocks
    mock_site_maps.return_value = asyncio.coroutine(lambda: mock_site_maps.return_value)()
    mock_mermaid.return_value = asyncio.coroutine(lambda: mock_mermaid.return_value)()
    mock_backend.return_value = asyncio.coroutine(lambda: mock_backend.return_value)()
    mock_rate.return_value = asyncio.coroutine(lambda: mock_rate.return_value)()
    
    project_data = {
        "name": "New Project",
        "description": "New project description"
    }
    
    response = client.post("/projects", json=project_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Project"
    assert data["description"] == "New project description"
    assert len(data["site_maps"]) > 0
    assert len(data["mermaid_diagrams"]) > 0
    assert len(data["backend_diagrams"]) > 0

def test_create_project_validation():
    """Test project creation validation"""
    # Missing required fields
    response = client.post("/projects", json={})
    assert response.status_code == 422
    
    # Missing description
    response = client.post("/projects", json={"name": "Test"})
    assert response.status_code == 422

def test_delete_project():
    """Test deleting a project"""
    # Add test project
    db = TestingSessionLocal()
    project = Project(name="Delete Me", description="To be deleted")
    db.add(project)
    db.commit()
    project_id = project.id
    db.close()
    
    # Delete project
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"
    
    # Verify deletion
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 404

def test_delete_project_not_found():
    """Test deleting non-existent project"""
    response = client.delete("/projects/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

# Fix for async tests
import asyncio