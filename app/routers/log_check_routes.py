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
from app.models import Category, Customer
from app.models.log_entry import LogEntry
from app.models.check_category import CheckCategory

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
    start_time: Optional[str] = None  # For manual mode: "HH:MM"
    start_period: Optional[str] = None  # "AM" or "PM"
    end_time: Optional[str] = None
    end_period: Optional[str] = None
    date_str: Optional[str] = None  # "MM/DD/YYYY"
    category_name: Optional[str] = None  # For custom checks
    message: Optional[str] = None  # For custom checks
    customer_id: Optional[int] = None


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
async def log_check_page(request: Request, db: Session = Depends(get_db)):
    """Render main log check page."""
    categories = db.query(Category).all()
    customers = db.query(Customer).order_by(Customer.name).all()
    check_categories = db.query(CheckCategory).order_by(CheckCategory.name).all()
    
    # Get recent logs for preview
    recent_logs = db.query(LogEntry).order_by(desc(LogEntry.created_at)).limit(5).all()
    
    return templates.TemplateResponse("log_check.html", {
        "request": request,
        "categories": categories,
        "customers": customers,
        "check_categories": check_categories,
        "recent_logs": recent_logs,
        "onsite_options": ONSITE_OPTIONS
    })


@router.get("/log-check/history", response_class=HTMLResponse)
async def log_history_page(request: Request, db: Session = Depends(get_db)):
    """Render log history page."""
    categories = db.query(Category).all()
    logs = db.query(LogEntry).order_by(desc(LogEntry.created_at)).all()
    check_categories = db.query(CheckCategory).order_by(CheckCategory.name).all()
    
    return templates.TemplateResponse("log_history.html", {
        "request": request,
        "categories": categories,
        "logs": logs,
        "check_categories": check_categories
    })


# ==================== API ROUTES ====================

@router.post("/api/log-check/generate")
async def generate_log(request: LogGenerateRequest, db: Session = Depends(get_db)):
    """Generate and save a log entry."""
    now = datetime.now()
    
    if request.mode == "manual":
        # Parse manual times
        if not all([request.start_time, request.start_period, request.end_time, request.end_period]):
            raise HTTPException(status_code=400, detail="Manual mode requires start and end times")
        
        date_str = request.date_str or format_date(now)
        start_time_str = f"{request.start_time} {request.start_period.lower().replace('am', 'a.m').replace('pm', 'p.m')}"
        end_time_str = f"{request.end_time} {request.end_period.lower().replace('am', 'a.m').replace('pm', 'p.m')}"
        
        # Calculate duration
        try:
            start_parts = request.start_time.split(":")
            end_parts = request.end_time.split(":")
            start_hour = int(start_parts[0])
            start_min = int(start_parts[1]) if len(start_parts) > 1 else 0
            end_hour = int(end_parts[0])
            end_min = int(end_parts[1]) if len(end_parts) > 1 else 0
            
            # Convert to 24-hour for calculation
            if request.start_period.upper() == "PM" and start_hour != 12:
                start_hour += 12
            elif request.start_period.upper() == "AM" and start_hour == 12:
                start_hour = 0
            if request.end_period.upper() == "PM" and end_hour != 12:
                end_hour += 12
            elif request.end_period.upper() == "AM" and end_hour == 12:
                end_hour = 0
            
            duration_minutes = (end_hour * 60 + end_min) - (start_hour * 60 + start_min)
            if duration_minutes <= 0:
                raise HTTPException(status_code=400, detail="End time must be after start time")
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid time format")
    else:
        # Automatic mode
        total_minutes = request.hours * 60 + request.minutes
        duration_minutes = total_minutes
        
        start_dt = now
        end_dt = now + timedelta(minutes=total_minutes)
        
        date_str = format_date(start_dt)
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
        full_entry=full_entry,
        customer_id=request.customer_id if request.customer_id else None
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
    customer_id: Optional[int] = None,
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
    if customer_id:
        query = query.filter(LogEntry.customer_id == customer_id)
    
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
                "customer_id": log.customer_id,
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
async def get_check_categories(db: Session = Depends(get_db)):
    """Get all check categories."""
    cats = db.query(CheckCategory).order_by(CheckCategory.name).all()
    return {
        "categories": [
            {"id": c.id, "name": c.name, "description": c.description}
            for c in cats
        ]
    }


@router.post("/api/log-check/categories")
async def create_check_category(request: CategoryRequest, db: Session = Depends(get_db)):
    """Create a new check category."""
    existing = db.query(CheckCategory).filter(CheckCategory.name == request.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    cat = CheckCategory(name=request.name, description=request.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    
    return {"success": True, "id": cat.id, "name": cat.name}


@router.put("/api/log-check/categories/{category_id}")
async def update_check_category(category_id: int, request: CategoryRequest, db: Session = Depends(get_db)):
    """Update a check category."""
    cat = db.query(CheckCategory).filter(CheckCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    cat.name = request.name
    cat.description = request.description
    db.commit()
    
    return {"success": True, "message": "Category updated"}


@router.delete("/api/log-check/categories/{category_id}")
async def delete_check_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a check category."""
    cat = db.query(CheckCategory).filter(CheckCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(cat)
    db.commit()
    
    return {"success": True, "message": "Category deleted"}
