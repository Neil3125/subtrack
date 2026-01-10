"""Saved Reports API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.saved_report import SavedReport
from app.models.user import User
from app.routers.auth_routes import get_current_user
from pydantic import BaseModel

router = APIRouter()


class SavedReportCreate(BaseModel):
    """Schema for creating a saved report."""
    name: str
    description: Optional[str] = None
    report_type: str
    configuration: dict


class SavedReportUpdate(BaseModel):
    """Schema for updating a saved report."""
    name: Optional[str] = None
    description: Optional[str] = None
    configuration: Optional[dict] = None


class SavedReportResponse(BaseModel):
    """Schema for saved report response."""
    id: int
    user_id: Optional[int]
    name: str
    description: Optional[str]
    report_type: str
    configuration: dict
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/saved-reports", response_model=SavedReportResponse, status_code=201)
def create_saved_report(
    report: SavedReportCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create a new saved report."""
    db_report = SavedReport(
        user_id=current_user.id if current_user else None,
        name=report.name,
        description=report.description,
        report_type=report.report_type,
        configuration=report.configuration
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/saved-reports", response_model=List[SavedReportResponse])
def list_saved_reports(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """List all saved reports for the current user."""
    if current_user:
        # Get user's reports
        reports = db.query(SavedReport).filter(
            SavedReport.user_id == current_user.id
        ).order_by(SavedReport.created_at.desc()).all()
    else:
        # If no user, return all reports (for demo purposes)
        reports = db.query(SavedReport).order_by(SavedReport.created_at.desc()).all()
    
    return reports


@router.get("/saved-reports/{report_id}", response_model=SavedReportResponse)
def get_saved_report(report_id: int, db: Session = Depends(get_db)):
    """Get a saved report by ID."""
    report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/saved-reports/{report_id}", response_model=SavedReportResponse)
def update_saved_report(
    report_id: int,
    report: SavedReportUpdate,
    db: Session = Depends(get_db)
):
    """Update a saved report."""
    db_report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    update_data = report.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db_report.updated_at = datetime.now()
    db.commit()
    db.refresh(db_report)
    return db_report


@router.delete("/saved-reports/{report_id}", status_code=204)
def delete_saved_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a saved report."""
    db_report = db.query(SavedReport).filter(SavedReport.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(db_report)
    db.commit()
    return None
