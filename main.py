"""Main application entry point."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from config import config

# Create FastAPI application
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered scam detection and intelligence extraction system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Agentic Honey-Pot API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "analyze": "/api/analyze",
            "health": "/health",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    print(f"""
╔════════════════════════════════════════════════════════════╗
║        Agentic Honey-Pot System Starting...                ║
╚════════════════════════════════════════════════════════════╝

🔒 API Endpoint: http://localhost:{config.PORT}/api/analyze
📚 Documentation: http://localhost:{config.PORT}/docs
❤️  Health Check: http://localhost:{config.PORT}/health

🤖 AI Provider: {config.AI_PROVIDER.upper()}
🔑 API Key Authentication: Required (X-API-Key header)

════════════════════════════════════════════════════════════
""")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=True,
        log_level="info"
    )
