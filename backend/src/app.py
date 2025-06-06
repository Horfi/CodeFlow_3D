"""
CodeFlow 3D Backend - Main FastAPI Application
AI-Augmented Codebase Dependency Explorer
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager

from src.api.routes import repository_routes, graph_routes, file_routes, analytics_routes, user_model_routes
from src.database.SQLiteManager import SQLiteManager
from src.services.analytics.SessionManager import SessionManager
from src.config import Config

# Global instances
db_manager = None
session_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_manager, session_manager
    
    print("🚀 Starting CodeFlow 3D Backend...")
    
    # Initialize database
    db_manager = SQLiteManager()
    db_manager.initialize_database()
    
    # Initialize session manager
    session_manager = SessionManager(db_manager)
    
    # Store in app state
    app.state.db_manager = db_manager
    app.state.session_manager = session_manager
    
    print("✅ Backend initialized successfully!")
    yield
    
    # Shutdown
    print("🛑 Shutting down CodeFlow 3D Backend...")
    if db_manager:
        db_manager.close()

# Create FastAPI app
app = FastAPI(
    title="CodeFlow 3D API",
    description="AI-Augmented Codebase Dependency Explorer Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(repository_routes.router, prefix="/api/repositories", tags=["repositories"])
app.include_router(graph_routes.router, prefix="/api/graph", tags=["graph"])
app.include_router(file_routes.router, prefix="/api/files", tags=["files"])
app.include_router(analytics_routes.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(user_model_routes.router, prefix="/api/user-model", tags=["user-model"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CodeFlow 3D Backend",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CodeFlow 3D API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    config = Config()
    uvicorn.run(
        "app:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )