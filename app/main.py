"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.routers import categories, groups, customers, subscriptions, ai_routes, search, search_routes
from app.routers import web_routes, export_routes, auth_routes, users, saved_reports_routes
from app.routers.auth_routes import get_session

# Create FastAPI app
app = FastAPI(
    title="SubTrack Web",
    description="Subscription tracking with AI-powered insights",
    version="1.0.0",
    debug=settings.debug
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
app.include_router(ai_routes.router, prefix="/api/ai", tags=["ai"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(search_routes.router, tags=["search-html"])
app.include_router(export_routes.router, prefix="/api", tags=["exports"])
app.include_router(saved_reports_routes.router, prefix="/api", tags=["saved-reports"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "ai_enabled": settings.subtrack_ai_api_key is not None}
