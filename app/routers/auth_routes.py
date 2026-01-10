"""Authentication routes."""
from fastapi import APIRouter, Request, Depends, HTTPException, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets

from app.database import get_db
from app.models.user import User
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Session storage (in production, use Redis or database sessions)
sessions = {}


def create_session(user_id: int) -> str:
    """Create a new session for a user."""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "user_id": user_id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(days=7)
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """Get session data if valid."""
    if session_id and session_id in sessions:
        session = sessions[session_id]
        if session["expires_at"] > datetime.now():
            return session
        else:
            # Clean up expired session
            del sessions[session_id]
    return None


def delete_session(session_id: str):
    """Delete a session."""
    if session_id in sessions:
        del sessions[session_id]


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get the current logged-in user from session."""
    session_id = request.cookies.get("session_id")
    session = get_session(session_id)
    if session:
        return db.query(User).filter(User.id == session["user_id"]).first()
    return None


def require_auth(request: Request, db: Session = Depends(get_db)) -> User:
    """Dependency that requires authentication."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    """Render login page."""
    # If already logged in, redirect to dashboard
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": None
    })


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission."""
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not user.verify_password(password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        }, status_code=401)
    
    if not user.is_active:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Your account has been deactivated"
        }, status_code=401)
    
    # Create session
    session_id = create_session(user.id)
    
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=60 * 60 * 24 * 7,  # 7 days
        samesite="lax"
    )
    return response


@router.get("/logout")
async def logout(request: Request):
    """Handle logout."""
    session_id = request.cookies.get("session_id")
    if session_id:
        delete_session(session_id)
    
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_id")
    return response


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """Render forgot password page."""
    return templates.TemplateResponse("forgot_password.html", {
        "request": request,
        "message": None,
        "error": None
    })


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle forgot password form submission."""
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Generate reset token
        token = User.generate_reset_token()
        user.reset_token = token
        user.reset_token_expires = datetime.now() + timedelta(hours=1)
        db.commit()
        
        # In a real app, send email here
        # For now, we'll show the reset link (in production, this would be emailed)
        reset_link = f"/reset-password?token={token}"
        
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "message": f"If an account exists with that email, a password reset link has been sent. For demo purposes, use this link: {reset_link}",
            "error": None
        })
    
    # Don't reveal if email exists or not
    return templates.TemplateResponse("forgot_password.html", {
        "request": request,
        "message": "If an account exists with that email, a password reset link has been sent.",
        "error": None
    })


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str = None, db: Session = Depends(get_db)):
    """Render reset password page."""
    if not token:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": "Invalid or missing reset token",
            "token": None
        })
    
    # Verify token
    user = db.query(User).filter(
        User.reset_token == token,
        User.reset_token_expires > datetime.now()
    ).first()
    
    if not user:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": "Invalid or expired reset token. Please request a new password reset.",
            "token": None
        })
    
    return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "error": None,
        "token": token
    })


@router.post("/reset-password")
async def reset_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle reset password form submission."""
    if password != confirm_password:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": "Passwords do not match",
            "token": token
        })
    
    if len(password) < 4:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": "Password must be at least 4 characters",
            "token": token
        })
    
    user = db.query(User).filter(
        User.reset_token == token,
        User.reset_token_expires > datetime.now()
    ).first()
    
    if not user:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "error": "Invalid or expired reset token",
            "token": None
        })
    
    # Update password
    user.set_password(password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": None,
        "success": "Your password has been reset successfully. Please log in."
    })
