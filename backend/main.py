from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import asyncio

from database import engine, get_db
from models import Base, Project
from ai_agents import AIAgents

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
ai_agents = AIAgents()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    site_maps: List[Dict[str, Any]]
    mermaid_diagrams: List[str]
    backend_diagrams: List[str]
    ratings: Dict[str, Any]
    created_at: str
    
class GenerationStatus(BaseModel):
    step: str
    message: str
    progress: int

@app.get("/")
async def root():
    return {"message": "Site Helper API"}

@app.get("/projects", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            site_maps=p.site_maps or [],
            mermaid_diagrams=p.mermaid_diagrams or [],
            backend_diagrams=p.backend_diagrams or [],
            ratings=p.ratings or {},
            created_at=p.created_at.isoformat()
        )
        for p in projects
    ]

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        site_maps=project.site_maps or [],
        mermaid_diagrams=project.mermaid_diagrams or [],
        backend_diagrams=project.backend_diagrams or [],
        ratings=project.ratings or {},
        created_at=project.created_at.isoformat()
    )

@app.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # Create new project
    db_project = Project(
        name=project.name,
        description=project.description
    )
    
    try:
        # Generate artifacts with progress updates
        # Step 1: Generate site maps
        print(f"Generating site maps for project: {project.name}")
        site_maps = await ai_agents.generate_site_maps(project.description)
        print(f"Generated site maps: {site_maps}")
        
        # Step 2: Use the generated site map directly (no rating needed for single generation)
        best_site_map = site_maps[0] if site_maps else {"pages": []}
        
        # Step 3: Generate Mermaid diagrams
        mermaid_diagrams = await ai_agents.generate_mermaid_diagrams(project.description, best_site_map)
        
        # Step 4: Generate backend diagrams
        backend_diagrams = await ai_agents.generate_backend_diagrams(project.description)
        
        # Skip rating step for faster generation
        
        # Store results
        db_project.site_maps = site_maps
        db_project.mermaid_diagrams = mermaid_diagrams
        db_project.backend_diagrams = backend_diagrams
        db_project.ratings = {}
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return ProjectResponse(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            site_maps=db_project.site_maps,
            mermaid_diagrams=db_project.mermaid_diagrams,
            backend_diagrams=db_project.backend_diagrams,
            ratings=db_project.ratings,
            created_at=db_project.created_at.isoformat()
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)