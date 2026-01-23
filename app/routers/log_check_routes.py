"""Log check routes for log generation and history."""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from app.models import Category
from app.models.log_entry import LogEntry
from app.models.check_category import CheckCategory
from app.models.user import User
from app.routers.auth_routes import get_current_user, require_auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Default log messages (from desktop app)
LOG_MESSAGES = {
    'service': "Logged onto Servers. Checked system logs, DNS and DHCP entries, disk health and usage. Checked ESET logs. Checked volume shadow copies.",
    'backup': "Logged onto Servers. Checked backup jobs. Checked data integrity and verified that all jobs finished successfully.",
}

# On-Site options
ONSITE_OPTIONS = [
    "Changed Backup Drive",
    "Changed Image Drive", 
    "Changed Backup and Image Drive"
]


# Pydantic models for request/response
class LogGenerateRequest(BaseModel):
    check_type: str  # 'service', 'backup', 'custom', 'onsite'
    mode: str = "automatic"  # 'automatic' or 'manual'
    hours: int = 0
    minutes: int = 30
    start_time: Optional[str] = None  # Formatted as "H:MM AM/PM" or just "HH:MM"
    end_time: Optional[str] = None    # Formatted as "H:MM AM/PM" or just "HH:MM"
    date_str: Optional[str] = None    # "MM/DD/YYYY"
    category_name: Optional[str] = None  # For custom checks
    message: Optional[str] = None  # For custom checks


class CategoryRequest(BaseModel):
    name: str
    description: Optional[str] = None


class LogUpdateRequest(BaseModel):
    full_entry: str


def format_date(dt: datetime) -> str:
    """Format date as M/D/YYYY (no leading zeros)."""
    return f"{dt.month}/{dt.day}/{dt.year}"


def format_time(dt: datetime) -> str:
    """Format time as H:MM a.m/p.m (no leading zeros)."""
    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    minute = dt.minute
    period = "a.m" if dt.hour < 12 else "p.m"
    return f"{hour}:{minute:02d} {period}"


def parse_human_time(time_str: str) -> tuple[int, int]:
    """
    Parse a user entered time string into (hour_24, minute).
    Supports: "10:30 PM", "1030", "14:00", "2pm"
    """
    if not time_str:
        raise ValueError("Time string is empty")
    
    clean = time_str.lower().strip()
    is_pm = "pm" in clean or "p.m" in clean
    is_am = "am" in clean or "a.m" in clean
    
    # Remove am/pm for parsing numbers
    clean = clean.replace("pm", "").replace("p.m", "").replace("am", "").replace("a.m", "").strip()
    
    if ":" in clean:
        parts = clean.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
    elif len(clean) >= 3 and clean.isdigit():
        # "1030" -> 10:30, "130" -> 1:30
        minute = int(clean[-2:])
        hour = int(clean[:-2])
    elif clean.isdigit():
        # "10" -> 10:00
        hour = int(clean)
        minute = 0
    else:
        raise ValueError("Invalid time format")
        
    # Handle AM/PM logic
    if is_pm and hour < 12:
        hour += 12
    if is_am and hour == 12:
        hour = 0
        
    if hour > 23 or minute > 59:
        raise ValueError("Invalid time value")
        
    return hour, minute


def format_time_str(hour: int, minute: int) -> str:
    """Format 24h hour/minute to display string e.g. '2:30 p.m'."""
    dt = datetime.now().replace(hour=hour, minute=minute)
    return format_time(dt)


def generate_log_entry(
    check_type: str,
    date_str: str,
    start_time_str: str,
    end_time_str: str,
    duration_minutes: int,
    message: str,
    category_name: Optional[str] = None
) -> str:
    """Generate a formatted log entry string."""
    if check_type == 'custom' and category_name:
        check_name = category_name
    elif check_type == 'onsite':
        check_name = 'On-Site'
    elif check_type == 'service':
        check_name = 'Service Check'
    elif check_type == 'backup':
        check_name = 'Backup Check'
    else:
        check_name = 'Check'
    
    entry = f"[{date_str}][Start: {start_time_str}][{check_name}] {message} [End: {end_time_str}] [Duration: {duration_minutes} mins]"
    return entry


# ==================== WEB ROUTES ====================

@router.get("/log-check", response_class=HTMLResponse)
async def log_check_page(request: Request, db: Session = Depends(get_db), user: User = Depends(require_auth)):
    """Render main log check page."""
    # Get user-specific categories
    check_categories = db.query(CheckCategory).filter(
        (CheckCategory.user_id == user.id) | (CheckCategory.user_id.is_(None))
    ).order_by(CheckCategory.name).all()
    
    # Get recent logs for preview
    recent_logs = db.query(LogEntry).order_by(desc(LogEntry.created_at)).limit(5).all()
    
    return templates.TemplateResponse("log_check.html", {
        "request": request,
        "check_categories": check_categories,
        "recent_logs": recent_logs,
        "onsite_options": ONSITE_OPTIONS,
        "user": user
    })


@router.get("/log-check/history", response_class=HTMLResponse)
async def log_history_page(request: Request, db: Session = Depends(get_db)):
    """Render log history page."""
    logs = db.query(LogEntry).order_by(desc(LogEntry.created_at)).all()
    
    # Need to fetch categories for filtering dropdown in history if needed
    categories = db.query(CheckCategory).all()
    
    return templates.TemplateResponse("log_history.html", {
        "request": request,
        "logs": logs,
        "check_categories": categories
    })


