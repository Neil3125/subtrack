"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.routers import categories, groups, customers, subscriptions, ai_routes, search, search_routes
from app.routers import web_routes, export_routes, auth_routes, users, saved_reports_routes, email_routes, log_check_routes, admin_routes
from app.routers import activity_routes
from app.routers.auth_routes import get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - runs on startup and shutdown."""
    # Startup: Initialize data persistence (restore data if DB is empty)
    from app.database import engine, Base
    # Explicitly import models to ensure they are registered with Base.metadata
    from app.models.subscription_template import SubscriptionTemplate
    Base.metadata.create_all(bind=engine)
    
    from app.data_persistence import init_data_persistence
    print("[Startup] Initializing data persistence...")
    init_data_persistence()
    print("[Startup] Data persistence initialized")
    
    yield
    
    # Shutdown: Final data save
    from app.data_persistence import auto_save
    from app.database import SessionLocal
    print("[Shutdown] Performing final data save...")
    db = SessionLocal()
    try:
        auto_save(db)
        print("[Shutdown] Final data save complete")
    finally:
        db.close()


# Create FastAPI app
app = FastAPI(
    title="SubTrack Web",
    description="Subscription tracking with AI-powered insights",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to protect routes that require authentication."""
    
    # Routes that don't require authentication
    PUBLIC_PATHS = {
        "/login",
        "/logout", 
        "/forgot-password",
        "/reset-password",
        "/static",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Allow public paths
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path) or path == public_path:
                return await call_next(request)
        
        # Check for valid session
        session_id = request.cookies.get("session_id")
        session = get_session(session_id)
        
        if not session:
            # Not authenticated - redirect to login
            if path.startswith("/api/"):
                # API requests get 401
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Not authenticated"}
                )
            # Web requests get redirected
            return RedirectResponse(url="/login", status_code=302)
        
        return await call_next(request)


# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include auth routes first (they handle login/logout)
app.include_router(auth_routes.router, tags=["auth"])

# Include other routers
app.include_router(web_routes.router)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
# app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(ai_routes.router, prefix="/api/ai", tags=["ai"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(search_routes.router, tags=["search-html"])
app.include_router(export_routes.router, prefix="/api", tags=["exports"])
app.include_router(saved_reports_routes.router, prefix="/api", tags=["saved-reports"])
app.include_router(email_routes.router, prefix="/api/email", tags=["email"])
app.include_router(log_check_routes.router, tags=["log-check"])
app.include_router(activity_routes.router, tags=["activity"])
app.include_router(admin_routes.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "ai_enabled": settings.subtrack_ai_api_key is not None}
