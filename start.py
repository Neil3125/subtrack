"""Simple script to start SubTrack Web application."""
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting SubTrack Web...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    print("⏹️  Press CTRL+C to stop the server\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