# ==================== API ROUTES ====================

@router.post("/api/log-check/generate")
async def generate_log(
    request: LogGenerateRequest, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user) # Optional auth for API
):
    """Generate and save a log entry."""
    now = datetime.now()
    date_str = request.date_str or format_date(now)

    if request.mode == "manual":
        # Parse flexible manual times
        try:
            start_h, start_m = parse_human_time(request.start_time)
            end_h, end_m = parse_human_time(request.end_time)
            
            start_time_str = format_time_str(start_h, start_m)
            end_time_str = format_time_str(end_h, end_m)
            
            # Calculate duration
            start_total = start_h * 60 + start_m
            end_total = end_h * 60 + end_m
            
            duration_minutes = end_total - start_total
            if duration_minutes <= 0:
                # Handle overnight or error - for now assume error
                raise HTTPException(status_code=400, detail="End time must be after start time")
                
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        # Automatic mode
        total_minutes = request.hours * 60 + request.minutes
        duration_minutes = total_minutes
        
        start_dt = now
        end_dt = now + timedelta(minutes=total_minutes)
        
        # Override date if provided, otherwise use today
        if request.date_str:
             date_str = request.date_str
        
        start_time_str = format_time(start_dt)
        end_time_str = format_time(end_dt)
    
    # Determine message
    if request.check_type == 'custom':
        if not request.message:
            raise HTTPException(status_code=400, detail="Custom check requires a message")
        message = request.message
    elif request.check_type == 'onsite':
        message = request.message or "On-site support provided."
    else:
        message = LOG_MESSAGES.get(request.check_type, "Check completed.")
    
    # Generate full entry
    full_entry = generate_log_entry(
        check_type=request.check_type,
        date_str=date_str,
        start_time_str=start_time_str,
        end_time_str=end_time_str,
        duration_minutes=duration_minutes,
        message=message,
        category_name=request.category_name
    )
    
    # Save to database
    log_entry = LogEntry(
        date_str=date_str,
        start_time=start_time_str,
        end_time=end_time_str,
        duration_minutes=duration_minutes,
        check_type=request.check_type,
        category_name=request.category_name,
        message=message,
        full_entry=full_entry
    )
    
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    return {
        "success": True,
        "log_id": log_entry.id,
        "full_entry": full_entry,
        "message": "Log entry generated and saved"
    }


@router.get("/api/log-check/logs")
async def get_logs(
    search: Optional[str] = None,
    check_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get log entries with optional filters."""
    query = db.query(LogEntry)
    
    if search:
        query = query.filter(LogEntry.full_entry.ilike(f"%{search}%"))
    if check_type:
        query = query.filter(LogEntry.check_type == check_type)
    
    total = query.count()
    logs = query.order_by(desc(LogEntry.created_at)).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "logs": [
            {
                "id": log.id,
                "created_at": log.created_at.isoformat(),
                "date_str": log.date_str,
                "check_type": log.check_type,
                "category_name": log.category_name,
                "full_entry": log.full_entry,
                "duration_minutes": log.duration_minutes
            }
            for log in logs
        ]
    }


@router.put("/api/log-check/logs/{log_id}")
async def update_log(log_id: int, request: LogUpdateRequest, db: Session = Depends(get_db)):
    """Update a log entry."""
    log = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")
    
    log.full_entry = request.full_entry
    db.commit()
    
    return {"success": True, "message": "Log entry updated"}


@router.delete("/api/log-check/logs/{log_id}")
async def delete_log(log_id: int, db: Session = Depends(get_db)):
    """Delete a log entry."""
    log = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")
    
    db.delete(log)
    db.commit()
    
    return {"success": True, "message": "Log entry deleted"}


# ==================== CATEGORY API ====================

@router.get("/api/log-check/categories")
async def get_check_categories(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get check categories for current user."""
    query = db.query(CheckCategory)
    
    if user:
        # Show global (null user_id) and user specific
        query = query.filter((CheckCategory.user_id == user.id) | (CheckCategory.user_id.is_(None)))
    else:
        # Only show global if no user
        query = query.filter(CheckCategory.user_id.is_(None))
        
    cats = query.order_by(CheckCategory.name).all()
    return {
        "categories": [
            {"id": c.id, "name": c.name, "description": c.description}
            for c in cats
        ]
    }


@router.post("/api/log-check/categories")
async def create_check_category(
    request: CategoryRequest, 
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """Create a new check category for the current user."""
    # Check if category already exists for this user
    existing = db.query(CheckCategory).filter(
        CheckCategory.name == request.name,
        CheckCategory.user_id == user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    cat = CheckCategory(
        name=request.name, 
        description=request.description,
        user_id=user.id
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    
    return {"success": True, "id": cat.id, "name": cat.name}


@router.delete("/api/log-check/categories/{category_id}")
async def delete_check_category(
    category_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(require_auth)
):
    """Delete a check category."""
    cat = db.query(CheckCategory).filter(CheckCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
        
    # Security check: only allow deleting own categories
    if cat.user_id and cat.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this category")
    
    db.delete(cat)
    db.commit()
    
    return {"success": True, "message": "Category deleted"}
