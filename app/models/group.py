"""Group model."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Group(Base):
    """Group model for organizing customers within a category."""
    
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="groups")
    customers = relationship("Customer", back_populates="group", viewonly=True)
    
    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}', category_id={self.category_id})>"
