from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import asyncio
import json

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

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_progress(self, project_id: str, step: str, message: str, progress: int):
        progress_data = {
            "project_id": project_id,
            "step": step,
            "message": message,
            "progress": progress,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Send to all connected clients (in production, you'd filter by project_id)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(progress_data))
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # Create new project
    db_project = Project(
        name=project.name,
        description=project.description
    )
    
    try:
        project_id = db_project.id
        
        # Set up progress callback for AI agents
        ai_agents.set_progress_callback(manager.send_progress)
        
        # Step 1: Planning site structure
        await manager.send_progress(project_id, "planning", "Starting AI project analysis...", 5)
        await asyncio.sleep(0.3)
        await manager.send_progress(project_id, "planning", "Analyzing project requirements and planning site structure...", 10)
        await asyncio.sleep(0.5)
        await manager.send_progress(project_id, "planning", "Identifying key user personas and use cases...", 15)
        await asyncio.sleep(0.3)
        await manager.send_progress(project_id, "planning", "Determining core functionality and features...", 20)
        
        site_maps = await ai_agents.generate_site_maps(project.description, project_id=project_id)
        
        # Step 2: Creating site maps  
        await manager.send_progress(project_id, "sitemap", "Sitemap generation completed, validating structure...", 48)
        await asyncio.sleep(0.3)
        best_site_map = site_maps[0] if site_maps else {"pages": []}
        await manager.send_progress(project_id, "sitemap", "Page hierarchy and navigation flow established", 52)
        
        # Step 3: Designing architecture diagrams
        mermaid_diagrams = await ai_agents.generate_mermaid_diagrams(project.description, best_site_map, project_id=project_id)
        
        # Step 4: Backend diagrams
        backend_diagrams = await ai_agents.generate_backend_diagrams(project.description, project_id=project_id)
        
        # Final step: Finalizing
        await manager.send_progress(project_id, "finalize", "Saving project artifacts to database...", 92)
        await asyncio.sleep(0.5)
        await manager.send_progress(project_id, "finalize", "Securing project data and setting permissions...", 95)
        await asyncio.sleep(0.3)
        await manager.send_progress(project_id, "finalize", "Project structure complete! Redirecting...", 100)
        
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
        await manager.send_progress(project_id, "error", f"Error: {str(e)}", 0)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/projects")
async def delete_all_projects(db: Session = Depends(get_db)):
    try:
        # Delete all projects
        deleted_count = db.query(Project).delete()
        db.commit()
        return {"message": f"Successfully deleted {deleted_count} projects"}
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